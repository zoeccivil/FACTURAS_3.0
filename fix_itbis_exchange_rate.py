#!/usr/bin/env python3
"""
fix_itbis_exchange_rate.py

Script para corregir el ITBIS en facturas con moneda extranjera.
El problema: El ITBIS no estaba siendo multiplicado por la tasa de cambio,
quedando en la moneda original en lugar de RD$.

Este script:
1. Busca todas las facturas con moneda diferente a RD$ o DOP
2. Verifica que exchange_rate > 1.0
3. Recalcula itbis_rd = itbis × exchange_rate
4. Actualiza los campos:
   - itbis_original_currency (valor original)
   - itbis_rd (valor convertido)
   - itbis (campo principal, ahora en RD$)
   - total_amount_original_currency (para referencia)
"""

import os
import sys
from typing import Optional

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("ERROR: firebase_admin no está instalado.")
    print("Instale con: pip install firebase-admin")
    sys.exit(1)


def initialize_firebase(cred_path: Optional[str] = None) -> firestore.Client:
    """Inicializa Firebase con las credenciales."""
    if not cred_path:
        # Buscar credenciales en config.json
        import json
        try:
            with open("facturas_config/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                cred_path = config.get("firebase_credentials_path")
        except Exception:
            pass
    
    if not cred_path or not os.path.exists(cred_path):
        print(f"ERROR: No se encontró el archivo de credenciales: {cred_path}")
        print("Por favor, proporcione la ruta al archivo de credenciales de Firebase.")
        sys.exit(1)
    
    # Inicializar Firebase
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    
    return firestore.client()


def fix_invoice_itbis(db: firestore.Client, dry_run: bool = True):
    """
    Corrige el ITBIS en facturas con moneda extranjera.
    
    Args:
        db: Cliente de Firestore
        dry_run: Si es True, solo muestra qué se haría sin modificar datos
    """
    print("=" * 80)
    print("CORRECCIÓN DE ITBIS EN FACTURAS CON MONEDA EXTRANJERA")
    print("=" * 80)
    print()
    
    if dry_run:
        print("⚠️  MODO DRY RUN - No se modificarán datos reales")
        print()
    else:
        print("🔴 MODO ESCRITURA - Los datos SERÁN modificados")
        print()
        response = input("¿Está seguro de continuar? (escriba 'SI' para confirmar): ")
        if response != "SI":
            print("Operación cancelada.")
            return
        print()
    
    # Buscar facturas con moneda extranjera
    invoices_ref = db.collection("invoices")
    
    # Obtener todas las facturas
    all_invoices = list(invoices_ref.stream())
    print(f"📊 Total de facturas en base de datos: {len(all_invoices)}")
    print()
    
    fixed_count = 0
    skipped_count = 0
    error_count = 0
    
    for doc in all_invoices:
        try:
            data = doc.to_dict()
            
            # Obtener campos relevantes
            currency = data.get("currency", "RD$")
            exchange_rate = float(data.get("exchange_rate", 1.0))
            itbis = float(data.get("itbis", 0.0))
            total_amount = float(data.get("total_amount", 0.0))
            invoice_number = data.get("invoice_number", "SIN-NCF")
            third_party = data.get("third_party_name", "Desconocido")
            
            # Verificar si necesita corrección
            # Solo corregir si:
            # 1. Moneda no es RD$ o DOP
            # 2. Exchange rate > 1.0 (indica moneda extranjera)
            # 3. ITBIS > 0
            # 4. No tiene ya el campo itbis_rd o es diferente del esperado
            
            if currency in ["RD$", "DOP", "RD", "DOP$"]:
                skipped_count += 1
                continue
            
            if exchange_rate <= 1.0:
                skipped_count += 1
                continue
            
            if itbis <= 0:
                skipped_count += 1
                continue
            
            # Verificar si ya fue corregido
            itbis_rd_existing = data.get("itbis_rd")
            itbis_original_existing = data.get("itbis_original_currency")
            
            # Calcular el ITBIS esperado en RD$
            expected_itbis_rd = itbis * exchange_rate
            
            # Si itbis_rd ya existe y es correcto, skip
            if itbis_rd_existing is not None:
                if abs(float(itbis_rd_existing) - expected_itbis_rd) < 0.01:
                    skipped_count += 1
                    continue
            
            # Si el ITBIS ya parece estar en RD$ (muy alto para ser USD), skip
            # Heurística: si itbis > total_amount / 5, probablemente ya está en RD$
            if total_amount > 0 and itbis > (total_amount / 5):
                skipped_count += 1
                continue
            
            # Esta factura necesita corrección
            print(f"🔧 Factura a corregir: {invoice_number}")
            print(f"   Tercero: {third_party}")
            print(f"   Moneda: {currency}")
            print(f"   Tasa de cambio: {exchange_rate}")
            print(f"   ITBIS actual: {itbis:,.2f} {currency}")
            print(f"   ITBIS corregido: RD$ {expected_itbis_rd:,.2f}")
            print(f"   Total: {total_amount:,.2f} {currency}")
            
            if not dry_run:
                # Preparar actualización
                update_data = {
                    "itbis_original_currency": itbis,  # Guardar valor original
                    "itbis_rd": expected_itbis_rd,     # Valor convertido a RD$
                    "itbis": expected_itbis_rd,        # Campo principal ahora en RD$
                    "total_amount_original_currency": total_amount,  # Guardar total original
                }
                
                # Actualizar documento
                doc.reference.update(update_data)
                print(f"   ✅ Actualizado en Firestore")
            else:
                print(f"   ℹ️  (No actualizado - modo dry run)")
            
            print()
            fixed_count += 1
            
        except Exception as e:
            print(f"❌ Error procesando factura {doc.id}: {e}")
            error_count += 1
            continue
    
    # Resumen
    print("=" * 80)
    print("RESUMEN DE OPERACIÓN")
    print("=" * 80)
    print(f"Total facturas procesadas: {len(all_invoices)}")
    print(f"✅ Facturas corregidas: {fixed_count}")
    print(f"⏭️  Facturas omitidas (no necesitaban corrección): {skipped_count}")
    print(f"❌ Errores: {error_count}")
    print()
    
    if dry_run and fixed_count > 0:
        print("⚠️  Esto fue un DRY RUN. Para aplicar los cambios, ejecute:")
        print("   python fix_itbis_exchange_rate.py --apply")
        print()


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Corrige el ITBIS en facturas con moneda extranjera"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplicar cambios reales (por defecto solo simula)"
    )
    parser.add_argument(
        "--cred",
        type=str,
        help="Ruta al archivo de credenciales de Firebase"
    )
    
    args = parser.parse_args()
    
    # Inicializar Firebase
    try:
        db = initialize_firebase(args.cred)
        print("✅ Conectado a Firebase exitosamente")
        print()
    except Exception as e:
        print(f"❌ Error conectando a Firebase: {e}")
        sys.exit(1)
    
    # Ejecutar corrección
    fix_invoice_itbis(db, dry_run=not args.apply)


if __name__ == "__main__":
    main()
