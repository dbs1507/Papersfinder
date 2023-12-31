from flask import Flask, render_template, request, jsonify
from pytrends.request import TrendReq

import trendsInterface
import googleScholar

import json
import requests
import os

from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)


def custom_filter(results):
    # Filtrar resultados que possuem 'cited_by'
    filtered_results = [
        result for result in results if 'cited_by' in result['inline_links']]
    # Ordenar os resultados filtrados pelo número de citações
    sorted_results = sorted(
        filtered_results, key=lambda x: x['inline_links']['cited_by']['total'], reverse=True)
    # Adicionar resultados com 0 citações
    for result in results:
        if 'cited_by' not in result['inline_links']:
            sorted_results.append(result)
    return sorted_results


# Registrar o filtro personalizado
app.add_template_filter(custom_filter)


@app.route('/')
def index():
    return render_template('index.html')


@app.route(f'/buscar', methods=['GET'])
def buscar():
    dado = request.args.get('dado')
    page = request.args.get('page', 1)

    if not dado or dado.strip() == "":
        alerta = "Pesquisa vazia, digite alguma palavra"
        return render_template('index.html', alerta=alerta)

    consultas_relacionadas = trendsInterface.obter_dados_completos(dado)
    totalResults, paginationResponses = googleScholar.obter_dados_google(
        dado, page)

    if consultas_relacionadas is None:
        alerta = "Não há dados de pesquisa suficientes para exibir o gráfico de interesse"
        consultas_relacionadas = "undefined"  # Defina como "undefined" se for None
        return render_template('resultado.html', consultas_relacionadas=consultas_relacionadas, google_scholar=paginationResponses, dado=dado, totalResults=totalResults, alerta=alerta)

    consultas_relacionadas = consultas_relacionadas.reset_index()
    consultas_relacionadas = consultas_relacionadas.values.tolist()
    return render_template('resultado.html', consultas_relacionadas=list(consultas_relacionadas), google_scholar=paginationResponses, dado=dado, totalResults=totalResults)


@app.route('/citacoes', methods=['GET'])
def citacoes():
    dado = request.args.get('dado')
    artigo = request.args.get("artigo")
    page = request.args.get('page', 1)
    id = request.args.get('serpapi_scholar_link')

    paginationResponses = googleScholar.citacoes(dado, page, artigo, id)

    if 'organic_results' not in paginationResponses:
        alerta = 'Não foi possível encontrar as informações'
        return render_template('citacoes.html', alerta=alerta)
    else:
        return render_template('citacoes.html', citacoes=paginationResponses['organic_results'], dado=dado, artigo=artigo)

    # return render_template('citacoes.html', citacoes=paginationResponses, dado=dado, artigo=artigo)


@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    senha = request.form.get('senha')

    user_id = auth.login(email, senha)
    if user_id:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Erro ao fazer login'})


# def citacoes(pagina):
#     dado = request.args.get('dado')
#     page = request.args.get('page', 1)
#     serpapi_scholar_link = request.args.get('serpapi_scholar_link')

#     params = {
#         "engine": "google_scholar",
#         "q": dado,
#         "api_key": os.getenv("API_KEY"),
#         "start": (page - 1) * 10
#     }

#     paginationResponses = []

#     paginationResponse = requests.get(
#         f"https://serpapi.com/search.json?cites={serpapi_scholar_link}", params=params).json()

#     paginationResponseData = {
#         "organic_results": paginationResponse["organic_results"],
#         "page": str(pagina)
#     }
#     paginationResponses.append(paginationResponseData)
#     totalResults = paginationResponse["search_information"]["total_results"]

#     return render_template('citacoes.html', response_content=paginationResponse)

    # link_cited_article = []

    # organic_results = response['organic_results']
    # for cited in organic_results:
    #     link_cited_article.append(cited['inline_links']
    #                               ['cited_by']['serpapi_scholar_link'])

    # cited_article = []
    # for citacoes in link_cited_article:
    #     request_cited = requests.get(citacoes, params=params).json()
    #     # print(request_cited)
    #     cited_article.append(request_cited['organic_results'])

    # return render_template('citacoes.html', response_content=cited_article)

if __name__ == '__main__':
    app.run(debug=True)
