import os
import pandas as pd
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Definir rutas relativas para los archivos CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VOTES_CSV = os.path.join(BASE_DIR, "archivos", "movies_votes.csv")
RELEASE_DATE_CSV = os.path.join(BASE_DIR, "archivos", "movies_release_date.csv")
SCORE_CSV = os.path.join(BASE_DIR, "archivos", "movies_score.csv")
RELEASE_DATE_CSV = os.path.join(BASE_DIR, "archivos", "movies_release_date.csv")
@app.get("/")
def read_root():
    return {"mensaje": "¡Bienvenido a mi aplicación FastAPI!"}

@app.get("/votos_titulo/{titulo}")
def votos_titulo(titulo: str):
    try:
        df = pd.read_csv(VOTES_CSV)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar el archivo: {str(e)}")

    film = df[df['title'].str.lower() == titulo.lower()]
    
    if film.empty:
        raise HTTPException(status_code=404, detail="Película no encontrada.")

    votos = film.iloc[0]['vote_count']
    promedio = film.iloc[0]['vote_average']

    if votos < 2000:
        return {"mensaje": "La película no cumple la condición de tener al menos 2000 valoraciones."}

    return {
        "mensaje": f"La película {titulo} fue estrenada en el año {film.iloc[0]['release_year']}. "
                   f"La misma cuenta con un total de {votos} valoraciones, con un promedio de {promedio}."
    }

@app.get("/cantidad_filmaciones_dia/{dia}")
def cantidad_filmaciones_dia(dia: str):
    # Mapeo de días en español a índices de pandas (lunes = 0, domingo = 6)
    dias = {
        'lunes': 0, 'martes': 1, 'miércoles': 2, 'jueves': 3,
        'viernes': 4, 'sábado': 5, 'domingo': 6
    }

    dia = dia.lower()
    if dia not in dias:
        raise HTTPException(status_code=400, detail="Día no válido.")

    try:
        df = pd.read_csv(RELEASE_DATE_CSV)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar el archivo: {str(e)}")

    # Convertir la fecha a formato datetime
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

    # Filtrar por el día de la semana usando el índice numérico
    cantidad = df[df['release_date'].dt.weekday == dias[dia]].shape[0]

    return {"mensaje": f"{cantidad} películas fueron estrenadas en {dia}"}

@app.get("/cantidad_filmaciones_mes/{mes}")
def cantidad_filmaciones_mes(mes: str):
    meses = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    
    mes = mes.lower()
    if mes not in meses:
        raise HTTPException(status_code=400, detail="Mes no válido.")

    try:
        df = pd.read_csv(RELEASE_DATE_CSV)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar el archivo: {str(e)}")

    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    cantidad = df[df['release_date'].dt.month == meses[mes]].shape[0]

    return {"mensaje": f"{cantidad} películas fueron estrenadas en el mes de {mes}"}

@app.get("/score_titulo/{titulo}")
def score_titulo(titulo: str):
    try:
        df = pd.read_csv(SCORE_CSV)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar el archivo: {str(e)}")

    film = df[df['title'].str.lower() == titulo.lower()]
    
    if film.empty:
        raise HTTPException(status_code=404, detail="Película no encontrada.")

    titulo = film.iloc[0]['title']
    año = film.iloc[0]['release_year']
    score = film.iloc[0]['popularity']

    return {"mensaje": f"La película {titulo} fue estrenada en el año {año} con un score/popularidad de {score}"}
