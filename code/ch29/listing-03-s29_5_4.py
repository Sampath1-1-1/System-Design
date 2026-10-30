# Extracted from manuscript/book1-traditional/29-distributed-data-processing.md §29.5.4 (listing 3). Edit the manuscript, not this file.
"""PySpark: the same aggregation with the RDD API and the DataFrame API, plus a broadcast join.
Tested with PySpark 4.0.1 in local mode (Java 21); results are checked against plain Python."""
import random
from collections import Counter

from pyspark.sql import SparkSession, functions as F

spark = (SparkSession.builder.master("local[4]").appName("ch29-demo")
         .config("spark.sql.shuffle.partitions", "8")          # default is 200
         .config("spark.sql.adaptive.enabled", "true")          # AQE (default on since 3.2)
         .getOrCreate())
spark.sparkContext.setLogLevel("ERROR")

rng = random.Random(29)
pages = ["/home", "/search", "/item", "/cart", "/checkout"]
events = [(rng.randrange(1_000), rng.choice(pages)) for _ in range(50_000)]
users = [(u, rng.choice(["IN", "US", "DE", "BR"])) for u in range(1_000)]

# 1. RDD API: explicit functions, lineage parallelize -> map -> reduceByKey
rdd = spark.sparkContext.parallelize(events, numSlices=8)
views_rdd = dict(rdd.map(lambda e: (e[1], 1)).reduceByKey(lambda a, b: a + b).collect())

# 2. DataFrame API: declarative, optimized by Catalyst
ev = spark.createDataFrame(events, ["user_id", "page"]).cache()      # reused twice below
us = spark.createDataFrame(users, ["user_id", "country"])
views_df = {r["page"]: r["n"] for r in ev.groupBy("page").agg(F.count("*").alias("n")).collect()}

# 3. Join + aggregate; the small side is broadcast, so the large side is never shuffled for the join
by_country = (ev.join(F.broadcast(us), "user_id")
                .groupBy("country", "page").agg(F.count("*").alias("views")))
by_country.explain()                        # physical plan: BroadcastHashJoin, then one Exchange
result = {(r["country"], r["page"]): r["views"] for r in by_country.collect()}

# Check against plain Python
truth_pages = Counter(p for _, p in events)
country = dict(users)
truth_join = Counter((country[u], p) for u, p in events)
assert views_rdd == views_df == dict(truth_pages)
assert result == dict(truth_join)
print("views per page:", dict(sorted(views_df.items())))
print("country/page groups:", len(result), "- all checks passed")
spark.stop()
