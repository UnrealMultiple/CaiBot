from sqlalchemy import BigInteger
from sqlalchemy.orm import mapped_column, Mapped

from caibot.db.model.base import Base


class Group(Base):
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, index=True)
    group_id: Mapped[int] = mapped_column(BigInteger, index=True, unique=True)
    allow_ban: Mapped[bool] = mapped_column(default=True)
    allow_use_bot: Mapped[bool] = mapped_column(default=True)