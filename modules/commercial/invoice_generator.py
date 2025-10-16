"""
Generador de facturas automáticas para SalesMind
Crea facturas en PDF con numeración secuencial y cálculos de impuestos
"""

import os
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from modules.models import db
from modules.commercial_models import Invoice, Order, Product

class InvoiceGenerator:
    """Generador automático de facturas en PDF"""
    
    def __init__(self):
        self.invoice_dir = "instance/invoices"
        self._ensure_invoice_directory()
    
    def generate_invoice_from_order(self, order_id: int, tax_info: Dict = None) -> Dict:
        """
        Genera una factura automática basada en una orden
        
        Args:
            order_id: ID de la orden
            tax_info: Información fiscal adicional (NIT, dirección fiscal, etc.)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return {'success': False, 'error': 'Orden no encontrada'}
            
            if order.status not in ['confirmed', 'processing', 'shipped', 'delivered']:
                return {
                    'success': False, 
                    'error': 'La orden debe estar confirmada para generar factura'
                }
            
            # Verificar si ya existe factura para esta orden
            existing_invoice = Invoice.query.filter_by(order_id=order_id).first()
            if existing_invoice:
                return {
                    'success': False,
                    'error': f'Ya existe factura {existing_invoice.invoice_number} para esta orden'
                }
            
            # Crear registro de factura
            invoice = Invoice(
                client_id=order.client_id,
                order_id=order_id,
                invoice_number=self._generate_invoice_number(order.client_id),
                tax_id=tax_info.get('company_tax_id', '') if tax_info else '',
                customer_tax_id=tax_info.get('customer_tax_id', '') if tax_info else '',
                subtotal=order.subtotal,
                discount_amount=order.discount_amount,
                tax_amount=order.tax_amount,
                total_amount=order.total_amount,
                issue_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=30),  # 30 días para pago
                status='generated'
            )
            
            db.session.add(invoice)
            db.session.flush()  # Para obtener el ID
            
            # Generar PDF
            pdf_result = self._generate_invoice_pdf(invoice, order, tax_info)
            
            if not pdf_result['success']:
                db.session.rollback()
                return pdf_result
            
            invoice.pdf_path = pdf_result['pdf_path']
            db.session.commit()
            
            return {
                'success': True,
                'invoice_id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'pdf_path': invoice.pdf_path,
                'total_amount': float(invoice.total_amount),
                'due_date': invoice.due_date.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error generando factura: {str(e)}'}
    
    def update_invoice_status(self, invoice_id: int, new_status: str, 
                             payment_date: datetime = None) -> Dict:
        """
        Actualiza el estado de una factura
        
        Estados válidos: generated, sent, paid, overdue, cancelled
        """
        try:
            invoice = Invoice.query.get(invoice_id)
            if not invoice:
                return {'success': False, 'error': 'Factura no encontrada'}
            
            old_status = invoice.status
            invoice.status = new_status
            
            if new_status == 'paid' and payment_date:
                invoice.paid_at = payment_date
            elif new_status == 'paid' and not payment_date:
                invoice.paid_at = datetime.now()
            
            db.session.commit()
            
            return {
                'success': True,
                'invoice_id': invoice_id,
                'invoice_number': invoice.invoice_number,
                'old_status': old_status,
                'new_status': new_status,
                'message': f'Estado de factura actualizado de {old_status} a {new_status}'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error actualizando factura: {str(e)}'}
    
    def get_invoice_details(self, invoice_id: int) -> Optional[Dict]:
        """Obtiene detalles completos de una factura"""
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return None
        
        return {
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'client_id': invoice.client_id,
            'order_id': invoice.order_id,
            'order_number': invoice.order.order_number,
            'customer_name': invoice.order.customer_name,
            'customer_email': invoice.order.customer_email,
            'tax_id': invoice.tax_id,
            'customer_tax_id': invoice.customer_tax_id,
            'status': invoice.status,
            'subtotal': float(invoice.subtotal),
            'discount_amount': float(invoice.discount_amount),
            'tax_amount': float(invoice.tax_amount),
            'total_amount': float(invoice.total_amount),
            'issue_date': invoice.issue_date.isoformat(),
            'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
            'paid_at': invoice.paid_at.isoformat() if invoice.paid_at else None,
            'pdf_path': invoice.pdf_path,
            'notes': invoice.notes,
            'items': [
                {
                    'product_name': item.product.name,
                    'product_sku': item.product.sku,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'discount_percentage': item.discount_percentage,
                    'line_total': float(item.line_total)
                }
                for item in invoice.order.order_items
            ]
        }
    
    def list_invoices_by_client(self, client_id: int, status: Optional[str] = None,
                               limit: int = 50) -> List[Dict]:
        """Lista facturas de un cliente"""
        query = Invoice.query.filter_by(client_id=client_id)
        
        if status:
            query = query.filter_by(status=status)
        
        invoices = query.order_by(Invoice.created_at.desc()).limit(limit).all()
        
        return [
            {
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'customer_name': invoice.order.customer_name,
                'status': invoice.status,
                'total_amount': float(invoice.total_amount),
                'issue_date': invoice.issue_date.isoformat(),
                'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
                'is_overdue': (
                    invoice.due_date and 
                    datetime.now() > invoice.due_date and 
                    invoice.status != 'paid'
                )
            }
            for invoice in invoices
        ]
    
    def get_overdue_invoices(self, client_id: int) -> List[Dict]:
        """Obtiene facturas vencidas de un cliente"""
        overdue_invoices = Invoice.query.filter(
            Invoice.client_id == client_id,
            Invoice.due_date < datetime.now(),
            Invoice.status != 'paid'
        ).all()
        
        return [
            {
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'customer_name': invoice.order.customer_name,
                'total_amount': float(invoice.total_amount),
                'due_date': invoice.due_date.isoformat(),
                'days_overdue': (datetime.now() - invoice.due_date).days
            }
            for invoice in overdue_invoices
        ]
    
    def get_invoice_statistics(self, client_id: int, days: int = 30) -> Dict:
        """Obtiene estadísticas de facturación"""
        from sqlalchemy import func
        
        start_date = datetime.now() - timedelta(days=days)
        
        invoices_query = Invoice.query.filter(
            Invoice.client_id == client_id,
            Invoice.issue_date >= start_date
        )
        
        total_invoices = invoices_query.count()
        total_billed = invoices_query.with_entities(func.sum(Invoice.total_amount)).scalar() or 0
        
        paid_invoices = invoices_query.filter_by(status='paid').count()
        paid_amount = invoices_query.filter_by(status='paid').with_entities(
            func.sum(Invoice.total_amount)
        ).scalar() or 0
        
        overdue_count = Invoice.query.filter(
            Invoice.client_id == client_id,
            Invoice.due_date < datetime.now(),
            Invoice.status != 'paid'
        ).count()
        
        return {
            'period_days': days,
            'total_invoices': total_invoices,
            'total_billed': float(total_billed),
            'total_paid': float(paid_amount),
            'pending_amount': float(total_billed - paid_amount),
            'paid_invoices': paid_invoices,
            'overdue_invoices': overdue_count,
            'payment_rate': (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0
        }
    
    def _generate_invoice_pdf(self, invoice: Invoice, order: Order, tax_info: Dict = None) -> Dict:
        """Genera el archivo PDF de la factura"""
        try:
            # Nombre del archivo
            filename = f"factura_{invoice.invoice_number}.pdf"
            filepath = os.path.join(self.invoice_dir, filename)
            
            # Crear documento
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            
            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.darkblue,
                alignment=TA_CENTER,
                spaceAfter=20
            )
            
            # Título
            story.append(Paragraph(f"FACTURA DE VENTA", title_style))
            story.append(Paragraph(f"No. {invoice.invoice_number}", styles['Heading2']))
            story.append(Spacer(1, 20))
            
            # Información de la empresa y cliente
            company_info = tax_info or {}
            info_data = [
                ['INFORMACIÓN DE LA EMPRESA', 'INFORMACIÓN DEL CLIENTE'],
                [
                    f"Empresa: {company_info.get('company_name', 'Mi Empresa')}\\n"
                    f"NIT: {company_info.get('company_tax_id', 'N/A')}\\n"
                    f"Dirección: {company_info.get('company_address', 'N/A')}\\n"
                    f"Teléfono: {company_info.get('company_phone', 'N/A')}",
                    
                    f"Cliente: {order.customer_name}\\n"
                    f"Email: {order.customer_email or 'N/A'}\\n"
                    f"Teléfono: {order.customer_phone or 'N/A'}\\n"
                    f"NIT/CC: {invoice.customer_tax_id or 'N/A'}"
                ]
            ]
            
            info_table = Table(info_data, colWidths=[3*inch, 3*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # Fechas
            dates_data = [
                ['Fecha de Emisión:', invoice.issue_date.strftime('%d/%m/%Y')],
                ['Fecha de Vencimiento:', invoice.due_date.strftime('%d/%m/%Y') if invoice.due_date else 'N/A'],
                ['Orden Relacionada:', order.order_number]
            ]
            
            dates_table = Table(dates_data, colWidths=[2*inch, 2*inch])
            dates_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(dates_table)
            story.append(Spacer(1, 20))
            
            # Detalles de productos
            products_data = [['Producto', 'SKU', 'Cant.', 'Precio Unit.', 'Desc.%', 'Total']]
            
            for item in order.order_items:
                products_data.append([
                    item.product.name,
                    item.product.sku or 'N/A',
                    str(item.quantity),
                    f"${item.unit_price:,.0f}",
                    f"{item.discount_percentage}%",
                    f"${item.line_total:,.0f}"
                ])
            
            products_table = Table(products_data, colWidths=[2.5*inch, 0.8*inch, 0.6*inch, 1*inch, 0.6*inch, 1*inch])
            products_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Números alineados a la derecha
            ]))
            
            story.append(products_table)
            story.append(Spacer(1, 20))
            
            # Totales
            totals_data = [
                ['Subtotal:', f"${invoice.subtotal:,.0f}"],
                ['Descuento:', f"${invoice.discount_amount:,.0f}"],
                ['IVA (19%):', f"${invoice.tax_amount:,.0f}"],
                ['TOTAL A PAGAR:', f"${invoice.total_amount:,.0f}"]
            ]
            
            totals_table = Table(totals_data, colWidths=[3*inch, 2*inch])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 14),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.darkblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(totals_table)
            story.append(Spacer(1, 30))
            
            # Notas y términos
            notes_text = f"""
            <b>TÉRMINOS Y CONDICIONES:</b><br/>
            • Esta factura debe ser pagada antes de la fecha de vencimiento.<br/>
            • Los pagos pueden realizarse por transferencia bancaria o efectivo.<br/>
            • Para reclamos sobre esta factura, contactar dentro de 5 días hábiles.<br/>
            • {invoice.notes or ''}
            """
            
            story.append(Paragraph(notes_text, styles['Normal']))
            
            # Generar PDF
            doc.build(story)
            
            return {
                'success': True,
                'pdf_path': filepath,
                'filename': filename
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error generando PDF: {str(e)}'
            }
    
    def _generate_invoice_number(self, client_id: int) -> str:
        """Genera número secuencial de factura por cliente"""
        # Obtener el último número de factura del cliente
        last_invoice = Invoice.query.filter_by(client_id=client_id).order_by(
            Invoice.id.desc()
        ).first()
        
        if last_invoice:
            # Extraer número secuencial del último invoice_number
            try:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                next_number = last_number + 1
            except:
                next_number = 1
        else:
            next_number = 1
        
        # Formato: FAC-YYYYMM-CLIENTEID-NNNN
        year_month = datetime.now().strftime("%Y%m")
        return f"FAC-{year_month}-{client_id}-{next_number:04d}"
    
    def _ensure_invoice_directory(self):
        """Crea el directorio de facturas si no existe"""
        if not os.path.exists(self.invoice_dir):
            os.makedirs(self.invoice_dir)