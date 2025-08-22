from flask import render_template, request, redirect, url_for, flash, send_file, jsonify
from app import app
from models import invoice_manager
from pdf_generator import generate_invoice_pdf
import logging

@app.route('/')
def index():
    """Home page with dashboard"""
    invoices = invoice_manager.get_all_invoices()
    recent_invoices = invoices[:5]  # Show only 5 recent invoices
    
    # Calculate stats
    total_invoices = len(invoices)
    total_revenue = sum(inv['total'] for inv in invoices)
    
    return render_template('index.html', 
                         recent_invoices=recent_invoices,
                         total_invoices=total_invoices,
                         total_revenue=total_revenue)

@app.route('/create_invoice', methods=['GET', 'POST'])
def create_invoice():
    """Create new invoice"""
    if request.method == 'POST':
        try:
            # Get form data
            customer_name = request.form.get('customer_name', '').strip()
            customer_phone = request.form.get('customer_phone', '').strip()
            discount = float(request.form.get('discount', 0))
            
            # Validate required fields
            if not customer_name or not customer_phone:
                flash('Nama pembeli dan nomor telepon harus diisi!', 'error')
                return render_template('create_invoice.html')
            
            # Get service items
            service_items = []
            item_count = int(request.form.get('item_count', 0))
            
            for i in range(item_count):
                description = request.form.get(f'item_description_{i}', '').strip()
                price = float(request.form.get(f'item_price_{i}', 0))
                quantity = int(request.form.get(f'item_quantity_{i}', 1))
                
                if description and price > 0:
                    service_items.append({
                        'description': description,
                        'price': price,
                        'quantity': quantity
                    })
            
            if not service_items:
                flash('Minimal satu item perbaikan harus diisi!', 'error')
                return render_template('create_invoice.html')
            
            # Create invoice
            invoice = invoice_manager.create_invoice(
                customer_name=customer_name,
                customer_phone=customer_phone,
                service_items=service_items,
                discount=discount
            )
            
            flash(f'Nota berhasil dibuat dengan ID: {invoice["id"]}', 'success')
            return redirect(url_for('view_invoice', invoice_id=invoice['id']))
            
        except Exception as e:
            logging.error(f"Error creating invoice: {e}")
            flash('Terjadi kesalahan saat membuat nota!', 'error')
    
    return render_template('create_invoice.html')

@app.route('/invoice/<int:invoice_id>')
def view_invoice(invoice_id):
    """View invoice details"""
    invoice = invoice_manager.get_invoice(invoice_id)
    if not invoice:
        flash('Nota tidak ditemukan!', 'error')
        return redirect(url_for('invoice_list'))
    
    return render_template('view_invoice.html', invoice=invoice)

@app.route('/invoice/<int:invoice_id>/pdf')
def download_pdf(invoice_id):
    """Generate and download PDF invoice"""
    invoice = invoice_manager.get_invoice(invoice_id)
    if not invoice:
        flash('Nota tidak ditemukan!', 'error')
        return redirect(url_for('invoice_list'))
    
    try:
        pdf_path = generate_invoice_pdf(invoice)
        return send_file(pdf_path, as_attachment=True, 
                        download_name=f'nota_{invoice_id}.pdf')
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        flash('Terjadi kesalahan saat membuat PDF!', 'error')
        return redirect(url_for('view_invoice', invoice_id=invoice_id))

@app.route('/invoices')
def invoice_list():
    """List all invoices with search"""
    query = request.args.get('q', '').strip()
    
    if query:
        invoices = invoice_manager.search_invoices(query)
    else:
        invoices = invoice_manager.get_all_invoices()
    
    return render_template('invoice_list.html', invoices=invoices, query=query)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
