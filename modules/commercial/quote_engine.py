"""
Motor de cotizaciones automáticas para SalesMind
Genera cotizaciones inteligentes basadas en consultas de IA
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from modules.models import db
from modules.commercial_models import Product, Quote, QuoteItem
import re
import json
import google.generativeai as genai
from config import Config

class QuoteEngine:
    """Motor para generar cotizaciones automáticas basadas en IA"""
    
    def __init__(self):
        # Configurar modelo de IA para análisis de consultas
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    def generate_quote_from_query(self, client_id: int, customer_query: str, 
                                customer_info: Dict) -> Dict:
        """
        Genera una cotización automática basada en una consulta del cliente
        
        Args:
            client_id: ID del cliente empresarial
            customer_query: Consulta del cliente (ej: "Quiero 3 apartamentos de 2 habitaciones")
            customer_info: Información del cliente final (nombre, email, teléfono)
            
        Returns:
            Dict con la cotización generada y productos incluidos
        """
        try:
            # 1. Analizar la consulta para extraer productos y cantidades
            products_requested = self._analyze_query_for_products(client_id, customer_query)
            
            if not products_requested:
                return {
                    'success': False,
                    'error': 'No se pudieron identificar productos específicos en la consulta'
                }
            
            # 2. Crear la cotización
            quote = self._create_quote(client_id, customer_info, products_requested)
            
            # 3. Calcular totales y aplicar reglas de negocio
            self._calculate_quote_totals(quote)
            
            # 4. Guardar en base de datos
            db.session.add(quote)
            db.session.commit()
            
            return {
                'success': True,
                'quote_id': quote.id,
                'quote_number': quote.quote_number,
                'total_amount': float(quote.total_amount),
                'products': [
                    {
                        'name': item.product.name,
                        'quantity': item.quantity,
                        'unit_price': float(item.unit_price),
                        'line_total': float(item.line_total)
                    }
                    for item in quote.quote_items
                ],
                'valid_until': quote.valid_until.isoformat() if quote.valid_until else None
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Error al generar cotización: {str(e)}'
            }
    
    def _analyze_query_for_products(self, client_id: int, query: str) -> List[Dict]:
        """
        Utiliza IA para analizar la consulta y extraer productos con cantidades
        """
        # Obtener productos disponibles del cliente
        products = Product.query.filter_by(client_id=client_id, is_active=True).all()
        
        if not products:
            return []
        
        # Crear prompt especializado para extracción de productos
        products_info = "\n".join([
            f"- {p.name}: ${p.base_price} (SKU: {p.sku or 'N/A'})"
            for p in products
        ])
        
        analysis_prompt = f"""
        Analiza la siguiente consulta de cliente y extrae los productos solicitados con sus cantidades.
        
        PRODUCTOS DISPONIBLES:
        {products_info}
        
        CONSULTA DEL CLIENTE: "{query}"
        
        Responde ÚNICAMENTE en formato JSON con esta estructura:
        {{
            "products": [
                {{
                    "product_name": "nombre_exacto_del_producto",
                    "quantity": numero_entero,
                    "confidence": 0.95
                }}
            ]
        }}
        
        Si no encuentras productos específicos, devuelve: {{"products": []}}
        """
        
        try:
            # Usar modelo de IA para análisis
            response = self.model.generate_content(analysis_prompt)
            
            # Extraer JSON de la respuesta
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                
                # Mapear nombres de productos a objetos Product
                result = []
                for item in analysis.get('products', []):
                    product = next(
                        (p for p in products if p.name.lower() in item['product_name'].lower() 
                         or item['product_name'].lower() in p.name.lower()),
                        None
                    )
                    if product and item.get('confidence', 0) > 0.7:
                        result.append({
                            'product': product,
                            'quantity': max(1, int(item.get('quantity', 1)))
                        })
                
                return result
                
        except Exception as e:
            print(f"Error analizando consulta: {e}")
        
        return []
    
    def _create_quote(self, client_id: int, customer_info: Dict, 
                     products_requested: List[Dict]) -> Quote:
        """Crea una nueva cotización con los productos solicitados"""
        
        quote = Quote(
            client_id=client_id,
            quote_number=self._generate_quote_number(),
            customer_name=customer_info.get('name', 'Cliente'),
            customer_email=customer_info.get('email', ''),
            customer_phone=customer_info.get('phone', ''),
            valid_until=datetime.now() + timedelta(days=30),  # 30 días de validez
            status='draft'
        )
        
        # Agregar items de la cotización
        for item_data in products_requested:
            product = item_data['product']
            quantity = item_data['quantity']
            
            # Calcular precio con descuentos
            unit_price = product.base_price
            discount_percentage = product.discount_percentage
            
            # Aplicar descuentos por volumen (regla de negocio)
            if quantity >= 10:
                discount_percentage = max(discount_percentage, 10.0)  # Mínimo 10% por volumen
            elif quantity >= 5:
                discount_percentage = max(discount_percentage, 5.0)   # Mínimo 5% por volumen
            
            line_total = Decimal(str(quantity)) * unit_price * (1 - Decimal(str(discount_percentage)) / 100)
            
            quote_item = QuoteItem(
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                discount_percentage=discount_percentage,
                line_total=line_total
            )
            
            quote.quote_items.append(quote_item)
        
        return quote
    
    def _calculate_quote_totals(self, quote: Quote):
        """Calcula los totales de la cotización"""
        subtotal = sum(item.line_total for item in quote.quote_items)
        
        # Aplicar descuento general si aplica
        discount_amount = Decimal('0')
        if subtotal > 10000:  # Descuento por monto alto
            discount_amount = subtotal * Decimal('0.05')  # 5% adicional
        
        # Calcular impuestos (IVA 19% por defecto - ajustar según país)
        tax_rate = Decimal('0.19')
        taxable_amount = subtotal - discount_amount
        tax_amount = taxable_amount * tax_rate
        
        # Asignar totales
        quote.subtotal = subtotal
        quote.discount_amount = discount_amount
        quote.tax_amount = tax_amount
        quote.total_amount = taxable_amount + tax_amount
    
    def _generate_quote_number(self) -> str:
        """Genera un número único de cotización"""
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"COT-{timestamp}-{unique_id}"
    
    def get_quote_details(self, quote_id: int) -> Optional[Dict]:
        """Obtiene los detalles completos de una cotización"""
        quote = Quote.query.get(quote_id)
        if not quote:
            return None
        
        return {
            'id': quote.id,
            'quote_number': quote.quote_number,
            'customer_name': quote.customer_name,
            'customer_email': quote.customer_email,
            'customer_phone': quote.customer_phone,
            'status': quote.status,
            'subtotal': float(quote.subtotal),
            'discount_amount': float(quote.discount_amount),
            'tax_amount': float(quote.tax_amount),
            'total_amount': float(quote.total_amount),
            'valid_until': quote.valid_until.isoformat() if quote.valid_until else None,
            'created_at': quote.created_at.isoformat(),
            'items': [
                {
                    'product_name': item.product.name,
                    'product_description': item.product.description,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'discount_percentage': item.discount_percentage,
                    'line_total': float(item.line_total)
                }
                for item in quote.quote_items
            ]
        }
    
    def update_quote_status(self, quote_id: int, new_status: str) -> bool:
        """Actualiza el estado de una cotización"""
        try:
            quote = Quote.query.get(quote_id)
            if quote:
                quote.status = new_status
                db.session.commit()
                return True
        except Exception as e:
            db.session.rollback()
            print(f"Error actualizando estado de cotización: {e}")
        
        return False
    
    def list_quotes_by_client(self, client_id: int, status: Optional[str] = None) -> List[Dict]:
        """Lista todas las cotizaciones de un cliente"""
        query = Quote.query.filter_by(client_id=client_id)
        
        if status:
            query = query.filter_by(status=status)
        
        quotes = query.order_by(Quote.created_at.desc()).all()
        
        return [
            {
                'id': quote.id,
                'quote_number': quote.quote_number,
                'customer_name': quote.customer_name,
                'status': quote.status,
                'total_amount': float(quote.total_amount),
                'created_at': quote.created_at.isoformat(),
                'valid_until': quote.valid_until.isoformat() if quote.valid_until else None
            }
            for quote in quotes
        ]
    
    def generate_quote_pdf(self, quote_id: int) -> Optional[str]:
        """Genera un PDF de la cotización (implementar con reportlab o similar)"""
        # TODO: Implementar generación de PDF
        # Esta sería la integración con reportlab o weasyprint
        pass