import sqlite3
import customtkinter as ctk
from password_encryption import encrypt_password, decrypt_password 

def signup(home):
    root = ctk.CTk()
    WIDTH = 400
    HEIGHT = 400
    root.geometry(f"{WIDTH}x{HEIGHT}")

    username_entry = ctk.CTkEntry(root, placeholder_text="Create your username: ")
    username_entry.place(relx=0.5, rely=0.1, anchor=ctk.CENTER)

    password_entry = ctk.CTkEntry(root, placeholder_text="Create your password: ", show="*")
    password_entry.place(relx=0.5, rely=0.2, anchor=ctk.CENTER)

    show_password = ctk.BooleanVar()
    show_password_check = ctk.CTkCheckBox(
        root, 
        text="Show password", 
        variable=show_password, 
        command=lambda: password_entry.configure(show="" if show_password.get() else "*")
    )
    show_password_check.place(relx=0.5, rely=0.3, anchor=ctk.CENTER)

    def submit_signup():
        username = username_entry.get()
        password = encrypt_password(password_entry.get())  # Encrypt password

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
        
        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone() is not None:
            ctk.CTkLabel(root, text="Username already taken.").place(relx=0.5, rely=0.4, anchor=ctk.CENTER)
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            ctk.CTkLabel(root, text="Signup successful!").place(relx=0.5, rely=0.4, anchor=ctk.CENTER)

        if cursor.fetchone() is None:
            cursor.close()
            conn.close()
            root.destroy()
            home()

    signup_button = ctk.CTkButton(root, text="Sign up", command=submit_signup)
    signup_button.place(relx=0.5, rely=0.35, anchor=ctk.CENTER)
    
    root.mainloop()

