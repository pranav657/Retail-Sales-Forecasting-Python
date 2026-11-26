# Retail Sales Forecasting using Python & Machine Learning
# Synthetic daily sales data, EDA, model comparison, rolling test forecast and 30-day future forecast.

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

warnings.filterwarnings("ignore")
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
# If run from project root, outputs/data paths are rooted there.
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

# 1. Generate synthetic daily sales data (3 years)
dates = pd.date_range("2023-01-01", "2025-12-31", freq="D")
data = pd.DataFrame({"Date": dates})
trend = np.linspace(1000, 1500, len(data))
weekly_effect = np.where(data["Date"].dt.dayofweek >= 5, 300, -100)
annual_effect = 200 * np.sin(2 * np.pi * data["Date"].dt.dayofyear / 365.25)
noise = np.random.normal(0, 120, len(data))
data["Sales"] = (trend + weekly_effect + annual_effect + noise).round(2)
data.to_csv(os.path.join(DATA_DIR, "synthetic_retail_sales.csv"), index=False)

# Introduce data-quality issues for cleaning practice
raw_data = data.copy()
missing_indices = np.random.choice(raw_data.index, size=30, replace=False)
raw_data.loc[missing_indices, "Sales"] = np.nan
raw_data = pd.concat([raw_data, raw_data.sample(20, random_state=42)], ignore_index=True)
raw_data.to_csv(os.path.join(DATA_DIR, "raw_retail_sales_with_issues.csv"), index=False)

# 2. Explore & clean
print("\\n--- Initial data ---")
print(raw_data.head())
print("Shape:", raw_data.shape)
print(raw_data.info())
print("Missing values:\\n", raw_data.isnull().sum())
print("Duplicates:", raw_data.duplicated().sum())

cleaned = raw_data.drop_duplicates().sort_values("Date").copy()
cleaned["Sales"] = cleaned["Sales"].interpolate(method="linear")
cleaned = cleaned.reset_index(drop=True)
print("\\n--- Cleaned data checks ---")
print("Shape:", cleaned.shape)
print("Missing values:", cleaned.isnull().sum().sum())
print("Duplicates:", cleaned.duplicated().sum())
cleaned.to_csv(os.path.join(OUT_DIR, "cleaned_retail_sales.csv"), index=False)

# 3. EDA
plt.figure(figsize=(13, 5))
plt.plot(cleaned["Date"], cleaned["Sales"])
plt.title("Daily Retail Sales Trend")
plt.xlabel("Date"); plt.ylabel("Sales"); plt.grid(True); plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "sales_trend.png"), dpi=200)
plt.show()

print("\\nSales summary:\\n", cleaned["Sales"].describe())
print("Total sales:", round(cleaned["Sales"].sum(), 2))
print("Average daily sales:", round(cleaned["Sales"].mean(), 2))
print("Highest daily sales:", round(cleaned["Sales"].max(), 2))
print("Lowest daily sales:", round(cleaned["Sales"].min(), 2))

cleaned["Day_Name"] = cleaned["Date"].dt.day_name()
weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
weekday_sales = cleaned.groupby("Day_Name")["Sales"].mean().reindex(weekday_order)
plt.figure(figsize=(9, 5))
weekday_sales.plot(kind="bar")
plt.title("Average Sales by Day of the Week"); plt.xlabel("Day"); plt.ylabel("Average Sales")
plt.xticks(rotation=45); plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "weekday_sales.png"), dpi=200); plt.show()

cleaned["Month"] = cleaned["Date"].dt.month
monthly_sales = cleaned.groupby("Month")["Sales"].mean()
plt.figure(figsize=(9, 5))
monthly_sales.plot(kind="bar")
plt.title("Average Sales by Month"); plt.xlabel("Month"); plt.ylabel("Average Sales")
plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR, "monthly_sales.png"), dpi=200); plt.show()

