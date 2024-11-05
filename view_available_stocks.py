import customtkinter as ctk
from price_predictor import StockPricePredictor 
import threading
from plyer import notification

def view_available_stocks_predictions(StockButton, logger, homeroot, home):
    homeroot.destroy()
    root = ctk.CTk()
    WIDTH = 1000  # Increased width to accommodate stock list and prediction
    HEIGHT = 800
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.title("Stock Price Predictor Hello")


    # Available stocks with company names - you can extend this list
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
            # Create and configure stock frame
            stock_frame = ctk.CTkFrame(results_frame)
            stock_frame.pack(pady=5, padx=10, fill="x")
            
            # Status label
            status_label = ctk.CTkLabel(stock_frame, text=f"Fetching data for {ticker}...")
            status_label.pack(pady=5)
            
            # Initialize predictor
            predictor = StockPricePredictor(ticker)
            
            # Attempt to fetch data with retry mechanism
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if predictor.fetch_data():
                        break
                    elif attempt < max_retries - 1:
                        status_label.configure(text=f"Retrying {ticker} (attempt {attempt + 2}/{max_retries})...")
                        continue
                    else:
                        raise Exception(f"Failed to fetch data after {max_retries} attempts")
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
            
            status_label.configure(text=f"Processing {ticker} data...")
            
            # Prepare data and build model
            predictor.prepare_data()
            predictor.build_model()
            
            # Training progress frame
            progress_frame = ctk.CTkFrame(stock_frame)
            progress_frame.pack(fill="x", padx=5, pady=5)
            progress_label = ctk.CTkLabel(progress_frame, text="Training model...")
            progress_label.pack()
            
            # Train model with progress updates
            history = predictor.train_model(epochs=10, batch_size=32)
            
            # Get predictions
            next_price, price_change, percentage_change = predictor.predict_next_day()
            current_price = predictor.data['Close'].iloc[-1]
            
            # Clear progress indicators
            progress_frame.destroy()
            status_label.destroy()
            
            # Create results display
            header_label = ctk.CTkLabel(stock_frame, 
                text=f"{ticker} Stock Prediction",
                font=("Arial", 16, "bold"))
            header_label.pack(pady=5)
            
            # Current price
            current_price_frame = ctk.CTkFrame(stock_frame)
            current_price_frame.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(current_price_frame, 
                text=f"Current Price: ${current_price:.2f}",
                font=("Arial", 14)).pack(side="left", padx=5)
            
            # Predicted price
            pred_price_frame = ctk.CTkFrame(stock_frame)
            pred_price_frame.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(pred_price_frame,
                text=f"Predicted Price: ${next_price:.2f}",
                font=("Arial", 14)).pack(side="left", padx=5)

            # Notifying user on predictions
            if percentage_change > 0:
                notification.notify(title="Stock Price Prediction", 
                    message=f"Stock {ticker} is predicted to go up by ${price_change:.2f} ({percentage_change:.2f}%).",
                    timeout=20)
            else:
                notification.notify(title="Stock Price Prediction", 
                    message=f"Stock {ticker} is predicted to go down by ${price_change:.2f} ({percentage_change:.2f}%).",
                    timeout=20)
            
            # Change indicators
            change_frame = ctk.CTkFrame(stock_frame)
            change_frame.pack(fill="x", padx=5, pady=2)
            
            change_color = "green" if percentage_change > 0 else "red"
            change_symbol = "▲" if percentage_change > 0 else "▼"
            
            ctk.CTkLabel(change_frame,
                text=f"{change_symbol} ${abs(price_change):.2f} ({abs(percentage_change):.2f}%)",
                text_color=change_color,
                font=("Arial", 14)).pack(side="left", padx=5)
            
            # Add a separator
            separator = ctk.CTkFrame(stock_frame, height=2)
            separator.pack(fill="x", padx=10, pady=10)
            
        except Exception as e:
            logger.error(f"Error processing {ticker}: {str(e)}")
            if 'status_label' in locals():
                status_label.configure(text=f"Error processing {ticker}: {str(e)}")
            else:
                ctk.CTkLabel(stock_frame,
                    text=f"Error processing {ticker}: {str(e)}",
                    text_color="red").pack(pady=5)

    def display_stock_prediction(ticker, company_name):
        # Create results frame if it doesn't exist
        for widget in results_frame.winfo_children():
            widget.destroy()
            
        # Header
        header = ctk.CTkLabel(results_frame,
            text=f"Processing {ticker} ({company_name})",
            font=("Arial", 20, "bold"))
        header.pack(pady=10)
        
        # Info label
        info_label = ctk.CTkLabel(results_frame,
            text="Fetching data... Please wait.",
            font=("Arial", 12))
        info_label.pack(pady=5)
        
        # Process stock in a separate thread
        thread = threading.Thread(
            target=process_stock,
            args=(ticker, results_frame),
            daemon=True
        )
        thread.start()
        
        # Update info label when thread completes
        def check_thread():
            if thread.is_alive():
                root.after(1000, check_thread)
            else:
                info_label.configure(text="Processing complete!")
        
        root.after(1000, check_thread)

    # Create main layout
    # Left panel for stock list
    left_panel = ctk.CTkFrame(root, width=300)
    left_panel.pack(side="left", fill="y", padx=10, pady=10)
    left_panel.pack_propagate(False)

    def return_home(home):
        root.destroy()
        home()

    return_home_button = ctk.CTkButton(root, text="Return Home", command=lambda:return_home(home=home))
    return_home_button.pack()
    # Stock list title
    title_label = ctk.CTkLabel(
        left_panel,
        text="Available Stocks",
        font=("Arial", 20, "bold"))
    title_label.pack(pady=10)

    # Scrollable frame for stock buttons
    stock_scroll = ctk.CTkScrollableFrame(left_panel)
    stock_scroll.pack(fill="both", expand=True, padx=5, pady=5)

    # Create buttons for each stock
    for ticker, company in AVAILABLE_STOCKS:
        button = StockButton(
            stock_scroll,
            ticker=ticker,
            company_name=company,
            text=f"{ticker}\n{company}",
            command=lambda t=ticker, c=company: display_stock_prediction(t, c),
            font=("Arial", 14),
            height=60,
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            anchor="w",
            width=250
        )
        button.pack(pady=2, padx=5, fill="x")

    # Right panel for results
    right_panel = ctk.CTkFrame(root)
    right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # Welcome header
    welcome_label = ctk.CTkLabel(
        right_panel,
        text="Welcome to Forecastr!",
        font=("Arial", 24, "bold"))
    welcome_label.pack(pady=10)

    instruction_label = ctk.CTkLabel(
        right_panel,
        text="Select a stock from the list to view its prediction",
        font=("Arial", 14))
    instruction_label.pack(pady=5)

    # Results frame
    results_frame = ctk.CTkFrame(right_panel)
    results_frame.pack(fill="both", expand=True, padx=10, pady=10)

    root.mainloop()

