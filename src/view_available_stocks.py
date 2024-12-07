import os
import customtkinter as ctk
from price_predictor import StockPricePredictor 
import threading
from plyer import notification

import price_predictor

def view_available_stocks_predictions(StockButton, logger, homeroot, home):
    homeroot.destroy()
    root = ctk.CTk()
    WIDTH = 1000
    HEIGHT = 800
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.title("Stock Price Predictor")

    AVAILABLE_STOCKS = [
        ("AAPL", "Apple Inc."),
        ("MSFT", "Microsoft Corporation"),
        ("GOOGL", "Alphabet Inc."),
        ("AMZN", "Amazon.com Inc."),
        ("NVDA", "NVIDIA Corporation"),
        ("META", "Meta Platforms Inc."),
        ("TSLA", "Tesla Inc."),
        ("JPM", "JPMorgan Chase & Co."),
        ("V", "Visa Inc."),
        ("WMT", "Walmart Inc."),
        ("KO", "The Coca-Cola Company"),
        ("DIS", "The Walt Disney Company"),
        ("NFLX", "Netflix Inc."),
        ("ADBE", "Adobe Inc."),
        ("PYPL", "PayPal Holdings Inc."),
        ("INTC", "Intel Corporation"),
        ("AMD", "Advanced Micro Devices Inc."),
        ("CRM", "Salesforce Inc."),
        ("BA", "Boeing Company"),
        ("GE", "General Electric Company")
    ]

    def process_stock(ticker, results_frame):
        try:
            stock_frame = ctk.CTkFrame(results_frame)
            stock_frame.pack(pady=5, padx=10, fill="x")

            status_label = ctk.CTkLabel(stock_frame, text=f"Fetching data for {ticker}...")
            status_label.pack(pady=5)

            predictor = StockPricePredictor(ticker)

            model_path = f"{ticker}_model.keras"
            if os.path.exists(model_path):
                status_label.configure(text=f"Loading existing model for {ticker}...")
                predictor.load_model(model_path)
            else:
                # Train a new model
                status_label.configure(text=f"Training new model for {ticker}...")
                if predictor.fetch_data():
                    predictor.prepare_data()
                    predictor.build_model()
                    predictor.train_model(epochs=10, batch_size=32)
                else:
                    raise Exception(f"Failed to fetch data for {ticker}")

            if predictor.fetch_data():
                predictor.prepare_data()
                predictor.build_model()
                predictor.train_model(epochs=10, batch_size=32)
                next_price, price_change, percentage_change = predictor.predict_next_day()
                status_label.configure(text=f"{ticker} - Predicted Price: ${next_price:.2f}")
            else:
                status_label.configure(text=f"Failed to fetch data for {ticker}")
        except Exception as e:
            logger.error(f"Error processing {ticker}: {str(e)}")
            status_label.configure(text=f"Error: {str(e)}")

    def display_stock_prediction(ticker, company_name):
        for widget in results_frame.winfo_children():
            widget.destroy()

        header = ctk.CTkLabel(results_frame, text=f"Processing {ticker} ({company_name})", font=("Arial", 20, "bold"))
        header.pack(pady=10)

        info_label = ctk.CTkLabel(results_frame, text="Fetching data... Please wait.", font=("Arial", 12))
        info_label.pack(pady=5)

        thread = threading.Thread(target=process_stock, args=(ticker, results_frame), daemon=True)
        thread.start()

    def return_home(home):
        with open("user_id.txt", "r") as f:
            lines = f.readlines()
            current_user_id = lines[0].strip()
            current_username = lines[1].strip()

        root.destroy()
        home(current_username)

    left_panel = ctk.CTkFrame(root, width=300)
    left_panel.pack(side="left", fill="y", padx=10, pady=10)
    left_panel.pack_propagate(False)

    return_home_button = ctk.CTkButton(left_panel, text="Return Home", command=lambda: return_home(home=home))
    return_home_button.pack(pady=10)

    stock_scroll = ctk.CTkScrollableFrame(left_panel)
    stock_scroll.pack(fill="both", expand=True, padx=5, pady=5)

    for ticker, company in AVAILABLE_STOCKS:
        button = ctk.CTkButton(
            stock_scroll,
            text=f"{ticker}\n{company}",
            command=lambda t=ticker, c=company: display_stock_prediction(t, c),
            font=("Arial", 14),
            height=60
        )
        button.pack(pady=2, padx=5, fill="x")

    right_panel = ctk.CTkFrame(root)
    right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    welcome_label = ctk.CTkLabel(right_panel, text="Welcome to Forecastr!", font=("Arial", 24, "bold"))
    welcome_label.pack(pady=10)

    instruction_label = ctk.CTkLabel(right_panel, text="Select a stock to view its prediction.", font=("Arial", 14))
    instruction_label.pack(pady=5)

    results_frame = ctk.CTkFrame(right_panel)
    results_frame.pack(fill="both", expand=True, padx=10, pady=10)

    root.mainloop()