cleaned["Year"] = cleaned["Date"].dt.year
yearly_sales = cleaned.groupby("Year")["Sales"].sum()
plt.figure(figsize=(8, 5))
yearly_sales.plot(kind="bar")
plt.title("Total Sales by Year"); plt.xlabel("Year"); plt.ylabel("Total Sales")
plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR, "yearly_sales.png"), dpi=200); plt.show()

# 4. Feature engineering
ml_data = cleaned.copy()
ml_data["Day"] = ml_data["Date"].dt.day
ml_data["Month"] = ml_data["Date"].dt.month
ml_data["Year"] = ml_data["Date"].dt.year
ml_data["DayOfWeek"] = ml_data["Date"].dt.dayofweek
ml_data["IsWeekend"] = (ml_data["DayOfWeek"] >= 5).astype(int)
ml_data["Sales_Lag_1"] = ml_data["Sales"].shift(1)
ml_data["Sales_Lag_7"] = ml_data["Sales"].shift(7)
ml_data["Sales_Lag_14"] = ml_data["Sales"].shift(14)
ml_data["Sales_Lag_28"] = ml_data["Sales"].shift(28)
ml_data["Rolling_Mean_7"] = ml_data["Sales"].shift(1).rolling(7).mean()
ml_data["Rolling_Mean_28"] = ml_data["Sales"].shift(1).rolling(28).mean()
ml_data = ml_data.dropna().reset_index(drop=True)

features = ["Day","Month","Year","DayOfWeek","IsWeekend",
            "Sales_Lag_1","Sales_Lag_7","Sales_Lag_14","Sales_Lag_28",
            "Rolling_Mean_7","Rolling_Mean_28"]
target = "Sales"

# 5. Chronological 30-day test split
forecast_horizon = 30
cutoff_date = cleaned["Date"].max() - pd.Timedelta(days=forecast_horizon - 1)
train_ml = ml_data[ml_data["Date"] < cutoff_date].copy()
test_ml = ml_data[ml_data["Date"] >= cutoff_date].copy()
X_train, y_train = train_ml[features], train_ml[target]
X_test, y_test = test_ml[features], test_ml[target]
test_dates = test_ml["Date"].tolist()
history_before_test = cleaned.loc[cleaned["Date"] < cutoff_date, "Sales"].tolist()

# 6. Train models
linear_model = LinearRegression().fit(X_train, y_train)
rf_model = RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_leaf=2,
                                 random_state=42, n_jobs=-1).fit(X_train, y_train)

def make_features_for_date(date, history):
    dow = date.dayofweek
    row = {"Day": date.day, "Month": date.month, "Year": date.year,
           "DayOfWeek": dow, "IsWeekend": int(dow >= 5),
           "Sales_Lag_1": history[-1], "Sales_Lag_7": history[-7],
           "Sales_Lag_14": history[-14], "Sales_Lag_28": history[-28],
           "Rolling_Mean_7": np.mean(history[-7:]),
           "Rolling_Mean_28": np.mean(history[-28:])}
    return pd.DataFrame([row])[features]

def recursive_forecast(model, dates_to_predict, history):
    history = list(history)
    predictions = []
    for date in dates_to_predict:
        x_next = make_features_for_date(date, history)
        pred = float(model.predict(x_next)[0])
        predictions.append(pred)
        history.append(pred)
    return np.array(predictions)

linear_predictions = recursive_forecast(linear_model, test_dates, history_before_test)
rf_predictions = recursive_forecast(rf_model, test_dates, history_before_test)

# 7. Evaluate
def evaluate_model(actual, predicted):
    return {"MAE": mean_absolute_error(actual, predicted),
            "RMSE": np.sqrt(mean_squared_error(actual, predicted)),
            "R2": r2_score(actual, predicted)}

metrics = pd.DataFrame([evaluate_model(y_test, linear_predictions),
                        evaluate_model(y_test, rf_predictions)],
                       index=["Linear Regression", "Random Forest"])
metrics.to_csv(os.path.join(OUT_DIR, "model_comparison.csv"))
print("\\n--- Model comparison (rolling 30-day test) ---\\n", metrics)

