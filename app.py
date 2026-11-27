
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Retail Sales Analytics",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

HISTORY_FILE = OUTPUT_DIR / "cleaned_retail_sales.csv"
FORECAST_FILE = OUTPUT_DIR / "retail_sales_forecast_30_days.csv"


# ==========================================
# 2. CUSTOM CSS
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: white;
}

[data-testid="stSidebar"] {
    background-color: #171B26;
}

[data-testid="stMetric"] {
    background-color: #1B2333;
    border: 1px solid #303B50;
    padding: 18px;
    border-radius: 12px;
}

[data-testid="stMetricLabel"] {
    color: #B8C4D9;
}

[data-testid="stMetricValue"] {
    color: #55D6BE;
}

h1, h2, h3 {
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. UPLOAD DATA FIRST — NO DEFAULT DATASET
# ==========================================

st.title("📈 Retail Sales Analytics Dashboard")
st.markdown("Upload your own CSV or Excel file to explore its historical performance and generate forecasts.")

uploaded_file = st.file_uploader(
    "📂 Upload your sales dataset (CSV or Excel)",
    type=["csv", "xlsx"],
    key="custom_tab_dataset_upload"
)

if uploaded_file is None:
    st.info("👆 Please upload a CSV or Excel file to display your dashboard. No sample or default historical data is shown.")
    st.stop()

try:
    uploaded_file.seek(0)
    if uploaded_file.name.lower().endswith(".csv"):
        uploaded_data = pd.read_csv(uploaded_file)
    else:
        uploaded_data = pd.read_excel(uploaded_file)
except Exception as upload_error:
    st.error(f"Unable to read the uploaded file: {upload_error}")
    st.stop()

if uploaded_data.empty:
    st.error("The uploaded file is empty. Please upload a file containing data.")
    st.stop()

# Detect likely date and numeric columns. The Upload & Predict tab lets the
# user change these selections; Historical Analysis follows those selections.
date_candidates = []
for col in uploaded_data.columns:
    parsed_dates = pd.to_datetime(uploaded_data[col], errors="coerce")
    if parsed_dates.notna().sum() >= max(2, int(len(uploaded_data) * 0.5)):
        date_candidates.append(col)
numeric_candidates = [
    col for col in uploaded_data.columns
    if pd.to_numeric(uploaded_data[col], errors="coerce").notna().any()
]

saved_date_col = st.session_state.get("custom_date_column")
saved_target_col = st.session_state.get("custom_target_column")
selected_date_col = saved_date_col if saved_date_col in uploaded_data.columns else (date_candidates[0] if date_candidates else None)
selected_target_col = saved_target_col if saved_target_col in numeric_candidates else next(
    (col for col in numeric_candidates if col != selected_date_col), None
)

if selected_date_col is None or selected_target_col is None:
    st.error("I couldn't identify both a date column and a numeric sales/value column. Please check your file has these columns.")
    st.write("Available columns:", list(uploaded_data.columns))
    st.stop()

active_history = uploaded_data[[selected_date_col, selected_target_col]].copy()
active_history["Date"] = pd.to_datetime(active_history[selected_date_col], errors="coerce")
active_history["Sales"] = pd.to_numeric(active_history[selected_target_col], errors="coerce")
active_history = active_history.dropna(subset=["Date", "Sales"])
active_history = (active_history.groupby("Date", as_index=False)["Sales"]
                  .sum().sort_values("Date"))

if active_history.empty:
    st.error("The selected columns do not contain valid date and numeric values.")
    st.stop()

historical_source_label = f"Uploaded file: {uploaded_file.name}"


# ==========================================
# CUSTOM DATA FORECASTING FUNCTION
# ==========================================

def create_features(values, forecast_date):

    values = list(values)

    return [
        forecast_date.day,
        forecast_date.month,
        forecast_date.dayofweek,
        forecast_date.dayofyear,
        int(forecast_date.dayofweek >= 5),
        values[-1],
        values[-7],
        values[-14],
        values[-28],
        np.mean(values[-7:]),
        np.mean(values[-28:])
    ]


def train_custom_forecast(data, date_col, target_col,
                          aggregation, forecast_days):

    df = data[[date_col, target_col]].copy()

    df[date_col] = pd.to_datetime(
        df[date_col], errors="coerce"
    )

    df[target_col] = pd.to_numeric(
        df[target_col], errors="coerce"
    )

    df = df.dropna(subset=[date_col, target_col])

    if df.empty:
        raise ValueError("No valid date and numeric values found.")

    # Aggregate records with the same date
    df = df.groupby(date_col)[target_col].agg(
        aggregation
    ).sort_index()

    # Convert to daily frequency
    df = df.resample("D").mean()

    # Fill missing daily values
    df = df.interpolate(method="linear").ffill().bfill()

    if len(df) < 60:
        raise ValueError(
            "Please upload at least 60 daily observations "
            "for this forecasting model."
        )

    values = df.to_numpy(dtype=float)
    dates = df.index

    X = []
    y = []

    # Build training features using previous observations
    for i in range(28, len(values)):

        X.append(
            create_features(
                values[:i],
                dates[i]
            )
        )

        y.append(values[i])

    X = np.array(X)
    y = np.array(y)

    # Chronological train/test split
    split = int(len(X) * 0.80)

    if split < 10 or len(X) - split < 2:
        raise ValueError(
            "Not enough observations for reliable model evaluation."
        )

    X_train = X[:split]
    y_train = y[:split]

    X_test = X[split:]
    y_test = y[split:]

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    test_predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test, test_predictions
    )

    rmse = np.sqrt(
        mean_squared_error(y_test, test_predictions)
    )

    r2 = r2_score(y_test, test_predictions)

    # Train final model on all available observations
    final_model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    final_model.fit(X, y)

    # Generate future predictions recursively
    history_values = list(values)
    future_dates = []
    future_predictions = []

    for _ in range(forecast_days):

        next_date = dates[-1] + pd.Timedelta(
            days=len(future_dates) + 1
        )

        next_features = create_features(
            history_values,
            next_date
        )

        prediction = final_model.predict(
            [next_features]
        )[0]

        future_dates.append(next_date)
        future_predictions.append(prediction)

        history_values.append(prediction)

    results = pd.DataFrame({
        "Forecast Date": future_dates,
        "Predicted Value": future_predictions
    })

    metrics = {
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    }

    return df, results, metrics, test_predictions, y_test



