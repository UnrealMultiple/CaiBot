from datetime import datetime

from sqlalchemy.orm import mapped_column, Mapped

from caibot.db.model.base import Base


class BanRecord(Base):
    __tablename__ = "ban_record"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(index=True)
    reason: Mapped[str] = mapped_column(default="")
    creator_user_id: Mapped[int] = mapped_column(index=True)
    creator_group_id: Mapped[int] = mapped_column(index=True)
    reviewer_id: Mapped[int] = mapped_column(default=0)
    time: Mapped[datetime] = mapped_column(default=datetime.now())
