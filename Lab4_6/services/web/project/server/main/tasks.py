"""Application tasks."""
import os
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

FT_MODEL_PATH = f'{os.environ["WEB_HOME"]}/server/main/dbpedia.bin'
SPARK_SQL_DEFAULT = 'com.mongodb.spark.sql.DefaultSource'
SPARK_MONGODB_CONFIG = 'spark.mongodb.input.uri'
SPARK_MONGODB_CONNECTION = f'mongodb://{os.environ["MONGODB_HOST"]}:'\
    + f'{os.environ["MONGODB_PORT"]}/reddits.submissions'


def check_models():
    """Checks whether the model files are present."""
    result = 1 if os.path.exists(f'{os.environ["WEB_SPARK_MODELS_PATH"]}/lr')\
        else 0
    results = {'present': result}

    return results


def load_submissions():
    """Loads Reddit submissions."""
    sc = SparkSession.builder.appName('MyModels')\
        .config(SPARK_MONGODB_CONFIG, SPARK_MONGODB_CONNECTION)\
        .getOrCreate()

    df = sc.read.format(SPARK_SQL_DEFAULT).load()
    df.createOrReplaceTempView('submissions')
    df = df.select("id", "time", "author", "title")

    def getrows(frame, rownums=None):
        return frame.rdd.zipWithIndex()\
            .filter(lambda x: x[1] in rownums)\
            .map(lambda x: x[0].asDict(True))

    row = getrows(df, rownums=range(10)).collect()
    sc.stop()

    return row


def _load_dataframe(sc):
    """Loads the submissions from MongoDB database."""
    df = sc.read.format(SPARK_SQL_DEFAULT).load()
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


def _split(data, ratio):
    """Splits into train and test datasets by indices."""
    count, train_count, test_count =\
        data.count(), int(data.count() * ratio),\
        int(data.count() * (1 - ratio) + 1)
    d = data.withColumn("index", F.monotonically_increasing_id())

    tr_data = d.filter(d.index.between(0, train_count - 1)).drop('index')
    t_data = d.filter(d.index.between(count - test_count, count - 1)).\
        drop('index')

    return tr_data, t_data


def _perform(tr_data, t_data, pipeline_method, key_attribute=None,
             proc_type='train', example=None):
    """Performs given pipelining."""
    if proc_type == 'test':
        result, measure = pipeline_method(proc_type=proc_type, example=example)
    else:
        result, measure = pipeline_method(
            tr_data.selectExpr('text_embedded as features',
                               f'{key_attribute} as label'),
            t_data.selectExpr('text_embedded as features',
                              f'{key_attribute} as label'),
            proc_type=proc_type,
            example=example
        )

    return result, measure


def proc_models(proc_type):
    """Processes (loads/trains/retrains) three ML models."""
    sc = SparkSession.builder.appName('MyModels')\
        .config(SPARK_MONGODB_CONFIG, SPARK_MONGODB_CONNECTION)\
        .getOrCreate()

    df = _load_dataframe(sc)

    train_data, test_data = _split(df, ratio=0.8)

    _, rmse = _perform(train_data, test_data,
                       pipeline_method=logistic_regression,
                       key_attribute='score', proc_type=proc_type)
    _, f1 = _perform(train_data, test_data,
                     pipeline_method=binary_classification,
                     key_attribute='is_nfsw', proc_type=proc_type)
    _, accuracy = _perform(train_data, test_data,
                           pipeline_method=multi_class_classification,
                           key_attribute='upvote_class', proc_type=proc_type)

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


def _embed(text):
    """Embedds text."""
    tokenizer = WordPunctTokenizer()
    ft_model = fasttext.load_model(FT_MODEL_PATH)

    example = [ft_model[token] for token in tokenizer.tokenize(text)]
    example = np.mean(example, axis=0).tolist()

    return example


def t_models(text):
    """Test all three ML models."""
    embeddings = _embed(text)

    sc = SparkSession.builder.appName('MyModels')\
        .config(SPARK_MONGODB_CONFIG, SPARK_MONGODB_CONNECTION)\
        .getOrCreate()

    emb_data = sc.createDataFrame(
        [(0., Vectors.dense(embeddings))], ['label', 'features'])

    lr_pred, _ = _perform(None, None,
                          pipeline_method=logistic_regression,
                          proc_type='test', example=emb_data)
    bc_pred, _ = _perform(None, None,
                          pipeline_method=binary_classification,
                          proc_type='test', example=emb_data)
    mcc_pred, _ = _perform(None, None,
                           pipeline_method=multi_class_classification,
                           proc_type='test', example=emb_data)

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
