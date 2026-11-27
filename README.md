# 📊 Retail Sales Analytics & Forecasting Dashboard

An interactive **Retail Sales Analytics and Forecasting** project built using Python, Pandas, Plotly, Scikit-learn and Streamlit. Explore historical sales performance, review future sales forecasts, and upload your own dataset to train a simple forecasting model and visualize actual versus predicted values.

## ✨ Dashboard Features

### 📊 Historical Analysis
- Interactive daily historical sales line chart
- Average sales by weekday
- Average monthly sales analysis
- Date-range filtering

### 🔮 Sales Forecast
- Combined **Historical Sales vs Predicted Sales** line chart
- Actual sales shown alongside future forecast values
- Forecast horizon selection
- Forecast KPIs and trend insights

### 📋 Forecast Data
- Forecast table for the selected forecast period
- View and download forecast results

### 🚀 Upload & Predict (Custom Dataset)
- Upload a CSV or Excel dataset within the **Upload & Predict** tab (not in the sidebar)
- Select the date column and the numeric target column
- Choose aggregation and forecast period settings, where available
- Train a forecasting model on your uploaded data
- View a line chart comparing historical values with predicted future values
- Review forecast results and download them

## 📁 Project Structure

```text
Retail-Sales-Forecasting-Python/
├── app.py
├── requirements.txt
├── README.md
├── notebooks/
│   └── Retail_Sales_Forecasting.ipynb
├── data/
└── outputs/
    ├── cleaned_retail_sales.csv
    └── retail_sales_forecast_30_days.csv
```

> The dashboard loads its default historical and forecast datasets from the `outputs/` folder. Make sure both CSV files are included in your repository and that the filenames match.

## 🛠️ Technologies Used

- Python
- Pandas and NumPy
- Plotly
- Scikit-learn
- Streamlit
- Jupyter Notebook

## ▶️ Run the Project Locally

1. Install Python (Python 3.10 or later recommended).
2. Clone or download the repository and open the project folder in VS Code.
3. Open a terminal in the project root directory (where `app.py` is located).
4. (Optional but recommended) Create a virtual environment:

   **Windows**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

   **macOS/Linux**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Confirm the `outputs/` folder contains the required CSV files.
7. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
8. Open the URL displayed in the terminal (typically `http://localhost:8501`).

## ☁️ Deploy on Streamlit Community Cloud

1. Push the project files to a GitHub repository. Include `app.py`, `requirements.txt`, the notebook and required `outputs/` CSV files.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with GitHub.
3. Select **Create app**.
4. Select your repository, branch and `app.py` as the main file.
5. Deploy the application.
6. Keep the `outputs/` folder and CSV files in the repository because the app uses them for the default dashboard.

## 📌 Notes

- Custom prediction expects a dataset with a date-like column and a numeric column to forecast.
- Check your data for missing or invalid values before forecasting.
- Forecasts are estimates and may not accurately reflect future sales.

## 👩‍💻 Portfolio Project

This project demonstrates data analysis, visualization, feature preparation and time-series forecasting concepts using Python, along with the development and deployment of an interactive dashboard.
