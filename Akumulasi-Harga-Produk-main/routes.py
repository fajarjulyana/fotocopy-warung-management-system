from flask import render_template, request, redirect, url_for, flash, make_response, jsonify
from app import app, db
from models import Product, MaterialCost, ServiceCost, MaintenanceCost, Inventory, StockMovement
from datetime import datetime

@app.route('/')
def index():
    """Homepage showing overview of all products"""
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('index.html', products=products)

@app.route('/products')
def products():
    """List all products with their total costs"""
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('products.html', products=products)

@app.route('/product/<int:product_id>')
def product_details(product_id):
    """Show detailed cost breakdown for a specific product"""
    product = Product.query.get_or_404(product_id)
    return render_template('product_details.html', product=product)

@app.route('/product/new', methods=['GET', 'POST'])
def new_product():
    """Create a new product"""
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        
        if not name:
            flash('Nama produk harus diisi!', 'danger')
            return render_template('add_cost.html', cost_type='product')
        
        product = Product()
        product.name = name
        product.description = description
        db.session.add(product)
        db.session.commit()
        
        flash(f'Produk "{name}" berhasil ditambahkan!', 'success')
        return redirect(url_for('product_details', product_id=product.id))
    
    return render_template('add_cost.html', cost_type='product')

@app.route('/product/<int:product_id>/cost/<cost_type>/add', methods=['GET', 'POST'])
def add_cost(product_id, cost_type):
    """Add material, service, or maintenance cost to a product"""
    product = Product.query.get_or_404(product_id)
    
    if cost_type not in ['material', 'service', 'maintenance']:
        flash('Jenis biaya tidak valid!', 'danger')
        return redirect(url_for('product_details', product_id=product_id))
    
    if request.method == 'POST':
        try:
            # Common fields
            quantity = float(request.form['quantity'])
            unit = request.form['unit']
            unit_cost = float(request.form['unit_cost'])
            notes = request.form.get('notes', '')
            
            cost_item = None
            if cost_type == 'material':
                material_name = request.form['name']
                cost_item = MaterialCost()
                cost_item.product_id = product_id
                cost_item.material_name = material_name
                cost_item.quantity = quantity
                cost_item.unit = unit
                cost_item.unit_cost = unit_cost
                cost_item.notes = notes
                cost_item.calculate_total_cost()
                
            elif cost_type == 'service':
                service_name = request.form['name']
                service_type = request.form['service_type']
                cost_item = ServiceCost()
                cost_item.product_id = product_id
                cost_item.service_name = service_name
                cost_item.service_type = service_type
                cost_item.quantity = quantity
                cost_item.unit = unit
                cost_item.unit_cost = unit_cost
                cost_item.notes = notes
                cost_item.calculate_total_cost()
                
            elif cost_type == 'maintenance':
                equipment_name = request.form['name']
                maintenance_type = request.form['maintenance_type']
                cost_item = MaintenanceCost()
                cost_item.product_id = product_id
                cost_item.equipment_name = equipment_name
                cost_item.maintenance_type = maintenance_type
                cost_item.quantity = quantity
                cost_item.unit = unit
                cost_item.unit_cost = unit_cost
                cost_item.notes = notes
                cost_item.calculate_total_cost()
            
            db.session.add(cost_item)
            db.session.commit()
            
            flash(f'Biaya {cost_type} berhasil ditambahkan!', 'success')
            return redirect(url_for('product_details', product_id=product_id))
            
        except ValueError as e:
            flash('Format angka tidak valid!', 'danger')
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('add_cost.html', cost_type=cost_type, product=product)

@app.route('/cost/<cost_type>/<int:cost_id>/delete', methods=['POST'])
def delete_cost(cost_type, cost_id):
    """Delete a cost item"""
    try:
        if cost_type == 'material':
            cost_item = MaterialCost.query.get_or_404(cost_id)
        elif cost_type == 'service':
            cost_item = ServiceCost.query.get_or_404(cost_id)
        elif cost_type == 'maintenance':
            cost_item = MaintenanceCost.query.get_or_404(cost_id)
        else:
            flash('Jenis biaya tidak valid!', 'danger')
            return redirect(url_for('index'))
        
        product_id = cost_item.product_id
        db.session.delete(cost_item)
        db.session.commit()
        
        flash(f'Biaya {cost_type} berhasil dihapus!', 'success')
        return redirect(url_for('product_details', product_id=product_id))
        
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
        db.session.rollback()
        return redirect(url_for('index'))

