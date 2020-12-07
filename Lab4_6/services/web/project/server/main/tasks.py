"""Application tasks."""
import traceback
import numpy as np
try:
    import fasttext
    from nltk.tokenize import WordPunctTokenizer

    from pyspark.sql import SparkSession

    from pyspark.ml.linalg import Vectors
    from pyspark.sql import Row
    from pyspark.sql import functions as F
    from pyspark.ml.feature import QuantileDiscretizer

    from server.main.ml import logistic_regression, binary_classification,\
        multi_class_classification
except Exception as e:
    print('Error!')
    tb = traceback.TracebackException.from_exception(e)
    print(''.join(tb.format()))

from server.main.docker_logs import get_logger
logging = get_logger('redis-flask-worker')


def load_submissions():
    """Loads Reddit submissions."""
    sc = SparkSession.builder.appName('MyModels')\
        .config('spark.mongodb.input.uri',
                'mongodb://mongodb:27017/reddits.submissions')\
        .getOrCreate()

    df = sc.read.format('com.mongodb.spark.sql.DefaultSource').load()
    df.createOrReplaceTempView('submissions')
    df = df.select("id", "time", "author", "title")

    def getrows(frame, rownums=None):
        return frame.rdd.zipWithIndex()\
            .filter(lambda x: x[1] in rownums)\
            .map(lambda x: x[0].asDict(True))

    row = getrows(df, rownums=range(10)).collect()
    sc.stop()

    return row


def load_dataframe(sc):
    """Loads the submissions from MongoDB database."""
    df = sc.read.format('com.mongodb.spark.sql.DefaultSource').load()
    df.createOrReplaceTempView('submissions')

    query = 'select score, upvote_ratio, is_nfsw, text_embedded\
        from submissions'
    df = sc.sql(query)

    df = df.rdd.map(lambda r: Row(
        score=r['score'],
        upvote_ratio=r['upvote_ratio'],
        is_nfsw=float(r['is_nfsw']),
        text_embedded=Vectors.dense(r['text_embedded']))).toDF()
    qd = QuantileDiscretizer(numBuckets=6, inputCol='upvote_ratio',
                             outputCol='upvote_class')
    df = qd.fit(df).transform(df)

    return df


def split(data, ratio):
    """Splits into train and test datasets by indices."""
    count, train_count, test_count =\
        data.count(), int(data.count() * ratio),\
        int(data.count() * (1 - ratio) + 1)
    d = data.withColumn("index", F.monotonically_increasing_id())

    tr_data = d.filter(d.index.between(0, train_count - 1)).drop('index')
    t_data = d.filter(d.index.between(count - test_count, count - 1)).\
        drop('index')

    return tr_data, t_data


def perform(tr_data, t_data, pipeline_method, key_attribute, example=None):
    """Performs given pipelining."""
    result, measure = pipeline_method(
        tr_data.selectExpr('text_embedded as features',
                           f'{key_attribute} as label'),
        t_data.selectExpr('text_embedded as features',
                          f'{key_attribute} as label'),
        example=example
    )

    return result, measure


def train_all_models():
    """Train all three ML models."""
    sc = SparkSession.builder.appName('MyModels')\
        .config('spark.mongodb.input.uri',
                'mongodb://mongodb:27017/reddits.submissions')\
        .getOrCreate()

    df = load_dataframe(sc)

    train_data, test_data = split(df, ratio=0.8)

    _, rmse = perform(train_data, test_data,
                      pipeline_method=logistic_regression,
                      key_attribute='score')
    _, f1 = perform(train_data, test_data,
                    pipeline_method=binary_classification,
                    key_attribute='is_nfsw')
    _, accuracy = perform(train_data, test_data,
                          pipeline_method=multi_class_classification,
                          key_attribute='upvote_class')

    results = {'total': df.count(), 'train': train_data.count(),
               'test': test_data.count(),
               'lr_title': 'Score logistic regression',
               'lr_abbr': 'RMSE', 'lr_result': rmse,
               'bc_title': 'Whether is NFSW binary classification',
               'bc_abbr': 'F1', 'bc_result': f1,
               'mcc_title': 'Upvote ratio class multi-class classification',
               'mcc_abbr': 'Accuracy', 'mcc_result': accuracy}

    sc.stop()

    return results


def embed(text):
    """Embedds text."""
    tokenizer = WordPunctTokenizer()
    model_path = 'server/main/dbpedia.bin'
    ft_model = fasttext.load_model(model_path)

    example = [ft_model[token] for token in tokenizer.tokenize(text)]
    example = np.mean(example, axis=0).tolist()

    return example


def test_all_models(text):
    """Test all three ML models."""
    embeddings = embed(text)
    logging.info(f'Embeddings: {embeddings}')

    sc = SparkSession.builder.appName('MyModels')\
        .config('spark.mongodb.input.uri',
                'mongodb://mongodb:27017/reddits.submissions')\
        .getOrCreate()

    df = load_dataframe(sc)

    emb_data = sc.createDataFrame(
        [(0., Vectors.dense(embeddings))], ['label', 'features'])

    train_data, test_data = split(df, ratio=0.8)

    lr_pred, rmse = perform(train_data, test_data,
                            pipeline_method=logistic_regression,
                            key_attribute='score', example=emb_data)
    bc_pred, f1 = perform(train_data, test_data,
                          pipeline_method=binary_classification,
                          key_attribute='is_nfsw', example=emb_data)
    mcc_pred, accuracy = perform(train_data, test_data,
                                 pipeline_method=multi_class_classification,
                                 key_attribute='upvote_class', example=emb_data)

    results = {'lr_pred': lr_pred[0]["prediction"],
               'lr_m': 'Logistic Regression',
               'lr_q': 'What score might the reddit gain?',
               'bc_pred': bc_pred[0]["prediction"],
               'bc_m': 'Binary Classification',
               'bc_q': 'Is reddit NFSW (not safe for work)?',
               'mcc_pred': mcc_pred[0]["prediction"],
               'mcc_m': 'Multi Class Classification',
               'mcc_q': 'Which upvote ratio class might the reddit gain?'}

    sc.stop()

    return results
