import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from yfinance import ticker
from database_manager import OwnedStock, User, session
from sqlalchemy.exc import SQLAlchemyError
from database_manager import OwnedStock

root = ctk.CTk()
root.title("Owned Stocks")

class OwnedStocksManager:

    def __init__(self, home, homeroot, current_username):
        self.root = ctk.CTk()
        self.homeroot = homeroot
        self.home = home
        self.current_username = current_username  # Store the current_username
        self.root.geometry("800x600")
        self.root.title("Manage Bank owned stocks")
        self.setup_gui()

    def return_home(self):
        self.home(self.current_username)



    def add_owned_stock(self):
        username = self.username_entry.get().strip()
        # stock_name = self.stock_name_entry.get().strip()
        date_purchased = self.date_purchased_entry.get().strip()
        stock_ticker = self.stocks_dropdown.get().split("-")[0]
        # stock_name = self.stocks_dropdown.get().split("-")[1]

        if not username:
            messagebox.showerror("Error", "Username is required")
            return

        if not date_purchased:
            messagebox.showerror("Error", "Purchase date is required")
            return

        if not stock_ticker:
            messagebox.showerror("Error", "Stock not selected")
       
        user = User.get_user_by_username(username)
        if user is None:
            messagebox.showerror("Error", "User not found")
            return

        owned_stock = OwnedStock(
           userid=user.userid,
           date_purchased=date_purchased,
           stock_ticker=stock_ticker,
                )

        if owned_stock.save_stock():
            messagebox.showinfo("Success", "Owned stock added successfully!")
            self.view_all_owned_stocks()
            self.clear_form()
        else:
            messagebox.showerror("Error", "Failed to add owned stock")

    def delete_owned_stock(self, stock_id: int):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this stock?"):
            if OwnedStock.delete_stock(stock_id):
                messagebox.showinfo("Success", "Owned stock deleted successfully!")
                self.view_all_owned_stocks()
            else:
                messagebox.showerror("Error", "Failed to delete owned stock")


    def create_owned_stock_frame(self, parent, stock_data):
        owned_stock_frame = ctk.CTkFrame(parent)
        owned_stock_frame.pack(pady=5, fill="x", expand=True)

        stock_id, stock_ticker, date_purchased, *_ = stock_data
        
        info_frame = ctk.CTkFrame(owned_stock_frame)
        info_frame.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        
        labels = [
            f"Stock ID: {stock_id}",
            f"Stock Ticker: {stock_ticker}",
            f"Date of purchase: {date_purchased}"
        ]
        
        for label_text in labels:
            ctk.CTkLabel(info_frame, text=label_text).pack(anchor="w")

        delete_btn = ctk.CTkButton(
            owned_stock_frame, text="Delete Stock", command=lambda cid=stock_id: self.delete_owned_stock(cid),
            fg_color="red", hover_color="darkred", width=100
        )
        delete_btn.pack(side="right", padx=10)

    def clear_form(self):
        self.username_entry.delete(0, tk.END)
        # self.stock_name_entry.delete(0, tk.END)
        self.date_purchased_entry.delete(0, tk.END)
        # self.owned_stock_type_var.set("Visa Debit")


    def setup_add_owned_stock_form(self, parent):
        form_frame = ctk.CTkFrame(parent)
        form_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(form_frame, text="Username:").pack(pady=(10, 0))
        self.username_entry = ctk.CTkEntry(form_frame)
        self.username_entry.pack(pady=(0, 10))
        self.username_entry.insert(0, "james_wilson")

        # ctk.CTkLabel(form_frame, text="Stock Name:").pack(pady=(10, 0))
        # self.stock_name_entry = ctk.CTkEntry(form_frame)
        # self.stock_name_entry.pack(pady=(0, 10))
        # self.stock_name_entry.insert(0, "Microsoft")

        ctk.CTkLabel(form_frame, text="Date Purchased (DD/MM/YY):").pack(pady=(10, 0))
        self.date_purchased_entry = ctk.CTkEntry(form_frame)
        self.date_purchased_entry.pack(pady=(0, 10))
        self.date_purchased_entry.insert(0, "01/12/24")

        ctk.CTkLabel(form_frame, text="Stock Ticker:").pack(pady=(10, 0))
        stocks = [
        "AAPL-Apple Inc.",
        "MSFT-Microsoft Corporation",
        "GOOGL-Alphabet Inc.",
        "AMZN-Amazon.com Inc.",
        "NVDA-NVIDIA Corporation",
        "META-Meta Platforms Inc.",
        "TSLA-Tesla Inc.",
        "JPM-JPMorgan Chase & Co.",
        "V-Visa Inc.",
        "WMT-Walmart Inc.",
        "KO-The Coca-Cola Company",
        "DIS-The Walt Disney Company",
        "NFLX-Netflix Inc.",
        "ADBE-Adobe Inc.",
        "PYPL-PayPal Holdings Inc.",
        "INTC-Intel Corporation",
        "AMD-Advanced Micro Devices Inc.",
        "CRM-Salesforce Inc.",
        "BA-Boeing Company",
        "GE-General Electric Company"
    ]

        self.owned_stock_type_var = ctk.StringVar(value=("AAPL-Apple Inc."))
        self.stocks_dropdown = ctk.CTkOptionMenu(form_frame, values=stocks, variable=self.owned_stock_type_var)
        self.stocks_dropdown.pack(pady=(0, 10))


        submit_btn = ctk.CTkButton(form_frame, text="Add Owned_stock", command=self.add_owned_stock)
        submit_btn.pack(pady=20)

        clear_btn = ctk.CTkButton(form_frame, text="Clear Form", command=self.clear_form)
        clear_btn.pack(pady=(0, 20))



    def view_all_owned_stocks(self):
        try:
            for widget in self.owned_stocks_frame.winfo_children():
                widget.destroy()

            stocks = session.query(OwnedStock).join(User).all()
            
            if not stocks:
                no_owned_stocks_label = ctk.CTkLabel(self.owned_stocks_frame, text="No stocks found", font=("Arial", 14))
                no_owned_stocks_label.pack(pady=20)
                return

            with open("user_id.txt", "r") as f:
                current_user_id = f.readline().strip()

            for stock in stocks:
                stock_data = (
                    # stock.userid,
                    stock.stockid,
                    stock.stock_ticker,
                    stock.date_purchased
                )
                
                # if account.userid == User.get_user_id(self.current_username):
                if str(stock.userid) == current_user_id:
                    self.create_owned_stock_frame(self.owned_stocks_frame, stock_data)

        except SQLAlchemyError as e:
            messagebox.showerror("Database Error", f"Failed to retrieve accounts: {str(e)}")

    def remove_stock(self, stock_id: int):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this stock?"):
            if OwnedStock.delete_stock(stock_id):
                messagebox.showinfo("Success", "Stock deleted successfully!")
                self.view_all_owned_stocks()
            else:
                messagebox.showerror("Error", "Failed to delete stock")



    def setup_gui(self):
        self.notebook = ctk.CTkTabview(self.root)
        self.notebook.pack(padx=20, pady=20, fill="both", expand=True)

        self.notebook.add("View All Owned Stocks")
        self.notebook.add("Add Stocks")

        view_frame = self.notebook.tab("View All Owned Stocks")
        view_button = ctk.CTkButton(view_frame, text="View/Refresh Owned Stocks", command=self.view_all_owned_stocks)
        view_button.pack(pady=10)

        self.owned_stocks_frame = ctk.CTkScrollableFrame(view_frame, height=400)
        self.owned_stocks_frame.pack(pady=10, fill="both", expand=True)

        add_frame = self.notebook.tab("Add Stocks")
        self.setup_add_owned_stock_form(add_frame)

        home_button = ctk.CTkButton(view_frame, command=self.return_home, text="Return Home")
        home_button.pack()




root.mainloop()
