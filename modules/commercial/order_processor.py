"""
Procesador de órdenes/pedidos para SalesMind
Gestiona el ciclo completo de órdenes desde creación hasta entrega
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from modules.models import db
from modules.commercial_models import Order, OrderItem, Quote, Product
from .inventory_manager import InventoryManager

class OrderProcessor:
    """Procesador completo de órdenes y pedidos"""
    
    def __init__(self):
        self.inventory_manager = InventoryManager()
    
    def create_order_from_quote(self, quote_id: int, additional_info: Dict = None) -> Dict:
        """
        Crea una orden basada en una cotización aceptada
        
        Args:
            quote_id: ID de la cotización base
            additional_info: Información adicional (dirección de envío, etc.)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Obtener la cotización
            quote = Quote.query.get(quote_id)
            if not quote:
                return {'success': False, 'error': 'Cotización no encontrada'}
            
            if quote.status != 'accepted':
                return {'success': False, 'error': 'La cotización debe estar aceptada'}
            
            # Verificar disponibilidad de inventario
            availability_check = self._check_inventory_availability(quote)
            if not availability_check['available']:
                return {
                    'success': False,
                    'error': f'Stock insuficiente: {availability_check["details"]}'
                }
            
            # Crear la orden
            order = Order(
                client_id=quote.client_id,
                quote_id=quote_id,
                order_number=self._generate_order_number(),
                customer_name=quote.customer_name,
                customer_email=quote.customer_email,
                customer_phone=quote.customer_phone,
                shipping_address=additional_info.get('shipping_address', '') if additional_info else '',
                subtotal=quote.subtotal,
                discount_amount=quote.discount_amount,
                tax_amount=quote.tax_amount,
                shipping_cost=self._calculate_shipping_cost(additional_info),
                total_amount=quote.total_amount + self._calculate_shipping_cost(additional_info),
                status='pending',
                estimated_delivery=datetime.now() + timedelta(days=7)  # 7 días por defecto
            )
            
            # Copiar items de la cotización a la orden
            for quote_item in quote.quote_items:
                order_item = OrderItem(
                    product_id=quote_item.product_id,
                    quantity=quote_item.quantity,
                    unit_price=quote_item.unit_price,
                    discount_percentage=quote_item.discount_percentage,
                    line_total=quote_item.line_total
                )
                order.order_items.append(order_item)
            
            # Guardar orden
            db.session.add(order)
            db.session.commit()
            
            # Reservar inventario
            self.inventory_manager.reserve_inventory_for_order(order.id)
            
            return {
                'success': True,
                'order_id': order.id,
                'order_number': order.order_number,
                'total_amount': float(order.total_amount),
                'estimated_delivery': order.estimated_delivery.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error creando orden: {str(e)}'}
    
    def create_direct_order(self, client_id: int, customer_info: Dict, 
                           products_data: List[Dict], additional_info: Dict = None) -> Dict:
        """
        Crea una orden directa sin cotización previa
        
        Args:
            client_id: ID del cliente empresarial
            customer_info: Información del cliente final
            products_data: Lista de productos con cantidades
            additional_info: Información adicional
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            # Validar productos y disponibilidad
            order_items_data = []
            subtotal = Decimal('0')
            
            for product_data in products_data:
                product = Product.query.get(product_data['product_id'])
                if not product or not product.is_active:
                    return {'success': False, 'error': f'Producto no válido: {product_data["product_id"]}'}
                
                if product.client_id != client_id:
                    return {'success': False, 'error': 'Producto no pertenece al cliente'}
                
                quantity = int(product_data['quantity'])
                if quantity <= 0:
                    return {'success': False, 'error': 'La cantidad debe ser mayor a 0'}
                
                # Verificar stock
                if product.stock_quantity < quantity:
                    return {
                        'success': False,
                        'error': f'Stock insuficiente para {product.name}. Disponible: {product.stock_quantity}'
                    }
                
                # Calcular precio línea
                unit_price = product.base_price
                discount_percentage = product.discount_percentage
                
                # Aplicar descuentos por volumen
                if quantity >= 10:
                    discount_percentage = max(discount_percentage, 10.0)
                elif quantity >= 5:
                    discount_percentage = max(discount_percentage, 5.0)
                
                line_total = Decimal(str(quantity)) * unit_price * (1 - Decimal(str(discount_percentage)) / 100)
                
                order_items_data.append({
                    'product': product,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'discount_percentage': discount_percentage,
                    'line_total': line_total
                })
                
                subtotal += line_total
            
            # Calcular totales
            discount_amount = Decimal('0')
            if subtotal > 10000:  # Descuento por monto alto
                discount_amount = subtotal * Decimal('0.05')
            
            tax_amount = (subtotal - discount_amount) * Decimal('0.19')  # IVA 19%
            shipping_cost = self._calculate_shipping_cost(additional_info)
            total_amount = subtotal - discount_amount + tax_amount + shipping_cost
            
            # Crear orden
            order = Order(
                client_id=client_id,
                order_number=self._generate_order_number(),
                customer_name=customer_info.get('name', 'Cliente'),
                customer_email=customer_info.get('email', ''),
                customer_phone=customer_info.get('phone', ''),
                shipping_address=additional_info.get('shipping_address', '') if additional_info else '',
                subtotal=subtotal,
                discount_amount=discount_amount,
                tax_amount=tax_amount,
                shipping_cost=shipping_cost,
                total_amount=total_amount,
                status='pending',
                estimated_delivery=datetime.now() + timedelta(days=7)
            )
            
            # Agregar items
            for item_data in order_items_data:
                order_item = OrderItem(
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    discount_percentage=item_data['discount_percentage'],
                    line_total=item_data['line_total']
                )
                order.order_items.append(order_item)
            
            # Guardar
            db.session.add(order)
            db.session.commit()
            
            # Reservar inventario
            self.inventory_manager.reserve_inventory_for_order(order.id)
            
            return {
                'success': True,
                'order_id': order.id,
                'order_number': order.order_number,
                'total_amount': float(order.total_amount),
                'estimated_delivery': order.estimated_delivery.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error creando orden: {str(e)}'}
    
    def update_order_status(self, order_id: int, new_status: str, notes: str = None) -> Dict:
        """
        Actualiza el estado de una orden
        
        Estados válidos: pending, confirmed, processing, shipped, delivered, cancelled
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return {'success': False, 'error': 'Orden no encontrada'}
            
            old_status = order.status
            order.status = new_status
            
            if notes:
                order.notes = (order.notes or '') + f"\n{datetime.now()}: {notes}"
            
            # Acciones específicas por estado
            if new_status == 'confirmed' and old_status == 'pending':
                # Confirmar reservas de inventario
                self.inventory_manager.confirm_inventory_reservation(order_id)
            
            elif new_status == 'delivered' and old_status in ['shipped', 'processing']:
                order.delivered_at = datetime.now()
                # El inventario ya se descontó al confirmar
            
            elif new_status == 'cancelled':
                # Liberar inventario reservado
                self.inventory_manager.release_inventory_reservation(order_id)
            
            db.session.commit()
            
            return {
                'success': True,
                'order_id': order.id,
                'new_status': new_status,
                'message': f'Estado actualizado de {old_status} a {new_status}'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error actualizando orden: {str(e)}'}
    
    def get_order_details(self, order_id: int) -> Optional[Dict]:
        """Obtiene detalles completos de una orden"""
        order = Order.query.get(order_id)
        if not order:
            return None
        
        return {
            'id': order.id,
            'order_number': order.order_number,
            'client_id': order.client_id,
            'quote_id': order.quote_id,
            'customer_name': order.customer_name,
            'customer_email': order.customer_email,
            'customer_phone': order.customer_phone,
            'shipping_address': order.shipping_address,
            'status': order.status,
            'subtotal': float(order.subtotal),
            'discount_amount': float(order.discount_amount),
            'tax_amount': float(order.tax_amount),
            'shipping_cost': float(order.shipping_cost),
            'total_amount': float(order.total_amount),
            'order_date': order.order_date.isoformat(),
            'estimated_delivery': order.estimated_delivery.isoformat() if order.estimated_delivery else None,
            'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
            'notes': order.notes,
            'items': [
                {
                    'product_name': item.product.name,
                    'product_sku': item.product.sku,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'discount_percentage': item.discount_percentage,
                    'line_total': float(item.line_total)
                }
                for item in order.order_items
            ]
        }
    
    def list_orders_by_client(self, client_id: int, status: Optional[str] = None,
                             limit: int = 50) -> List[Dict]:
        """Lista órdenes de un cliente"""
        query = Order.query.filter_by(client_id=client_id)
        
        if status:
            query = query.filter_by(status=status)
        
        orders = query.order_by(Order.created_at.desc()).limit(limit).all()
        
        return [
            {
                'id': order.id,
                'order_number': order.order_number,
                'customer_name': order.customer_name,
                'status': order.status,
                'total_amount': float(order.total_amount),
                'order_date': order.order_date.isoformat(),
                'estimated_delivery': order.estimated_delivery.isoformat() if order.estimated_delivery else None
            }
            for order in orders
        ]
    
    def get_order_statistics(self, client_id: int, days: int = 30) -> Dict:
        """Obtiene estadísticas de órdenes de un cliente"""
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Consultas estadísticas
        orders_query = Order.query.filter(
            Order.client_id == client_id,
            Order.created_at >= start_date
        )
        
        total_orders = orders_query.count()
        total_revenue = orders_query.with_entities(func.sum(Order.total_amount)).scalar() or 0
        
        orders_by_status = {}
        for status in ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']:
            count = orders_query.filter_by(status=status).count()
            orders_by_status[status] = count
        
        avg_order_value = float(total_revenue / total_orders) if total_orders > 0 else 0
        
        return {
            'period_days': days,
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'average_order_value': avg_order_value,
            'orders_by_status': orders_by_status,
            'conversion_rate': (orders_by_status.get('delivered', 0) / total_orders * 100) if total_orders > 0 else 0
        }
    
    def _check_inventory_availability(self, quote: Quote) -> Dict:
        """Verifica disponibilidad de inventario para una cotización"""
        unavailable_products = []
        
        for item in quote.quote_items:
            if item.product.stock_quantity < item.quantity:
                unavailable_products.append({
                    'product': item.product.name,
                    'requested': item.quantity,
                    'available': item.product.stock_quantity
                })
        
        return {
            'available': len(unavailable_products) == 0,
            'details': unavailable_products
        }
    
    def _calculate_shipping_cost(self, additional_info: Dict = None) -> Decimal:
        """Calcula costo de envío basado en información adicional"""
        if not additional_info:
            return Decimal('0')
        
        # Lógica simple de cálculo de envío
        # Puede ser más compleja basada en ubicación, peso, etc.
        base_shipping = Decimal('50000')  # $50,000 base
        
        # Envío gratuito para órdenes grandes
        if additional_info.get('free_shipping', False):
            return Decimal('0')
        
        return base_shipping
    
    def _generate_order_number(self) -> str:
        """Genera número único de orden"""
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"ORD-{timestamp}-{unique_id}"