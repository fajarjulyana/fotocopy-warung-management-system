from app import db
from datetime import datetime
from sqlalchemy import func

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    material_costs = db.relationship('MaterialCost', backref='product', lazy=True, cascade='all, delete-orphan')
    service_costs = db.relationship('ServiceCost', backref='product', lazy=True, cascade='all, delete-orphan')
    maintenance_costs = db.relationship('MaintenanceCost', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    @property
    def total_material_cost(self):
        return db.session.query(func.sum(MaterialCost.total_cost)).filter_by(product_id=self.id).scalar() or 0
    
    @property
    def total_service_cost(self):
        return db.session.query(func.sum(ServiceCost.total_cost)).filter_by(product_id=self.id).scalar() or 0
    
    @property
    def total_maintenance_cost(self):
        return db.session.query(func.sum(MaintenanceCost.total_cost)).filter_by(product_id=self.id).scalar() or 0
    
    @property
    def total_cost(self):
        return self.total_material_cost + self.total_service_cost + self.total_maintenance_cost
    
    def cost_per_unit(self, units=1):
        """Calculate cost per unit (e.g., cost per sheet of paper)"""
        if units <= 0:
            return 0
        return self.total_cost / units

class MaterialCost(db.Model):
    __tablename__ = 'material_costs'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    material_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(20), nullable=False, default='pcs')  # pcs, kg, liter, etc.
    unit_cost = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MaterialCost {self.material_name}>'
    
    def calculate_total_cost(self):
        """Calculate total cost based on quantity and unit cost"""
        self.total_cost = self.quantity * self.unit_cost
        return self.total_cost

class ServiceCost(db.Model):
    __tablename__ = 'service_costs'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String(50), nullable=False, default='labor')  # labor, design, consulting, etc.
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(20), nullable=False, default='hour')  # hour, day, project, etc.
    unit_cost = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ServiceCost {self.service_name}>'
    
    def calculate_total_cost(self):
        """Calculate total cost based on quantity and unit cost"""
        self.total_cost = self.quantity * self.unit_cost
        return self.total_cost

class MaintenanceCost(db.Model):
    __tablename__ = 'maintenance_costs'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    equipment_name = db.Column(db.String(100), nullable=False)
    maintenance_type = db.Column(db.String(50), nullable=False, default='routine')  # routine, repair, replacement, etc.
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit = db.Column(db.String(20), nullable=False, default='service')  # service, hour, replacement, etc.
    unit_cost = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MaintenanceCost {self.equipment_name}>'
    
    def calculate_total_cost(self):
        """Calculate total cost based on quantity and unit cost"""
        self.total_cost = self.quantity * self.unit_cost
        return self.total_cost

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # material, maintenance
    item_type = db.Column(db.String(50))  # kertas, tinta, cartridge, dll
    unit = db.Column(db.String(20), nullable=False, default='pcs')
    current_stock = db.Column(db.Float, nullable=False, default=0)
    minimum_stock = db.Column(db.Float, nullable=False, default=10)
    unit_price = db.Column(db.Float, nullable=False, default=0)
    supplier = db.Column(db.String(100))
    location = db.Column(db.String(100))  # gudang, lemari, dll
    notes = db.Column(db.Text)
    last_restock = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stock_movements = db.relationship('StockMovement', backref='item', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Inventory {self.item_name}>'
    
    @property
    def stock_status(self):
        """Determine stock status based on current vs minimum stock"""
        if self.current_stock <= 0:
            return 'danger'  # Habis
        elif self.current_stock <= self.minimum_stock:
            return 'warning'  # Rendah
        elif self.current_stock <= self.minimum_stock * 2:
            return 'info'  # Sedang
        else:
            return 'success'  # Aman
    
    @property
    def total_value(self):
        """Calculate total inventory value"""
        return self.current_stock * self.unit_price
    
    def is_low_stock(self):
        """Check if item has low stock"""
        return self.current_stock <= self.minimum_stock
    
    def days_until_empty(self, daily_usage=1):
        """Estimate days until stock runs out based on daily usage"""
        if daily_usage <= 0:
            return float('inf')
        return self.current_stock / daily_usage

class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # in, out, adjustment
    quantity = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(100))  # purchase, usage, damage, dll
    reference = db.Column(db.String(100))  # nomor PO, project, dll
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(50), default='System')
    
    def __repr__(self):
        return f'<StockMovement {self.movement_type}: {self.quantity}>'
