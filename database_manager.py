from sqlalchemy.orm.decl_api import DeclarativeBase
from password_encryption import encrypt_password
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///users_and_details.db")
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = "users"
    username = Column("username", String, unique=True)
    password = Column("password", String)
    userid = Column("userid", Integer, primary_key=True, autoincrement=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f"User({self.username}, {self.password}, {self.userid})"


class Card(Base):
    __tablename__ = "cards"

    cardid = Column("cardid", Integer, primary_key=True)
    userid = Column("userid", Integer, ForeignKey("users.userid"))
    card_holder_name = Column("card_holder_name", String)
    card_number = Column("card_number", String)
    expiration_date = Column("expiration_date", String)
    card_type = Column("card_type", String)
    cvv_code = Column("cvv_code", String)

    def __init__(self, cardid, userid, card_holder_name, card_number, expiration_date, card_type, cvv_code):
        self.cardid = cardid
        self.userid = userid
        self.card_holder_name = card_holder_name
        self.card_number = card_number
        self.expiration_date = expiration_date
        self.card_type = card_type
        self.cvv_code = cvv_code

    def __repr__(self):
        return f"Card({self.cardid}, {self.userid}, {self.card_holder_name}, {self.card_number}, {self.expiration_date}, {self.card_type}, {self.cvv_code})"

    def save_card(self):
        engine = create_engine("sqlite:///users_and_details.db")
        Base.metadata.create_all(bind=engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        session.add(self)
        session.commit()

    @staticmethod
    def delete_card(card_id: int) -> bool:
        try:
            card = session.query(Card).filter_by(cardid=card_id).first()
            if card:
                session.delete(card)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            messagebox.showerror("Database Error", f"Failed to delete card: {str(e)}")
            return False
