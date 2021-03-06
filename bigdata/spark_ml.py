from pyspark.ml import Pipeline
from pyspark import SparkContext
import pyspark.sql.functions as fn
from pyspark.sql import SQLContext
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
from pyspark.ml.evaluation import BinaryClassificationEvaluator


sc = SparkContext()
sql_context = SQLContext(sc)

data = sql_context.read.format('com.databricks.spark.csv').options(header='true', inferschema='true'). \
    load(r"D:\workspace\sample\classification\breast_cancer.csv")
data = data.select([f for f in data.columns if f not in ['id']])
data.withColumn('bare_nuclei', data['bare_nuclei'].cast('int'))


print(data.filter(fn.isnull('bare_nuclei')).count())
data = data.dropna()
print(data.count(), data.filter(fn.isnull('bare_nuclei')).count())

print(data.show(5))
print(data.count())
print(data.describe().show())
print(data.select(fn.mean('class')).show())
print(data.groupBy('class').count().show())
print(data)


fields = data.columns
target = 'class'
feature_label = ['clump_thickness', 'unif_cell_size', 'unif_cell_shape', 'marg_adhesion',
                 'single_epith_cell_size', 'bare_nuclei', 'bland_chrom', 'norm_nucleoli', 'mitoses']

label_string = StringIndexer(inputCol='class', outputCol='label')
vec = VectorAssembler(inputCols=feature_label, outputCol="features")
pipeline = Pipeline(stages=[vec, label_string])

pipeline_model = pipeline.fit(data)
data_set = pipeline_model.transform(data)


train_data, test_data = data_set.randomSplit([0.7, 0.3], seed=0)
print(train_data.count(), test_data.count())

clf = LogisticRegression()
clf_model = clf.fit(train_data)
predict = clf_model.transform(test_data)

evaluator = BinaryClassificationEvaluator()
print(evaluator.evaluate(predict))


rf = RandomForestClassifier()
grid = ParamGridBuilder().addGrid(rf.numTrees, [1, 3, 5]) \
                         .addGrid(rf.maxDepth, [3, 5, 7]) \
                         .addGrid(rf.maxBins, [20, 30, 40]).build()

cv = CrossValidator(estimator=rf, evaluator=evaluator, estimatorParamMaps=grid, numFolds=5)

cv_model = cv.fit(train_data)
cv_model_predict = cv_model.transform(test_data)
print(evaluator.evaluate(cv_model_predict))


metrics = ComputeModelStatistics(evaluationMetric='classification',
                                 labelCol='label',
                                 scoresCol='probability',
                                 scoredLabelsCol='prediction').transform(test_predict)


