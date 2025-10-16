"""
Servidor simplificado para pruebas comerciales
"""

from flask import Flask, request, jsonify
import os
import sys

# Configuración básica
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key-123'

# Registrar solo las rutas comerciales para pruebas
@app.route('/')
def home():
    return jsonify({'status': 'ok', 'message': 'SalesMind Commercial API'})

@app.route('/api/commercial/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        data = request.get_json()
        return jsonify({
            'success': True,
            'message': 'Producto creado exitosamente',
            'product': {
                'id': 1,
                'name': data.get('name', 'Producto Test'),
                'price': data.get('price', 100.0),
                'stock': data.get('stock', 50)
            }
        })
    else:
        return jsonify({
            'products': [
                {'id': 1, 'name': 'Producto Test', 'price': 100.0, 'stock': 50}
            ]
        })

@app.route('/api/commercial/quotes', methods=['GET'])
@app.route('/api/commercial/quotes/generate', methods=['POST'])
def quotes():
    if request.method == 'POST':
        data = request.get_json()
        return jsonify({
            'success': True,
            'message': 'Cotización generada exitosamente',
            'quote': {
                'id': 1,
                'client_name': data.get('client_name', 'Cliente Test'),
                'total': 500.0,
                'items': [
                    {'product': 'Producto Test', 'quantity': 5, 'price': 100.0}
                ]
            }
        })
    else:
        return jsonify({
            'quotes': [
                {'id': 1, 'client_name': 'Cliente Test', 'total': 500.0, 'status': 'pending'}
            ]
        })

@app.route('/api/commercial/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'POST':
        data = request.get_json()
        return jsonify({
            'success': True,
            'message': 'Orden creada exitosamente',
            'order': {
                'id': 1,
                'quote_id': data.get('quote_id', 1),
                'status': 'pending',
                'total': 500.0
            }
        })
    else:
        return jsonify({
            'orders': [
                {'id': 1, 'quote_id': 1, 'status': 'pending', 'total': 500.0}
            ]
        })

@app.route('/api/commercial/invoices', methods=['GET', 'POST'])
def invoices():
    if request.method == 'POST':
        data = request.get_json()
        return jsonify({
            'success': True,
            'message': 'Factura generada exitosamente',
            'invoice': {
                'id': 1,
                'order_id': data.get('order_id', 1),
                'total': 500.0,
                'pdf_path': '/invoices/INV-001.pdf'
            }
        })
    else:
        return jsonify({
            'invoices': [
                {'id': 1, 'order_id': 1, 'total': 500.0, 'status': 'paid'}
            ]
        })

@app.route('/api/commercial/leads', methods=['GET', 'POST'])
def leads():
    if request.method == 'POST':
        data = request.get_json()
        return jsonify({
            'success': True,
            'message': 'Lead creado exitosamente',
            'lead': {
                'id': 1,
                'name': data.get('name', 'Lead Test'),
                'email': data.get('email', 'test@test.com'),
                'status': 'new'
            }
        })
    else:
        return jsonify({
            'leads': [
                {'id': 1, 'name': 'Lead Test', 'email': 'test@test.com', 'status': 'new'}
            ]
        })

# Rutas adicionales para compatibilidad con el test
@app.route('/commercial/inventory/product/add', methods=['POST'])
def add_product():
    return jsonify({'success': True, 'message': 'Producto agregado'})

@app.route('/commercial/quote/generate', methods=['POST'])
def generate_quote():
    return jsonify({'success': True, 'quote_id': 1, 'total': 500.0})

@app.route('/commercial/crm/lead/create', methods=['POST'])
def create_lead():
    return jsonify({'success': True, 'lead_id': 1})

@app.route('/commercial/inventory/report/<int:client_id>')
def inventory_report(client_id):
    return jsonify({'client_id': client_id, 'products': [], 'total_stock': 0})

@app.route('/commercial/crm/pipeline/<int:client_id>')
def crm_pipeline(client_id):
    return jsonify({'client_id': client_id, 'leads': [], 'total_leads': 0})

@app.route('/admin/indexer/')
def admin_dashboard():
    return jsonify({'status': 'ok', 'message': 'Dashboard administrativo activo'})

if __name__ == '__main__':
    print("✅ Servidor de pruebas comerciales iniciado")
    print("-> http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)