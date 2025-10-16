"""
Rutas para el módulo comercial de SalesMind
Endpoints para cotizaciones, órdenes, inventario, facturas y CRM
"""

from flask import Blueprint, request, jsonify, render_template
from modules.models import db
from modules.commercial_models import Product, Quote, Order, Invoice, Lead
from .quote_engine import QuoteEngine
from .order_processor import OrderProcessor
from .inventory_manager import InventoryManager
from .invoice_generator import InvoiceGenerator
from .crm_system import CRMSystem

# Crear blueprint
commercial_bp = Blueprint('commercial', __name__, url_prefix='/commercial')

# Inicializar sistemas
quote_engine = QuoteEngine()
order_processor = OrderProcessor()
inventory_manager = InventoryManager()
invoice_generator = InvoiceGenerator()
crm_system = CRMSystem()

# ==================== RUTAS DE COTIZACIONES ====================

@commercial_bp.route('/quote/generate', methods=['POST'])
def generate_quote():
    """Genera cotización automática desde consulta de IA"""
    try:
        data = request.json
        result = quote_engine.generate_quote_from_query(
            client_id=data['client_id'],
            customer_query=data['customer_query'],
            customer_info=data['customer_info']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@commercial_bp.route('/quote/<int:quote_id>', methods=['GET'])
def get_quote_details(quote_id):
    """Obtiene detalles de una cotización"""
    result = quote_engine.get_quote_details(quote_id)
    if result:
        return jsonify({'success': True, 'quote': result})
    return jsonify({'success': False, 'error': 'Cotización no encontrada'}), 404

@commercial_bp.route('/quote/<int:quote_id>/status', methods=['PUT'])
def update_quote_status(quote_id):
    """Actualiza estado de cotización"""
    data = request.json
    result = quote_engine.update_quote_status(quote_id, data['status'])
    return jsonify({'success': result})

@commercial_bp.route('/quotes/client/<int:client_id>', methods=['GET'])
def list_client_quotes(client_id):
    """Lista cotizaciones de un cliente"""
    status = request.args.get('status')
    quotes = quote_engine.list_quotes_by_client(client_id, status)
    return jsonify({'success': True, 'quotes': quotes})

# ==================== RUTAS DE ÓRDENES ====================

@commercial_bp.route('/order/create-from-quote', methods=['POST'])
def create_order_from_quote():
    """Crea orden desde cotización aceptada"""
    data = request.json
    result = order_processor.create_order_from_quote(
        quote_id=data['quote_id'],
        additional_info=data.get('additional_info', {})
    )
    return jsonify(result)

@commercial_bp.route('/order/create-direct', methods=['POST'])
def create_direct_order():
    """Crea orden directa sin cotización"""
    data = request.json
    result = order_processor.create_direct_order(
        client_id=data['client_id'],
        customer_info=data['customer_info'],
        products_data=data['products'],
        additional_info=data.get('additional_info', {})
    )
    return jsonify(result)

@commercial_bp.route('/order/<int:order_id>', methods=['GET'])
def get_order_details(order_id):
    """Obtiene detalles de una orden"""
    result = order_processor.get_order_details(order_id)
    if result:
        return jsonify({'success': True, 'order': result})
    return jsonify({'success': False, 'error': 'Orden no encontrada'}), 404

@commercial_bp.route('/order/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Actualiza estado de orden"""
    data = request.json
    result = order_processor.update_order_status(
        order_id=order_id,
        new_status=data['status'],
        notes=data.get('notes')
    )
    return jsonify(result)

@commercial_bp.route('/orders/client/<int:client_id>', methods=['GET'])
def list_client_orders(client_id):
    """Lista órdenes de un cliente"""
    status = request.args.get('status')
    limit = int(request.args.get('limit', 50))
    orders = order_processor.list_orders_by_client(client_id, status, limit)
    return jsonify({'success': True, 'orders': orders})

@commercial_bp.route('/orders/statistics/<int:client_id>', methods=['GET'])
def get_order_statistics(client_id):
    """Obtiene estadísticas de órdenes"""
    days = int(request.args.get('days', 30))
    stats = order_processor.get_order_statistics(client_id, days)
    return jsonify({'success': True, 'statistics': stats})

# ==================== RUTAS DE INVENTARIO ====================

@commercial_bp.route('/inventory/product/add', methods=['POST'])
def add_product():
    """Agrega nuevo producto al inventario"""
    data = request.json
    result = inventory_manager.add_product(data['client_id'], data['product_data'])
    return jsonify(result)

@commercial_bp.route('/inventory/product/<int:product_id>/stock', methods=['PUT'])
def update_product_stock(product_id):
    """Actualiza stock de producto"""
    data = request.json
    result = inventory_manager.update_product_stock(
        product_id=product_id,
        new_stock=data['new_stock'],
        reason=data.get('reason', 'Ajuste manual')
    )
    return jsonify(result)

@commercial_bp.route('/inventory/alerts/<int:client_id>', methods=['GET'])
def get_low_stock_alerts(client_id):
    """Obtiene alertas de stock bajo"""
    alerts = inventory_manager.get_low_stock_alerts(client_id)
    return jsonify({'success': True, 'alerts': alerts})

@commercial_bp.route('/inventory/report/<int:client_id>', methods=['GET'])
def get_inventory_report(client_id):
    """Genera reporte de inventario"""
    report = inventory_manager.get_inventory_report(client_id)
    return jsonify({'success': True, 'report': report})

@commercial_bp.route('/inventory/movements', methods=['GET'])
def get_inventory_movements():
    """Obtiene historial de movimientos de inventario"""
    product_id = request.args.get('product_id', type=int)
    movement_type = request.args.get('movement_type')
    limit = int(request.args.get('limit', 50))
    
    movements = inventory_manager.get_inventory_movements(product_id, movement_type, limit)
    return jsonify({'success': True, 'movements': movements})

# ==================== RUTAS DE FACTURACIÓN ====================

@commercial_bp.route('/invoice/generate', methods=['POST'])
def generate_invoice():
    """Genera factura desde orden"""
    data = request.json
    result = invoice_generator.generate_invoice_from_order(
        order_id=data['order_id'],
        tax_info=data.get('tax_info', {})
    )
    return jsonify(result)

@commercial_bp.route('/invoice/<int:invoice_id>', methods=['GET'])
def get_invoice_details(invoice_id):
    """Obtiene detalles de factura"""
    result = invoice_generator.get_invoice_details(invoice_id)
    if result:
        return jsonify({'success': True, 'invoice': result})
    return jsonify({'success': False, 'error': 'Factura no encontrada'}), 404

@commercial_bp.route('/invoice/<int:invoice_id>/status', methods=['PUT'])
def update_invoice_status(invoice_id):
    """Actualiza estado de factura"""
    data = request.json
    result = invoice_generator.update_invoice_status(
        invoice_id=invoice_id,
        new_status=data['status'],
        payment_date=data.get('payment_date')
    )
    return jsonify(result)

@commercial_bp.route('/invoices/client/<int:client_id>', methods=['GET'])
def list_client_invoices(client_id):
    """Lista facturas de un cliente"""
    status = request.args.get('status')
    limit = int(request.args.get('limit', 50))
    invoices = invoice_generator.list_invoices_by_client(client_id, status, limit)
    return jsonify({'success': True, 'invoices': invoices})

@commercial_bp.route('/invoices/overdue/<int:client_id>', methods=['GET'])
def get_overdue_invoices(client_id):
    """Obtiene facturas vencidas"""
    overdue = invoice_generator.get_overdue_invoices(client_id)
    return jsonify({'success': True, 'overdue_invoices': overdue})

@commercial_bp.route('/invoices/statistics/<int:client_id>', methods=['GET'])
def get_invoice_statistics(client_id):
    """Obtiene estadísticas de facturación"""
    days = int(request.args.get('days', 30))
    stats = invoice_generator.get_invoice_statistics(client_id, days)
    return jsonify({'success': True, 'statistics': stats})

# ==================== RUTAS DE CRM ====================

@commercial_bp.route('/crm/lead/create', methods=['POST'])
def create_lead():
    """Crea nuevo lead"""
    data = request.json
    result = crm_system.create_lead(data['client_id'], data['lead_data'])
    return jsonify(result)

@commercial_bp.route('/crm/lead/<int:lead_id>', methods=['GET'])
def get_lead_details(lead_id):
    """Obtiene detalles de lead"""
    result = crm_system.get_lead_details(lead_id)
    if result:
        return jsonify({'success': True, 'lead': result})
    return jsonify({'success': False, 'error': 'Lead no encontrado'}), 404

@commercial_bp.route('/crm/lead/<int:lead_id>/status', methods=['PUT'])
def update_lead_status(lead_id):
    """Actualiza estado de lead"""
    data = request.json
    result = crm_system.update_lead_status(
        lead_id=lead_id,
        new_status=data['status'],
        probability=data.get('probability'),
        notes=data.get('notes')
    )
    return jsonify(result)

@commercial_bp.route('/crm/lead/<int:lead_id>/interaction', methods=['POST'])
def record_interaction():
    """Registra interacción con lead"""
    data = request.json
    lead_id = data['lead_id']
    result = crm_system.record_interaction(lead_id, data['interaction_data'])
    return jsonify(result)

@commercial_bp.route('/crm/pipeline/<int:client_id>', methods=['GET'])
def get_pipeline_overview(client_id):
    """Obtiene resumen del pipeline"""
    overview = crm_system.get_pipeline_overview(client_id)
    return jsonify({'success': True, 'pipeline': overview})

@commercial_bp.route('/crm/attention/<int:client_id>', methods=['GET'])
def get_leads_requiring_attention(client_id):
    """Obtiene leads que requieren atención"""
    leads = crm_system.get_leads_requiring_attention(client_id)
    return jsonify({'success': True, 'leads': leads})

@commercial_bp.route('/crm/statistics/<int:client_id>', methods=['GET'])
def get_crm_statistics(client_id):
    """Obtiene estadísticas del CRM"""
    days = int(request.args.get('days', 30))
    stats = crm_system.get_crm_statistics(client_id, days)
    return jsonify({'success': True, 'statistics': stats})

@commercial_bp.route('/crm/search/<int:client_id>', methods=['GET'])
def search_leads(client_id):
    """Busca leads por criterios"""
    query = request.args.get('q', '')
    status = request.args.get('status')
    leads = crm_system.search_leads(client_id, query, status)
    return jsonify({'success': True, 'leads': leads})

# ==================== DASHBOARD COMERCIAL ====================

@commercial_bp.route('/dashboard/<int:client_id>')
def commercial_dashboard(client_id):
    """Dashboard comercial principal"""
    # Obtener estadísticas generales
    pipeline_overview = crm_system.get_pipeline_overview(client_id)
    order_stats = order_processor.get_order_statistics(client_id)
    inventory_report = inventory_manager.get_inventory_report(client_id)
    invoice_stats = invoice_generator.get_invoice_statistics(client_id)
    
    # Alertas importantes
    low_stock_alerts = inventory_manager.get_low_stock_alerts(client_id)
    attention_leads = crm_system.get_leads_requiring_attention(client_id)
    overdue_invoices = invoice_generator.get_overdue_invoices(client_id)
    
    return render_template('commercial/dashboard.html',
                         client_id=client_id,
                         pipeline=pipeline_overview,
                         order_stats=order_stats,
                         inventory=inventory_report,
                         invoice_stats=invoice_stats,
                         alerts={
                             'low_stock': low_stock_alerts,
                             'attention_leads': attention_leads[:5],  # Top 5
                             'overdue_invoices': overdue_invoices[:5]
                         })

# ==================== RUTAS DE INTEGRACIÓN CON IA ====================

@commercial_bp.route('/ai/process-customer-message', methods=['POST'])
def process_customer_message():
    """
    Procesa mensaje de cliente y determina si se debe generar cotización,
    crear lead, etc.
    """
    try:
        data = request.json
        client_id = data['client_id']
        customer_message = data['message']
        customer_info = data.get('customer_info', {})
        
        # Usar IA para analizar intención del mensaje
        # Esta es la integración clave que convierte SalesMind en un sistema comercial completo
        
        # Determinar si el mensaje requiere cotización
        if any(keyword in customer_message.lower() for keyword in 
               ['precio', 'cotizar', 'cuesta', 'valor', 'comprar', 'adquirir']):
            
            # Generar cotización automática
            quote_result = quote_engine.generate_quote_from_query(
                client_id=client_id,
                customer_query=customer_message,
                customer_info=customer_info
            )
            
            if quote_result['success']:
                # También crear lead si no existe
                lead_data = {
                    'name': customer_info.get('name', 'Cliente desde Chat'),
                    'email': customer_info.get('email', ''),
                    'phone': customer_info.get('phone', ''),
                    'source': 'chat_bot',
                    'estimated_value': quote_result.get('total_amount', 0),
                    'probability': 30,  # 30% por consulta de precio
                    'notes': f'Consulta original: {customer_message}'
                }
                
                crm_system.create_lead(client_id, lead_data)
                
                return jsonify({
                    'success': True,
                    'action': 'quote_generated',
                    'quote': quote_result,
                    'message': f'He generado una cotización automática por ${quote_result["total_amount"]:,.0f}. ¿Te interesa proceder con la orden?'
                })
        
        # Si no es una consulta de precio, crear lead básico
        elif customer_info.get('email') or customer_info.get('phone'):
            lead_data = {
                'name': customer_info.get('name', 'Cliente desde Chat'),
                'email': customer_info.get('email', ''),
                'phone': customer_info.get('phone', ''),
                'source': 'chat_bot',
                'notes': f'Consulta: {customer_message}'
            }
            
            crm_result = crm_system.create_lead(client_id, lead_data)
            
            return jsonify({
                'success': True,
                'action': 'lead_created',
                'lead': crm_result,
                'message': 'Gracias por tu consulta. He registrado tu información para seguimiento.'
            })
        
        return jsonify({
            'success': True,
            'action': 'info_only',
            'message': 'Información proporcionada. Si deseas una cotización o tienes interés en comprar, por favor proporciona tus datos de contacto.'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Registrar el blueprint
def register_commercial_routes(app):
    """Función para registrar el blueprint comercial"""
    app.register_blueprint(commercial_bp)