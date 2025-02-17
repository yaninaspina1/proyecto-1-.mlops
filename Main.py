
from fastapi import FastAPI, HTTPException
import pandas as pd





app = FastAPI()
@app.head("/")
async def read_root():
    return {}
@app.get("/")
def read_root():
    return {"mensaje": "¡Bienvenido a mi aplicación FastAPI!"}

# Función para convertir el mes y el día a español
meses = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}

dias = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']

@app.get("/cantidad_filmaciones_mes/{mes}")
def cantidad_filmaciones_mes(mes: str):
    mes = mes.lower()
    if mes not in meses:
        raise HTTPException(status_code=400, detail="Mes no válido.")
    
    mes_num = meses[mes]
    df = pd.read_csv("C:\\Users\\yanin\\OneDrive\\Desktop\\Nueva carpeta\\archivos\\movies_release_date.csv")
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    cantidad = df[df['release_date'].dt.month == mes_num].shape[0]
    return {"mensaje": f"{cantidad} cantidad de películas fueron estrenadas en el mes de {mes}"}

@app.get("/cantidad_filmaciones_dia/{dia}")
def cantidad_filmaciones_dia(dia: str):
    dia = dia.lower()
    if dia not in dias:
        raise HTTPException(status_code=400, detail="Día no válido.")
    
    df = pd.read_csv("C:\\Users\\yanin\\OneDrive\\Desktop\\Nueva carpeta\\archivos\\movies_release_date.csv")
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    cantidad = df[df['release_date'].dt.day_name(locale='es_ES').str.lower() == dia].shape[0]
    return {"mensaje": f"{cantidad} cantidad de películas fueron estrenadas en los días {dia}"}

@app.get("/score_titulo/{titulo}")
def score_titulo(titulo: str):
    df = pd.read_csv("C:\\Users\\yanin\\OneDrive\\Desktop\\Nueva carpeta\\archivos\\movies_score.csv")
    film = df[df['title'].str.lower() == titulo.lower()]
    if film.empty:
        raise HTTPException(status_code=404, detail="Película no encontrada.")
    
    titulo = film.iloc[0]['title']
    año = film.iloc[0]['release_year']
    score = film.iloc[0]['popularity']
    return {"mensaje": f"La película {titulo} fue estrenada en el año {año} con un score/popularidad de {score}"}

@app.get("/votos_titulo/{titulo}")
def votos_titulo(titulo: str):
    df = pd.read_csv("C:\\Users\\yanin\\OneDrive\\Desktop\\Nueva carpeta\\archivos\\movies_votes.csv")
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

