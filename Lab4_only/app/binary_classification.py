
"""Binary classification pipeline."""

from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression, OneVsRest
from pyspark.ml.evaluation import MulticlassClassificationEvaluator


def binary_classification(tr_data, t_data):
    """Performs binary classification pipelining."""
    lr = LogisticRegression(tol=1e-6, fitIntercept=True)
    ovr = OneVsRest(classifier=lr)

    pipeline = Pipeline(stages=[ovr])

    model = pipeline.fit(tr_data)
    prediction = model.transform(t_data)
    # prediction.show(5)

    evaluator = MulticlassClassificationEvaluator(labelCol='label',
                                                  predictionCol='prediction',
                                                  metricName='f1')
    f1Score = evaluator.evaluate(prediction)

    result = prediction.collect()

    return result, f1Score
