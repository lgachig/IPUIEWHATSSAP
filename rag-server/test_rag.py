import os
import requests

def obtener_url():
    if os.getenv("RAG_URL"):
        return os.getenv("RAG_URL")
    try:
        r = requests.get("http://rag:8000/salud", timeout=2)
        if r.status_code == 200:
            return "http://rag:8000/verificar-lectura"
    except Exception:
        pass
    return "http://127.0.0.1:8000/verificar-lectura"

URL = obtener_url()


PRUEBAS = [
    {
        "nombre": "Caso 1: Versículo Válido de Hoy (1 Pedro 4:1 - Texto escrito)",
        "payload": {
            "telefono": "+573001234567",
            "texto": "Puesto que Cristo ha padecido por nosotros en la carne, vosotros también armaos del mismo pensamiento",
            "fecha": "2026-09-02",
        },
        "veredicto_esperado": "valido",
        "coincide_esperado": True,
    },
    {
        "nombre": "Caso 2: Cita Bíblica Directa Válida de Hoy ('1 Pedro 4:1')",
        "payload": {
            "telefono": "+573001234567",
            "texto": "1 Pedro 4:1",
            "fecha": "2026-09-02",
        },
        "veredicto_esperado": "valido",
        "coincide_esperado": True,
    },
    {
        "nombre": "Caso 3: Cita Bíblica Directa de OTRO DÍA ('Génesis 1:1')",
        "payload": {
            "telefono": "+573001234567",
            "texto": "Génesis 1:1",
            "fecha": "2026-09-02",
        },
        "veredicto_esperado": "invalido",
        "coincide_esperado": False,
    },
    {
        "nombre": "Caso 4: Versículo Bíblico de OTRO DÍA (Texto escrito)",
        "payload": {
            "telefono": "+573001234567",
            "texto": "En el principio creo Dios los cielos y la tierra",
            "fecha": "2026-09-02",
        },
        "veredicto_esperado": "invalido",
        "coincide_esperado": False,
    },
    {
        "nombre": "Caso 5: Mensaje No Relacionado (Texto no bíblico)",
        "payload": {
            "telefono": "+573001234567",
            "texto": "Hola grupo bendiciones hoy no alcancé a hacer la lectura",
            "fecha": "2026-09-02",
        },
        "veredicto_esperado": "invalido",
        "coincide_esperado": False,
    },
    {
        "nombre": "Caso 6: Prueba Dinámica sin 'fecha' (Usa la fecha de HOY automáticamente - 'Salmos 15:1')",
        "payload": {
            "telefono": "+573001234567",
            "texto": "Salmos 15:1",
        },
        "veredicto_esperado": "valido",
        "coincide_esperado": True,
    },
    {
        "nombre": "Caso 7: Mensaje con Saludo/Intro + Cita Bíblica Válida de Hoy",
        "payload": {
            "telefono": "+573001234567",
            "texto": "buenos dias este es el versiculo que me llamo la atencion, 1 Pedro 4:1",
            "fecha": "2026-09-02",
        },
        "veredicto_esperado": "valido",
        "coincide_esperado": True,
    },
    {
        "nombre": "Caso 8: Mensaje con Saludo/Intro + Versículo Completo Escrito de Hoy",
        "payload": {
            "telefono": "+573001234567",
            "texto": "buenos dias este es el versiculo que me llamo la atencion, Puesto que Cristo ha padecido por nosotros en la carne, vosotros también armaos del mismo pensamiento",
            "fecha": "2026-09-02",
        },
        "veredicto_esperado": "valido",
        "coincide_esperado": True,
    },
    {
        "nombre": "Caso 9: Mensaje con Saludo/Intro + Cita Bíblica de OTRO DÍA",
        "payload": {
            "telefono": "+573001234567",
            "texto": "buenos dias este es el versiculo que me llamo la atencion, Génesis 1:1",
            "fecha": "2026-09-02",
        },
        "veredicto_esperado": "invalido",
        "coincide_esperado": False,
    },
    {
        "nombre": "Caso 10: Mensaje con Saludo/Intro + Versículo Escrito de OTRO DÍA",
        "payload": {
            "telefono": "+573001234567",
            "texto": "buenos dias este es el versiculo que me llamo la atencion, En el principio creo Dios los cielos y la tierra",
            "fecha": "2026-09-02",
        },
        "veredicto_esperado": "invalido",
        "coincide_esperado": False,
    },
]



def ejecutar_pruebas():
    print("==================================================")
    print("   EJECUTANDO PRUEBAS UNITARIAS DEL MOTOR RAG")
    print("==================================================\n")

    exitos = 0
    for p in PRUEBAS:
        print(f"➜ Ejecutando: {p['nombre']}")
        try:
            r = requests.post(URL, json=p["payload"], timeout=10)
            if r.status_code != 200:
                print(f"  ❌ ERROR HTTP {r.status_code}: {r.text}")
                continue

            data = r.json()
            valido_veredicto = data.get("veredicto") == p["veredicto_esperado"]
            valido_coincide = data.get("coincide_con_hoy") == p["coincide_esperado"]

            if valido_veredicto and valido_coincide:
                print(f"  ✅ PASÓ - Veredicto: {data['veredicto']} | Método: {data.get('metodo')} | Match: {data.get('match')}")
                exitos += 1
            else:
                print(f"  ❌ FALLÓ - Obtenido: {data}")
        except Exception as e:
            print(f"  ❌ ERROR DE CONEXIÓN: {e}")
        print("-" * 50)

    print(f"\nResumen: {exitos}/{len(PRUEBAS)} pruebas pasaron correctamente.")


if __name__ == "__main__":
    ejecutar_pruebas()
