"""
Modelos comerciales extendidos para SalesMind
Versión 2.0.0 - Sistema Comercial Completo
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from modules.models import db
import uuid
from datetime import datetime

class Product(db.Model):
    """Modelo para productos/servicios de cada cliente"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    public_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Información del producto
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    sku = Column(String(50))
    
    # Precios
    base_price = Column(Numeric(10, 2), nullable=False)
    discount_percentage = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.0)  # IVA u otros impuestos
    
    # Inventario
    stock_quantity = Column(Integer, default=0)
    min_stock_alert = Column(Integer, default=10)
    
    # Estados
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Metadatos
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    client = relationship("Client", back_populates="products")
    quote_items = relationship("QuoteItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    inventory_movements = relationship("InventoryMovement", back_populates="product")

class Quote(db.Model):
    """Modelo para cotizaciones automáticas"""
    __tablename__ = 'quotes'
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    quote_number = Column(String(50), unique=True, nullable=False)
    
    # Información del cliente final
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255))
    customer_phone = Column(String(50))
    
    # Totales
    subtotal = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    # Estados
    status = Column(String(20), default='draft')  # draft, sent, accepted, rejected, expired
    valid_until = Column(DateTime)
    
    # Metadatos
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    notes = Column(Text)
    
    # Relaciones
    client = relationship("Client", back_populates="quotes")
    quote_items = relationship("QuoteItem", back_populates="quote", cascade="all, delete-orphan")

class QuoteItem(db.Model):
    """Elementos individuales de una cotización"""
    __tablename__ = 'quote_items'
    
    id = Column(Integer, primary_key=True)
    quote_id = Column(Integer, ForeignKey('quotes.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount_percentage = Column(Float, default=0.0)
    line_total = Column(Numeric(10, 2), nullable=False)
    
    # Relaciones
    quote = relationship("Quote", back_populates="quote_items")
    product = relationship("Product", back_populates="quote_items")

class Order(db.Model):
    """Modelo para órdenes/pedidos"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    quote_id = Column(Integer, ForeignKey('quotes.id'), nullable=True)  # Puede venir de una cotización
    order_number = Column(String(50), unique=True, nullable=False)
    
    # Información del cliente final
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255))
    customer_phone = Column(String(50))
    shipping_address = Column(Text)
    
    # Totales (copiados de la cotización o calculados)
    subtotal = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    shipping_cost = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    # Estados y fechas
    status = Column(String(20), default='pending')  # pending, confirmed, processing, shipped, delivered, cancelled
    order_date = Column(DateTime, default=func.now())
    estimated_delivery = Column(DateTime)
    delivered_at = Column(DateTime)
    
    # Metadatos
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    notes = Column(Text)
    
    # Relaciones
    client = relationship("Client", back_populates="orders")
    quote = relationship("Quote", backref="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="order")

class OrderItem(db.Model):
    """Elementos individuales de una orden"""
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount_percentage = Column(Float, default=0.0)
    line_total = Column(Numeric(10, 2), nullable=False)
    
    # Relaciones
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

class Invoice(db.Model):
    """Modelo para facturas generadas automáticamente"""
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    invoice_number = Column(String(50), unique=True, nullable=False)
    
    # Información fiscal
    tax_id = Column(String(50))  # NIT/RFC de la empresa cliente
    customer_tax_id = Column(String(50))  # NIT/RFC del cliente final
    
    # Totales
    subtotal = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    
    # Estados y fechas
    status = Column(String(20), default='generated')  # generated, sent, paid, overdue, cancelled
    issue_date = Column(DateTime, default=func.now())
    due_date = Column(DateTime)
    paid_at = Column(DateTime)
    
    # Archivos
    pdf_path = Column(String(500))  # Ruta del PDF generado
    
    # Metadatos
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    notes = Column(Text)
    
    # Relaciones
    client = relationship("Client", back_populates="invoices")
    order = relationship("Order", back_populates="invoices")

class InventoryMovement(db.Model):
    """Registro de movimientos de inventario"""
    __tablename__ = 'inventory_movements'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    movement_type = Column(String(20), nullable=False)  # 'in', 'out', 'adjustment'
    quantity = Column(Integer, nullable=False)
    reference_type = Column(String(50))  # 'order', 'adjustment', 'return', etc.
    reference_id = Column(Integer)  # ID de la orden, ajuste, etc.
    
    reason = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    created_by = Column(String(100))  # Usuario que hizo el movimiento
    
    # Relaciones
    product = relationship("Product", back_populates="inventory_movements")

class Lead(db.Model):
    """Modelo para leads y CRM"""
    __tablename__ = 'leads'
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    
    # Información del lead
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    company = Column(String(255))
    
    # Pipeline
    status = Column(String(30), default='new')  # new, contacted, qualified, proposal, negotiation, won, lost
    source = Column(String(50))  # website, chat, referral, etc.
    assigned_to = Column(String(100))  # Vendedor asignado
    
    # Valores
    estimated_value = Column(Numeric(10, 2))
    probability = Column(Integer, default=0)  # 0-100%
    
    # Fechas importantes
    created_at = Column(DateTime, default=func.now())
    last_contact = Column(DateTime)
    expected_close_date = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Notas y seguimiento
    notes = Column(Text)
    next_action = Column(String(500))
    next_action_date = Column(DateTime)
    
    # Relaciones
    client = relationship("Client", back_populates="leads")
    interactions = relationship("LeadInteraction", back_populates="lead", cascade="all, delete-orphan")

class LeadInteraction(db.Model):
    """Interacciones con leads para seguimiento CRM"""
    __tablename__ = 'lead_interactions'
    
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=False)
    
    interaction_type = Column(String(30), nullable=False)  # call, email, meeting, chat, etc.
    direction = Column(String(10), nullable=False)  # inbound, outbound
    
    subject = Column(String(255))
    description = Column(Text)
    outcome = Column(String(100))
    
    scheduled_at = Column(DateTime)
    completed_at = Column(DateTime, default=func.now())
    created_by = Column(String(100))
    
    # Relaciones
    lead = relationship("Lead", back_populates="interactions")

# Actualizar modelo Client existente con nuevas relaciones
def extend_client_model():
    """Función para extender el modelo Client existente"""
    from modules.models import Client
    
    # Agregar nuevas relaciones al modelo Client existente
    if not hasattr(Client, 'products'):
        Client.products = relationship("Product", back_populates="client")
    if not hasattr(Client, 'quotes'):
        Client.quotes = relationship("Quote", back_populates="client")
    if not hasattr(Client, 'orders'):
        Client.orders = relationship("Order", back_populates="client")
    if not hasattr(Client, 'invoices'):
        Client.invoices = relationship("Invoice", back_populates="client")
    if not hasattr(Client, 'leads'):
        Client.leads = relationship("Lead", back_populates="client")