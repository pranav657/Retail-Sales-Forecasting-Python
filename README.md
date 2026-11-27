# 📊 Retail Sales Forecasting & Analytics

A Python-based retail sales analytics and forecasting project. The Jupyter Notebook covers data cleaning, exploratory analysis, feature engineering and forecasting. The Streamlit application presents historical sales trends, weekday and monthly bar charts, a sales-contribution pie chart, forecasting visuals, and a CSV download.

## Project files

- `notebooks/Retail_Sales_Forecasting.ipynb` — original analysis notebook (kept unchanged).
- `app.py` — updated Streamlit app; **the separate Business Overview section has been removed**.
- `outputs/cleaned_retail_sales.csv` — cleaned historical data required by the app.
- `outputs/retail_sales_forecast_30_days.csv` — forecast data required by the app.
- `requirements.txt` — required Python packages.

> The Streamlit app currently loads the two CSV files from the `outputs/` folder. Ensure these files are included in your repository with the exact names above.

## Dashboard features

- Historical date-range filtering
- Daily historical sales line chart
- Average sales by weekday (bar chart)
- Average sales by month (bar chart)
- Sales contribution by weekday (pie chart)
- Forecast visualization and forecast KPIs
- Forecast details and CSV download
- Upload your own CSV or Excel file and generate a custom forecast

## Run locally

1. Install Python (3.10+ recommended).
2. Clone or download this repository and open its folder in VS Code.
3. Open the terminal in the project root (the folder containing `app.py`).
4. (Recommended) Create and activate a virtual environment:

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

5. Install packages:
   ```bash
   pip install -r requirements.txt
   ```
6. Confirm the `outputs` folder contains `cleaned_retail_sales.csv` and `retail_sales_forecast_30_days.csv`.
7. Start the dashboard:
   ```bash
   streamlit run app.py
   ```
8. Streamlit opens in your browser. If it does not, copy the local URL shown in the terminal (usually `http://localhost:8501`).

## Publish / deploy using GitHub and Streamlit Community Cloud

1. Push the complete project to a GitHub repository. Include `app.py`, `requirements.txt`, the notebook, and the required `outputs` CSV files.
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/) and sign in using GitHub.
3. Select **Create app** / **Deploy an app**.
4. Choose your repository, branch (typically `main`), and main file path `app.py`.
5. Deploy. Keep the `outputs/` folder and CSVs in the repository because the app reads them at startup.
6. After future changes are pushed to GitHub, Streamlit Cloud can redeploy the app.

## Libraries

Python, Pandas, NumPy, Matplotlib (Notebook), Plotly, Scikit-learn, Streamlit.

## Disclaimer

Forecasts are estimates based on historical data and should not be treated as guaranteed results.
