import sqlalchemy as sa
from sqlalchemy import orm
from .db_session import SqlAlchemyBase

import datetime as dt


class Project(SqlAlchemyBase):
    __tablename__ = "projects"

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True, unique=True)
    name = sa.Column(sa.String)  # название проекта
    short_desc = sa.Column(sa.String)  # краткое описание
    full_desc = sa.Column(sa.String)  # полное описание
    budget = sa.Column(sa.Float)  # бюджет в рублях
    founded = sa.Column(sa.Float, default=0)
    categories = sa.Column(sa.String)  # строка с id через пробел "1 3 15"
    start_time = sa.Column(sa.DateTime, default=dt.datetime.utcnow)  # время начала
    duration = sa.Column(sa.Integer, default=2592000)  # seconds, default = 30 days
    image_path = sa.Column(sa.String)  # путь до изображения
    author_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    featured = sa.Column(sa.Boolean, default=False)
    sponsors = sa.Column(sa.String, default="{}")

    author = orm.relation("User")

