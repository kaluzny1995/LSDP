
"""Logistic regression pipeline."""

from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import RegressionEvaluator


def logistic_regression(tr_data, t_data):
    """Performs logistic regression pipelining."""
    lr = LogisticRegression(regParam=0.001, family='multinomial')

    pipeline = Pipeline(stages=[lr])

    model = pipeline.fit(tr_data)
    prediction = model.transform(t_data)
    # prediction.show(5)

    evaluator = RegressionEvaluator(metricName="rmse", labelCol="label",
                                    predictionCol="prediction")
    rmse = evaluator.evaluate(prediction)

    result = prediction.collect()

    return result, rmse
