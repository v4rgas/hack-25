#!/usr/bin/env python3
"""
Script para probar el flujo de detección de fraudes.
Acepta un tender_id como argumento de línea de comandos.

Uso:
    python test_fraud_detection.py --tender-id 4831-19-LE20
    python test_fraud_detection.py -t 4831-19-LE20 --model google/gemini-2.5-flash-preview-09-2025
    python test_fraud_detection.py -t 4831-19-LE20 --verbose
"""
import argparse
import sys
import os
from datetime import datetime
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from app.workflow import FraudDetectionWorkflow


def print_separator(char="=", length=70):
    """Print a separator line"""
    print(char * length)


def print_header(text):
    """Print a formatted header"""
    print_separator()
    print(f" {text}")
    print_separator()


def format_task_result(task_result, verbose=False):
    """Format task investigation result for display"""
    status_emoji = "✅" if task_result.validation_passed else "❌"

    print(f"\n{status_emoji} Tarea: {task_result.task_code} - {task_result.task_name}")
    print(f"   Estado: {'PASÓ validación' if task_result.validation_passed else 'FALLÓ validación'}")

    if task_result.findings:
        print(f"\n   📋 Hallazgos encontrados: {len(task_result.findings)}")
        for i, finding in enumerate(task_result.findings, 1):
            confidence_emoji = "🔴" if finding.confidence >= 0.7 else "🟡" if finding.confidence >= 0.5 else "⚪"
            print(f"\n   {i}. {confidence_emoji} {finding.anomaly_name}")
            print(f"      Confianza: {finding.confidence:.2f}")

            if verbose:
                print(f"      Descripción: {finding.description}")

                if finding.evidence:
                    print(f"      Evidencia:")
                    for evidence in finding.evidence[:3]:  # Mostrar primeras 3
                        print(f"        • {evidence}")
                    if len(finding.evidence) > 3:
                        print(f"        ... y {len(finding.evidence) - 3} más")

                if finding.affected_documents:
                    print(f"      Documentos afectados: {', '.join(finding.affected_documents)}")
    else:
        print(f"   ℹ️  No se encontraron hallazgos")

    print()


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Prueba el flujo de detección de fraudes en licitaciones públicas chilenas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s --tender-id 4831-19-LE20
  %(prog)s -t 4831-19-LE20 --verbose
  %(prog)s -t 4831-19-LE20 --model google/gemini-2.5-flash-preview-09-2025
  %(prog)s -t 4831-19-LE20 --temperature 0.5 -v
        """
    )

    parser.add_argument(
        "-t", "--tender-id",
        required=True,
        help="ID de la licitación a investigar (ej: 4831-19-LE20)"
    )

    parser.add_argument(
        "-m", "--model",
        default="google/gemini-2.5-flash-preview-09-2025",
        help="Modelo de IA a usar (default: google/gemini-2.5-flash-preview-09-2025)"
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperatura del modelo (0.0-1.0, default: 0.7)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Mostrar información detallada de los hallazgos"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Mostrar resultados en formato JSON"
    )

    args = parser.parse_args()

    # Validar temperatura
    if not 0.0 <= args.temperature <= 1.0:
        print("❌ Error: La temperatura debe estar entre 0.0 y 1.0")
        sys.exit(1)

    # Print header
    if not args.json:
        print_header(f"🔍 DETECCIÓN DE FRAUDES - {args.tender_id}")
        print(f"\n⚙️  Configuración:")
        print(f"   • Tender ID: {args.tender_id}")
        print(f"   • Modelo: {args.model}")
        print(f"   • Temperatura: {args.temperature}")
        print(f"   • Modo verbose: {'Sí' if args.verbose else 'No'}")
        print(f"   • Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # Initialize workflow
        if not args.json:
            print("🚀 Inicializando workflow...\n")

        workflow = FraudDetectionWorkflow(
            ranking_model=args.model,
            detection_model=args.model,
            temperature=args.temperature
        )

        # Run workflow
        if not args.json:
            print("📊 Ejecutando investigación...")
            print("   1️⃣  Obteniendo datos de la licitación...")
            print("   2️⃣  Cargando tareas de investigación...")
            print("   3️⃣  Ranking de prioridades (seleccionando top 5)...")
            print("   4️⃣  Investigando tareas en paralelo...")
            print("   5️⃣  Agregando resultados...\n")

        result = workflow.run(args.tender_id)

        # Display results
        if args.json:
            # JSON output for programmatic use
            json_result = {
                "tender_id": args.tender_id,
                "workflow_summary": result.get("workflow_summary", ""),
                "tasks_investigated": len(result.get("tasks_by_id", [])),
                "tasks_failed": sum(1 for t in result.get("tasks_by_id", []) if not t.validation_passed),
                "total_findings": sum(len(t.findings) for t in result.get("tasks_by_id", [])),
                "errors": result.get("errors", []),
                "tasks": [
                    {
                        "task_code": t.task_code,
                        "task_description": t.task_description,
                        "severity": t.severity,
                        "validation_passed": t.validation_passed,
                        "findings": [
                            {
                                "anomaly_name": f.anomaly_name,
                                "description": f.description,
                                "confidence": f.confidence,
                                "evidence": f.evidence,
                                "affected_documents": f.affected_documents
                            }
                            for f in t.findings
                        ]
                    }
                    for t in result.get("tasks_by_id", [])
                ]
            }
            print(json.dumps(json_result, indent=2, ensure_ascii=False))
        else:
            # Human-readable output
            print_header("📋 RESULTADOS DE LA INVESTIGACIÓN")

            # Summary
            print(f"\n{result.get('workflow_summary', 'No hay resumen disponible')}\n")

            # Tender info
            if result.get("tender_response"):
                tender = result["tender_response"]
                print_separator("-")
                print(f"📄 Información de la licitación:")
                print(f"   • Nombre: {tender.name}")
                print(f"   • Comprador: {tender.tenderPurchaseData.organization.name}")
                print(f"   • Código: {tender.tenderId}")
                print(f"   • Fecha publicación: {tender.TenderDate.publish.strftime('%Y-%m-%d')}")
                print(f"   • Fecha cierre: {tender.TenderDate.close.strftime('%Y-%m-%d')}")
                if tender.type:
                    print(f"   • Tipo: {tender.type.description}")
                    print(f"   • Moneda: {tender.type.currency}")
                print_separator("-")

            # Task results
            tasks_by_id = result.get("tasks_by_id", [])
            if tasks_by_id:
                print(f"\n🔎 Tareas investigadas: {len(tasks_by_id)}")
                failed_tasks = [t for t in tasks_by_id if not t.validation_passed]
                total_findings = sum(len(t.findings) for t in tasks_by_id)

                print(f"   • Tareas que fallaron validación: {len(failed_tasks)}")
                print(f"   • Total de hallazgos: {total_findings}")

                # Display each task
                for task_result in tasks_by_id:
                    format_task_result(task_result, verbose=args.verbose)

            # Errors
            if result.get("errors"):
                print_separator("-")
                print(f"\n⚠️  Errores encontrados durante la ejecución:")
                for error in result["errors"]:
                    print(f"   • {error}")

            # Footer
            print_separator()
            print(f"✅ Investigación completada - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print_separator()

            # Summary stats
            if tasks_by_id:
                high_confidence_findings = sum(
                    1 for t in tasks_by_id
                    for f in t.findings
                    if f.confidence >= 0.7
                )

                if high_confidence_findings > 0:
                    print(f"\n🚨 Hallazgos de alta confianza (≥0.7): {high_confidence_findings}")
                else:
                    print(f"\n✅ No se encontraron hallazgos de alta confianza")

    except KeyboardInterrupt:
        print("\n\n⚠️  Ejecución interrumpida por el usuario")
        sys.exit(130)

    except Exception as e:
        if args.json:
            error_result = {
                "error": str(e),
                "tender_id": args.tender_id,
                "success": False
            }
            print(json.dumps(error_result, indent=2, ensure_ascii=False))
        else:
            print(f"\n❌ Error durante la ejecución: {e}")
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
