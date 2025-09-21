from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from datetime import datetime
import os

class PDFGenerator:
    def __init__(self, company_name):
        self.company_name = company_name
        self.styles = getSampleStyleSheet()
        
        # Register fonts if needed
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
            self.font_name = 'Arial'
        except:
            self.font_name = 'Helvetica'
    
    def generate_invoice(self, invoice_data, items, file_path):
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        elements = []
        
        # Company header
        company_style = ParagraphStyle(
            'CompanyStyle',
            parent=self.styles['Heading1'],
            fontName=self.font_name,
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        elements.append(Paragraph(self.company_name, company_style))
        
        # Invoice title
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=self.styles['Heading2'],
            fontName=self.font_name,
            fontSize=14,
            spaceAfter=12,
            alignment=1
        )
        invoice_type = "TAX INVOICE" if invoice_data['type'] == 'SALE' else "PURCHASE INVOICE"
        elements.append(Paragraph(invoice_type, title_style))
        
        # Invoice details
        invoice_info = [
            [f"Invoice Number: {invoice_data['invoice_number']}", f"Date: {invoice_data['date']}"],
            [f"Client: {invoice_data['client_name']}", ""]
        ]
        
        if invoice_data.get('gst_number'):
            invoice_info.append([f"GSTIN: {invoice_data['gst_number']}", ""])
        
        invoice_table = Table(invoice_info, colWidths=[3.5*inch, 3.5*inch])
        invoice_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(invoice_table)
        elements.append(Spacer(1, 20))
        
        # Items table
        items_data = [['SNo', 'Description', 'HSN Code', 'Quantity', 'Rate', 'Amount']]
        
        for i, item in enumerate(items, 1):
            items_data.append([
                str(i),
                item['description'] or item.get('product_name', ''),
                item['hsn_code'],
                str(item['quantity']),
                f"{item['rate']:.2f}",
                f"{item['amount']:.2f}"
            ])
        
        # Add total row
        items_data.append(['', '', '', '', 'Total:', f"{invoice_data['total_amount']:.2f}"])
        
        items_table = Table(items_data, colWidths=[0.4*inch, 2.5*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
        items_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
            ('FONT', (0, -1), (4, -1), self.font_name, 10),
            ('FONT', (5, -1), (5, -1), self.font_name, 10),
            ('BACKGROUND', (0, -1), (4, -1), colors.lightgrey),
            ('BACKGROUND', (5, -1), (5, -1), colors.beige),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            ('GRID', (0, -1), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 30))
        
        # Footer
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=self.styles['Normal'],
            fontName=self.font_name,
            fontSize=8,
            alignment=2
        )
        elements.append(Paragraph("Thank you for your business!", self.styles['Normal']))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Powered by PhoenixTechSolutions.inc", footer_style))
        
        # Build PDF
        doc.build(elements)
        return True