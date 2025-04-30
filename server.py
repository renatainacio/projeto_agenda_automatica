
from flask import Flask, request, jsonify
from api_alunos import AlunoAPI

app = Flask(__name__)
api = AlunoAPI()

@app.route('/registrar', methods=['POST'])
def registrar_aluno():
    data = request.get_json()
    nome = data.get('nome')
    telefone = data.get('telefone')
    senha = data.get('senha')
    resultado = api.criar_aluno(nome, telefone, senha)
    return jsonify(resultado)


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    telefone = data.get('telefone')
    senha = data.get('senha')
    resultado = api.login(telefone, senha)
    return jsonify(resultado)

@app.route('/salas', methods=['GET'])
def listar_salas():
    resultado = api.listar_salas()
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
