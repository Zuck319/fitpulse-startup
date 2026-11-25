"""
Modulo de Base de Datos SQLite para FitPulse Analytics.
Gestiona usuarios, contraseñas con hash seguro, sesiones persistentes y pasarela de pagos.
Presupuesto FinOps: $0 MXN (SQLite nativo sin cargos de Cloud SQL/RDS).
"""

import os
import sqlite3
import hashlib
import secrets
from datetime import datetime
from typing import Optional, Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "fitpulse_auth.db")


def get_connection():
    """Obtiene una conexion a la base de datos SQLite con row_factory como diccionario."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    """Genera un hash SHA-256 seguro con sal estatica para contraseñas."""
    salt = "fitpulse_finops_2026_salt"
    return hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()


def init_db():
    """Inicializa las tablas de usuarios, sesiones y pagos si no existen."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla de Usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        nombre_dueno TEXT NOT NULL,
        nombre_gym TEXT NOT NULL,
        num_sucursales INTEGER DEFAULT 1,
        plan_activo TEXT DEFAULT 'Pro',
        estado_pago TEXT DEFAULT 'Activo',
        fecha_registro TEXT NOT NULL,
        ultimo_acceso TEXT
    );
    """)

    # Tabla de Sesiones Activas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sesiones (
        token TEXT PRIMARY KEY,
        usuario_id INTEGER NOT NULL,
        fecha_creacion TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
    );
    """)

    # Tabla de Pagos y Transacciones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pagos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_transaccion TEXT UNIQUE NOT NULL,
        usuario_id INTEGER NOT NULL,
        plan TEXT NOT NULL,
        monto_subtotal REAL NOT NULL,
        monto_iva REAL NOT NULL,
        monto_total REAL NOT NULL,
        moneda TEXT DEFAULT 'MXN',
        metodo_pago TEXT NOT NULL,
        marca_tarjeta TEXT,
        ultimos_4 TEXT,
        titular TEXT,
        estado TEXT NOT NULL,
        folio_fiscal TEXT NOT NULL,
        fecha TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    );
    """)

    conn.commit()

    # Sembrar usuario por defecto (Dylan Espinosa) si no existe
    cursor.execute("SELECT id FROM usuarios WHERE email = ?", ("espinosadylan616@gmail.com",))
    if not cursor.fetchone():
        fecha_ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        INSERT INTO usuarios (email, password_hash, nombre_dueno, nombre_gym, num_sucursales, plan_activo, estado_pago, fecha_registro, ultimo_acceso)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "espinosadylan616@gmail.com",
            hash_password("fitpulse123"),
            "Dylan Espinosa",
            "Titan Fitness Center",
            2,
            "Pro",
            "Activo",
            fecha_ahora,
            fecha_ahora
        ))
        user_id = cursor.lastrowid

        # Registrar un pago inicial de ejemplo
        cursor.execute("""
        INSERT INTO pagos (id_transaccion, usuario_id, plan, monto_subtotal, monto_iva, monto_total, moneda, metodo_pago, marca_tarjeta, ultimos_4, titular, estado, folio_fiscal, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "FP-TXN-2026-00104",
            user_id,
            "Pro",
            775.00,
            124.00,
            899.00,
            "MXN",
            "Tarjeta de Credito / Debito",
            "Visa",
            "4242",
            "Dylan Espinosa",
            "Aprobado",
            "CFDI-FP-9901428",
            fecha_ahora
        ))
        conn.commit()

    conn.close()


