import customtkinter as ctk
import sqlite3
# from typing import Optional
import tkinter as tk
from tkinter import messagebox
import re
from datetime import datetime

class BankAccount:
    def __init__(self, card_holder_name: str, card_number: str, expiration_date: str, 
                 card_type: str, cvv_code: str, username: str):
        self.card_holder_name = card_holder_name
        self.card_number = card_number
        self.expiration_date = expiration_date
        self.card_type = card_type
        self.cvv_code = cvv_code
        self.username = username

    def save_card(self) -> bool:
        try:
            with sqlite3.connect("users_and_details.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS bankcards (
                        cardid INTEGER PRIMARY KEY AUTOINCREMENT,
                        userid INTEGER,
                        card_holder_name TEXT,
                        card_number TEXT,
                        expiration_date TEXT,
                        card_type TEXT,
                        cvv_code TEXT,
                        FOREIGN KEY (userid) REFERENCES users(userid)
                    )
                """)
                
                cursor.execute("SELECT userid FROM users WHERE username = ?", (self.username,))
                userid = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT INTO bankcards (userid, card_holder_name, card_number, 
                                         expiration_date, card_type, cvv_code)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (userid, self.card_holder_name, self.card_number,
                     self.expiration_date, self.card_type, self.cvv_code))
                conn.commit()
                return True
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save card: {str(e)}")
            return False

    @staticmethod
    def delete_card(card_id: int) -> bool:
        try:
            with sqlite3.connect("users_and_details.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM bankcards WHERE cardid = ?", (card_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete card: {str(e)}")
            return False


class BankAccountManager:
    def __init__(self, home, homeroot):
        self.root = ctk.CTk()
        self.homeroot = homeroot
        self.home = home
        self.root.geometry("800x600")
        self.root.title("Manage Bank Cards")
        self.setup_gui()
        homeroot.destroy()


    def return_home(self):
        self.root.destroy()
        self.home()

    def setup_gui(self):

        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(self.root)
        self.notebook.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Add tabs
        self.notebook.add("View Cards")
        self.notebook.add("Add Card")
        
        # Setup View Cards tab
        view_frame = self.notebook.tab("View Cards")
        view_button = ctk.CTkButton(
            view_frame,
            text="Refresh Bank Cards",
            command=self.view_all_bank_accounts
        )
        view_button.pack(pady=10)
        
        # Create a frame to hold the cards
        self.cards_frame = ctk.CTkScrollableFrame(view_frame, height=400)
        self.cards_frame.pack(pady=10, fill="both", expand=True)
        
        # Setup Add Card tab
        add_frame = self.notebook.tab("Add Card")
        self.setup_add_card_form(add_frame)

        # Setup Home button
        home_button = ctk.CTkButton(view_frame, command=self.return_home, text="Return Home")
        home_button.pack()

    def delete_card(self, card_id: int):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this card?"):
            if BankAccount.delete_card(card_id):
                messagebox.showinfo("Success", "Card deleted successfully!")
                self.view_all_bank_accounts()
            else:
                messagebox.showerror("Error", "Failed to delete card")

    def create_card_frame(self, parent, account_data):
        card_frame = ctk.CTkFrame(parent)
        card_frame.pack(pady=5, fill="x", expand=True)
        
        # Format card information
        card_id, username, card_holder, card_number, expiry, card_type = account_data
        masked_card = f"****-****-****-{card_number[-4:]}"
        
        # Create labels for card information
        info_frame = ctk.CTkFrame(card_frame)
        info_frame.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        
        labels = [
            f"Card ID: {card_id}",
            f"Username: {username}",
            f"Cardholder: {card_holder}",
            f"Card Number: {masked_card}",
            f"Expiry: {expiry}",
            f"Type: {card_type}"
        ]
        
        for label_text in labels:
            ctk.CTkLabel(info_frame, text=label_text).pack(anchor="w")
        
        # Create delete button
        delete_btn = ctk.CTkButton(
            card_frame,
            text="Delete Card",
            command=lambda cid=card_id: self.delete_card(cid),
            fg_color="red",
            hover_color="darkred",
            width=100
        )
        delete_btn.pack(side="right", padx=10)

    def view_all_bank_accounts(self):
        try:
            # Clear previous cards
            for widget in self.cards_frame.winfo_children():
                widget.destroy()

            with sqlite3.connect("users_and_details.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT b.cardid, u.username, b.card_holder_name, b.card_number, 
                           b.expiration_date, b.card_type 
                    FROM bankcards b
                    JOIN users u ON b.userid = u.userid
                """)
                accounts = cursor.fetchall()

                if not accounts:
                    no_cards_label = ctk.CTkLabel(
                        self.cards_frame,
                        text="No cards found",
                        font=("Arial", 14)
                    )
                    no_cards_label.pack(pady=20)
                    return

                # Create a frame for each card
                for account in accounts:
                    self.create_card_frame(self.cards_frame, account)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to retrieve accounts: {str(e)}")

    def setup_add_card_form(self, parent):
        form_frame = ctk.CTkFrame(parent)
        form_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Username
        ctk.CTkLabel(form_frame, text="Username:").pack(pady=(10, 0))
        self.username_entry = ctk.CTkEntry(form_frame)
        self.username_entry.pack(pady=(0, 10))
        self.username_entry.insert(0, "james_wilson")  # Default test value
        
        # Card holder name
        ctk.CTkLabel(form_frame, text="Cardholder Name:").pack(pady=(10, 0))
        self.card_holder_entry = ctk.CTkEntry(form_frame)
        self.card_holder_entry.pack(pady=(0, 10))
        self.card_holder_entry.insert(0, "James Wilson")  # Default test value
        
        # Card number
        ctk.CTkLabel(form_frame, text="Card Number:").pack(pady=(10, 0))
        self.card_number_entry = ctk.CTkEntry(form_frame)
        self.card_number_entry.pack(pady=(0, 10))
        self.card_number_entry.insert(0, "4929 0000 0000 6")  # Default test value
        
        # Expiration date
        ctk.CTkLabel(form_frame, text="Expiry Date (MM/YY):").pack(pady=(10, 0))
        self.expiration_entry = ctk.CTkEntry(form_frame)
        self.expiration_entry.pack(pady=(0, 10))
        self.expiration_entry.insert(0, "12/25")  # Default test value
        
        # Card type
        ctk.CTkLabel(form_frame, text="Card Type:").pack(pady=(10, 0))
        self.card_type_var = ctk.StringVar(value="Visa Debit")
        card_types = [
            "Visa Debit",
            "Mastercard Debit",
            "American Express",
            "Visa Credit",
            "Mastercard Credit",
            "Barclaycard",
            "Halifax",
            "NatWest",
            "Lloyds Bank",
            "HSBC"
        ]
        self.card_type_dropdown = ctk.CTkOptionMenu(
            form_frame,
            values=card_types,
            variable=self.card_type_var
        )
        self.card_type_dropdown.pack(pady=(0, 10))
        
        # CVV
        ctk.CTkLabel(form_frame, text="CVV:").pack(pady=(10, 0))
        self.cvv_entry = ctk.CTkEntry(form_frame, show="*")
        self.cvv_entry.pack(pady=(0, 10))
        self.cvv_entry.insert(0, "123")  # Default test value
        
        # Submit button
        submit_btn = ctk.CTkButton(
            form_frame,
            text="Add Card",
            command=self.add_card
        )
        submit_btn.pack(pady=20)
        
        # Clear button
        clear_btn = ctk.CTkButton(
            form_frame,
            text="Clear Form",
            command=self.clear_form
        )
        clear_btn.pack(pady=(0, 20))

    def clear_form(self):
        self.username_entry.delete(0, tk.END)
        self.card_holder_entry.delete(0, tk.END)
        self.card_number_entry.delete(0, tk.END)
        self.expiration_entry.delete(0, tk.END)
        self.cvv_entry.delete(0, tk.END)
        self.card_type_var.set("Visa Debit")

    def validate_card_number(self, card_number: str) -> bool:
        # Remove spaces and dashes
        card_number = card_number.replace(" ", "").replace("-", "")
        
        # UK cards are typically 16 digits, but some are 13-19
        if not (13 <= len(card_number) <= 19) or not card_number.isdigit():
            return False
            
        # Luhn algorithm check
        digits = [int(d) for d in card_number]
        checksum = 0
        for i in range(len(digits) - 1, -1, -1):
            d = digits[i]
            if i % 2 == len(digits) % 2:
                d *= 2
                if d > 9:
                    d -= 9
            checksum += d
        return checksum % 10 == 0

    def validate_expiration_date(self, exp_date: str) -> bool:
        if not re.match(r"^(0[1-9]|1[0-2])/([0-9]{2})$", exp_date):
            return False
        
        month, year = map(int, exp_date.split("/"))
        exp_date = datetime(2000 + year, month, 1)
        current_date = datetime.now()
        return exp_date > current_date

    def validate_cvv(self, cvv: str) -> bool:
        # UK cards typically use 3 digits, except Amex which uses 4
        if not cvv.isdigit():
            return False
        if self.card_type_var.get() == "American Express":
            return len(cvv) == 4
        return len(cvv) == 3

    def add_card(self):
        # Get values from form
        username = self.username_entry.get().strip()
        card_holder = self.card_holder_entry.get().strip()
        card_number = self.card_number_entry.get().strip()
        expiration = self.expiration_entry.get().strip()
        card_type = self.card_type_var.get()
        cvv = self.cvv_entry.get().strip()
        
        # Validate inputs
        if not username:
            messagebox.showerror("Error", "Username is required")
            return
            
        if not card_holder:
            messagebox.showerror("Error", "Cardholder name is required")
            return
            
        if not self.validate_card_number(card_number):
            messagebox.showerror("Error", "Invalid card number")
            return
            
        if not self.validate_expiration_date(expiration):
            messagebox.showerror("Error", "Invalid expiry date")
            return
            
        if not self.validate_cvv(cvv):
            messagebox.showerror("Error", "Invalid CVV")
            return
        
        # Create and save new card
        try:
            bank_card = BankAccount(
                card_holder_name=card_holder,
                card_number=card_number.replace(" ", "").replace("-", ""),
                expiration_date=expiration,
                card_type=card_type,
                cvv_code=cvv,
                username=username
            )
            
            if bank_card.save_card():
                messagebox.showinfo("Success", "Card added successfully!")
                self.clear_form()
                # Refresh view
                self.view_all_bank_accounts()
                # Switch to view tab
                self.notebook.set("View Cards")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add card: {str(e)}")


    def run(self):
        self.root.mainloop()

