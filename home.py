# Create separate windows for available stocks, owned stocks, user bank account info

import sqlite3
import customtkinter as ctk
from cryptography.fernet import Fernet
from encryption_key import load_key
from signup import signup
from login import login

# Load the encryption key
key = load_key()
cipher_suite = Fernet(key)

# Home window
def home():
    root = ctk.CTk()
    WIDTH = 400
    HEIGHT = 400
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.title("Stock Price Predictor")
    
    def display_owned_stocks():
        # owned_stocks_label = ctk.CTkLabel(root, text="Owned stocks", font=("Arial", 16))
        # owned_stocks_label.place(relx=0.5, rely=0.18, anchor=ctk.CENTER)
        owned_stocks_popup = ctk.CTkToplevel(root)
        owned_stocks_popup.title("Owned stocks")
        owned_stocks = ["AAPL", "TSLA", "NVDA"]
        variable = ctk.StringVar()
        variable.set(owned_stocks[0])
        combobox = ctk.CTkComboBox(root, values=owned_stocks, variable=variable)
        combobox.pack()

    def display_available_stocks():
        available_stocks_label = ctk.CTkLabel(root, text="Available stocks", font=("Arial", 16))
        available_stocks_label.place(relx=0.5, rely=0.18, anchor=ctk.CENTER)

    welcome_label = ctk.CTkLabel(root, text="Welcome to Forecastr!", font=("Arial", 16))
    welcome_label.place(relx=0.5, rely=0.03, anchor=ctk.CENTER)

    owned_stocks_button = ctk.CTkButton(root, text="View currently owned stocks", command=display_owned_stocks, font=("Arial", 16))
    owned_stocks_button.place(relx=0.5, rely=0.08, anchor=ctk.CENTER)

    available_stocks_button = ctk.CTkButton(root, text="View stocks available for purchase", command=display_available_stocks, font=("Arial", 16))
    available_stocks_button.place(relx=0.5, rely=0.13, anchor=ctk.CENTER)

    root.mainloop()

# Uncomment to test signup or login functionality
# signup(home)
# login(home)
