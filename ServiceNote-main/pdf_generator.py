import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfutils
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import tempfile

def format_currency(amount):
    """Format currency in Indonesian Rupiah"""
    return f"Rp{amount:,.2f}".replace(",", ".")

def generate_invoice_pdf(invoice_data):
    """Generate PDF invoice matching the template design"""
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.close()
    
    # Create PDF document
    doc = SimpleDocTemplate(temp_file.name, pagesize=A4,
                           rightMargin=20*mm, leftMargin=20*mm,
                           topMargin=20*mm, bottomMargin=20*mm)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=colors.blue
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=6
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_LEFT,
        spaceAfter=6
    )
    
    # Build content
    content = []
    
    # Company header
    content.append(Paragraph("FJ SERVICE KOMPUTER LAPTOP HANDPHONE", title_style))
    content.append(Paragraph("KP Jl. Pasir Wangi No.RT 01, RW 11, Kec. Lembang, Kabupaten", subtitle_style))
    content.append(Paragraph("Bandung Barat, Jawa Barat 40391", subtitle_style))
    content.append(Paragraph("Nomor Telepon / WA : 0818-0441-1937", subtitle_style))
    content.append(Spacer(1, 20))
    
    # Customer info and date
    customer_data = [
        ["Nama Pembeli:", invoice_data['customer_name'], "Tanggal:", invoice_data['date']],
        ["No. Telepon:", invoice_data['customer_phone'], "", ""]
    ]
    
    customer_table = Table(customer_data, colWidths=[25*mm, 70*mm, 20*mm, 30*mm])
    customer_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    content.append(customer_table)
    content.append(Spacer(1, 15))
    
    # Service items table header
    table_data = [["No", "Perbaikan", "Harga", "Jumlah"]]
    
    # Add service items
    for i, item in enumerate(invoice_data['service_items'], 1):
        table_data.append([
            str(i),
            item['description'],
            format_currency(item['price']),
            str(item['quantity'])
        ])
    
    # Fill empty rows to match template (up to 10 rows)
    while len(table_data) < 11:  # 1 header + 10 data rows
        table_data.append(["", "", "", ""])
    
    # Create main table
    col_widths = [10*mm, 90*mm, 30*mm, 20*mm]
    items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Style the table
    items_table.setStyle(TableStyle([
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        
        # Data rows styling
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # No column center
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Description left
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),   # Price right
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Quantity center
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    content.append(items_table)
    content.append(Spacer(1, 10))
    
    # Totals section
    totals_data = [
        ["Harga Asli", format_currency(invoice_data['subtotal'])],
        ["Diskon", format_currency(invoice_data['discount_amount'])],
        ["Harga Total", format_currency(invoice_data['total'])]
    ]
    
    totals_table = Table(totals_data, colWidths=[40*mm, 30*mm])
    totals_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('BACKGROUND', (0, 1), (-1, 1), colors.blue),
        ('BACKGROUND', (0, 2), (-1, 2), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    # Position totals table to the right
    totals_frame_data = [["", totals_table]]
    totals_frame = Table(totals_frame_data, colWidths=[100*mm, 70*mm])
    totals_frame.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    content.append(totals_frame)
    content.append(Spacer(1, 15))
    
    # Warranty notice
    warranty_text = "* struk ini adalah bukti pembayaran dan klaim garansi"
    content.append(Paragraph(warranty_text, styles['Normal']))
    content.append(Spacer(1, 20))
    
    # Bottom section with warranty and signature
    bottom_data = [
        ["GARANSI 3 BULAN", "Hormat Kami"],
        ["", ""],
        ["", ""],
        ["", "Fajar Julyana"]
    ]
    
    bottom_table = Table(bottom_data, colWidths=[85*mm, 85*mm])
    bottom_table.setStyle(TableStyle([
        # Warranty box
        ('BOX', (0, 0), (0, 0), 2, colors.green),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 12),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.green),
        ('LINESTYLE', (0, 0), (0, 0), 'dashed'),
        
        # Signature section
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTSIZE', (1, 0), (1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    content.append(bottom_table)
    
    # Build PDF
    doc.build(content)
    
    return temp_file.name
