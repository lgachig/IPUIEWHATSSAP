import sys
import unittest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestVerificarActividad(unittest.TestCase):

    # =================================================================
    # PRUEBA PREGUNTA / APLICACIÓN (Binario: 1 pt o 0 pts)
    # =================================================================
    def test_pregunta_aplicacion_con_actividad(self):
        payload = {
            "actividad": "pregunta_aplicacion",
            "pregunta": "¿Qué enseñanza práctica te deja el pasaje de hoy sobre el amor al prójimo?",
            "respuesta_esperada": "Debemos amar a nuestro prójimo con acciones verdaderas y no solo de palabra.",
            "respuesta_usuario": "Hola grupo buenos días, la enseñanza es que hay que demostrar el amor al prójimo con obras reales y no solo hablando."
        }
        response = client.post("/verificar-actividad", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["veredicto"], "valido")
        self.assertEqual(data["puntos"], 1)
        self.assertGreaterEqual(data["similitud"], 0.68)
        self.assertTrue(len(data["explicacion"]) > 0)

    def test_pregunta_aplicacion_invalida(self):
        payload = {
            "actividad": "pregunta_aplicacion",
            "pregunta": "¿Qué enseñanza práctica te deja el pasaje de hoy sobre el perdón?",
            "respuesta_esperada": "Debemos perdonar a quienes nos ofenden para recibir perdón de Dios.",
            "respuesta_usuario": "Bendiciones, hoy voy a salir de viaje con mi familia."
        }
        response = client.post("/verificar-actividad", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["veredicto"], "invalido")
        self.assertEqual(data["puntos"], 0)

    # =================================================================
    # PRUEBA DETECTIVE BÍBLICO (Binario: 2 pts o 0 pts)
    # =================================================================
    def test_detective_biblico_con_actividad(self):
        payload = {
            "actividad": "detective_biblico",
            "pregunta": "¿Quién fue el personaje que lideró al pueblo a través del Mar Rojo?",
            "respuesta_esperada": "Moisés",
            "respuesta_usuario": "Buenas tardes hermano, la respuesta al reto de hoy es Moisés."
        }
        response = client.post("/verificar-actividad", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["veredicto"], "valido")
        self.assertEqual(data["puntos"], 2)
        self.assertEqual(data["similitud"], 1.0)

    def test_detective_biblico_invalido(self):
        payload = {
            "actividad": "detective_biblico",
            "pregunta": "¿En qué monte recibió Moisés los diez mandamientos?",
            "respuesta_esperada": "Monte Sinaí",
            "respuesta_usuario": "Hola bendiciones creo que fue en el Monte de los Olivos"
        }
        response = client.post("/verificar-actividad", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["veredicto"], "invalido")
        self.assertEqual(data["puntos"], 0)

    # =================================================================
    # PRUEBA RETO 20 SEGUNDOS (Binario: 2 pts o 0 pts por ítems)
    # =================================================================
    def test_reto_20_segundos_con_actividad(self):
        payload = {
            "actividad": "reto_20_segundos",
            "pregunta": "Menciona 3 frutos del Espíritu Santo en el reto de hoy.",
            "respuesta_esperada": "amor, gozo, paz",
            "respuesta_usuario": "Bendiciones a todos, mis respuestas son: amor, gozo y paz"
        }
        response = client.post("/verificar-actividad", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["veredicto"], "valido")
        self.assertEqual(data["puntos"], 2)
        self.assertEqual(data["similitud"], 1.0)

    def test_reto_20_segundos_parcial_valido(self):
        payload = {
            "actividad": "reto_20_segundos",
            "pregunta": "Menciona 3 frutos del Espíritu Santo.",
            "respuesta_esperada": "amor, gozo, paz",
            "respuesta_usuario": "Hola grupo, me acordé de amor y gozo"
        }
        response = client.post("/verificar-actividad", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["veredicto"], "valido")  # 2 de 3 es >= 60%
        self.assertEqual(data["puntos"], 2)

    def test_reto_20_segundos_invalido(self):
        payload = {
            "actividad": "reto_20_segundos",
            "pregunta": "Menciona 3 frutos del Espíritu Santo.",
            "respuesta_esperada": "amor, gozo, paz",
            "respuesta_usuario": "Hola solo recuerdo paciencia"
        }
        response = client.post("/verificar-actividad", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["veredicto"], "invalido")
        self.assertEqual(data["puntos"], 0)

    # =================================================================
    # PRUEBA COMPLETA LA IDEA (Binario: 1 pt o 0 pts)
    # =================================================================
    def test_completa_idea_con_actividad(self):
        payload = {
            "actividad": "completa_idea",
            "pregunta": "Completa el versículo: 'El Señor es mi pastor...'",
            "respuesta_esperada": "nada me faltará",
            "respuesta_usuario": "Amén hermanos, nada me faltará"
        }
        response = client.post("/verificar-actividad", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["veredicto"], "valido")
        self.assertEqual(data["puntos"], 1)

    def test_completa_idea_invalida(self):
        payload = {
            "actividad": "completa_idea",
            "pregunta": "Completa el versículo: 'El Señor es mi pastor...'",
            "respuesta_esperada": "nada me faltará",
            "respuesta_usuario": "Hola bendiciones, todo lo puedo en Cristo que me fortalece"
        }
        response = client.post("/verificar-actividad", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["veredicto"], "invalido")
        self.assertEqual(data["puntos"], 0)

    # =================================================================
    # PRUEBA RETO SORPRESA (Binario: 2 pts o 0 pts)
    # =================================================================
    def test_reto_sorpresa_con_actividad(self):
        payload = {
            "actividad": "reto_sorpresa",
            "pregunta": "Reto Sorpresa: Explica qué hizo Abraham cuando Dios probó su fe.",
            "respuesta_esperada": "Abraham estuvo dispuesto a obedecer a Dios y ofrecer a su hijo Isaac.",
            "respuesta_usuario": "Buenas noches hermanos, la respuesta es que Abraham demostró su fe obedeciendo a Dios al ofrecer a Isaac."
        }
        response = client.post("/verificar-actividad", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["veredicto"], "valido")
        self.assertEqual(data["puntos"], 2)

    # =================================================================
    # PRUEBA PRUEBA DE FUEGO (PONDERADO: 0 a 5 pts)
    # =================================================================
    def test_prueba_fuego_con_actividad(self):
        payload = {
            "actividad": "prueba_fuego",
            "pregunta": "Prueba de fuego: Resume los 3 puntos principales del Éxodo de Israel.",
            "respuesta_esperada": "1. Moisés guió al pueblo\n2. Cruzaron el Mar Rojo\n3. Recibieron la ley en el Sinaí",
            "respuesta_usuario": "Hola bendiciones a todos. 1. Moisés fue quien guió al pueblo de Israel out of Egipto. 2. Milagrosamente cruzaron el Mar Rojo. 3. Dios les entregó la ley en el monte Sinaí."
        }
        response = client.post("/verificar-actividad", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["veredicto"], "valido")
        self.assertEqual(data["puntos"], 5)
        self.assertGreaterEqual(data["similitud"], 0.9)

    def test_prueba_fuego_3_puntos(self):
        payload = {
            "actividad": "prueba_fuego",
            "pregunta": "Prueba de fuego: Resume los 3 puntos principales del Éxodo de Israel.",
            "respuesta_esperada": "1. Moisés guió al pueblo\n2. Cruzaron el Mar Rojo\n3. Recibieron la ley en el Sinaí",
            "respuesta_usuario": "Buenas tardes, Moisés guió al pueblo de Israel y también cruzaron el Mar Rojo."
        }
        response = client.post("/verificar-actividad", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["veredicto"], "valido")
        self.assertIn(data["puntos"], [3, 4])

    # =================================================================
    # PRUEBA ACTIVIDAD INVÁLIDA O FALTANTE
    # =================================================================
    def test_actividad_invalida(self):
        payload = {
            "actividad": "actividad_inexistente",
            "pregunta": "Prueba de actividad no registrada",
            "respuesta_esperada": "Prueba",
            "respuesta_usuario": "Hola"
        }
        response = client.post("/verificar-actividad", json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("no es válido", data["detail"])

    def test_sin_campo_actividad(self):
        payload = {
            "pregunta": "Prueba sin campo actividad",
            "respuesta_esperada": "Prueba",
            "respuesta_usuario": "Hola"
        }
        response = client.post("/verificar-actividad", json=payload)
        self.assertEqual(response.status_code, 422)  # Pydantic validation error para campo requerido


if __name__ == "__main__":
    unittest.main()