# ==========================================
# 4. SIDEBAR FILTERS
# ==========================================

st.sidebar.title("📊 Retail Analytics")
st.sidebar.markdown("---")

st.sidebar.subheader("Historical Date Filter")

min_date = active_history["Date"].min().date()
max_date = active_history["Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

st.sidebar.markdown("---")

st.sidebar.subheader("Forecast Settings")

forecast_days = st.sidebar.select_slider(
    "Select forecast period",
    options=[7, 15, 30],
    value=30
)

st.sidebar.markdown("---")

st.sidebar.info(f"Using uploaded file: {uploaded_file.name}")



# ==========================================
# 5. FILTER DATA
# ==========================================

if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:

    start_date, end_date = selected_dates

    filtered = active_history[
        (active_history["Date"].dt.date >= start_date) &
        (active_history["Date"].dt.date <= end_date)
    ].copy()

else:
    filtered = active_history.copy()


if filtered.empty:
    st.warning("No historical sales found for this date range.")
    st.stop()


# ==========================================
# 6. DASHBOARD HEADER
# ==========================================

st.markdown("---")
st.caption(f"Historical data source: {historical_source_label}")


# ==========================================
# 7. HISTORICAL KPI CARDS
# ==========================================

st.subheader("Historical Performance")
st.caption(f"Historical data source: {historical_source_label}")

total_sales = filtered["Sales"].sum()
average_sales = filtered["Sales"].mean()
highest_sales = filtered["Sales"].max()
total_orders_days = len(filtered)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Sales", f"₹{total_sales:,.0f}")
c2.metric("Average Daily Sales", f"₹{average_sales:,.0f}")
c3.metric("Highest Daily Sales", f"₹{highest_sales:,.0f}")
c4.metric("Days Analysed", f"{total_orders_days:,}")


# ==========================================
# 8. TABS
# ==========================================

tab1, tab2 = st.tabs([
    "📊 Historical Analysis",
    "🚀 Upload & Predict"
])

# ==========================================
# 9. HISTORICAL ANALYSIS
# ==========================================

with tab1:

    st.subheader("Daily Sales Trend")

    fig = px.line(
        filtered,
        x="Date",
        y="Sales",
        template="plotly_dark",
        markers=False,
        title="Historical Daily Sales"
    )

    fig.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#171B26",
        font_color="white",
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Sales (₹)"
    )

    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    # Weekday analysis

    with left:

        weekday_data = filtered.copy()
        weekday_data["Weekday"] = (
            weekday_data["Date"].dt.day_name()
        )

        weekday_order = [
            "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"
        ]

        weekday_sales = (
            weekday_data.groupby("Weekday", as_index=False)["Sales"]
            .mean()
        )

        weekday_sales["Weekday"] = pd.Categorical(
            weekday_sales["Weekday"],
            categories=weekday_order,
            ordered=True
        )

        weekday_sales = weekday_sales.sort_values("Weekday")

        fig_week = px.bar(
            weekday_sales,
            x="Weekday",
            y="Sales",
            title="Average Sales by Weekday",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig_week,
            use_container_width=True
        )

    # Monthly analysis

    with right:

        monthly_data = filtered.copy()
        monthly_data["Month"] = (
            monthly_data["Date"].dt.month
        )

        monthly_sales = (
            monthly_data.groupby("Month", as_index=False)["Sales"]
            .mean()
        )

        monthly_sales["Month"] = monthly_sales["Month"].map({
            1: "Jan", 2: "Feb", 3: "Mar",
            4: "Apr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep",
            10: "Oct", 11: "Nov", 12: "Dec"
        })

        fig_month = px.bar(
            monthly_sales,
            x="Month",
            y="Sales",
            title="Average Monthly Sales",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig_month,
            use_container_width=True
        )


