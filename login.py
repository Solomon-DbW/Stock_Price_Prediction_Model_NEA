import customtkinter as ctk
# import sqlite3
from password_encryption import encrypt_password, decrypt_password
from database_manager import session, User

def login(home):
    root = ctk.CTk()
    WIDTH = 400
    HEIGHT = 400
    root.geometry(f"{WIDTH}x{HEIGHT}")

    username_entry = ctk.CTkEntry(root, placeholder_text="Enter your username: ")
    username_entry.place(relx=0.5, rely=0.1, anchor=ctk.CENTER)

    password_entry = ctk.CTkEntry(root, placeholder_text="Enter your password: ", show="*")
    password_entry.place(relx=0.5, rely=0.2, anchor=ctk.CENTER)

    show_password = ctk.BooleanVar()
    show_password_check = ctk.CTkCheckBox(root, text="Show password", variable=show_password, command=lambda: password_entry.configure(show="" if show_password.get() else "*"))
    show_password_check.place(relx=0.5, rely=0.3, anchor=ctk.CENTER)

    def submit_login():
        username = username_entry.get()
        password = password_entry.get()

        ###### USE SQLALCHEMY ######
        # conn = sqlite3.connect("users_and_details.db")
        # cursor = conn.cursor()
        # cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
        # cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        # user = cursor.fetchone()

        ###### USE DATABASE MANAGER ######
        user = session.query(User).filter_by(username=username).first()
        if user:
            try:
                stored_password = decrypt_password(user.password)  # Decrypt stored password
                if stored_password == password:
                    ctk.CTkLabel(root, text="Login successful!").place(relx=0.5, rely=0.4, anchor=ctk.CENTER)
                    current_user_id = user.userid #Stores the current user's id

                    with open("user_id.txt", "w") as f:
                        f.write(str(current_user_id))

                    root.destroy()
                    home(current_user_id)  # Call home window after login
                else:
                    ctk.CTkLabel(root, text="Incorrect password").place(relx=0.5, rely=0.4, anchor=ctk.CENTER)
            except Exception as e:
                ctk.CTkLabel(root, text=f"Decryption error: {e}").place(relx=0.5, rely=0.4, anchor=ctk.CENTER)
        else:
            ctk.CTkLabel(root, text="Username not found").place(relx=0.5, rely=0.4, anchor=ctk.CENTER)

    login_button = ctk.CTkButton(root, text="Log in", command=submit_login)
    login_button.place(relx=0.5, rely=0.35, anchor=ctk.CENTER)
    
    root.mainloop()


