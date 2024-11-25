import matplotlib
matplotlib.use('Agg')  # Chạy ở chế độ không GUI để tránh lỗi
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, request, redirect, url_for
import os
import joblib
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

# Path to saved models
MODELS_DIR = "models_and_results"
DATA_PATH = os.path.join("data", "gld_price_data_cleaned.csv")

# Get list of available models
model_files = [f for f in os.listdir(MODELS_DIR) if f.endswith(".joblib")]
model_names = [f.split("_model.joblib")[0].replace("_", " ").title() for f in model_files]

# Historical predictions storage
history = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get user inputs
        selected_model_name = request.form.get("model")
        num_days = int(request.form.get("num_days"))
        
        # Redirect to results page
        return redirect(url_for("results", model_name=selected_model_name, days=num_days))
    
    return render_template("index.html", models=model_names)

@app.route("/results", methods=["GET"])
def results():
    # Get parameters from request
    selected_model_name = request.args.get("model_name")
    num_days = int(request.args.get("days"))
    
    # Load the selected model
    model_file = f"{selected_model_name.lower().replace(' ', '_')}_model.joblib"
    model_path = os.path.join(MODELS_DIR, model_file)
    model = joblib.load(model_path)
    
    # Load the dataset and get the last date
    gold_price_data = pd.read_csv(DATA_PATH)
    gold_price_data['Date'] = pd.to_datetime(gold_price_data['Date'])
    last_date = gold_price_data['Date'].max()

    # Generate future dates starting from the last date in the dataset
    future_dates = [last_date + timedelta(days=i) for i in range(1, num_days + 1)]
    
    # Prepare input data for prediction
    future_data = pd.DataFrame({
        "SPX": [1500] * num_days,        # Replace with realistic values or user inputs
        "USO": [70] * num_days,
        "SLV": [15] * num_days,
        "EUR/USD": [1.2] * num_days,
        "Year": [date.year for date in future_dates],
        "Month": [date.month for date in future_dates],
        "Day": [date.day for date in future_dates],
        "DayOfWeek": [date.weekday() for date in future_dates],
        "IsWeekend": [1 if date.weekday() >= 5 else 0 for date in future_dates]
    })
    
    # Make predictions
    predictions = model.predict(future_data)
    
    # Save to history
    for date, pred in zip(future_dates, predictions):
        history.append({"Date": date.strftime("%Y-%m-%d"), "Prediction": pred, "Model": selected_model_name})
    
    # Prepare data for visualization
    history_df = pd.DataFrame(history)
    recent_predictions = history_df[history_df["Model"] == selected_model_name]
    
    # Plot results
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=recent_predictions, x="Date", y="Prediction", marker="o")
    plt.title(f"Predictions by {selected_model_name}")
    plt.xlabel("Date")
    plt.ylabel("GLD Price")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plot_path = os.path.join("static", "prediction_plot.png")
    plt.savefig(plot_path)
    plt.close()
    
    return render_template("results.html", predictions=recent_predictions, plot_path=plot_path)

if __name__ == "__main__":
    app.run(debug=True)