@app.route('/product/<int:product_id>/calculate')
def calculate_unit_cost(product_id):
    """Calculate cost per unit for a product"""
    product = Product.query.get_or_404(product_id)
    units = request.args.get('units', 1, type=int)
    
    if units <= 0:
        flash('Jumlah unit harus lebih dari 0!', 'danger')
        return redirect(url_for('product_details', product_id=product_id))
    
    cost_per_unit = product.cost_per_unit(units)
    
    flash(f'Biaya per unit ({units} unit): Rp {cost_per_unit:,.2f}', 'info')
    return redirect(url_for('product_details', product_id=product_id))

@app.route('/print/price-list')
def print_price_list():
    """Print price list of all products"""
    products = Product.query.order_by(Product.name).all()
    return render_template('print_price_list.html', products=products)

@app.route('/api/products')
def api_products():
    """API endpoint for products data"""
    products = Product.query.all()
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'total_material_cost': float(product.total_material_cost),
            'total_service_cost': float(product.total_service_cost),
            'total_maintenance_cost': float(product.total_maintenance_cost),
            'total_cost': float(product.total_cost),
            'created_at': product.created_at.isoformat()
        })
    return jsonify(products_data)

@app.route('/inventory')
def inventory():
    """Halaman daftar inventory"""
    items = Inventory.query.order_by(Inventory.item_name).all()
    
    # Hitung statistik
    total_items = len(items)
    low_stock_items = [item for item in items if item.is_low_stock()]
    total_value = sum(item.total_value for item in items)
    
    return render_template('inventory.html', 
                         items=items,
                         total_items=total_items,
                         low_stock_count=len(low_stock_items),
                         total_value=total_value,
                         low_stock_items=low_stock_items)

@app.route('/inventory/new', methods=['GET', 'POST'])
def new_inventory_item():
    """Tambah item inventory baru"""
    if request.method == 'POST':
        try:
            item = Inventory()
            item.item_name = request.form['item_name']
            item.category = request.form['category']
            item.item_type = request.form.get('item_type')
            item.unit = request.form['unit']
            item.current_stock = float(request.form.get('current_stock', 0))
            item.minimum_stock = float(request.form.get('minimum_stock', 10))
            item.unit_price = float(request.form.get('unit_price', 0))
            item.supplier = request.form.get('supplier')
            item.location = request.form.get('location')
            item.notes = request.form.get('notes')
            
            if item.current_stock > 0:
                item.last_restock = datetime.utcnow()
            
            db.session.add(item)
            db.session.commit()
            
            # Buat stock movement untuk stok awal
            if item.current_stock > 0:
                movement = StockMovement()
                movement.inventory_id = item.id
                movement.movement_type = 'in'
                movement.quantity = item.current_stock
                movement.reason = 'Stok awal'
                movement.notes = 'Setup inventory awal'
                db.session.add(movement)
                db.session.commit()
            
            flash(f'Item {item.item_name} berhasil ditambahkan!', 'success')
            return redirect(url_for('inventory'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('inventory_form.html')

@app.route('/inventory/<int:item_id>/stock', methods=['POST'])
def update_stock(item_id):
    """Update stok item"""
    item = Inventory.query.get_or_404(item_id)
    
    try:
        movement_type = request.form['movement_type']  # in, out, adjustment
        quantity = float(request.form['quantity'])
        reason = request.form.get('reason', '')
        reference = request.form.get('reference', '')
        notes = request.form.get('notes', '')
        
        # Validasi
        if movement_type == 'out' and quantity > item.current_stock:
            flash('Stok tidak mencukupi!', 'danger')
            return redirect(url_for('inventory'))
        
        # Update stok
        old_stock = item.current_stock
        if movement_type == 'in':
            item.current_stock += quantity
            item.last_restock = datetime.utcnow()
        elif movement_type == 'out':
            item.current_stock -= quantity
        elif movement_type == 'adjustment':
            item.current_stock = quantity
        
        # Simpan movement
        movement = StockMovement()
        movement.inventory_id = item.id
        movement.movement_type = movement_type
        movement.quantity = quantity
        movement.reason = reason
        movement.reference = reference
        movement.notes = notes
        
        db.session.add(movement)
        db.session.commit()
        
        flash(f'Stok {item.item_name} berhasil diupdate: {old_stock} → {item.current_stock} {item.unit}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('inventory'))

@app.route('/api/inventory/low-stock')
def api_low_stock():
    """API untuk mendapatkan item dengan stok rendah"""
    items = Inventory.query.all()
    low_stock_items = []
    
    for item in items:
        if item.is_low_stock():
            low_stock_items.append({
                'id': item.id,
                'item_name': item.item_name,
                'current_stock': item.current_stock,
                'minimum_stock': item.minimum_stock,
                'unit': item.unit,
                'status': item.stock_status,
                'days_until_empty': item.days_until_empty()
            })
    
    return jsonify(low_stock_items)
