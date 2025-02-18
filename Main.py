<<<<<<< HEAD
import os
import pandas as pd
from fastapi import FastAPI, HTTPException
=======

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import hstack, csr_matrix
from sklearn.neighbors import NearestNeighbors
>>>>>>> c323769 (Guardando cambios antes del pull)

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

<<<<<<< HEAD
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
=======


# Definir modelos para la API
class RecommendationRequest(BaseModel):
    title: str
    n: int = 5

# Clase para configurar el modelo de recomendación basado en Nearest Neighbors
class ConfigurableNN:
    def __init__(self, metric="cosine", algorithm="auto"):
        self.nn = NearestNeighbors(metric=metric, algorithm=algorithm)

    def fit(self, features):
        self.nn.fit(features)

    def kneighbors(self, feature, n_neighbors=5):
        return self.nn.kneighbors(feature, n_neighbors=n_neighbors)

# Cargar y procesar los datasets
movies_api = pd.read_csv("C:\\Users\\yanin\\OneDrive\\Desktop\\Nueva carpeta\\archivos\\recomendacion_api.csv")
movies_api["id"] = movies_api["id"].astype(str)

# Crear la representación de características combinadas
tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
tfidf_matrix = tfidf.fit_transform(movies_api["title"].fillna(""))

# Escalar características numéricas
scaler = MinMaxScaler()
movies_api[["vote_average", "popularity"]] = scaler.fit_transform(movies_api[["vote_average", "popularity"]])

# Convertir características numéricas en matriz dispersa
numerical_features = csr_matrix(movies_api[["vote_average", "popularity"]].values)

# Unir características textuales y numéricas
final_features = hstack([tfidf_matrix, numerical_features])

# Instanciar y entrenar el modelo de vecinos más cercanos
nn = ConfigurableNN(metric="cosine", algorithm="auto")
nn.fit(final_features)

# Función para encontrar películas similares
def find_similar_movies(title, n=5):
    if title not in movies_api["title"].values:
        raise ValueError(f"La película '{title}' no se encontró en la base de datos.")
    
    idx = movies_api[movies_api["title"] == title].index[0]
    distances, indices = nn.kneighbors(final_features[idx], n_neighbors=n+1)
    recommended_titles = movies_api.iloc[indices[0]]['title'].tolist()
    recommended_titles = [t for t in recommended_titles if t != title]
    
    # Rellenar con títulos adicionales si faltan recomendaciones
    if len(recommended_titles) < n:
        extra_titles = movies_api[~movies_api["title"].isin(recommended_titles + [title])]["title"].tolist()
        recommended_titles.extend(extra_titles[:n - len(recommended_titles)])
    
    return recommended_titles[:n]

# Endpoints de la API
@app.get("/")
def root():
    return {"message": "Bienvenido a la API de recomendación de películas."}

@app.post("/recommendations/")
def get_recommendations(request: RecommendationRequest):
    try:
        if not request.title:
            raise HTTPException(status_code=400, detail="El título de la película es obligatorio.")
        recommendations = find_similar_movies(request.title, request.n)
        return {"title": request.title, "recommendations": recommendations}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
>>>>>>> c323769 (Guardando cambios antes del pull)
