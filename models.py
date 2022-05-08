from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

#MODELS go below
# class Table_Name(singular)(db.Model):
#     __tablename__ = 'table_name(s)'
#
#     @classmethods go here
#
#     def __repr__(self):
#         s = self
#         return f"<Table_Name id={s.id} col1={s.col1} col2={s.col2}"
#
#     id = db.Column(
#         db.Integer,
#         primary_key=True,
#         autoincrement=True
#     )
#
#     col1_name = db.Column(
#         db.String(50),
#         nullable=False,
#         unique=True,
#         default=X
#     )
#
#     col2_name = db.Column(
#         db.Data_type,
#         arg1,
#         arg2,
#         etc...
#     )
#
#     def custom_method(self): 