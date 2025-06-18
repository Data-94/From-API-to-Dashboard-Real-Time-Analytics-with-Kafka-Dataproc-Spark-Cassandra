

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("spark-kafka-cassandra") \
    .config("spark.cassandra.connection.host", "34.78.12.94") \
    .config("spark.cassandra.connection.port", "9042") \
    .getOrCreate()

# spark = SparkSession.builder.appName("spark-kafka-cassandra") \
#     .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
#     .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.12:3.2.0") \
#     .config("spark.cassandra.connection.host", "34.78.12.94") \
#     .config("spark.cassandra.connection.port", "9042") \
#     .getOrCreate()

# spark daki kurulu jarları görmek için
# spark.sparkContext.getConf().getAll()

df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "34.78.12.94:9092") \
    .option("subscribe", "kur").load()

df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
from pyspark.sql.types import StructType, StructField, StringType, FloatType,TimestampType

schema = StructType([
    StructField("id", StringType(), True),
    StructField("BanknoteBuying", FloatType(), True),
    StructField("BanknoteSelling", FloatType(), True),
    StructField("CrossRateOther", StringType(), True),
    StructField("CrossRateUSD", FloatType(), True),
    StructField("CurrencyName", StringType(), True),
    StructField("ForexBuying", FloatType(), True),
    StructField("ForexSelling", FloatType(), True),
    StructField("Isim", StringType(), True),
    StructField("Tarih", StringType(), True)
])


from pyspark.sql.functions import from_json

df = df.withColumn("value", from_json("value", schema)).select("value.*")


df = df.withColumnRenamed("BanknoteBuying", "banknotebuying") \
    .withColumnRenamed("BanknoteSelling", "banknoteselling") \
    .withColumnRenamed("CrossRateOther", "crossrateother") \
    .withColumnRenamed("CrossRateUSD", "crossrateusd") \
    .withColumnRenamed("CurrencyName", "currencyname") \
    .withColumnRenamed("ForexBuying", "forexbuying") \
    .withColumnRenamed("ForexSelling", "forexselling") \
    .withColumnRenamed("Isim", "isim") \
    .withColumnRenamed("Tarih", "tarih")

# tarih formatını değiştirme '2024-05-01 15:40:00' -> '2024-05-01 15:40:00'
from pyspark.sql.functions import to_timestamp
df = df.withColumn("tarih", to_timestamp("tarih", "yyyy-MM-dd HH:mm:ss"))



df.writeStream.format("org.apache.spark.sql.cassandra") \
    .option("keyspace", "test") \
    .option("table", "currency") \
    .option("checkpointLocation", "/tmp/checkpoint") \
    .start() \
    .awaitTermination()