results = pd.DataFrame({"Date": test_dates, "Actual_Sales": y_test.values,
                        "Linear_Regression_Predictions": linear_predictions,
                        "Random_Forest_Predictions": rf_predictions})
results.to_csv(os.path.join(OUT_DIR, "test_predictions.csv"), index=False)

plt.figure(figsize=(13, 5))
plt.plot(results["Date"], results["Actual_Sales"], label="Actual Sales")
plt.plot(results["Date"], results["Linear_Regression_Predictions"], label="Linear Regression")
plt.title("Actual vs Linear Regression Forecast"); plt.xlabel("Date"); plt.ylabel("Sales")
plt.legend(); plt.grid(True); plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "linear_test_forecast.png"), dpi=200); plt.show()

plt.figure(figsize=(13, 5))
plt.plot(results["Date"], results["Actual_Sales"], label="Actual Sales")
plt.plot(results["Date"], results["Random_Forest_Predictions"], label="Random Forest")
plt.title("Actual vs Random Forest Forecast"); plt.xlabel("Date"); plt.ylabel("Sales")
plt.legend(); plt.grid(True); plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "random_forest_test_forecast.png"), dpi=200); plt.show()

# 8. Select by test MAE and train on all available historical data for future forecast
selected_name = "Random Forest" if metrics.loc["Random Forest", "MAE"] < metrics.loc["Linear Regression", "MAE"] else "Linear Regression"
print("\\nSelected model by test MAE:", selected_name)

final_linear = LinearRegression().fit(ml_data[features], ml_data[target])
final_rf = RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_leaf=2,
                                 random_state=42, n_jobs=-1).fit(ml_data[features], ml_data[target])
future_dates = pd.date_range(cleaned["Date"].max() + pd.Timedelta(days=1), periods=30, freq="D")
full_history = cleaned["Sales"].tolist()
future_linear = recursive_forecast(final_linear, future_dates, full_history)
future_rf = recursive_forecast(final_rf, future_dates, full_history)
future_results = pd.DataFrame({"Date": future_dates,
                               "Linear_Regression_Forecast": future_linear,
                               "Random_Forest_Forecast": future_rf})
future_results["Forecasted_Sales"] = (future_rf if selected_name == "Random Forest" else future_linear)
future_results.to_csv(os.path.join(OUT_DIR, "retail_sales_forecast_30_days.csv"), index=False)

plt.figure(figsize=(13, 5))
plt.plot(cleaned["Date"].tail(90), cleaned["Sales"].tail(90), label="Historical Sales")
plt.plot(future_results["Date"], future_results["Forecasted_Sales"], label=f"Forecast ({selected_name})")
plt.title("Retail Sales: Recent History and 30-Day Forecast")
plt.xlabel("Date"); plt.ylabel("Sales"); plt.legend(); plt.grid(True); plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "sales_forecast_30_days.png"), dpi=200); plt.show()

# 9. Business insights and summary
best_day = weekday_sales.idxmax()
lowest_day = weekday_sales.idxmin()
best_month = monthly_sales.idxmax()
lowest_month = monthly_sales.idxmin()
forecast_total = future_results["Forecasted_Sales"].sum()
forecast_average = future_results["Forecasted_Sales"].mean()

summary = f"""PROJECT SUMMARY
Best average sales weekday: {best_day} ({weekday_sales[best_day]:.2f})
Lowest average sales weekday: {lowest_day} ({weekday_sales[lowest_day]:.2f})
Best average sales month number: {best_month} ({monthly_sales[best_month]:.2f})
Lowest average sales month number: {lowest_month} ({monthly_sales[lowest_month]:.2f})
Selected model based on rolling test MAE: {selected_name}
Forecast total sales next 30 days: {forecast_total:.2f}
Forecast average daily sales next 30 days: {forecast_average:.2f}
"""
with open(os.path.join(OUT_DIR, "business_summary.txt"), "w", encoding="utf-8") as f:
    f.write(summary)
print("\\n" + summary)

print("\\nProject completed. Review the outputs folder for CSVs, charts and summary.")
