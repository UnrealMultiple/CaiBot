from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from caibot.db.model.base import Base


class CheckLog(Base):
    __tablename__ = "check_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(index=True)
    group_id: Mapped[int] = mapped_column(index=True)
    rejected: Mapped[bool] = mapped_column()
    time: Mapped[datetime] = mapped_column(default=datetime.now())
