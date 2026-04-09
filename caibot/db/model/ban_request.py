from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy.orm import mapped_column, Mapped

from caibot.db.model.base import Base


class BanRequest(Base):
    __tablename__ = "ban_request"

    id: Mapped[int] = mapped_column(BigInteger,primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger,index=True)
    reason: Mapped[str] = mapped_column(default="")
    creator_user_id: Mapped[int] = mapped_column(BigInteger,index=True)
    creator_group_id: Mapped[int] = mapped_column(BigInteger,index=True)
    reviewed: Mapped[bool] = mapped_column(default=False)
    approve: Mapped[bool] = mapped_column(default=False)
    reviewer_id: Mapped[int] = mapped_column(BigInteger,index=True, default=0)
    time: Mapped[datetime] = mapped_column(default=datetime.now())
