import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import csr_matrix, hstack

app = FastAPI()

# Definir ruta para el archivo CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECOMMENDATION_CSV = os.path.join(BASE_DIR, "archivos", "recomendacion_api.csv")

# Cargar dataset
try:
    df_recommendation = pd.read_csv(RECOMMENDATION_CSV)

    df_recommendation["id"] = df_recommendation["id"].astype(str)
                                                            
    df_recommendation = df_recommendation.dropna(subset=["title"])

    # Procesar características para recomendaciones
    df_recommendation["combined_features"] = df_recommendation["title"].fillna("")

    # Vectorización TF-IDF
    tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
    tfidf_matrix = tfidf.fit_transform(df_recommendation["combined_features"])

    # Escalar características numéricas
    scaler = MinMaxScaler()
    df_recommendation[["vote_average", "popularity"]] = scaler.fit_transform(
        df_recommendation[["vote_average", "popularity"]]
    )

    numerical_features = csr_matrix(df_recommendation[["vote_average", "popularity"]].values)
    final_features = hstack([tfidf_matrix, numerical_features])

    # Configurar modelo de vecinos más cercanos
    class ConfigurableNN:
        def __init__(self, metric="cosine", algorithm="auto"):
            self.nn = NearestNeighbors(metric=metric, algorithm=algorithm)
            self.nn.fit(final_features)

        def kneighbors(self, feature, n_neighbors=5):
            return self.nn.kneighbors(feature, n_neighbors=n_neighbors)

    nn = ConfigurableNN()

except Exception as e:
    raise RuntimeError(f"Error al cargar datasets: {str(e)}")

# Modelos para la API
class RecommendationRequest(BaseModel):
    title: str
    n: int = 5

# Endpoints
@app.get("/")
def read_root():
    return {"mensaje": "¡Bienvenido a la API de películas!"}

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

@app.get("/recomendacion/{titulo}")
def recomendacion(titulo: str):
    try:
        titulo = titulo.lower()
        df_recommendation["title"] = df_recommendation["title"].str.lower()

        if titulo not in df_recommendation["title"].values:
            raise HTTPException(status_code=404, detail=f"La película '{titulo}' no se encontró en la base de datos.")
        
        idx = df_recommendation[df_recommendation["title"] == titulo].index[0]
        distances, indices = nn.kneighbors(final_features[idx], n_neighbors=6)
        recommended_titles = df_recommendation.iloc[indices[0]]['title'].tolist()
        recommended_titles = [t for t in recommended_titles if t != titulo]

        return {"recomendaciones": recommended_titles[:5]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
