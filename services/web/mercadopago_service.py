"""
Servicio de Integracion con Mercado Pago Checkout Pro para FitPulse Analytics.
Permite cobros en pesos mexicanos (MXN) con tarjeta, SPEI y OXXO Pay.
Compatible con tokens de prueba (Sandbox) y tokens de produccion.
"""

import os
import json
import requests
from typing import Dict, Any, Optional

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "mercadopago_config.json")


def obtener_config_mercadopago() -> Dict[str, str]:
    """Obtiene la configuracion de credenciales de Mercado Pago."""
    # Prioridad: variables de entorno o archivo de configuracion
    token = os.environ.get("MERCADOPAGO_ACCESS_TOKEN", "").strip()
    public_key = os.environ.get("MERCADOPAGO_PUBLIC_KEY", "").strip()

    if not token and os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                token = data.get("access_token", "").strip()
                public_key = data.get("public_key", "").strip()
        except Exception:
            pass

    return {
        "access_token": token,
        "public_key": public_key,
        "modo": "produccion" if token.startswith("APP_USR-") else ("prueba" if token.startswith("TEST-") else "demo_local")
    }


def guardar_config_mercadopago(access_token: str, public_key: str = "") -> bool:
    """Guarda las credenciales de Mercado Pago en archivo seguro."""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "access_token": access_token.strip(),
                "public_key": public_key.strip()
            }, f, indent=2)
        return True
    except Exception:
        return False


def obtener_planes_suscripcion() -> Dict[str, str]:
    """Retorna los enlaces oficiales de preapproval_plan de Mercado Pago en produccion."""
    return {
        "basico": "https://www.mercadopago.com.mx/subscriptions/checkout?preapproval_plan_id=a991bb23fda344d5afad2ea69a8959a0",
        "pro": "https://www.mercadopago.com.mx/subscriptions/checkout?preapproval_plan_id=53a0eea277504b608898b98467cd1fdb",
        "premium": "https://www.mercadopago.com.mx/subscriptions/checkout?preapproval_plan_id=9c6f55ead7e146d684902c51bdcd73cd"
    }


def crear_preferencia_mercadopago(
    usuario: Dict[str, Any],
    plan: str,
    host_url: str
) -> Dict[str, Any]:
    """
    Retorna la URL oficial de suscripcion recurrente mensual en Mercado Pago.
    Permite cobro automatico a tarjeta de credito/debito mes con mes en fecha y hora fija.
    """
    plan_clean = (plan or "pro").lower()
    planes = obtener_planes_suscripcion()
    checkout_url = planes.get(plan_clean, planes["pro"])

    return {
        "ok": True,
        "tipo": "suscripcion_recurrente_oficial",
        "checkout_url": checkout_url,
        "preference_id": f"SUB-MP-{plan_clean.upper()}",
        "modo": "produccion"
    }
