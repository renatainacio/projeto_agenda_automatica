
from flask import Flask, request, jsonify
from api_alunos import AlunoAPI
from aluno_service import AlunoService

app = Flask(__name__)
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

@app.route('/agendar', methods=['POST'])
def agendar():
    data = request.get_json()
    token = data.get('token')
    data_aula = data.get('data')
    horario = data.get('horario')
    sala_nome = data.get('sala_nome')
    resultado = api.agendar_aula(token, data_aula, horario, sala_nome)
    return jsonify(resultado)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
