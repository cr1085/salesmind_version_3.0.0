# modules/indexer_admin/__init__.py
from flask import Blueprint

indexer_bp = Blueprint('indexer_admin', __name__, url_prefix='/admin/indexer')

from . import routes