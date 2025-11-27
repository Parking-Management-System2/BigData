from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.sql.functions import col
from pyspark.sql.types import DoubleType

def get_spark_session(app_name="TelcoChurn"):
    return SparkSession.builder \
        .appName(app_name) \
        .master("local[*]") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.6.0") \
        .getOrCreate()

def load_and_clean_data(spark, file_path):
    df = spark.read.csv(file_path, header=True, inferSchema=True)
    
    # Czyszczenie danych
    df = df.withColumn("TotalCharges", col("TotalCharges").cast(DoubleType()))
    df = df.fillna(0.0, subset=["TotalCharges"])
    
    return df

def build_pipeline():
    categorical_cols = [
        "InternetService", "OnlineSecurity",
        "DeviceProtection", "TechSupport",
        "Contract", "PaymentMethod"
    ]
    numeric_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
    
    stages = []
    
    # Indeksowanie ciągów znaków (String Indexing)
    for categoricalCol in categorical_cols:
        stringIndexer = StringIndexer(inputCol=categoricalCol, outputCol=categoricalCol + "_Index", handleInvalid="keep")
        stages += [stringIndexer]
    
    # Składanie wektora cech (Vector Assembler)
    assemblerInputs = [c + "_Index" for c in categorical_cols] + numeric_cols
    assembler = VectorAssembler(inputCols=assemblerInputs, outputCol="features", handleInvalid="keep")
    stages += [assembler]
    
    return Pipeline(stages=stages)
