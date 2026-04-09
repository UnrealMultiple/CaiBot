from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from caibot.db.model.base import Base


class GroupAdmin(Base):
    __tablename__ = "group_admin"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    group_id: Mapped[int] = mapped_column(BigInteger,index=True)