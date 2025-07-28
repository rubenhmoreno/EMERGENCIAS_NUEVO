#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Emergencias Villa Allende
Modelos de Base de Datos - Versión Independiente

IMPORTANTE: Este archivo ya no se usa directamente.
Los modelos ahora están integrados en app.py para evitar importaciones circulares.

Este archivo se mantiene por compatibilidad, pero los modelos reales
están definidos en app.py
"""

# Este archivo ya no es necesario pero se mantiene por compatibilidad
# Los modelos están ahora definidos directamente en app.py

print("⚠️ AVISO: models.py ya no se usa. Los modelos están en app.py")
print("   Si ve este mensaje, actualice sus imports para usar app.py directamente")

# Si alguien importa desde aquí, redirigir a app.py
try:
    from app import Usuario, Persona, Llamado, Guardia, Configuracion, db
    print("✅ Modelos importados desde app.py correctamente")
except ImportError:
    print("❌ Error: No se pudieron importar modelos desde app.py")
    print("   Verifique que app.py existe y está configurado correctamente")