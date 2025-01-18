import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, TIMESTAMP, JSON, ForeignKey

from app.database import Base


class Order(Base):
    __tablename__ = 'order'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    items: Mapped[list] = mapped_column(JSON, default=[])
    created_by: Mapped[int] = mapped_column(Integer)

    order_details = relationship('OrderDetail', back_populates='order', lazy='selectin')

    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),
                                                          default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),
                                                          default=lambda: datetime.datetime.now(datetime.timezone.utc),
                                                          onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

class OrderDetail(Base):
    __tablename__ = 'order_detail'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey('order.id'))
    product_detail: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(255), default='pending')

    order = relationship('Order', back_populates='order_details', lazy='selectin')

    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),
                                                            default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True),
                                                            default=lambda: datetime.datetime.now(datetime.timezone.utc),
                                                            onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

