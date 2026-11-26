# Retail Sales Forecasting Using Python

## Project Overview

This project analyzes historical retail sales data, identifies sales trends and patterns, and forecasts sales for the next 30 days using machine learning.

The project uses Python for data cleaning, exploratory data analysis (EDA), feature engineering, machine learning model development, model evaluation, and business-oriented visualization.

## Business Problem

Retail businesses need to understand historical sales patterns to plan inventory, manage stock, and anticipate future demand.

This project explores historical sales data and develops forecasting models to estimate future sales and identify patterns that could support business planning.

## Objectives

- Clean and prepare retail sales data.
- Handle missing values and duplicate records.
- Perform Exploratory Data Analysis (EDA).
- Identify sales trends and weekly/monthly patterns.
- Create time-series features such as lag values and rolling averages.
- Build and compare machine learning models.
- Forecast retail sales for the next 30 days.
- Visualize the findings using Python.

## Tools and Technologies

- Python
- Jupyter Notebook
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn

## Project Workflow

1. Dataset generation and data loading
2. Data inspection and cleaning
3. Missing value handling
4. Duplicate removal
5. Exploratory Data Analysis
6. Feature engineering
7. Train-test splitting based on time
8. Model development
9. Model evaluation
10. 30-day forecasting
11. Visualization and business interpretation

## Data Cleaning

The dataset was prepared by:

- Identifying missing sales values.
- Interpolating missing sales values.
- Removing duplicate records.
- Sorting the dataset chronologically.
- Preparing data for analysis and forecasting.

## Exploratory Data Analysis

The project explores:

- Historical sales trends.
- Average sales by weekday.
- Monthly sales patterns.
- Annual sales trends.
- Sales distribution and patterns.

## Feature Engineering

The following features were created to improve forecasting:

- Day
- Month
- Year
- Day of Week
- Weekend Indicator
- 1-Day Lag
- 7-Day Lag
- 14-Day Lag
- 28-Day Lag
- 7-Day Rolling Mean
- 28-Day Rolling Mean

## Machine Learning Models

Two machine learning models were implemented:

### Linear Regression
Used as a baseline model to estimate future retail sales.

### Random Forest Regressor
Used to model more complex relationships between historical sales patterns and future sales.

## Model Evaluation

The models were evaluated using:

- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- R² (R-squared)

The models were compared using a chronological test period to evaluate forecasting performance.

## Sales Forecasting

The project generates a forecast for the next 30 days using the trained machine learning models.

The forecast is intended to demonstrate how historical sales data can be used for demand planning and business analysis.

## Visualizations

### Historical Sales Trend

![Sales Trend](outputs/sales_trend.png)

### Average Sales by Weekday

![Weekday Sales](outputs/weekday_sales.png)

### Monthly Sales

![Monthly Sales](outputs/monthly_sales.png)

### 30-Day Sales Forecast

![30-Day Sales Forecast](outputs/sales_forecast_30_days.png)

### Sales Forecast Dashboard

![Sales Dashboard](outputs/yearly_sales.png)

## Business Applications

The analysis and forecast could help retail businesses:

- Understand historical sales trends.
- Identify high and low sales periods.
- Support inventory planning.
- Prepare for potential changes in demand.
- Compare forecasting model performance.
- Support data-driven decision-making.

## Project Limitations

- The dataset is synthetic and not actual company sales data.
- Forecast accuracy depends on the patterns present in the dataset.
- Real-world sales may be influenced by promotions, prices, holidays, stock availability, competition and external events.
- Forecasting results should not be treated as guaranteed future sales.

## Project Files

- `notebooks/` – Jupyter Notebook containing the complete project.
- `data/` – Dataset files.
- `outputs/` – Forecasts, charts, model comparison and business summary.
- `run_project.py` – Python script to execute the project.
- `requirements.txt` – Required Python libraries.

## Author

Data Analytics Portfolio Project

**Skills Demonstrated:** Python, Pandas, NumPy, Data Cleaning, EDA, Feature Engineering, Machine Learning, Data Visualization, Time-Series Forecasting.