# ==========================================
# 12. UPLOAD YOUR OWN DATA & PREDICT
# ==========================================

with tab2:

    st.header("🚀 Custom Dataset Prediction")

    st.write(
        "Upload your own CSV or Excel dataset below, select its date and numeric columns, "
        "and generate a custom forecast."
    )

    st.subheader("📂 Upload Your Dataset")
    st.info(
        "Your dataset must contain a date column and a numeric column to forecast. "
        "This version supports daily time-series forecasting."
    )

    if uploaded_file is not None:

        try:

            # Read uploaded file from the beginning (the same file is also
            # read earlier to populate Historical Analysis).
            uploaded_file.seek(0)
            if uploaded_file.name.lower().endswith(".csv"):
                uploaded_data = pd.read_csv(uploaded_file)
            else:
                uploaded_data = pd.read_excel(uploaded_file)

            if uploaded_data.empty:
                st.error("The uploaded file is empty.")

            else:

                st.success("Dataset uploaded successfully!")

                st.subheader("Dataset Preview")

                st.dataframe(
                    uploaded_data.head(10),
                    use_container_width=True,
                    hide_index=True
                )

                st.write(
                    f"Total records: {len(uploaded_data):,}"
                )

                st.write(
                    f"Total columns: {len(uploaded_data.columns)}"
                )

                # Select columns
                st.subheader("Select Your Columns")

                date_options = uploaded_data.columns.tolist()

                date_default = next((c for c in date_options if c in date_candidates), date_options[0])
                date_col = st.selectbox(
                    "Select Date Column",
                    options=date_options,
                    index=date_options.index(st.session_state.get("custom_date_column", date_default))
                    if st.session_state.get("custom_date_column", date_default) in date_options else date_options.index(date_default),
                    key="custom_date_column"
                )

                numeric_options = [
                    col for col in uploaded_data.columns
                    if pd.to_numeric(
                        uploaded_data[col],
                        errors="coerce"
                    ).notna().any()
                ]

                if not numeric_options:

                    st.error(
                        "No numeric column found in your dataset."
                    )

                else:

                    target_default = next((c for c in numeric_options if c != date_col), numeric_options[0])
                    target_col = st.selectbox(
                        "Select Numeric Column to Predict",
                        options=numeric_options,
                        index=numeric_options.index(st.session_state.get("custom_target_column", target_default))
                        if st.session_state.get("custom_target_column", target_default) in numeric_options else numeric_options.index(target_default),
                        key="custom_target_column"
                    )

                    aggregation = st.selectbox(
                        "How should records with the same date be combined?",
                        options=["sum", "mean"],
                        index=0,
                        help="Choose Sum for transaction sales or "
                             "Mean for measurements such as temperature."
                    )

                    forecast_days_custom = st.select_slider(
                        "How many days do you want to predict?",
                        options=[7, 15, 30, 60, 90],
                        value=30
                    )

                    st.markdown("---")

                    if st.button(
                        "🧠 Train Model & Generate Prediction",
                        type="primary",
                        use_container_width=True
                    ):

                        try:

                            with st.spinner(
                                "Cleaning data and training your model..."
                            ):

                                (
                                    cleaned_custom,
                                    custom_results,
                                    custom_metrics,
                                    test_predictions,
                                    actual_values
                                ) = train_custom_forecast(
                                    uploaded_data,
                                    date_col,
                                    target_col,
                                    aggregation,
                                    forecast_days_custom
                                )

                            st.session_state["custom_results"] = (
                                custom_results
                            )

                            st.session_state["custom_metrics"] = (
                                custom_metrics
                            )

                            st.session_state["custom_actual"] = (
                                actual_values
                            )

                            st.session_state["custom_test"] = (
                                test_predictions
                            )

                            st.session_state["custom_cleaned"] = (
                                cleaned_custom
                            )

                            st.session_state["custom_target"] = (
                                target_col
                            )

                            st.success(
                                "Model training and prediction completed!"
                            )

                        except Exception as error:

                            st.error(
                                f"Unable to generate predictions: {error}"
                            )

        except Exception as error:

            st.error(
                f"Unable to read the uploaded file: {error}"
            )


