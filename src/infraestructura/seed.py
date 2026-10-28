"""Datos iniciales de demostracion para OptiFiber FTTH."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.infraestructura.modelos import (
    CategoriaModel,
    ClienteModel,
    EtiquetaModel,
    ProductoModel,
)

CATEGORIAS = [
    ("Fibra Optica", "Cables drop, ADSS y soluciones de fibra optica."),
    ("Equipos ONT/ONU", "Equipos terminales para clientes FTTH."),
    ("Accesorios de Instalacion", "Rosetas, conectores, pigtails e insumos."),
    ("Herramientas", "Equipos para instalacion y mantenimiento de red."),
    ("Redes y Conectividad", "Switches, routers y cableado estructurado."),
]

ETIQUETAS = [
    "hogar",
    "empresa",
    "mayorista",
    "promocion",
    "instalacion",
    "equipo",
    "fibra",
]

PRODUCTOS = [
    {
        "sku": "FIB-001",
        "nombre": "Cable drop 1 hilo 100 m",
        "descripcion": "Cable de fibra optica para acometida de clientes residenciales.",
        "precio": 85.0,
        "stock": 40,
        "categoria": "Fibra Optica",
        "etiquetas": ["fibra", "instalacion", "hogar"],
    },
    {
        "sku": "FIB-002",
        "nombre": "Cable ADSS 12 hilos 500 m",
        "descripcion": "Cable autosoportado para tendido aereo y redes troncales.",
        "precio": 890.0,
        "stock": 8,
        "categoria": "Fibra Optica",
        "etiquetas": ["fibra", "empresa", "mayorista"],
    },
    {
        "sku": "ONT-001",
        "nombre": "ONT GPON WiFi 5 dual band",
        "descripcion": "Equipo terminal optico para planes residenciales de 100 a 500 Mbps.",
        "precio": 220.0,
        "stock": 25,
        "categoria": "Equipos ONT/ONU",
        "etiquetas": ["equipo", "hogar", "empresa"],
    },
    {
        "sku": "ONT-002",
        "nombre": "ONU XPON WiFi 6",
        "descripcion": "Equipo terminal WiFi 6 para planes de alta velocidad.",
        "precio": 310.0,
        "stock": 15,
        "categoria": "Equipos ONT/ONU",
        "etiquetas": ["equipo", "hogar", "promocion"],
    },
    {
        "sku": "ACC-001",
        "nombre": "Roseta optica 2 puertos",
        "descripcion": "Caja terminal de pared para instalacion interna.",
        "precio": 18.0,
        "stock": 80,
        "categoria": "Accesorios de Instalacion",
        "etiquetas": ["instalacion", "hogar"],
    },
    {
        "sku": "ACC-002",
        "nombre": "Conector SC/APC",
        "descripcion": "Conector de campo para fibra optica monomodo.",
        "precio": 4.5,
        "stock": 300,
        "categoria": "Accesorios de Instalacion",
        "etiquetas": ["instalacion", "fibra"],
    },
    {
        "sku": "HER-001",
        "nombre": "Fusionadora de fibra optica",
        "descripcion": "Equipo de fusion por arco electrico para instalaciones profesionales.",
        "precio": 4200.0,
        "stock": 3,
        "categoria": "Herramientas",
        "etiquetas": ["equipo", "instalacion", "empresa"],
    },
    {
        "sku": "HER-002",
        "nombre": "OTDR portatil",
        "descripcion": "Reflectometro optico para diagnostico y certificacion de redes.",
        "precio": 6800.0,
        "stock": 2,
        "categoria": "Herramientas",
        "etiquetas": ["equipo", "empresa"],
    },
    {
        "sku": "RED-001",
        "nombre": "Switch Gigabit 8 puertos",
        "descripcion": "Switch administrable para redes empresariales y nodos.",
        "precio": 260.0,
        "stock": 12,
        "categoria": "Redes y Conectividad",
        "etiquetas": ["equipo", "empresa"],
    },
    {
        "sku": "RED-002",
        "nombre": "Router MikroTik hEX",
        "descripcion": "Router Gigabit de 5 puertos para pequenas y medianas redes.",
        "precio": 390.0,
        "stock": 10,
        "categoria": "Redes y Conectividad",
        "etiquetas": ["equipo", "empresa"],
    },
]

CLIENTES = [
    {
        "nombre": "Ana Quispe",
        "documento": "12345678",
        "telefono": "987654321",
        "email": "ana.quispe@example.com",
        "direccion": "Av. Los Alamos 123, Lima",
    },
    {
        "nombre": "Luis Ramos",
        "documento": "87654321",
        "telefono": "912345678",
        "email": "luis.ramos@example.com",
        "direccion": "Jr. Puno 456, Arequipa",
    },
    {
        "nombre": "Maria Huaman",
        "documento": "45678912",
        "telefono": "998877665",
        "email": "maria.huaman@example.com",
        "direccion": "Calle Real 789, Huancayo",
    },
    {
        "nombre": "Inversiones Andinas SAC",
        "documento": "20512345678",
        "telefono": "014567890",
        "email": "compras@andinas.example.com",
        "direccion": "Av. Javier Prado 1500, Lima",
    },
]


def base_ya_sembrada(session: Session) -> bool:
    """Indica si ya existen datos para evitar duplicarlos."""
    return bool(session.scalar(select(func.count(CategoriaModel.id))))


def sembrar_datos(session: Session) -> None:
    """Carga categorias, etiquetas, productos y clientes de demostracion."""
    if base_ya_sembrada(session):
        return

    categorias = {
        nombre: CategoriaModel(nombre=nombre, descripcion=descripcion)
        for nombre, descripcion in CATEGORIAS
    }
    etiquetas = {nombre: EtiquetaModel(nombre=nombre) for nombre in ETIQUETAS}

    session.add_all(categorias.values())
    session.add_all(etiquetas.values())
    session.flush()

    for datos in PRODUCTOS:
        producto = ProductoModel(
            sku=datos["sku"],
            nombre=datos["nombre"],
            descripcion=datos["descripcion"],
            precio=datos["precio"],
            stock=datos["stock"],
            categoria=categorias[datos["categoria"]],
            etiquetas=[etiquetas[nombre] for nombre in datos["etiquetas"]],
        )
        session.add(producto)

    for datos in CLIENTES:
        session.add(ClienteModel(**datos))

    session.commit()
