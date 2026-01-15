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