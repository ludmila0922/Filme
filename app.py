import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests


load_dotenv()


app = Flask(__name__)

#chaves da API
OMDB_API_KEY = os.getenv('OMDB_API_KEY')
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

@app.route('/')
def home():
    return '''
        <h1>API de Busca de Filmes</h1>
        <form action="/buscar_filme" method="POST">
            <label for="titulo">Título:</label>
            <input type="text" id="titulo" name="titulo" required>
            <br>
            <label for="ano">Ano:</label>
            <input type="text" id="ano" name="ano" required>
            <br>
            <button type="submit">Buscar</button>
        </form>
    '''  

@app.route('/buscar_filme', methods=['POST'])
def buscar_filme():
    titulo = request.form.get('titulo')
    ano = request.form.get('ano')

    if not titulo or not ano:
        return jsonify({"error": "Título e ano são necessários!"}), 400

    # Busca dados da OMDB
    omdb_url = f"http://www.omdbapi.com/?t={titulo}&y={ano}&apikey={OMDB_API_KEY}"
    omdb_response = requests.get(omdb_url)
    omdb_data = omdb_response.json()

    # Caso nao encontre o filme
    if omdb_data.get("Response") == "False":
        return jsonify({"error": "Filme não encontrado na OMDb!"}), 404

    # Busca o filme na TMDb API
    tmdb_url = f"https://api.themoviedb.org/3/search/movie?query={titulo}&year={ano}&api_key={TMDB_API_KEY}"
    tmdb_response = requests.get(tmdb_url)
    tmdb_data = tmdb_response.json()

    # Verifica se o filme foi encontrado
    if tmdb_data['results']:
        movie_id = tmdb_data['results'][0]['id']  # Pega o ID do primeiro filme encontrado
        reviews_url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={TMDB_API_KEY}&language=en-US"
        reviews_response = requests.get(reviews_url)
        reviews_data = reviews_response.json()

        # Pegar as reviews
        reviews = [review['content'] for review in reviews_data['results'][:3]]
    else:
        reviews = ['No reviews available']

    # Resultado do navegador
    resultado = {
        "titulo": omdb_data.get("Title"),
        "ano": omdb_data.get("Year"),
        "sinopse": omdb_data.get("Plot"),
        "reviews": reviews
    }

    return jsonify(resultado)  

if __name__ == '__main__':
    app.run(debug=True)
