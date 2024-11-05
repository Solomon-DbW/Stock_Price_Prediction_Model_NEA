import customtkinter as ctk
from sqlalchemy.orm.decl_api import DeclarativeBase
from password_encryption import encrypt_password
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from database_manager import User, Base

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

        while not username or not password:
            ctk.CTkLabel(root, text="Please fill in all fields.").place(relx=0.5, rely=0.4, anchor=ctk.CENTER)
            return

        engine = create_engine("sqlite:///users_and_details.db")
        Base.metadata.create_all(bind=engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        # Check if username already exists
        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            ctk.CTkLabel(root, text="Username already taken.").place(relx=0.5, rely=0.4, anchor=ctk.CENTER)
        else:
            user = User(username, password)
            session.add(user)
            session.commit()
            ctk.CTkLabel(root, text="Signup successful!").place(relx=0.5, rely=0.4, anchor=ctk.CENTER)
        
        results = session.query(User).filter(User.username == "Bill")
        for result in results:
            print(result.username, result.password)
        session.close()


    signup_button = ctk.CTkButton(root, text="Sign up", command=submit_signup)
    signup_button.place(relx=0.5, rely=0.35, anchor=ctk.CENTER)
    
    root.mainloop()
