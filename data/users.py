import sqlalchemy as sa
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin

import datetime as dt


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True)
    email = sa.Column(sa.String, index=True, unique=True)
    login = sa.Column(sa.String, index=True, unique=True)
    personal_info = sa.Column(sa.String, nullable=True)
    image_path = sa.Column(sa.String, nullable=True)
    password_hash = sa.Column(sa.String)

    projects = orm.relation("Project", back_populates='author')

