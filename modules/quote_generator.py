# modules/quote_generator.py
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os
from datetime import datetime, timedelta
import uuid
import re

class QuoteGenerator:
    """Generador de cotizaciones PDF profesionales"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Crear estilos personalizados para la cotización"""
        
        # Estilo para el título principal
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E86AB')
        )
        
        # Estilo para subtítulos
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#A23B72')
        )
        
        # Estilo para texto normal
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_LEFT
        )
        
        # Estilo para precios destacados
        self.price_style = ParagraphStyle(
            'PriceStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#F18F01'),
            alignment=TA_RIGHT,
            spaceAfter=6
        )
    
    def extract_quote_info(self, ai_response: str, client_name: str) -> dict:
        """
        Extrae información estructurada de la respuesta de IA para crear la cotización
        """
        quote_data = {
            'client_name': client_name,
            'quote_number': f"COT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
            'date': datetime.now().strftime('%d/%m/%Y'),
            'valid_until': (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y'),
            'items': [],
            'subtotal': 0,
            'tax_rate': 0.19,  # 19% IVA
            'total': 0,
            'notes': ai_response,
            'currency': 'USD'
        }
        
        # Intentar extraer precios del texto de IA
        price_patterns = [
            r'\$[\d,]+\.?\d*',  # $100,000 o $100,000.00
            r'[\d,]+\.?\d*\s*(?:USD|usd|dólares|dollars)',  # 100,000 USD
            r'[\d,]+\.?\d*\s*(?:COP|cop|pesos)',  # 100,000 COP
        ]
        
        found_prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, ai_response)
            for match in matches:
                # Limpiar el precio
                clean_price = re.sub(r'[^\d.]', '', match.split()[0])
                if clean_price:
                    try:
                        price_value = float(clean_price)
                        found_prices.append(price_value)
                    except ValueError:
                        continue
        
        # Si encontramos precios, crear items
        if found_prices:
            for i, price in enumerate(found_prices[:5]):  # Máximo 5 items
                item_name = f"Propiedad/Servicio {i+1}"
                # Intentar extraer nombres de propiedades del contexto
                property_patterns = [
                    r'casa\s+\w+',
                    r'apartamento\s+\w+',
                    r'lote\s+\w+',
                    r'house\s+\w+',
                    r'apartment\s+\w+'
                ]
                
                for pattern in property_patterns:
                    match = re.search(pattern, ai_response, re.IGNORECASE)
                    if match:
                        item_name = match.group().title()
                        break
                
                quote_data['items'].append({
                    'description': item_name,
                    'quantity': 1,
                    'unit_price': price,
                    'total': price
                })
        else:
            # Si no hay precios, crear un item genérico
            quote_data['items'].append({
                'description': 'Consultoría y Asesoría Inmobiliaria',
                'quantity': 1,
                'unit_price': 0,
                'total': 0
            })
        
        # Calcular totales
        quote_data['subtotal'] = sum(item['total'] for item in quote_data['items'])
        quote_data['tax_amount'] = quote_data['subtotal'] * quote_data['tax_rate']
        quote_data['total'] = quote_data['subtotal'] + quote_data['tax_amount']
        
        return quote_data
    
    def generate_pdf_quote(self, ai_response: str, client_name: str, output_dir: str = "instance/quotes") -> str:
        """
        Genera una cotización PDF profesional basada en la respuesta de IA
        
        Args:
            ai_response: Respuesta generada por la IA
            client_name: Nombre del cliente
            output_dir: Directorio donde guardar el PDF
            
        Returns:
            Ruta del archivo PDF generado
        """
        # Asegurar que el directorio existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Extraer información de la cotización
        quote_data = self.extract_quote_info(ai_response, client_name)
        
        # Crear nombre de archivo
        filename = f"cotizacion_{quote_data['quote_number']}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        # Crear documento PDF
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Contenido del PDF
        story = []
        
        # Encabezado
        story.append(Paragraph("COTIZACIÓN OFICIAL", self.title_style))
        story.append(Spacer(1, 12))
        
        # Información de la empresa y cotización
        company_info = [
            ["SalesMind Real Estate", f"Cotización N°: {quote_data['quote_number']}"],
            ["Asesoría Inmobiliaria Profesional", f"Fecha: {quote_data['date']}"],
            ["📧 info@salesmind.com", f"Válida hasta: {quote_data['valid_until']}"],
            ["📱 +1 (555) 123-4567", f"Cliente: {quote_data['client_name']}"]
        ]
        
        company_table = Table(company_info, colWidths=[3*inch, 2.5*inch])
        company_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F0F8FF'))
        ]))
        
        story.append(company_table)
        story.append(Spacer(1, 20))
        
        # Detalles de la cotización
        story.append(Paragraph("DETALLES DE LA COTIZACIÓN", self.subtitle_style))
        
        # Tabla de items
        table_data = [["Descripción", "Cantidad", "Precio Unitario", "Total"]]
        
        for item in quote_data['items']:
            table_data.append([
                item['description'],
                str(item['quantity']),
                f"${item['unit_price']:,.2f}",
                f"${item['total']:,.2f}"
            ])
        
        # Filas de totales
        table_data.append(["", "", "Subtotal:", f"${quote_data['subtotal']:,.2f}"])
        table_data.append(["", "", f"IVA ({quote_data['tax_rate']*100}%):", f"${quote_data['tax_amount']:,.2f}"])
        table_data.append(["", "", "TOTAL:", f"${quote_data['total']:,.2f}"])
        
        # Crear tabla
        items_table = Table(table_data, colWidths=[3*inch, 0.8*inch, 1.2*inch, 1.2*inch])
        items_table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            
            # Contenido
            ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -4), 10),
            ('GRID', (0, 0), (-1, -4), 1, colors.black),
            
            # Totales
            ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -3), (-1, -1), 11),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F18F01')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('GRID', (0, -3), (-1, -1), 1, colors.black),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 20))
        
        # Notas y condiciones
        story.append(Paragraph("INFORMACIÓN ADICIONAL", self.subtitle_style))
        story.append(Paragraph(quote_data['notes'], self.normal_style))
        story.append(Spacer(1, 20))
        
        # Términos y condiciones
        terms = """
        <b>TÉRMINOS Y CONDICIONES:</b><br/>
        • Esta cotización es válida por 30 días.<br/>
        • Los precios están sujetos a disponibilidad.<br/>
        • Se requiere anticipo del 30% para separar la propiedad.<br/>
        • Incluye asesoría legal y acompañamiento en todo el proceso.<br/>
        • No incluye gastos notariales ni de registro.<br/>
        """
        
        story.append(Paragraph(terms, self.normal_style))
        story.append(Spacer(1, 30))
        
        # Firma
        signature_text = """
        <br/><br/>
        ________________________________<br/>
        <b>SalesMind Real Estate</b><br/>
        Asesor Comercial<br/>
        📧 asesor@salesmind.com<br/>
        📱 +1 (555) 123-4567
        """
        
        story.append(Paragraph(signature_text, self.normal_style))
        
        # Construir PDF
        doc.build(story)
        
        print(f"✅ Cotización PDF generada: {filepath}")
        return filepath
    
    def get_quote_download_url(self, pdf_path: str) -> str:
        """
        Genera URL de descarga para la cotización
        """
        # Extraer solo el nombre del archivo
        filename = os.path.basename(pdf_path)
        return f"/download-quote/{filename}"

