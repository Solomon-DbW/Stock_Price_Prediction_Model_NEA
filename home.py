import customtkinter as ctk
from cryptography.fernet import Fernet
from encryption_key import load_key
from price_predictor import StockPricePredictor
import threading
import logging
import os
import yfinance as yf
from view_available_stocks import view_available_stocks_predictions
from bank_accounts import BankAccountManager
from database_manager import User

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TF logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the encryption key
key = load_key()
cipher_suite = Fernet(key)

# Create a class for the stock button
class StockButton(ctk.CTkButton):
    def __init__(self, master, ticker, company_name, **kwargs):
        super().__init__(master, **kwargs)
        self.ticker = ticker
        self.company_name = company_name

def home(current_user_name):
    root = ctk.CTk()
    WIDTH = 1000  # Increased width to accommodate stock list and prediction
    HEIGHT = 800
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.title("Stock Price Predictor")
    
    view_available_stocks_button = ctk.CTkButton(
        root, 
        text="View available stocks", 
        command=lambda: view_available_stocks_predictions(StockButton, logger, homeroot=root, home=home)
    )
    view_available_stocks_button.pack(pady=10)

    # current_username = User.get_username(current_user_id)
    bank_accounts_button = ctk.CTkButton(
        root, 
        text="Manage bank accounts", 
        command=lambda: BankAccountManager(home=home, homeroot=root, current_username=current_user_name)
    )
    bank_accounts_button.pack(pady=10)

    root.mainloop()

# if __name__ == "__main__":
    # home()

