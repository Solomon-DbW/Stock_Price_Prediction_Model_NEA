# Create separate windows for available stocks, owned stocks, user bank account info

import customtkinter as ctk
from cryptography.fernet import Fernet
from encryption_key import load_key
from price_predictor import StockPricePredictor
import threading
import logging
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TF logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the encryption key
key = load_key()
cipher_suite = Fernet(key)

def home():
    root = ctk.CTk()
    WIDTH = 600  # Increased width for better visibility
    HEIGHT = 800  # Increased height for scrollable content
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.title("Stock Price Predictor")
    
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
            if status_label:
                status_label.configure(text=f"Error processing {ticker}: {str(e)}")
            else:
                ctk.CTkLabel(stock_frame,
                    text=f"Error processing {ticker}: {str(e)}",
                    text_color="red").pack(pady=5)
    
    def display_available_stocks():
        # Create popup window
        results_popup = ctk.CTkToplevel(root)
        results_popup.title("Stock Predictions")
        results_popup.geometry("580x700")
        
        # Add scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(results_popup)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header = ctk.CTkLabel(scrollable_frame,
            text="Real-Time Stock Predictions",
            font=("Arial", 20, "bold"))
        header.pack(pady=10)
        
        # Info label
        info_label = ctk.CTkLabel(scrollable_frame,
            text="Processing stocks... Please wait.",
            font=("Arial", 12))
        info_label.pack(pady=5)
        
        # Available stocks - you might want to fetch this from an API or database
        available_stocks = ["AAPL", "NVDA", "GOOGL"]
        
        # Process each stock in a separate thread
        threads = []
        for ticker in available_stocks:
            thread = threading.Thread(
                target=process_stock,
                args=(ticker, scrollable_frame),
                daemon=True
            )
            thread.start()
            threads.append(thread)
        
        # Update info label when all threads complete
        def check_threads():
            if any(t.is_alive() for t in threads):
                results_popup.after(1000, check_threads)
            else:
                info_label.configure(text="All stocks processed!")
        
        results_popup.after(1000, check_threads)
    
    # Main window elements
    title_frame = ctk.CTkFrame(root)
    title_frame.pack(fill="x", padx=20, pady=20)
    
    welcome_label = ctk.CTkLabel(
        title_frame,
        text="Welcome to Forecastr!",
        font=("Arial", 24, "bold"))
    welcome_label.pack(pady=10)
    
    button_frame = ctk.CTkFrame(root)
    button_frame.pack(fill="x", padx=20)
    
    available_stocks_button = ctk.CTkButton(
        button_frame,
        text="View Stock Predictions",
        command=display_available_stocks,
        font=("Arial", 16))
    available_stocks_button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    home()
