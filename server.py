
from flask import Flask, request, jsonify
from flask_cors import CORS
from api_alunos import AlunoAPI
from aluno_service import AlunoService

app = Flask(__name__)
CORS(app)
api = AlunoAPI()
service = AlunoService()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    telefone = data.get('telefone')
    senha = data.get('senha')
    resultado = api.login(telefone, senha)
    return jsonify(resultado)

@app.route('/cadastro', methods=['POST'])
def cadastro():
    data = request.get_json()
    nome = data.get('nome')
    telefone = data.get('telefone')
    senha = data.get('senha')
    aulas_semana = data.get('aulas_semana')
    resultado = service.criar_aluno(
        nome = nome,
        telefone = telefone,
        aulas_semana = aulas_semana,
        senha = senha
    )
    return jsonify(resultado)


@app.route('/aulas', methods=['GET'])
def listar_aulas():
    resultado = api.listar_aulas()
    return jsonify(resultado)


def getToken(request):
    token = request.headers.get("Authorization")

    if token and token.startswith("Bearer "):
        return token[7:]  # remove "Bearer "
    return None


@app.route('/agendamentos', methods=['POST'])
def agendar():
    data = request.get_json()
    token = getToken(request)

    id_aula = data.get('id_aula')
    resultado = api.agendar_aula(token, id_aula)
    return jsonify(resultado)

@app.route('/agendamentos', methods=['GET'])
def listar_agendamentos():
    token = getToken(request)
    resultado = api.listar_agendamentos(token)
    return jsonify(resultado)

@app.route('/agendamentos/<id_agendamento>', methods=['DELETE'])
def cancelar_agendamento(id_agendamento):
    token = getToken(request)
    resultado = api.cancelar_agendamento(token, id_agendamento)
    return jsonify(resultado)

    
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
