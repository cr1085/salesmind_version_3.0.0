"""
Gestor de inventarios para SalesMind
Controla stock, movimientos y alertas de productos
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from sqlalchemy import and_, func
from modules.models import db
from modules.commercial_models import Product, InventoryMovement, Order, OrderItem

class InventoryManager:
    """Gestor completo de inventarios y stock"""
    
    def __init__(self):
        pass
    
    def add_product(self, client_id: int, product_data: Dict) -> Dict:
        """
        Agrega un nuevo producto al inventario
        
        Args:
            client_id: ID del cliente empresarial
            product_data: Datos del producto (nombre, precio, stock inicial, etc.)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            product = Product(
                client_id=client_id,
                name=product_data['name'],
                description=product_data.get('description', ''),
                category=product_data.get('category', ''),
                sku=product_data.get('sku', ''),
                base_price=Decimal(str(product_data['base_price'])),
                discount_percentage=float(product_data.get('discount_percentage', 0)),
                tax_rate=float(product_data.get('tax_rate', 19)),  # IVA 19% por defecto
                stock_quantity=int(product_data.get('stock_quantity', 0)),
                min_stock_alert=int(product_data.get('min_stock_alert', 10)),
                is_active=product_data.get('is_active', True),
                is_featured=product_data.get('is_featured', False)
            )
            
            db.session.add(product)
            db.session.flush()  # Para obtener el ID
            
            # Registrar movimiento inicial de inventario si hay stock
            if product.stock_quantity > 0:
                self._record_inventory_movement(
                    product_id=product.id,
                    movement_type='in',
                    quantity=product.stock_quantity,
                    reason='Stock inicial',
                    reference_type='initial_stock'
                )
            
            db.session.commit()
            
            return {
                'success': True,
                'product_id': product.id,
                'public_id': product.public_id,
                'message': f'Producto {product.name} agregado exitosamente'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error agregando producto: {str(e)}'}
    
    def update_product_stock(self, product_id: int, new_stock: int, 
                            reason: str = 'Ajuste manual') -> Dict:
        """
        Actualiza el stock de un producto y registra el movimiento
        
        Args:
            product_id: ID del producto
            new_stock: Nueva cantidad de stock
            reason: Motivo del ajuste
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            product = Product.query.get(product_id)
            if not product:
                return {'success': False, 'error': 'Producto no encontrado'}
            
            old_stock = product.stock_quantity
            difference = new_stock - old_stock
            
            # Actualizar stock
            product.stock_quantity = new_stock
            
            # Registrar movimiento
            movement_type = 'in' if difference > 0 else 'out'
            self._record_inventory_movement(
                product_id=product_id,
                movement_type=movement_type,
                quantity=abs(difference),
                reason=reason,
                reference_type='adjustment'
            )
            
            db.session.commit()
            
            # Verificar alerta de stock bajo
            alert_message = ""
            if new_stock <= product.min_stock_alert:
                alert_message = f" ⚠️ ALERTA: Stock bajo (mínimo: {product.min_stock_alert})"
            
            return {
                'success': True,
                'product_id': product_id,
                'old_stock': old_stock,
                'new_stock': new_stock,
                'difference': difference,
                'message': f'Stock actualizado de {old_stock} a {new_stock}{alert_message}'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error actualizando stock: {str(e)}'}
    
    def reserve_inventory_for_order(self, order_id: int) -> Dict:
        """
        Reserva inventario para una orden (no lo descuenta aún)
        
        Args:
            order_id: ID de la orden
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return {'success': False, 'error': 'Orden no encontrada'}
            
            # Verificar disponibilidad y reservar
            reserved_items = []
            for item in order.order_items:
                product = item.product
                
                if product.stock_quantity < item.quantity:
                    # Liberar reservas ya hechas si una falla
                    self._release_reservations(reserved_items)
                    return {
                        'success': False,
                        'error': f'Stock insuficiente para {product.name}. Disponible: {product.stock_quantity}, Solicitado: {item.quantity}'
                    }
                
                # "Reservar" actualizando el stock temporalmente
                # En una implementación más robusta, se usaría una tabla separada de reservas
                product.stock_quantity -= item.quantity
                reserved_items.append((product.id, item.quantity))
                
                # Registrar movimiento de reserva
                self._record_inventory_movement(
                    product_id=product.id,
                    movement_type='out',
                    quantity=item.quantity,
                    reason=f'Reserva para orden {order.order_number}',
                    reference_type='order_reservation',
                    reference_id=order_id
                )
            
            db.session.commit()
            
            return {
                'success': True,
                'order_id': order_id,
                'reserved_items': len(reserved_items),
                'message': 'Inventario reservado exitosamente'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error reservando inventario: {str(e)}'}
    
    def confirm_inventory_reservation(self, order_id: int) -> Dict:
        """
        Confirma la reserva de inventario (descuento definitivo)
        """
        # En esta implementación simple, la reserva ya descontó el stock
        # En una implementación más robusta, aquí se haría el descuento real
        try:
            order = Order.query.get(order_id)
            if not order:
                return {'success': False, 'error': 'Orden no encontrada'}
            
            # Actualizar razón en movimientos existentes
            movements = InventoryMovement.query.filter_by(
                reference_type='order_reservation',
                reference_id=order_id
            ).all()
            
            for movement in movements:
                movement.reason = f'Confirmación orden {order.order_number}'
                movement.reference_type = 'order_confirmed'
            
            db.session.commit()
            
            return {
                'success': True,
                'order_id': order_id,
                'message': 'Reserva de inventario confirmada'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error confirmando reserva: {str(e)}'}
    
    def release_inventory_reservation(self, order_id: int) -> Dict:
        """
        Libera la reserva de inventario (devuelve stock)
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return {'success': False, 'error': 'Orden no encontrada'}
            
            # Devolver stock de cada item
            for item in order.order_items:
                product = item.product
                product.stock_quantity += item.quantity
                
                # Registrar movimiento de devolución
                self._record_inventory_movement(
                    product_id=product.id,
                    movement_type='in',
                    quantity=item.quantity,
                    reason=f'Liberación reserva orden {order.order_number}',
                    reference_type='order_cancelled',
                    reference_id=order_id
                )
            
            db.session.commit()
            
            return {
                'success': True,
                'order_id': order_id,
                'message': 'Inventario liberado exitosamente'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error liberando inventario: {str(e)}'}
    
    def get_low_stock_alerts(self, client_id: int) -> List[Dict]:
        """
        Obtiene productos con stock bajo para un cliente
        """
        products = Product.query.filter(
            and_(
                Product.client_id == client_id,
                Product.is_active == True,
                Product.stock_quantity <= Product.min_stock_alert
            )
        ).all()
        
        return [
            {
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'current_stock': product.stock_quantity,
                'min_stock_alert': product.min_stock_alert,
                'status': 'critical' if product.stock_quantity == 0 else 'low'
            }
            for product in products
        ]
    
    def get_inventory_report(self, client_id: int) -> Dict:
        """
        Genera reporte completo de inventario para un cliente
        """
        # Productos activos
        products = Product.query.filter_by(client_id=client_id, is_active=True).all()
        
        total_products = len(products)
        total_stock_value = sum(
            float(p.stock_quantity * p.base_price) for p in products
        )
        
        # Alertas de stock
        low_stock_count = len([p for p in products if p.stock_quantity <= p.min_stock_alert])
        out_of_stock_count = len([p for p in products if p.stock_quantity == 0])
        
        # Productos más vendidos (basado en movimientos)
        top_products_query = db.session.query(
            Product.name,
            func.sum(InventoryMovement.quantity).label('total_sold')
        ).join(InventoryMovement).filter(
            and_(
                Product.client_id == client_id,
                InventoryMovement.movement_type == 'out',
                InventoryMovement.reference_type.in_(['order_confirmed', 'order_reservation'])
            )
        ).group_by(Product.id).order_by(func.sum(InventoryMovement.quantity).desc()).limit(5).all()
        
        return {
            'summary': {
                'total_products': total_products,
                'total_stock_value': total_stock_value,
                'low_stock_alerts': low_stock_count,
                'out_of_stock': out_of_stock_count
            },
            'top_selling_products': [
                {'name': name, 'total_sold': int(total_sold)}
                for name, total_sold in top_products_query
            ],
            'products': [
                {
                    'id': p.id,
                    'name': p.name,
                    'sku': p.sku,
                    'category': p.category,
                    'stock_quantity': p.stock_quantity,
                    'base_price': float(p.base_price),
                    'stock_value': float(p.stock_quantity * p.base_price),
                    'status': (
                        'out_of_stock' if p.stock_quantity == 0
                        else 'low_stock' if p.stock_quantity <= p.min_stock_alert
                        else 'in_stock'
                    )
                }
                for p in products
            ]
        }
    
    def get_inventory_movements(self, product_id: int = None, 
                               movement_type: str = None, limit: int = 50) -> List[Dict]:
        """
        Obtiene historial de movimientos de inventario
        """
        query = InventoryMovement.query
        
        if product_id:
            query = query.filter_by(product_id=product_id)
        
        if movement_type:
            query = query.filter_by(movement_type=movement_type)
        
        movements = query.order_by(InventoryMovement.created_at.desc()).limit(limit).all()
        
        return [
            {
                'id': m.id,
                'product_name': m.product.name if m.product else 'N/A',
                'movement_type': m.movement_type,
                'quantity': m.quantity,
                'reference_type': m.reference_type,
                'reference_id': m.reference_id,
                'reason': m.reason,
                'created_at': m.created_at.isoformat(),
                'created_by': m.created_by
            }
            for m in movements
        ]
    
    def _record_inventory_movement(self, product_id: int, movement_type: str,
                                  quantity: int, reason: str, reference_type: str = None,
                                  reference_id: int = None, created_by: str = 'system'):
        """
        Registra un movimiento de inventario
        """
        movement = InventoryMovement(
            product_id=product_id,
            movement_type=movement_type,
            quantity=quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            reason=reason,
            created_by=created_by
        )
        
        db.session.add(movement)
    
    def _release_reservations(self, reserved_items: List[tuple]):
        """
        Libera reservas parciales en caso de error
        """
        for product_id, quantity in reserved_items:
            product = Product.query.get(product_id)
            if product:
                product.stock_quantity += quantity