
"""Sample pySpark app."""

from docker_logs import get_logger

from pyspark.sql import SparkSession
from pyspark.ml.linalg import Vectors
from pyspark.sql import Row
from pyspark.sql import functions as F
from pyspark.ml.feature import QuantileDiscretizer

from logistic_regression import logistic_regression
from binary_classification import binary_classification
from multi_class_classification import multi_class_classification


logging = get_logger('spark_worker')

spark = SparkSession.builder.appName('MyModels').\
    config('spark.mongodb.input.uri',
           'mongodb://mongodb:27017/reddits.submissions').\
    getOrCreate()


def load(dev):
    """Loads the submissions from MongoDB database."""
    logging.info('Loading submissions...')
    df = dev.read.format('com.mongodb.spark.sql.DefaultSource').load()

    df.createOrReplaceTempView('submissions')
    df.printSchema()

    query = 'select score, upvote_ratio, is_nfsw, text_embedded from \
    submissions'
    df = dev.sql(query)

    df = df.rdd.map(lambda r: Row(
        score=r['score'],
        upvote_ratio=r['upvote_ratio'],
        is_nfsw=float(r['is_nfsw']),
        text_embedded=Vectors.dense(r['text_embedded']))).toDF()
    qd = QuantileDiscretizer(numBuckets=6, inputCol='upvote_ratio',
                             outputCol='upvote_class')
    df = qd.fit(df).transform(df)

    df.printSchema()
    df.show()
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


def perform(tr_data, t_data, pipeline_method, key_attribute, title, abbr, ind):
    """Performs given pipelining."""
    result, measure = pipeline_method(
        tr_data.selectExpr('text_embedded as features',
                           f'{key_attribute} as label'),
        t_data.selectExpr('text_embedded as features',
                          f'{key_attribute} as label'))
    result = spark.createDataFrame(Row('embeddings',
                                       f'{key_attribute}',
                                       'prediction')(x[0], x[1], x[ind])
                                   for i, x in enumerate(result))
    logging.info(f'{title}:')
    result.show(5)
    logging.info(f'{abbr}: {measure}')


def main():
    """Main function."""
    df = load(spark)

    train_data, test_data = split(df, ratio=0.8)
    logging.info(f'Total available: {df.count()}')
    logging.info(f'Train: {train_data.count()}')
    logging.info(f'Test: {test_data.count()}')

    perform(train_data, test_data, pipeline_method=logistic_regression,
            key_attribute='score', title='Score logistic regression',
            abbr='RMSE', ind=4)
    perform(train_data, test_data, pipeline_method=binary_classification,
            key_attribute='is_nfsw', title='NFSW binary classification',
            abbr='F1 score', ind=2)
    perform(train_data, test_data, pipeline_method=multi_class_classification,
            key_attribute='upvote_class',
            title='Upvote class multi-class classification', abbr='Accuracy',
            ind=4)


if __name__ == '__main__':
    main()
