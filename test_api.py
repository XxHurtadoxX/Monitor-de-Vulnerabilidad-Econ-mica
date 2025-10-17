"""
Script de prueba para la API de Vulnerabilidad Económica
Prueba todos los endpoints de la API

Uso: python test_api.py
"""

import requests
import json

# Configuración
API_URL = "http://localhost:8000"

def print_section(title):
    """Imprime una sección con formato"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_root():
    """Prueba el endpoint raíz"""
    print_section("TEST 1: Endpoint Raíz (/)")
    
    try:
        response = requests.get(f"{API_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_health():
    """Prueba el health check"""
    print_section("TEST 2: Health Check (/health)")
    
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_questionnaire():
    """Prueba obtener el cuestionario"""
    print_section("TEST 3: Obtener Cuestionario (/questionnaire)")
    
    try:
        response = requests.get(f"{API_URL}/questionnaire")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Título: {data.get('titulo')}")
        print(f"Secciones: {len(data.get('secciones', []))}")
        print(f"Total preguntas: {sum(len(s.get('preguntas', [])) for s in data.get('secciones', []))}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_predict_caso_vulnerable():
    """Prueba predicción - Caso vulnerable"""
    print_section("TEST 4: Predicción - Caso Probable Vulnerable (/predict)")
    
    # Usuario con características de vulnerabilidad
    usuario_vulnerable = {
        "edad": 28,
        "sexo": "mujer",
        "departamento": 13,  # Bolívar
        "nivel_educativo": "primaria",
        "años_educacion": 5,
        "tiene_salud": True,
        "tipo_salud": "subsidiado",
        "requirio_atencion_medica": True,
        "gasto_salud_ultimos_30_dias": 120000,
        "empleo_formal": False,
        "tipo_vivienda": "cuarto",
        "tenencia_vivienda": "arriendo",
        "num_cuartos": 2,
        "num_personas_hogar": 6,
        "material_pisos": "tierra",
        "tiene_acueducto": False,
        "tiene_alcantarillado": False,
        "tiene_gas": False,
        "tiene_energia": True,
        "gasto_energia_mensual": 300000,
        "tiene_recoleccion_basuras": False,
        "tiene_hijos_menores": True,
        "num_menores_hogar": 3
    }
    
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=usuario_vulnerable,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"\n📊 RESULTADO:")
            print(f"  Es vulnerable: {'SÍ ⚠️' if resultado['es_vulnerable'] else 'NO ✓'}")
            print(f"  Probabilidad: {resultado['probabilidad_vulnerable']:.2%}")
            print(f"  Nivel de riesgo: {resultado['nivel_riesgo'].upper()}")
            print(f"  Umbral usado: {resultado['umbral_usado']:.4f}")
            print(f"\n💬 Mensaje:")
            print(f"  {resultado['mensaje']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_predict_caso_no_vulnerable():
    """Prueba predicción - Caso no vulnerable"""
    print_section("TEST 5: Predicción - Caso Probable No Vulnerable (/predict)")
    
    # Usuario con características de estabilidad
    usuario_estable = {
        "edad": 38,
        "sexo": "hombre",
        "departamento": 11,  # Bogotá
        "nivel_educativo": "superior",
        "años_educacion": 16,
        "tiene_salud": True,
        "tipo_salud": "contributivo",
        "requirio_atencion_medica": False,
        "gasto_salud_ultimos_30_dias": 0,
        "empleo_formal": True,
        "tipo_vivienda": "apartamento",
        "tenencia_vivienda": "propia",
        "num_cuartos": 4,
        "num_personas_hogar": 3,
        "material_pisos": "baldosa",
        "tiene_acueducto": True,
        "tiene_alcantarillado": True,
        "tiene_gas": True,
        "tiene_energia": True,
        "gasto_energia_mensual": 600000,
        "tiene_recoleccion_basuras": True,
        "tiene_hijos_menores": True,
        "num_menores_hogar": 1
    }
    
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=usuario_estable,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"\n📊 RESULTADO:")
            print(f"  Es vulnerable: {'SÍ ⚠️' if resultado['es_vulnerable'] else 'NO ✓'}")
            print(f"  Probabilidad: {resultado['probabilidad_vulnerable']:.2%}")
            print(f"  Nivel de riesgo: {resultado['nivel_riesgo'].upper()}")
            print(f"  Umbral usado: {resultado['umbral_usado']:.4f}")
            print(f"\n💬 Mensaje:")
            print(f"  {resultado['mensaje']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_predict_minimo():
    """Prueba predicción con datos mínimos (todos defaults)"""
    print_section("TEST 6: Predicción - Datos Mínimos (Defaults) (/predict)")
    
    # Solo enviar un par de campos, el resto usará defaults
    usuario_minimo = {
        "edad": 25,
        "sexo": "mujer"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=usuario_minimo,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"\n📊 RESULTADO:")
            print(f"  Es vulnerable: {'SÍ ⚠️' if resultado['es_vulnerable'] else 'NO ✓'}")
            print(f"  Probabilidad: {resultado['probabilidad_vulnerable']:.2%}")
            print(f"  Nivel de riesgo: {resultado['nivel_riesgo'].upper()}")
            print(f"\n💬 Mensaje:")
            print(f"  {resultado['mensaje']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*80)
    print("🧪 PRUEBAS DE LA API DE VULNERABILIDAD ECONÓMICA")
    print("="*80)
    print(f"\nAPI URL: {API_URL}")
    print("\n⚠️  Asegúrate de que la API esté corriendo en {API_URL}")
    input("\nPresiona ENTER para comenzar las pruebas...")
    
    # Ejecutar pruebas
    results = []
    results.append(("Endpoint Raíz", test_root()))
    results.append(("Health Check", test_health()))
    results.append(("Cuestionario", test_questionnaire()))
    results.append(("Predicción Vulnerable", test_predict_caso_vulnerable()))
    results.append(("Predicción No Vulnerable", test_predict_caso_no_vulnerable()))
    results.append(("Predicción Mínima", test_predict_minimo()))
    
    # Resumen
    print_section("RESUMEN DE PRUEBAS")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    print(f"\n{'='*80}")
    print(f"  Total: {total} pruebas | Pasadas: {passed} | Fallidas: {total - passed}")
    print(f"{'='*80}\n")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")

if __name__ == "__main__":
    main()

