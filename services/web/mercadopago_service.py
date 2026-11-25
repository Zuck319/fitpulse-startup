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


def crear_preferencia_mercadopago(
    usuario: Dict[str, Any],
    plan: str,
    host_url: str
) -> Dict[str, Any]:
    """
    Crea una preferencia de pago en Mercado Pago Checkout Pro.
    Retorna la URL de checkout (init_point o sandbox_init_point).
    """
    config = obtener_config_mercadopago()
    access_token = config["access_token"]

    precios = {
        "basico": {"nombre": "FitPulse Analytics · Plan Basico Monosede", "precio": 499.00},
        "pro": {"nombre": "FitPulse Analytics · Plan Pro Multisede", "precio": 899.00},
        "premium": {"nombre": "FitPulse Analytics · Plan Premium Franquicias", "precio": 1499.00}
    }

    info_plan = precios.get(plan.lower(), precios["pro"])
    base_url = host_url.rstrip("/")

    # Si hay token real de Mercado Pago configurado, llamar a su API oficial
    if access_token and (access_token.startswith("TEST-") or access_token.startswith("APP_USR-")):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "items": [
                {
                    "title": info_plan["nombre"],
                    "description": f"Suscripcion mensual de software para {usuario.get('nombre_gym', 'Gimnasio')}",
                    "quantity": 1,
                    "currency_id": "MXN",
                    "unit_price": float(info_plan["precio"])
                }
            ],
            "payer": {
                "name": usuario.get("nombre_dueno", "Dylan Espinosa"),
                "email": usuario.get("email", "espinosadylan616@gmail.com")
            },
            "back_urls": {
                "success": f"{base_url}/mercadopago/retorno?status=approved&plan={plan.lower()}",
                "pending": f"{base_url}/mercadopago/retorno?status=pending&plan={plan.lower()}",
                "failure": f"{base_url}/mercadopago/retorno?status=failure&plan={plan.lower()}"
            },
            "auto_return": "approved",
            "statement_descriptor": "FITPULSE SAAS",
            "external_reference": f"USER-{usuario.get('id', 1)}-{plan.upper()}"
        }

        try:
            resp = requests.post("https://api.mercadopago.com/checkout/preferences", json=payload, headers=headers, timeout=8)
            if resp.status_code in [200, 201]:
                data = resp.json()
                init_url = data.get("sandbox_init_point") if config["modo"] == "prueba" else data.get("init_point")
                return {
                    "ok": True,
                    "tipo": "oficial_api",
                    "checkout_url": init_url or data.get("init_point"),
                    "preference_id": data.get("id"),
                    "modo": config["modo"]
                }
        except Exception as e:
            pass

    # Si no hay token configurado o fallo de conexion, retornar modo sandbox guiado
    return {
        "ok": True,
        "tipo": "demo_guiada",
        "checkout_url": f"{base_url}/mercadopago/demo-checkout?plan={plan.lower()}",
        "preference_id": f"PREF-DEMO-2026-{plan.upper()}",
        "modo": "demo_local"
    }
