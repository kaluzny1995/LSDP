"""Machine learning operations."""
import os
import shutil

from pyspark.ml import Pipeline
from pyspark.ml.classification import (LogisticRegression,
                                       OneVsRest,
                                       RandomForestClassifier,
                                       LogisticRegressionModel)
from pyspark.ml.evaluation import (RegressionEvaluator,
                                   MulticlassClassificationEvaluator)

LR_PATH = 'server/main/spark_models/lr.model'
BC_PATH = 'server/main/spark_models/bc.model'
MCC_PATH = 'server/main/spark_models/mcc.model'


def logistic_regression(tr_data, t_data, example=None):
    """Performs logistic regression pipelining."""
    lr = LogisticRegression(regParam=0.001, family='multinomial')

    pipeline = Pipeline(stages=[lr])

    model = pipeline.fit(tr_data)
    prediction = model.transform(t_data)

    evaluator = RegressionEvaluator(metricName="rmse", labelCol="label",
                                    predictionCol="prediction")
    rmse = evaluator.evaluate(prediction)

    if os.path.exists(LR_PATH):
        shutil.rmtree(LR_PATH)
    model.save(LR_PATH)

    result = None if not example else model.transform(example).collect()

    return result, rmse


def get_lr_model():
    """Loads the LogisticRegressionModel from path."""
    return LogisticRegressionModel.load(LR_PATH)


def binary_classification(tr_data, t_data, example=None):
    """Performs binary classification pipelining."""
    lr = LogisticRegression(tol=1e-6, fitIntercept=True)
    ovr = OneVsRest(classifier=lr)

    pipeline = Pipeline(stages=[ovr])

    model = pipeline.fit(tr_data)
    prediction = model.transform(t_data)

    evaluator = MulticlassClassificationEvaluator(labelCol='label',
                                                  predictionCol='prediction',
                                                  metricName='f1')
    f1Score = evaluator.evaluate(prediction)

    if os.path.exists(BC_PATH):
        shutil.rmtree(BC_PATH)
    model.save(BC_PATH)

    result = None if not example else model.transform(example).collect()

    return result, f1Score


def multi_class_classification(tr_data, t_data, example=None):
    """Performs multi-class classification pipelining."""
    rfc = RandomForestClassifier(labelCol='label', featuresCol='features',
                                 numTrees=10)

    pipeline = Pipeline(stages=[rfc])

    model = pipeline.fit(tr_data)
    prediction = model.transform(t_data)

    evaluator = MulticlassClassificationEvaluator(labelCol='label',
                                                  predictionCol='prediction',
                                                  metricName='accuracy')
    accuracy = evaluator.evaluate(prediction)

    if os.path.exists(MCC_PATH):
        shutil.rmtree(MCC_PATH)
    model.save(MCC_PATH)

    result = None if not example else model.transform(example).collect()

    return result, accuracy
