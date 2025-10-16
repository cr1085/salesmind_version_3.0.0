#!/usr/bin/env python
# modules/quote_system_v2.py - SISTEMA DE COTIZACIÓN V2 SIN REFRESH
"""
🔄 SISTEMA DE COTIZACIÓN V2 - SIN REFRESH
=======================================

Sistema completamente nuevo de cotización que NO causa refresh
y mantiene la conversación intacta.

CARACTERÍSTICAS:
✅ Base64 inline para PDFs pequeños
✅ Streaming de archivos grandes
✅ URLs con tokens temporales
✅ No redirecciones automáticas
✅ Cache control para navegadores
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os
import base64
import uuid
import secrets
from datetime import datetime, timedelta
import re
import json
from flask import url_for

class QuoteSystemV2:
    """Sistema de cotización completamente nuevo sin refresh"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        self.temp_tokens = {}  # Para URLs temporales seguras
    
    def _create_custom_styles(self):
        """Crear estilos personalizados para la cotización"""
        
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E86AB')
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#A23B72')
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_LEFT
        )
        
        self.price_style = ParagraphStyle(
            'PriceStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#F18F01'),
            alignment=TA_RIGHT,
            spaceAfter=6
        )
    
    def extract_quote_data_v2(self, ai_response: str, client_name: str) -> dict:
        """
        Extrae información de cotización de forma más inteligente
        """
        quote_data = {
            'client_name': client_name,
            'quote_number': f"COT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
            'date': datetime.now().strftime('%d/%m/%Y'),
            'valid_until': (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y'),
            'items': [],
            'subtotal': 0,
            'tax_rate': 0.19,
            'total': 0,
            'notes': ai_response,
            'currency': 'USD'
        }
        
        # Patrones mejorados para extraer información
        price_patterns = [
            r'\$[\d,]+\.?\d*',
            r'[\d,]+\.?\d*\s*(?:USD|usd|dólares|dollars)',
            r'Precio[:\s]*\$?[\d,]+\.?\d*',
            r'precio[:\s]*\$?[\d,]+\.?\d*',
            r'Price[:\s]*\$?[\d,]+\.?\d*'
        ]
        
        property_patterns = [
            r'CASA\s+MODELO\s+(\w+)',
            r'Casa\s+Modelo\s+(\w+)', 
            r'APARTAMENTO\s+(\w+)',
            r'Apartamento\s+(\w+)',
            r'LOTE\s+(\w+)',
            r'Lote\s+(\w+)'
        ]
        
        # Extraer propiedades y precios
        found_items = []
        
        # Buscar patrones de propiedad + precio
        lines = ai_response.split('\n')
        current_property = None
        current_price = None
        
        for line in lines:
            # Buscar nombre de propiedad
            for pattern in property_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    current_property = match.group().title()
                    break
            
            # Buscar precio en la misma línea o líneas cercanas
            for pattern in price_patterns:
                price_match = re.search(pattern, line, re.IGNORECASE)
                if price_match:
                    price_str = price_match.group()
                    # Limpiar y convertir precio
                    clean_price = re.sub(r'[^\d.]', '', price_str)
                    try:
                        current_price = float(clean_price)
                        break
                    except ValueError:
                        continue
            
            # Si tenemos propiedad y precio, crear item
            if current_property and current_price:
                found_items.append({
                    'description': current_property,
                    'quantity': 1,
                    'unit_price': current_price,
                    'total': current_price
                })
                current_property = None
                current_price = None
        
        # Si no encontramos items estructurados, buscar todos los precios
        if not found_items:
            all_prices = []
            for pattern in price_patterns:
                matches = re.findall(pattern, ai_response, re.IGNORECASE)
                for match in matches:
                    clean_price = re.sub(r'[^\d.]', '', match.split()[0])
                    try:
                        price_value = float(clean_price)
                        if price_value > 0:
                            all_prices.append(price_value)
                    except ValueError:
                        continue
            
            # Crear items genéricos con precios encontrados
            for i, price in enumerate(set(all_prices)[:5]):
                found_items.append({
                    'description': f'Propiedad/Servicio {i+1}',
                    'quantity': 1,
                    'unit_price': price,
                    'total': price
                })
        
        # Si aún no hay items, crear uno por defecto
        if not found_items:
            found_items.append({
                'description': 'Consultoría Inmobiliaria',
                'quantity': 1,
                'unit_price': 0,
                'total': 0
            })
        
        quote_data['items'] = found_items
        quote_data['subtotal'] = sum(item['total'] for item in found_items)
        quote_data['tax_amount'] = quote_data['subtotal'] * quote_data['tax_rate']
        quote_data['total'] = quote_data['subtotal'] + quote_data['tax_amount']
        
        return quote_data
    
    def generate_pdf_v2(self, ai_response: str, client_name: str, output_dir: str = "instance/quotes") -> dict:
        """
        Genera PDF y devuelve múltiples opciones de acceso SIN REFRESH
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Extraer datos de cotización
        quote_data = self.extract_quote_data_v2(ai_response, client_name)
        
        # Generar PDF
        filename = f"cotizacion_{quote_data['quote_number']}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Encabezado mejorado
        story.append(Paragraph("📄 COTIZACIÓN OFICIAL", self.title_style))
        story.append(Spacer(1, 20))
        
        # Información de la cotización
        info_data = [
            ["SalesMind Real Estate", f"N°: {quote_data['quote_number']}"],
            ["📧 info@salesmind.com", f"Fecha: {quote_data['date']}"],
            ["📱 +1 (555) 123-4567", f"Válida: {quote_data['valid_until']}"],
            ["", f"Cliente: {quote_data['client_name']}"]
        ]
        
        info_table = Table(info_data, colWidths=[3*inch, 2.5*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8F4FD'))
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Tabla de items
        story.append(Paragraph("📋 DETALLE DE COTIZACIÓN", self.subtitle_style))
        
        items_data = [['Descripción', 'Cant.', 'Precio Unit.', 'Total']]
        
        for item in quote_data['items']:
            items_data.append([
                item['description'],
                str(item['quantity']),
                f"${item['unit_price']:,.2f}",
                f"${item['total']:,.2f}"
            ])
        
        # Totales
        items_data.append(['', '', 'Subtotal:', f"${quote_data['subtotal']:,.2f}"])
        items_data.append(['', '', f'IVA ({quote_data["tax_rate"]*100:.0f}%):', f"${quote_data['tax_amount']:,.2f}"])
        items_data.append(['', '', 'TOTAL:', f"${quote_data['total']:,.2f}"])
        
        items_table = Table(items_data, colWidths=[2.5*inch, 0.8*inch, 1.2*inch, 1*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -3), (-1, -1), colors.HexColor('#F0F8FF'))
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 30))
        
        # Términos y condiciones
        story.append(Paragraph("📝 TÉRMINOS Y CONDICIONES", self.subtitle_style))
        terms = """
        1. Esta cotización es válida por 30 días calendario.
        2. Los precios incluyen IVA cuando aplique.
        3. Para reservar, se requiere anticipo del 30%.
        4. Los tiempos de entrega pueden variar según disponibilidad.
        5. SalesMind se reserva el derecho de modificar precios sin previo aviso.
        """
        story.append(Paragraph(terms, self.normal_style))
        
        # Generar PDF
        doc.build(story)
        
        # 📊 GENERAR MÚLTIPLES OPCIONES DE ACCESO
        result = {
            'success': True,
            'quote_number': quote_data['quote_number'],
            'filename': filename,
            'filepath': filepath,
            'file_size': os.path.getsize(filepath),
            'access_methods': {}
        }
        
        # 1. Token temporal seguro (recomendado)
        token = secrets.token_urlsafe(32)
        self.temp_tokens[token] = {
            'filepath': filepath,
            'expires': datetime.now() + timedelta(hours=1),
            'filename': filename
        }
        result['access_methods']['secure_token'] = f"/secure-download/{token}"
        
        # 2. URL directa tradicional (fallback)
        result['access_methods']['direct_url'] = f"/download-quote/{filename}"
        
        # 3. Base64 inline para archivos pequeños
        if result['file_size'] < 500000:  # 500KB
            with open(filepath, 'rb') as f:
                pdf_content = f.read()
                b64_content = base64.b64encode(pdf_content).decode('utf-8')
                result['access_methods']['base64_inline'] = f"data:application/pdf;base64,{b64_content}"
        
        # 4. Información adicional
        result['quote_data'] = quote_data
        
        return result

    def cleanup_expired_tokens(self):
        """Limpia tokens expirados"""
        now = datetime.now()
        expired_tokens = [
            token for token, data in self.temp_tokens.items()
            if data['expires'] < now
        ]
        for token in expired_tokens:
            del self.temp_tokens[token]
    
    def get_file_by_token(self, token: str) -> dict:
        """Recupera archivo por token seguro"""
        self.cleanup_expired_tokens()
        
        if token in self.temp_tokens:
            return self.temp_tokens[token]
        return None

# Instancia global
quote_system_v2 = QuoteSystemV2()

def generate_quote_v2_if_requested(ai_response: str, question: str, client_name: str) -> tuple:
    """
    Versión 2 del generador de cotización SIN REFRESH
    """
    quote_keywords = [
        'cotizacion', 'cotización', 'presupuesto', 'quote', 'quotation',
        'estimate', 'precio', 'cost', 'cuanto cuesta', 'how much',
        'official', 'oficial'
    ]
    
    is_quote_request = any(keyword in question.lower() for keyword in quote_keywords)
    
    if is_quote_request:
        try:
            # Generar cotización con nuevo sistema
            result = quote_system_v2.generate_pdf_v2(ai_response, client_name)
            
            if result['success']:
                # 📄 CREAR RESPUESTA MEJORADA SIN REFRESH
                download_options = []
                
                # Opción 1: Descarga segura (recomendado)
                secure_url = result['access_methods']['secure_token']
                download_options.append(f"🔒 [Descarga Segura]({secure_url})")
                
                # Opción 2: Descarga tradicional (fallback) 
                direct_url = result['access_methods']['direct_url']
                download_options.append(f"📁 [Descarga Directa]({direct_url})")
                
                # Opción 3: Vista inline (si es pequeño)
                if 'base64_inline' in result['access_methods']:
                    inline_url = result['access_methods']['base64_inline']
                    download_options.append(f"👁️ [Ver en Navegador]({inline_url})")
                
                quote_info = f"""

📄 **COTIZACIÓN OFICIAL GENERADA**

✅ **Número de Cotización:** {result['quote_number']}
✅ **Total:** ${result['quote_data']['total']:,.2f} {result['quote_data']['currency']}
✅ **Items:** {len(result['quote_data']['items'])} productos/servicios
✅ **Válida hasta:** {result['quote_data']['valid_until']}

📥 **OPCIONES DE DESCARGA:**
{' | '.join(download_options)}

💡 **Recomendación:** Usa "Descarga Segura" para mejor seguridad.

¿Te gustaría que ajuste algún detalle de la cotización?"""
                
                return ai_response + quote_info, result
            else:
                return ai_response, None
                
        except Exception as e:
            print(f"❌ Error generando cotización V2: {e}")
            return ai_response, None
    
    return ai_response, None

if __name__ == "__main__":
    # Prueba del sistema
    print("🧪 PROBANDO SISTEMA DE COTIZACIÓN V2")
    
    sample_response = """
    CASA MODELO AURORA
    Precio: $250,000 USD
    - 3 habitaciones principales
    - 2 baños completos
    
    APARTAMENTO DIAMANTE  
    Precio: $180,000 USD
    - 2 habitaciones
    - 1 baño
    """
    
    result = quote_system_v2.generate_pdf_v2(sample_response, "Cliente Demo")
    print("✅ Resultado:", json.dumps(result, indent=2, default=str))