def registrar_usuario(email: str, password: str, nombre_dueno: str, nombre_gym: str, num_sucursales: int, plan: str) -> Optional[Dict[str, Any]]:
    """Registra un nuevo usuario en la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()
    fecha_ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    p_hash = hash_password(password)

    try:
        cursor.execute("""
        INSERT INTO usuarios (email, password_hash, nombre_dueno, nombre_gym, num_sucursales, plan_activo, estado_pago, fecha_registro, ultimo_acceso)
        VALUES (?, ?, ?, ?, ?, ?, 'Pendiente', ?, ?)
        """, (email.strip().lower(), p_hash, nombre_dueno.strip(), nombre_gym.strip(), num_sucursales, plan.title(), fecha_ahora, fecha_ahora))
        conn.commit()
        user_id = cursor.lastrowid
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def autenticar_usuario(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Verifica credenciales y retorna el usuario si son correctas."""
    conn = get_connection()
    cursor = conn.cursor()
    p_hash = hash_password(password)

    cursor.execute("SELECT * FROM usuarios WHERE email = ? AND password_hash = ?", (email.strip().lower(), p_hash))
    row = cursor.fetchone()

    if row:
        usuario = dict(row)
        fecha_ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE usuarios SET ultimo_acceso = ? WHERE id = ?", (fecha_ahora, usuario["id"]))
        conn.commit()
        conn.close()
        return usuario

    conn.close()
    return None


def crear_sesion(usuario_id: int) -> str:
    """Crea un token de sesion unico para el usuario."""
    token = secrets.token_hex(24)
    conn = get_connection()
    cursor = conn.cursor()
    fecha_ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("INSERT INTO sesiones (token, usuario_id, fecha_creacion) VALUES (?, ?, ?)", (token, usuario_id, fecha_ahora))
    conn.commit()
    conn.close()
    return token


def obtener_usuario_por_sesion(token: str) -> Optional[Dict[str, Any]]:
    """Obtiene los datos del usuario a partir de su token de sesion."""
    if not token:
        return None
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT u.* FROM usuarios u
    JOIN sesiones s ON u.id = s.usuario_id
    WHERE s.token = ?
    """, (token,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def cerrar_sesion(token: str):
    """Elimina el token de sesion de la base de datos."""
    if not token:
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sesiones WHERE token = ?", (token,))
    conn.commit()
    conn.close()


def registrar_pago(
    usuario_id: int,
    plan: str,
    monto_total: float,
    metodo_pago: str,
    marca_tarjeta: str,
    ultimos_4: str,
    titular: str
) -> Dict[str, Any]:
    """Registra una transaccion exitosa y actualiza el plan y estado de suscripcion del usuario."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Desglose de IVA en Mexico (16%)
    subtotal = round(monto_total / 1.16, 2)
    iva = round(monto_total - subtotal, 2)
    
    fecha_ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id_transaccion = f"FP-TXN-{datetime.now().strftime('%Y%m')}-{secrets.randbelow(89999) + 10000}"
    folio_fiscal = f"CFDI-FP-{secrets.randbelow(8999999) + 1000000}"

    cursor.execute("""
    INSERT INTO pagos (
        id_transaccion, usuario_id, plan, monto_subtotal, monto_iva, monto_total,
        moneda, metodo_pago, marca_tarjeta, ultimos_4, titular, estado, folio_fiscal, fecha
    ) VALUES (?, ?, ?, ?, ?, ?, 'MXN', ?, ?, ?, ?, 'Aprobado', ?, ?)
    """, (
        id_transaccion, usuario_id, plan.title(), subtotal, iva, monto_total,
        metodo_pago, marca_tarjeta, ultimos_4, titular, folio_fiscal, fecha_ahora
    ))

    # Actualizar estado del usuario a Activo con su nuevo plan
    cursor.execute("""
    UPDATE usuarios 
    SET plan_activo = ?, estado_pago = 'Activo'
    WHERE id = ?
    """, (plan.title(), usuario_id))

    conn.commit()

    cursor.execute("SELECT * FROM pagos WHERE id_transaccion = ?", (id_transaccion,))
    pago = dict(cursor.fetchone())
    conn.close()
    return pago


def obtener_pagos_usuario(usuario_id: int) -> List[Dict[str, Any]]:
    """Obtiene el historial de transacciones de un usuario."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pagos WHERE usuario_id = ? ORDER BY id DESC", (usuario_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obtener_pago_por_id(id_transaccion: str) -> Optional[Dict[str, Any]]:
    """Obtiene el detalle de un comprobante de pago."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT p.*, u.nombre_gym, u.nombre_dueno, u.email
    FROM pagos p
    JOIN usuarios u ON p.usuario_id = u.id
    WHERE p.id_transaccion = ?
    """, (id_transaccion,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# Inicializar DB al importar
init_db()
