
import os
import pandas as pd
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Rutas relativas
@app.get("/")
def read_root():
    return {"mensaje": "¡Bienvenido a mi aplicación FastAPI!"}

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
    
    # Ruta relativa para el archivo CSV
    archivo_csv = os.path.join(os.path.dirname(__file__), 'archivos', 'movies_release_date.csv')
    
    try:
        df = pd.read_csv(archivo_csv)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    cantidad = df[df['release_date'].dt.month == meses[mes]].shape[0]
    return {"mensaje": f"{cantidad} películas fueron estrenadas en el mes de {mes}"}

@app.get("/score_titulo/{titulo}")
def score_titulo(titulo: str):
    archivo_csv = os.path.join(os.path.dirname(__file__), 'archivos', 'movies_score.csv')
    
    try:
        df = pd.read_csv(archivo_csv)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
    
    film = df[df['title'].str.lower() == titulo.lower()]
    if film.empty:
        raise HTTPException(status_code=404, detail="Película no encontrada.")
    
    titulo = film.iloc[0]['title']
    año = film.iloc[0]['release_year']
    score = film.iloc[0]['popularity']
    return {"mensaje": f"La película {titulo} fue estrenada en el año {año} con un score/popularidad de {score}"}