# ======================================
# BUSINESS-FRIENDLY PREDICTION RESULTS
# ======================================

    if "custom_results" in st.session_state:

        results = st.session_state["custom_results"].copy()

        target_name = st.session_state["custom_target"]

        st.markdown("---")

        st.header("📊 Your Future Prediction")

        st.write(
            "Here is a simple summary of what your uploaded "
            "data suggests for the coming days."
        )

        # ----------------------------------
        # 1. BUSINESS SUMMARY
        # ----------------------------------

        average_value = results["Predicted Value"].mean()
        total_value = results["Predicted Value"].sum()
        highest_value = results["Predicted Value"].max()
        lowest_value = results["Predicted Value"].min()

        highest_date = results.loc[
            results["Predicted Value"].idxmax(),
            "Forecast Date"
        ]

        lowest_date = results.loc[
            results["Predicted Value"].idxmin(),
            "Forecast Date"
        ]

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Total Expected Value",
            f"{total_value:,.2f}"
        )

        c2.metric(
            "Average Per Day",
            f"{average_value:,.2f}"
        )

        c3.metric(
            "Highest Expected Value",
            f"{highest_value:,.2f}"
        )

        c4.metric(
            "Lowest Expected Value",
            f"{lowest_value:,.2f}"
        )

        # ----------------------------------
        # 2. SIMPLE BUSINESS INSIGHTS
        # ----------------------------------

        st.subheader("💡 Business Insights")

        col1, col2 = st.columns(2)

        with col1:

            st.info(
                f"**Best expected day:** "
                f"{highest_date.strftime('%d %B %Y')} "
                f"with an expected value of "
                f"{highest_value:,.2f}."
            )

        with col2:

            st.info(
                f"**Lowest expected day:** "
                f"{lowest_date.strftime('%d %B %Y')} "
                f"with an expected value of "
                f"{lowest_value:,.2f}."
            )

        # ----------------------------------
        # 3. HISTORICAL + PREDICTED LINE CHART
        # ----------------------------------

        st.subheader("📈 Historical vs Predicted Trend")

        custom_history = st.session_state["custom_cleaned"].copy()
        if isinstance(custom_history, pd.Series):
            custom_history = custom_history.rename(target_name).reset_index()
            custom_history.columns = ["Date", target_name]
        else:
            custom_history = custom_history.reset_index()
            custom_history.columns = ["Date", target_name]

        custom_history["Date"] = pd.to_datetime(custom_history["Date"])
        results["Forecast Date"] = pd.to_datetime(results["Forecast Date"])

        combined_fig = go.Figure()
        combined_fig.add_trace(go.Scatter(
            x=custom_history["Date"],
            y=custom_history[target_name],
            mode="lines",
            name="Historical",
            line=dict(width=3),
            hovertemplate="Date: %{x|%d %b %Y}<br>Actual: %{y:,.2f}<extra></extra>"
        ))
        combined_fig.add_trace(go.Scatter(
            x=results["Forecast Date"],
            y=results["Predicted Value"],
            mode="lines+markers",
            name="Predicted",
            line=dict(width=3, dash="dash"),
            marker=dict(size=6),
            hovertemplate="Date: %{x|%d %b %Y}<br>Predicted: %{y:,.2f}<extra></extra>"
        ))
        combined_fig.update_layout(
            title=f"Historical {target_name} vs Future Prediction",
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#171B26",
            font_color="white",
            xaxis_title="Date",
            yaxis_title=target_name,
            hovermode="x unified",
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(combined_fig, use_container_width=True)

        # ----------------------------------
        # 4. FUTURE PREDICTION CHART
        # ----------------------------------

        st.subheader("📈 Expected Future Trend")

        custom_fig = px.line(
            results,
            x="Forecast Date",
            y="Predicted Value",
            markers=True,
            title="Expected Future Performance",
            template="plotly_dark"
        )

        custom_fig.add_hline(
            y=average_value,
            line_dash="dash",
            annotation_text="Average Expected Value"
        )

        custom_fig.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#171B26",
            font_color="white",
            xaxis_title="Forecast Date",
            yaxis_title=f"Expected {target_name}",
            hovermode="x unified"
        )

        st.plotly_chart(
            custom_fig,
            use_container_width=True
        )

        # ----------------------------------
        # 4. EASY-TO-UNDERSTAND TABLE
        # ----------------------------------

        st.subheader("📅 Daily Prediction Details")

        st.write(
            "This table shows how much value is expected "
            "on each upcoming day."
        )

        display_results = results.copy()

        display_results["Day"] = (
            display_results["Forecast Date"].dt.day_name()
        )

        display_results["Outlook"] = display_results[
            "Predicted Value"
        ].apply(
            lambda x:
                "Above average" if x > average_value
                else "Below average" if x < average_value
                else "Around average"
        )

        display_results = display_results.rename(
            columns={
                "Forecast Date": "Date",
                "Predicted Value": f"Expected {target_name}"
            }
        )

        display_results["Date"] = (
            display_results["Date"].dt.strftime("%d %b %Y")
        )

        value_column = f"Expected {target_name}"

        display_results[value_column] = (
            display_results[value_column].map(
                lambda x: f"{x:,.2f}"
            )
        )

        display_results = display_results[
            ["Date", "Day", value_column, "Outlook"]
        ]

        st.dataframe(
            display_results,
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------
        # 5. DOWNLOAD PREDICTIONS
        # ----------------------------------

        st.subheader("⬇️ Download Your Results")

        download_results = results.rename(
            columns={
                "Forecast Date": "Date",
                "Predicted Value": f"Expected {target_name}"
            }
        )

        csv_download = download_results.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Prediction Report",
            data=csv_download,
            file_name="business_prediction_report.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.caption(
            "Note: These are estimates based on historical data. "
            "Actual future results may differ."
        )



# ==========================================
# 12. FOOTER
# ==========================================

st.markdown("---")

st.caption(
    "Retail Sales Analytics | Python | Pandas | "
    "Scikit-learn | Streamlit | Plotly"
)

st.caption(
    "Disclaimer: This project uses simulated data. "
    "Forecast values are illustrative, not guaranteed predictions."
)
