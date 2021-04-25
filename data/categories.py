import sqlalchemy as sa
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Category(SqlAlchemyBase):
    __tablename__ = "categories"

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True, unique=True)
    name = sa.Column(sa.String)

