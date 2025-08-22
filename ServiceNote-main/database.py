from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Dict

class Base(DeclarativeBase):
    pass

# Global database instance
db = SQLAlchemy(model_class=Base)

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    date: Mapped[str] = mapped_column(String(10), nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    discount_percent: Mapped[float] = mapped_column(Float, default=0.0)
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Relationship
    service_items: Mapped[List["ServiceItem"]] = relationship("ServiceItem", back_populates="invoice", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for template compatibility"""
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "date": self.date,
            "subtotal": self.subtotal,
            "discount_percent": self.discount_percent,
            "discount_amount": self.discount_amount,
            "total": self.total,
            "created_at": self.created_at.isoformat(),
            "service_items": [item.to_dict() for item in self.service_items]
        }

class ServiceItem(db.Model):
    __tablename__ = 'service_items'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey('invoices.id'), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Relationship
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="service_items")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for template compatibility"""
        return {
            "description": self.description,
            "price": self.price,
            "quantity": self.quantity
        }