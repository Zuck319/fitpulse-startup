import os
import sys

# Agregar la ruta raiz al sys.path para importaciones
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.web.main import app
