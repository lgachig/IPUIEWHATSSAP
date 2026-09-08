from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.actividades import verificar_actividad
from app.matching import verificar_lectura
from app.supabase_client import guardar_verificacion

app = FastAPI(title="MODO ÍNTEGRO - Motor RAG de verificación bíblica")


class SolicitudVerificacion(BaseModel):
    telefono: str
    texto: str
    fecha: str | None = None  # 'YYYY-MM-DD', si no se manda se usa hoy


class RespuestaVerificacion(BaseModel):
    veredicto: str            # 'valido' | 'invalido' | 'revision_manual'
    metodo: str                # 'exacto' | 'embedding' | 'llm_fallback' | 'sin_lectura_programada'
    similitud: float | None = None
    match: str | None = None
    coincide_con_hoy: bool | None = None


class SolicitudActividad(BaseModel):
    actividad: str
    pregunta: str
    respuesta_esperada: str
    respuesta_usuario: str


class RespuestaActividad(BaseModel):
    veredicto: str            # 'valido' | 'invalido'
    similitud: float
    puntos: int
    explicacion: str


@app.get("/salud")
def salud():
    return {"status": "ok"}


@app.post("/verificar-lectura", response_model=RespuestaVerificacion)
def verificar_lectura_endpoint(solicitud: SolicitudVerificacion):
    fecha_iso = solicitud.fecha or date.today().isoformat()
    resultado = verificar_lectura(solicitud.texto, fecha_iso)

    # Log propio del servidor, independiente de lo que n8n decida registrar.
    guardar_verificacion(
        {
            "telefono": solicitud.telefono,
            "fecha_mensaje": fecha_iso,
            "texto_recibido": solicitud.texto,
            "metodo": resultado["metodo"],
            "similitud": resultado.get("similitud"),
            "coincide_con_hoy": resultado.get("coincide_con_hoy"),
            "veredicto": resultado["veredicto"],
        }
    )

    return RespuestaVerificacion(
        veredicto=resultado["veredicto"],
        metodo=resultado["metodo"],
        similitud=resultado.get("similitud"),
        match=resultado.get("match"),
        coincide_con_hoy=resultado.get("coincide_con_hoy"),
    )


@app.post("/verificar-actividad", response_model=RespuestaActividad)
def verificar_actividad_endpoint(solicitud: SolicitudActividad):
    try:
        resultado = verificar_actividad(
            actividad=solicitud.actividad,
            pregunta=solicitud.pregunta,
            respuesta_esperada=solicitud.respuesta_esperada,
            respuesta_usuario=solicitud.respuesta_usuario,
        )
        return RespuestaActividad(
            veredicto=resultado["veredicto"],
            similitud=resultado["similitud"],
            puntos=resultado["puntos"],
            explicacion=resultado["explicacion"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