# --- FUNCIÓN DE UTILIDAD GLOBAL ---
def generate_quote_if_requested(ai_response: str, question: str, client_name: str) -> tuple:
    """
    Verifica si la pregunta es solicitud de cotización y genera PDF si es necesario
    
    Returns:
        (updated_response, pdf_url_or_none)
    """
    quote_keywords = [
        'cotizacion', 'cotización', 'presupuesto', 'quote', 'quotation', 
        'estimate', 'precio', 'cost', 'cuanto cuesta', 'how much'
    ]
    
    is_quote_request = any(keyword in question.lower() for keyword in quote_keywords)
    
    if is_quote_request and any(keyword in ai_response.lower() for keyword in ['$', 'precio', 'price', 'costo', 'cost']):
        try:
            generator = QuoteGenerator()
            pdf_path = generator.generate_pdf_quote(ai_response, client_name)
            download_url = generator.get_quote_download_url(pdf_path)
            
            # Agregar información de descarga a la respuesta
            pdf_info = f"""

📄 **COTIZACIÓN OFICIAL GENERADA**

He preparado una cotización oficial en formato PDF con todos los detalles, precios y términos.

🔗 **[Descargar Cotización PDF]({download_url})**

Esta cotización incluye:
✅ Precios detallados
✅ Términos y condiciones
✅ Validez de 30 días
✅ Información de contacto

¿Te gustaría que ajuste algún detalle de la cotización?"""
            
            return ai_response + pdf_info, download_url
            
        except Exception as e:
            print(f"❌ Error generando cotización PDF: {e}")
            return ai_response, None
    
    return ai_response, None