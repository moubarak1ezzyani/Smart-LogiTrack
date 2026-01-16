# Notes autour du projet

## DateTime
### strFtime vs strPtime : The Trick (pandas)
* `str F time:` Format.

    * **Action:** Date_obj --(format)--> Text
    

    * **Direction:** Object → String.

* `str P time:` Parse.
      
    * **Action:** Text --(parse/understand)--> Date_obj
    * **Direction:** String → Object.

## Instructions de Lancement

* Placez le fichier bronze_taxi.parquet dans le dossier data/.

* Exécutez : `docker-compose up --build`.

* Accédez à Airflow (localhost:8080, admin/admin) et activez le DAG smart_logitrack_pipeline.

* Une fois le DAG terminé (Données Silver créées + Modèle entraîné), testez l'API sur localhost:8000/docs.

## Bornze vs Silver vs Gold
In Data Engineering (specifically in the **Medallion Architecture**), **"Bronze"** refers to the **Raw Data Layer**.

Here is the hierarchy:

1. **🥉 Bronze (Raw):** The data exactly as it arrived from the source (CSV, Logs, APIs). No cleaning, no filtering. It is the "dump" of everything.
2. **🥈 Silver (Cleaned):** Data that has been filtered, cleaned, and has a fixed schema (removed nulls, fixed timestamps).
3. **🥇 Gold (Aggregated):** Business-level data ready for reports (e.g., "Daily Revenue", "Average Trip Time").

***
## venv in WSL / ubuntu
```bash
deactivate              # exit spark-venv
rm -rf venv     # Delete the Windows venv (from WSL)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pyspark     # if needed by this project
python -m ipykernel install --user --name proj --display-name "Python (proj)"
```
## columns
| Goal | Command |
| :---: | :---: |
Count Columns | `len(df_bronze.columns)` |
Count Rows | `df_bronze.count()` |
List Column Names | `print(df_bronze.columns)` |
Print Schema (Type & Name)	| `df_bronze.printSchema()` |

## selecting : object types 
```python
# Inline list comprehension : c -> col | t -> types => choose which one u will keep
df_bronze.select([c for c, t in df_bronze.dtypes if t.startswith('string')]).show(100)

# Get unique val
df_bronze.select('store_and_fwd_flag').distinct().show()
```

## 💡 The Golden Rule of Big Data Visualization

"Compute globally, plot locally."

* Aggregate or Sample the data using Spark (Server side).

* Convert that small result to Pandas (Local RAM).

* Plot using Matplotlib/Seaborn (Standard way).

## 📊 Recommended Graphs
For your Taxi/Logistics project, these are the only three you strictly need to start:
1. The Histogram (Target Distribution)

    * Why: To check if your data is normal or skewed (e.g., "Are most trips short, but some take 5 hours?").

    * Search for: Distribution Plot, Histogram.

2. The Scatter Plot (Feature vs. Target)

    * Why: To see relationships. Does trip_distance actually increase duration linearly? Are there weird outliers?

    * Search for: Bivariate Analysis, Scatter Plot.

3. Correlation Heatmap

    * Why: To see which columns are useless. If two columns are 99% correlated, you drop one.

    * Search for: Correlation Matrix Heatmap.


## distributions : with target OR not ?
You need to see both, but they serve different purposes. As a Junior Data Scientist, your priority should be Relationship with the Target.

=> **"Does this variable help me predict the answer?"**

### Feature vs. Target (Priority: ⭐⭐⭐⭐⭐)
* Numerical vs. Numerical (e.g., Distance vs. Duration)
    * Graph: **Scatter Plot**.

    * What to look for: A clear pattern (line or curve). If it looks like a random cloud of dust
    the feature is weak.

* Categorical vs. Numerical (e.g., Day of Week vs. Duration)
    * Graph: **Box Plot**.

    * What to look for: If the "boxes" are at different heights, that category matters. If all boxes look the same, the category is useless.

### Feature vs. Feature (Priority: ⭐⭐⭐)
=> **"Are these two variables saying the exact same thing?"**
You check this to avoid Multicollinearity (redundancy). 
If `Fare_Amount` and `Total_Amount` move perfectly together, you don't need both. It confuses linear models.

* Numerical vs. Numerical

    * Graph: Correlation Heatmap.

    * What to look for: Dark red or dark blue squares (values near 1.0 or -1.0). If two input features have 0.9 correlation, drop one of them.

## Commit to github:
| Prefix | Meaning | When to use it |
| :---: | :---: | :---: |
| `feat` | Feature | "You added something new (e.g., a new column, a new plot, a new calculation)."|
| `fix` | Fix | "You repaired a bug (e.g., the code was crashing, and now it works)."| 
| `docs` | Documentation | You only changed comments or the README file.|
| `chore` | Chore | "Maintenance work (e.g., moving files, updating libraries) that doesn't change the code logic."|
| `refactor` | Refactoring | You rewrote code to make it cleaner but didn't change what it actually does.|


