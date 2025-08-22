from datetime import datetime
from typing import List, Dict, Optional
from database import db, Invoice, ServiceItem

class InvoiceManager:
    def create_invoice(self, customer_name: str, customer_phone: str, 
                      service_items: List[Dict], discount: float = 0.0) -> Dict:
        """Create a new invoice"""
        # Calculate totals
        subtotal = sum(item['price'] * item['quantity'] for item in service_items)
        discount_amount = subtotal * (discount / 100)
        total = subtotal - discount_amount
        
        # Create invoice
        invoice = Invoice(
            customer_name=customer_name,
            customer_phone=customer_phone,
            date=datetime.now().strftime("%d/%m/%Y"),
            subtotal=subtotal,
            discount_percent=discount,
            discount_amount=discount_amount,
            total=total
        )
        
        # Add service items
        for item_data in service_items:
            service_item = ServiceItem(
                description=item_data['description'],
                price=item_data['price'],
                quantity=item_data['quantity']
            )
            invoice.service_items.append(service_item)
        
        db.session.add(invoice)
        db.session.commit()
        
        return invoice.to_dict()
    
    def get_invoice(self, invoice_id: int) -> Optional[Dict]:
        """Get invoice by ID"""
        invoice = db.session.get(Invoice, invoice_id)
        return invoice.to_dict() if invoice else None
    
    def get_all_invoices(self) -> List[Dict]:
        """Get all invoices"""
        invoices = db.session.query(Invoice).order_by(Invoice.created_at.desc()).all()
        return [invoice.to_dict() for invoice in invoices]
    
    def search_invoices(self, query: str) -> List[Dict]:
        """Search invoices by customer name or phone"""
        query = f"%{query.lower()}%"
        from sqlalchemy import or_
        invoices = db.session.query(Invoice).filter(
            or_(
                Invoice.customer_name.ilike(query),
                Invoice.customer_phone.like(query)
            )
        ).order_by(Invoice.created_at.desc()).all()
        
        return [invoice.to_dict() for invoice in invoices]

# Global invoice manager instance
invoice_manager = InvoiceManager()
