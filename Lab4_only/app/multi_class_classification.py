
"""Multi-class classification pipeline."""

from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator


def multi_class_classification(tr_data, t_data):
    """Performs multi-class classification pipelining."""
    rfc = RandomForestClassifier(labelCol='label', featuresCol='features',
                                 numTrees=10)

    pipeline = Pipeline(stages=[rfc])

    model = pipeline.fit(tr_data)
    prediction = model.transform(t_data)
    # prediction.show(5)

    evaluator = MulticlassClassificationEvaluator(labelCol='label',
                                                  predictionCol='prediction',
                                                  metricName='accuracy')
    accuracy = evaluator.evaluate(prediction)

    result = prediction.collect()

    return result, accuracy
