"""Machine learning operations."""
import os
import shutil

from pyspark.ml import Pipeline
from pyspark.ml.pipeline import PipelineModel
from pyspark.ml.classification import (LogisticRegression,
                                       OneVsRest,
                                       RandomForestClassifier)
from pyspark.ml.evaluation import (RegressionEvaluator,
                                   MulticlassClassificationEvaluator)

LR_PATH = f'{os.environ["WEB_SPARK_MODELS_PATH"]}/lr'
BC_PATH = f'{os.environ["WEB_SPARK_MODELS_PATH"]}/bc'
MCC_PATH = f'{os.environ["WEB_SPARK_MODELS_PATH"]}/mcc'


def logistic_regression(tr_data=None, t_data=None,
                        proc_type='train', example=None):
    """Performs logistic regression pipelining."""
    lr = LogisticRegression(regParam=0.001, family='multinomial')

    pipeline = Pipeline(stages=[lr])

    if proc_type == 'load' or proc_type == 'test':
        model = PipelineModel.load(LR_PATH)
    else:
        model = pipeline.fit(tr_data)
        if os.path.exists(LR_PATH):
            shutil.rmtree(LR_PATH)
        model.save(LR_PATH)

    if proc_type == 'test':
        result = model.transform(example).collect()

        return result, 0.
    else:
        prediction = model.transform(t_data)
        evaluator = RegressionEvaluator(metricName="rmse", labelCol="label",
                                        predictionCol="prediction")
        rmse = evaluator.evaluate(prediction)

        return None, rmse


def binary_classification(tr_data=None, t_data=None,
                          proc_type='train', example=None):
    """Performs binary classification pipelining."""
    lr = LogisticRegression(tol=1e-6, fitIntercept=True)
    ovr = OneVsRest(classifier=lr)

    pipeline = Pipeline(stages=[ovr])

    if proc_type == 'load' or proc_type == 'test':
        model = PipelineModel.load(BC_PATH)
    else:
        model = pipeline.fit(tr_data)
        if os.path.exists(BC_PATH):
            shutil.rmtree(BC_PATH)
        model.save(BC_PATH)

    if proc_type == 'test':
        result = model.transform(example).collect()

        return result, 0.
    else:
        prediction = model.transform(t_data)
        evaluator = MulticlassClassificationEvaluator(
            labelCol='label', predictionCol='prediction',
            metricName='f1')
        f1Score = evaluator.evaluate(prediction)

        return None, f1Score


def multi_class_classification(tr_data=None, t_data=None,
                               proc_type='train', example=None):
    """Performs multi-class classification pipelining."""
    rfc = RandomForestClassifier(labelCol='label', featuresCol='features',
                                 numTrees=10)

    pipeline = Pipeline(stages=[rfc])

    if proc_type == 'load' or proc_type == 'test':
        model = PipelineModel.load(MCC_PATH)
    else:
        model = pipeline.fit(tr_data)
        if os.path.exists(MCC_PATH):
            shutil.rmtree(MCC_PATH)
        model.save(MCC_PATH)

    if proc_type == 'test':
        result = model.transform(example).collect()

        return result, 0.
    else:
        prediction = model.transform(t_data)
        evaluator = MulticlassClassificationEvaluator(
            labelCol='label', predictionCol='prediction',
            metricName='accuracy')
        accuracy = evaluator.evaluate(prediction)

        return None, accuracy