## Encoding
Variable Type,Example,Technique,Result
Binary,Yes / No,StringIndexer only,"0, 1"
Nominal,Vendor A / B / C,StringIndexer + OneHot,"[1,0,0], [0,1,0]..."
Ordinal,Low / Med / High,StringIndexer (sometimes),"0, 1, 2"

## The "Spark Twist": Frequency vs. Alphabet

    Standard LabelEncoder (Python/Pandas): usually assigns numbers Alphabetically.

        Apple → 0

        Banana → 1

        Carrot → 2

    Spark StringIndexer: assigns numbers by Frequency (Count).

        The most common category gets 0.

        The second most common gets 1.

        Why? It's an optimization. It lets you easily filter out "rare" categories later (e.g., "Drop any index > 100").

**=> syntax**
```python
from pyspark.ml.feature import StringIndexer, OneHotEncoder

# 1. StringIndexer: Turns "Cash" into 0, "Credit" into 1...
indexer = StringIndexer(inputCol="payment_type", outputCol="payment_type_index")
df_indexed = indexer.fit(df_silver).transform(df_silver)

# 2. OneHotEncoder: Turns 0 into [1, 0, 0...]
# Note: dropLast=True is standard for Regression to avoid "dummy variable trap"
encoder = OneHotEncoder(inputCol="payment_type_index", outputCol="payment_type_vec")
df_encoded = encoder.fit(df_indexed).transform(df_indexed)

# Check the result
df_encoded.select("payment_type", "payment_type_index", "payment_type_vec").show(5)
```

## The Big Data Rule for EDA ⚠️

You cannot plot 3 million rows. Libraries like Matplotlib and Seaborn run on your computer's RAM. If you feed them a Spark DataFrame with millions of rows, your kernel will crash.

The Strategy:

* Take a Sample (e.g., 10%) from Spark.

* Convert it to Pandas.

* Plot using Seaborn/Matplotlib.

## Training process
Since you have your cleaned data (`df_silver` or `df_final`) in memory, here is the **Standard Machine Learning Workflow** in PySpark.

This process has **4 non-negotiable steps**. You cannot skip any of them.

### Phase 1: The "Funnel" (VectorAssembler) 🌪️

PySpark models are picky. They do not accept multiple columns like "Distance", "Passenger", etc. They accept **only one column** called `features` (which is a list of numbers).
We use a `VectorAssembler` to glue your columns together.

```python
from pyspark.ml.feature import VectorAssembler

# 1. Define your inputs (Features)
# Use 'payment_type_index' if you encoded it, or 'payment_type' if you didn't.
feature_cols = ["trip_distance", "passenger_count", "fare_amount", "payment_type_index"]

# 2. Configure the Assembler
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

# 3. Transform the data
df_ready = assembler.transform(df_silver)

# Verification: You should see a 'features' column
df_ready.select("features", "duration_minutes").show(5, truncate=False)

```

### Phase 2: The Split (Train vs Test) ✂️

We never train on 100% of the data. We keep 20% hidden to test if the model is actually smart or just memorizing answers.

```python
# 80% for Training, 20% for Testing. Seed=42 makes it reproducible.
train_data, test_data = df_ready.randomSplit([0.8, 0.2], seed=42)

print(f"Training Rows: {train_data.count()}")
print(f"Testing Rows:  {test_data.count()}")

```

### Phase 3: The Training (Linear Regression) 🤖

Now we create the model. We start with **Linear Regression** because it is fast, simple, and perfect for predicting time/price.

```python
from pyspark.ml.regression import LinearRegression

# 1. Initialize the algorithm
lr = LinearRegression(featuresCol="features", labelCol="duration_minutes")

# 2. Train the model (This is the heavy lifting)
print("Training model...")
lr_model = lr.fit(train_data)
print("Training Complete.")

```

### Phase 4: The Evaluation (Did it work?) 📊

We use **RMSE (Root Mean Squared Error)**.

* **Formula:** $\sqrt{Average Squared Error​}$
* **Meaning:** "My model is usually wrong by **X** minutes." (Lower is better).

```python
from pyspark.ml.evaluation import RegressionEvaluator

# 1. Generate predictions on the Test set
predictions = lr_model.transform(test_data)

# 2. Calculate the Error (RMSE)
evaluator = RegressionEvaluator(
    labelCol="duration_minutes", 
    predictionCol="prediction", 
    metricName="rmse"
)
rmse = evaluator.evaluate(predictions)

print(f"RMSE: {rmse:.2f} minutes")

```

**Next Step:** Run these 4 blocks in order.
**Goal:** If your RMSE is around **5 to 8 minutes**, you have a very solid baseline model! Tell me what number you get.

***
## The Score: RMSE = 6.41 minutes
Is this good? It depends on the average length of a taxi trip in NYC.

* If the average trip is 50 minutes, an error of 6 minutes is excellent (only ~12% error).

* If the average trip is 10 minutes, an error of 6 minutes is not great (it's huge).