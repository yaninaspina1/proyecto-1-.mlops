import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import csr_matrix, hstack

app = FastAPI()

# Definir rutas para los archivos CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VOTES_CSV = os.path.join(BASE_DIR, "archivos", "movies_votes.csv")
RELEASE_DATE_CSV = os.path.join(BASE_DIR, "archivos", "movies_release_date.csv")
SCORE_CSV = os.path.join(BASE_DIR, "archivos", "movies_score.csv")
RECOMMENDATION_CSV = os.path.join(BASE_DIR, "archivos", "recomendacion_api.csv")

# Cargar datasets una sola vez para optimizar rendimiento
try:
    df_votes = pd.read_csv(VOTES_CSV)
    df_release = pd.read_csv(RELEASE_DATE_CSV)
    df_score = pd.read_csv(SCORE_CSV)
    df_recommendation = pd.read_csv(RECOMMENDATION_CSV)

    df_recommendation["id"] = df_recommendation["id"].astype(str)

    # Crear la representación de características combinadas
    tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
    tfidf_matrix = tfidf.fit_transform(df_recommendation["title"].fillna(""))

    # Escalar características numéricas
    scaler = MinMaxScaler()
    df_recommendation[["vote_average", "popularity"]] = scaler.fit_transform(
        df_recommendation[["vote_average", "popularity"]]
    )

    # Convertir características numéricas en matriz dispersa
    numerical_features = csr_matrix(df_recommendation[["vote_average", "popularity"]].values)

    # Unir características textuales y numéricas
    final_features = hstack([tfidf_matrix, numerical_features])

    # Instanciar y entrenar el modelo de vecinos más cercanos
    class ConfigurableNN:
        def __init__(self, metric="cosine", algorithm="auto"):
            self.nn = NearestNeighbors(metric=metric, algorithm=algorithm)
            self.nn.fit(final_features)

        def kneighbors(self, feature, n_neighbors=5):
            return self.nn.kneighbors(feature, n_neighbors=n_neighbors)

    nn = ConfigurableNN()

except Exception as e:
    raise RuntimeError(f"Error al cargar datasets: {str(e)}")


@app.get("/")
def read_root():
    return {"mensaje": "¡Bienvenido a la API de películas!"}


@app.get("/votos_titulo/{titulo}")
def votos_titulo(titulo: str):
    film = df_votes[df_votes['title'].str.lower() == titulo.lower()]
    
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
    dias = {
        'lunes': 0, 'martes': 1, 'miércoles': 2, 'jueves': 3,
        'viernes': 4, 'sábado': 5, 'domingo': 6
    }

    dia = dia.lower()
    if dia not in dias:
        raise HTTPException(status_code=400, detail="Día no válido.")

    df_release['release_date'] = pd.to_datetime(df_release['release_date'], errors='coerce')
    cantidad = df_release[df_release['release_date'].dt.weekday == dias[dia]].shape[0]

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

    df_release['release_date'] = pd.to_datetime(df_release['release_date'], errors='coerce')
    cantidad = df_release[df_release['release_date'].dt.month == meses[mes]].shape[0]

    return {"mensaje": f"{cantidad} películas fueron estrenadas en el mes de {mes}"}


@app.get("/score_titulo/{titulo}")
def score_titulo(titulo: str):
    film = df_score[df_score['title'].str.lower() == titulo.lower()]
    
    if film.empty:
        raise HTTPException(status_code=404, detail="Película no encontrada.")

    return {
        "mensaje": f"La película {film.iloc[0]['title']} fue estrenada en el año {film.iloc[0]['release_year']} "
                   f"con un score/popularidad de {film.iloc[0]['popularity']}"
    }


class RecommendationRequest(BaseModel):
    title: str
    n: int = 5


@app.post("/recommendations/")
def get_recommendations(request: RecommendationRequest):
    try:
        if request.title not in df_recommendation["title"].values:
            raise HTTPException(status_code=404, detail=f"La película '{request.title}' no se encontró en la base de datos.")

        idx = df_recommendation[df_recommendation["title"] == request.title].index[0]
        distances, indices = nn.kneighbors(final_features[idx], n_neighbors=request.n+1)

        recommended_titles = df_recommendation.iloc[indices[0]]['title'].tolist()
        recommended_titles = [t for t in recommended_titles if t != request.title]

        if len(recommended_titles) < request.n:
            extra_titles = df_recommendation[~df_recommendation["title"].isin(recommended_titles + [request.title])]["title"].tolist()
            recommended_titles.extend(extra_titles[:request.n - len(recommended_titles)])

        return {"title": request.title, "recommendations": recommended_titles[:request.n]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
