from planilha import PlanilhaService
from datetime import datetime, timedelta
import json
import uuid

class AlunoAPI:
    def __init__(self):
        self.planilha = PlanilhaService()

    def login(self, cpf, senha):
        """Realiza o login do aluno e retorna o token."""
        return self.planilha.autenticar_aluno(cpf, senha)

    def _verificar_autenticacao(self, token):
        """Verifica se o token é válido."""
        user = self.planilha.verificar_autenticacao(token)
        if not user:
            return False, "Token inválido ou expirado"
        return True, user

    def listar_atendimentos(self):
        """Lista todas os atendimentos disponíveis."""
        try:
            atendimentos = self.planilha.ler_dados("Atendimentos!A2:H")
            return {
                "sucesso": True,
                "atendimentos": [
                    {
                        "id": a[0],
                        "data": a[1],
                        "horário": a[2],
                        "modalidade": a[3],
                        "fisio": a[4],
                        "duracao": a[5],
                        "maximo_alunos": a[6],
                        "vagas_ocupadas": a[7]
                    }
                    for a in atendimentos
                ]
            }
        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def agendar_atendimento(self, token, id_atendimento):
        """Agenda um novo atendimento para o cliente."""
        sucesso, user = self._verificar_autenticacao(token)
        if not sucesso:
            return {"sucesso": False, "mensagem": user}

        try:
            # Verificar se a sala existe
            atendimentos = self.planilha.ler_dados("Atendimentos!A2:H")
            linha_atendimento = None
            atendimentos_info = None
            for idx, atendimento in enumerate(atendimentos, start=2):
                if atendimento[0] == id_atendimento:
                    atendimentos_info = atendimento
                    linha_atendimento = idx
                    break
            if not atendimentos_info:
                return {"sucesso": False, "mensagem": "Atendimento não encontrado"}
            if atendimentos_info[6] <= atendimentos_info[7]:
                return {"sucesso": False, "mensagem": "Atendimento está lotado"}

            # Verificar se o cliente já tem agendamento para esse atendimento
            agendamentos = self.planilha.ler_dados("Agendamentos!A2:F")
            if any(
                a[1] == user["cpf"] and a[3] == atendimentos_info[0]
                for a in agendamentos
            ):
                return {"sucesso": False, "mensagem": "Aluno já está agendado nesse atendimento"}
            
            # Verificar cadastro aluno
            aluno = self.planilha.ler_dados(f"Alunos!A2:E")
            aluno_info = next((a for a in aluno if a[1] == user["cpf"]), None)
            if not aluno_info:
                return {"sucesso": False, "mensagem": "Aluno não encontrado"}

            limite_atendimentos = int(aluno_info[2])
            
            # Verificar limite de atendimentos por semana
            semana_alvo = datetime.strptime(atendimentos_info[1], "%d/%m/%Y").isocalendar().week

            agendamentos_semana = [
                a for a in agendamentos
                if a[1] == user["cpf"]
                and len(a) >= 5
                and datetime.strptime(a[4], "%d/%m/%Y").isocalendar().week == semana_alvo
            ]
            if len(agendamentos_semana) >= limite_atendimentos:
                return {"sucesso": False, "mensagem": "Limite de atendimentos da semana atingido"}

            # Inserir atendimento
            novo_agendamento = [[
                str(uuid.uuid4()),
                user["cpf"], 
                user["nome"],  
                atendimentos_info[0],
                atendimentos_info[1],
                atendimentos_info[2],
                atendimentos_info[3],
                atendimentos_info[4],
                atendimentos_info[5]
            ]]
            sucesso, mensagem = self.planilha.inserir_dados("Agendamentos!A:I", novo_agendamento)
            
            if sucesso:
                atual = int(atendimentos_info[7]) if len(atendimentos_info) > 7 and atendimentos_info[7].isdigit() else 0
                self.planilha.atualizar_dados(f"Atendimentos!H{linha_atendimento}", [[str(atual + 1)]], "USER_ENTERED")
                return {"sucesso": True, "mensagem": "Atendimento agendado com sucesso"}
            return {"sucesso": False, "mensagem": mensagem}

        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def cancelar_agendamento(self, token, id_agendamento):
        """Cancela um atendimento agendado."""
        sucesso, user = self._verificar_autenticacao(token)
        if not sucesso:
            return {"sucesso": False, "mensagem": user}

        cpf = user["cpf"]
        if not sucesso:
            return {"sucesso": False, "mensagem": cpf}

        try:
            # Buscar agendamento
            agendamentos = self.planilha.ler_dados("Agendamentos!A2:I")
            atendimentos = self.planilha.ler_dados("Atendimentos!A2:H")

            # Procura a linha e a info do agendamento com base no ID
            resultado = next(
                ((i + 2, a) for i, a in enumerate(agendamentos) if a[0] == id_agendamento),
                (None, None)
            )

            linha_agendamento, agendamento_info = resultado
            print("Agendamento a ser deletado: {resultado}")

            if not linha_agendamento:
                return {"sucesso": False, "mensagem": "Agendamento não encontrado"}

            if agendamento_info[1] != cpf:
                return {"sucesso": False, "mensagem": "Agendamento não pertence ao aluno logado"}

            # Procura o atendimento para reduzir o numero de vagas ocupadas
            atendimentos_info = None
            linha_atendimento = None
            for idx, atendimento in enumerate(atendimentos, start=2):
                if atendimento[0] == agendamento_info[3]:
                    atendimentos_info = atendimento
                    linha_atendimento = idx
                    break
            print("Atendimento para reduzir vagas ocupadas: {linha_atendimento}")

            # Remover agendamento
            sucesso, mensagem = self.planilha.remover_dados("Agendamentos!A:I", linha_agendamento, "Agendamentos")
            print("Sucesso remover agendamento: {sucesso}")

            if sucesso:
                atual = int(atendimentos_info[7]) if len(atendimentos_info) > 7 and atendimentos_info[7].isdigit() else 1
                self.planilha.atualizar_dados(f"Atendimentos!H{linha_atendimento}", [[str(atual - 1)]], "USER_ENTERED")
                return {"sucesso": True, "mensagem": "Agendamento cancelada com sucesso"}
            return {"sucesso": False, "mensagem": mensagem}

        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def listar_agendamentos(self, token):
        """Lista todos os agendamentos do cliente."""
        sucesso, user = self._verificar_autenticacao(token)
        if not sucesso:
            return {"sucesso": False, "mensagem": user}

        cpf = user["cpf"]
        if not sucesso:
            return {"sucesso": False, "mensagem": cpf}

        try:
            agendamentos = self.planilha.ler_dados("Agendamentos!A2:I")
            if not agendamentos:
                return {"sucesso": True, "agendamentos": []}
            agendamentos_aluno = [a for a in agendamentos if a[1] == cpf]
            
            return {
                "sucesso": True,
                "agendamentos": [
                    {
                        "id": agendamento[0],
                        "id_atendimento": agendamento[3],
                        "data": agendamento[4],
                        "horario": agendamento[5],
                        "modalidade": agendamento[6],
                        "fisio": agendamento[7],
                        "duração": agendamento[8]
                    }
                    for agendamento in agendamentos_aluno
                ]
            }
        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def atualizar_perfil(self, token, dados):
        """Atualiza os dados do perfil do aluno."""
        sucesso, cpf = self._verificar_autenticacao(token)
        if not sucesso:
            return {"sucesso": False, "mensagem": cpf}

        try:
            # Buscar aluno
            alunos = self.planilha.ler_dados("Alunos!A2:E")
            aluno_index = None
            
            for i, aluno in enumerate(alunos):
                if aluno[0] == cpf:
                    aluno_index = i + 2
                    break

            if not aluno_index:
                return {"sucesso": False, "mensagem": "Aluno não encontrado"}

            # Atualizar dados
            dados_atualizados = [
                cpf,
                dados.get("nome", alunos[aluno_index-2][1]),
                dados.get("cpf", alunos[aluno_index-2][2]),
                dados.get("atendimentos_semana", alunos[aluno_index-2][3]),
                alunos[aluno_index-2][4]  # Manter a senha atual
            ]

            sucesso, mensagem = self.planilha.atualizar_dados(
                f"Alunos!A{aluno_index}:E{aluno_index}",
                [dados_atualizados]
            )
            
            if sucesso:
                return {"sucesso": True, "mensagem": "Perfil atualizado com sucesso"}
            return {"sucesso": False, "mensagem": mensagem}

        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)} 