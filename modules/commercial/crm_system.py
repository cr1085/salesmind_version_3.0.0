"""
Sistema CRM completo para SalesMind
Gestión de leads, pipeline de ventas y seguimiento de clientes
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import and_, func, or_
from modules.models import db
from modules.commercial_models import Lead, LeadInteraction, Quote, Order

class CRMSystem:
    """Sistema completo de gestión de relaciones con clientes (CRM)"""
    
    def __init__(self):
        pass
    
    def create_lead(self, client_id: int, lead_data: Dict) -> Dict:
        """
        Crea un nuevo lead en el sistema CRM
        
        Args:
            client_id: ID del cliente empresarial
            lead_data: Datos del lead (nombre, email, teléfono, empresa, etc.)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            lead = Lead(
                client_id=client_id,
                name=lead_data['name'],
                email=lead_data.get('email', ''),
                phone=lead_data.get('phone', ''),
                company=lead_data.get('company', ''),
                status='new',
                source=lead_data.get('source', 'website'),
                assigned_to=lead_data.get('assigned_to', ''),
                estimated_value=lead_data.get('estimated_value', 0),
                probability=lead_data.get('probability', 10),  # 10% inicial
                expected_close_date=self._calculate_expected_close_date(),
                notes=lead_data.get('notes', ''),
                next_action=lead_data.get('next_action', 'Contactar al lead'),
                next_action_date=datetime.now() + timedelta(days=1)
            )
            
            db.session.add(lead)
            db.session.flush()  # Para obtener el ID
            
            # Registrar interacción inicial
            self._record_interaction(
                lead_id=lead.id,
                interaction_type='lead_created',
                direction='inbound',
                subject='Nuevo lead registrado',
                description=f'Lead creado desde {lead.source}',
                outcome='lead_registered'
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'lead_id': lead.id,
                'message': f'Lead {lead.name} creado exitosamente'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error creando lead: {str(e)}'}
    
    def update_lead_status(self, lead_id: int, new_status: str, 
                          probability: int = None, notes: str = None) -> Dict:
        """
        Actualiza el estado de un lead en el pipeline
        
        Estados válidos: new, contacted, qualified, proposal, negotiation, won, lost
        """
        try:
            lead = Lead.query.get(lead_id)
            if not lead:
                return {'success': False, 'error': 'Lead no encontrado'}
            
            old_status = lead.status
            lead.status = new_status
            
            # Actualizar probabilidad automáticamente según el estado
            if probability is not None:
                lead.probability = probability
            else:
                lead.probability = self._get_default_probability_by_status(new_status)
            
            # Actualizar fecha de cierre si se ganó o perdió
            if new_status in ['won', 'lost']:
                lead.closed_at = datetime.now()
            
            if notes:
                lead.notes = (lead.notes or '') + f"\n{datetime.now()}: {notes}"
            
            # Registrar cambio de estado como interacción
            self._record_interaction(
                lead_id=lead_id,
                interaction_type='status_change',
                direction='outbound',
                subject=f'Cambio de estado: {old_status} → {new_status}',
                description=notes or f'Lead movido de {old_status} a {new_status}',
                outcome=f'status_{new_status}'
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'lead_id': lead_id,
                'old_status': old_status,
                'new_status': new_status,
                'probability': lead.probability,
                'message': f'Lead actualizado de {old_status} a {new_status}'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error actualizando lead: {str(e)}'}
    
    def record_interaction(self, lead_id: int, interaction_data: Dict) -> Dict:
        """
        Registra una nueva interacción con un lead
        
        Args:
            lead_id: ID del lead
            interaction_data: Datos de la interacción (tipo, dirección, descripción, etc.)
        """
        try:
            lead = Lead.query.get(lead_id)
            if not lead:
                return {'success': False, 'error': 'Lead no encontrado'}
            
            interaction = LeadInteraction(
                lead_id=lead_id,
                interaction_type=interaction_data['type'],
                direction=interaction_data.get('direction', 'outbound'),
                subject=interaction_data.get('subject', ''),
                description=interaction_data.get('description', ''),
                outcome=interaction_data.get('outcome', ''),
                scheduled_at=interaction_data.get('scheduled_at'),
                completed_at=datetime.now(),
                created_by=interaction_data.get('created_by', 'system')
            )
            
            # Actualizar última interacción en el lead
            lead.last_contact = datetime.now()
            
            # Actualizar próxima acción si se proporciona
            if interaction_data.get('next_action'):
                lead.next_action = interaction_data['next_action']
                lead.next_action_date = interaction_data.get('next_action_date', 
                                                           datetime.now() + timedelta(days=3))
            
            db.session.add(interaction)
            db.session.commit()
            
            return {
                'success': True,
                'interaction_id': interaction.id,
                'message': 'Interacción registrada exitosamente'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error registrando interacción: {str(e)}'}
    
    def get_pipeline_overview(self, client_id: int) -> Dict:
        """Obtiene resumen del pipeline de ventas"""
        leads = Lead.query.filter_by(client_id=client_id).all()
        
        # Contar leads por estado
        pipeline_counts = {}
        total_value = 0
        weighted_value = 0
        
        for status in ['new', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost']:
            status_leads = [l for l in leads if l.status == status]
            pipeline_counts[status] = {
                'count': len(status_leads),
                'value': sum(float(l.estimated_value or 0) for l in status_leads)
            }
            
            if status not in ['won', 'lost']:  # Solo contar leads activos
                total_value += pipeline_counts[status]['value']
                # Valor ponderado por probabilidad
                weighted_value += sum(
                    float(l.estimated_value or 0) * (l.probability / 100)
                    for l in status_leads
                )
        
        # Estadísticas adicionales
        active_leads = len([l for l in leads if l.status not in ['won', 'lost']])
        won_leads = len([l for l in leads if l.status == 'won'])
        lost_leads = len([l for l in leads if l.status == 'lost'])
        
        conversion_rate = (won_leads / len(leads) * 100) if leads else 0
        
        return {
            'pipeline': pipeline_counts,
            'summary': {
                'total_leads': len(leads),
                'active_leads': active_leads,
                'won_leads': won_leads,
                'lost_leads': lost_leads,
                'total_pipeline_value': total_value,
                'weighted_pipeline_value': weighted_value,
                'conversion_rate': round(conversion_rate, 2)
            }
        }
    
    def get_leads_requiring_attention(self, client_id: int) -> List[Dict]:
        """Obtiene leads que requieren atención inmediata"""
        today = datetime.now().date()
        
        # Leads con próxima acción vencida o para hoy
        attention_leads = Lead.query.filter(
            and_(
                Lead.client_id == client_id,
                Lead.status.notin_(['won', 'lost']),
                or_(
                    Lead.next_action_date <= datetime.now(),
                    Lead.last_contact <= datetime.now() - timedelta(days=7),  # Sin contacto por 7 días
                    Lead.next_action_date.is_(None)  # Sin próxima acción definida
                )
            )
        ).all()
        
        return [
            {
                'id': lead.id,
                'name': lead.name,
                'company': lead.company,
                'status': lead.status,
                'estimated_value': float(lead.estimated_value or 0),
                'last_contact': lead.last_contact.isoformat() if lead.last_contact else None,
                'next_action': lead.next_action,
                'next_action_date': lead.next_action_date.isoformat() if lead.next_action_date else None,
                'days_without_contact': (datetime.now() - lead.last_contact).days if lead.last_contact else None,
                'priority': self._calculate_lead_priority(lead)
            }
            for lead in attention_leads
        ]
    
    def get_lead_details(self, lead_id: int) -> Optional[Dict]:
        """Obtiene detalles completos de un lead"""
        lead = Lead.query.get(lead_id)
        if not lead:
            return None
        
        # Obtener historial de interacciones
        interactions = LeadInteraction.query.filter_by(lead_id=lead_id).order_by(
            LeadInteraction.completed_at.desc()
        ).all()
        
        # Buscar cotizaciones y órdenes relacionadas
        related_quotes = Quote.query.filter_by(
            client_id=lead.client_id,
            customer_email=lead.email
        ).all() if lead.email else []
        
        related_orders = Order.query.filter_by(
            client_id=lead.client_id,
            customer_email=lead.email
        ).all() if lead.email else []
        
        return {
            'id': lead.id,
            'name': lead.name,
            'email': lead.email,
            'phone': lead.phone,
            'company': lead.company,
            'status': lead.status,
            'source': lead.source,
            'assigned_to': lead.assigned_to,
            'estimated_value': float(lead.estimated_value or 0),
            'probability': lead.probability,
            'created_at': lead.created_at.isoformat(),
            'last_contact': lead.last_contact.isoformat() if lead.last_contact else None,
            'expected_close_date': lead.expected_close_date.isoformat() if lead.expected_close_date else None,
            'closed_at': lead.closed_at.isoformat() if lead.closed_at else None,
            'notes': lead.notes,
            'next_action': lead.next_action,
            'next_action_date': lead.next_action_date.isoformat() if lead.next_action_date else None,
            'interactions': [
                {
                    'id': i.id,
                    'type': i.interaction_type,
                    'direction': i.direction,
                    'subject': i.subject,
                    'description': i.description,
                    'outcome': i.outcome,
                    'completed_at': i.completed_at.isoformat(),
                    'created_by': i.created_by
                }
                for i in interactions
            ],
            'related_quotes': len(related_quotes),
            'related_orders': len(related_orders),
            'total_quoted': sum(float(q.total_amount) for q in related_quotes),
            'total_ordered': sum(float(o.total_amount) for o in related_orders)
        }
    
    def get_crm_statistics(self, client_id: int, days: int = 30) -> Dict:
        """Obtiene estadísticas del CRM"""
        start_date = datetime.now() - timedelta(days=days)
        
        # Leads creados en el período
        new_leads = Lead.query.filter(
            Lead.client_id == client_id,
            Lead.created_at >= start_date
        ).count()
        
        # Leads cerrados (ganados/perdidos)
        closed_leads = Lead.query.filter(
            Lead.client_id == client_id,
            Lead.closed_at >= start_date,
            Lead.status.in_(['won', 'lost'])
        ).all()
        
        won_leads = [l for l in closed_leads if l.status == 'won']
        lost_leads = [l for l in closed_leads if l.status == 'lost']
        
        # Valor de leads ganados
        won_value = sum(float(l.estimated_value or 0) for l in won_leads)
        
        # Tiempo promedio en el pipeline
        avg_pipeline_time = 0
        if closed_leads:
            pipeline_times = [
                (l.closed_at - l.created_at).days for l in closed_leads
                if l.closed_at and l.created_at
            ]
            avg_pipeline_time = sum(pipeline_times) / len(pipeline_times) if pipeline_times else 0
        
        # Fuentes de leads más efectivas
        lead_sources = db.session.query(
            Lead.source,
            func.count(Lead.id).label('total'),
            func.count(Lead.id).filter(Lead.status == 'won').label('won')
        ).filter(
            Lead.client_id == client_id,
            Lead.created_at >= start_date
        ).group_by(Lead.source).all()
        
        return {
            'period_days': days,
            'new_leads': new_leads,
            'closed_leads': len(closed_leads),
            'won_leads': len(won_leads),
            'lost_leads': len(lost_leads),
            'won_value': won_value,
            'conversion_rate': (len(won_leads) / len(closed_leads) * 100) if closed_leads else 0,
            'average_pipeline_days': round(avg_pipeline_time, 1),
            'lead_sources': [
                {
                    'source': source,
                    'total_leads': total,
                    'won_leads': won or 0,
                    'conversion_rate': ((won or 0) / total * 100) if total > 0 else 0
                }
                for source, total, won in lead_sources
            ]
        }
    
    def search_leads(self, client_id: int, query: str, status: str = None) -> List[Dict]:
        """Busca leads por nombre, email, empresa, etc."""
        search_filter = Lead.client_id == client_id
        
        if query:
            search_filter = and_(
                search_filter,
                or_(
                    Lead.name.ilike(f'%{query}%'),
                    Lead.email.ilike(f'%{query}%'),
                    Lead.company.ilike(f'%{query}%'),
                    Lead.phone.ilike(f'%{query}%')
                )
            )
        
        if status:
            search_filter = and_(search_filter, Lead.status == status)
        
        leads = Lead.query.filter(search_filter).order_by(Lead.created_at.desc()).all()
        
        return [
            {
                'id': lead.id,
                'name': lead.name,
                'email': lead.email,
                'company': lead.company,
                'status': lead.status,
                'estimated_value': float(lead.estimated_value or 0),
                'probability': lead.probability,
                'created_at': lead.created_at.isoformat(),
                'last_contact': lead.last_contact.isoformat() if lead.last_contact else None
            }
            for lead in leads
        ]
    
    def _record_interaction(self, lead_id: int, interaction_type: str, direction: str,
                           subject: str, description: str, outcome: str = None):
        """Registra una interacción interna"""
        interaction = LeadInteraction(
            lead_id=lead_id,
            interaction_type=interaction_type,
            direction=direction,
            subject=subject,
            description=description,
            outcome=outcome,
            completed_at=datetime.now(),
            created_by='system'
        )
        db.session.add(interaction)
    
    def _get_default_probability_by_status(self, status: str) -> int:
        """Retorna probabilidad por defecto según el estado"""
        probabilities = {
            'new': 10,
            'contacted': 20,
            'qualified': 40,
            'proposal': 60,
            'negotiation': 80,
            'won': 100,
            'lost': 0
        }
        return probabilities.get(status, 10)
    
    def _calculate_expected_close_date(self, days_ahead: int = 30) -> datetime:
        """Calcula fecha esperada de cierre"""
        return datetime.now() + timedelta(days=days_ahead)
    
    def _calculate_lead_priority(self, lead: Lead) -> str:
        """Calcula prioridad de un lead"""
        priority_score = 0
        
        # Valor estimado
        if lead.estimated_value and lead.estimated_value > 1000000:
            priority_score += 3
        elif lead.estimated_value and lead.estimated_value > 500000:
            priority_score += 2
        elif lead.estimated_value and lead.estimated_value > 100000:
            priority_score += 1
        
        # Probabilidad
        if lead.probability >= 70:
            priority_score += 3
        elif lead.probability >= 40:
            priority_score += 2
        elif lead.probability >= 20:
            priority_score += 1
        
        # Tiempo sin contacto
        if lead.last_contact:
            days_without_contact = (datetime.now() - lead.last_contact).days
            if days_without_contact >= 7:
                priority_score += 2
            elif days_without_contact >= 3:
                priority_score += 1
        
        # Próxima acción vencida
        if lead.next_action_date and lead.next_action_date < datetime.now():
            priority_score += 2
        
        if priority_score >= 6:
            return 'high'
        elif priority_score >= 3:
            return 'medium'
        else:
            return 'low'