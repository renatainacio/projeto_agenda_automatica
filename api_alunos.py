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

    def listar_aulas(self):
        """Lista todas as salas disponíveis."""
        try:
            aulas = self.planilha.ler_dados("Aulas!A2:H")
            return {
                "sucesso": True,
                "aulas": [
                    {
                        "id": aula[0],
                        "data": aula[1],
                        "horário": aula[2],
                        "modalidade": aula[3],
                        "professor": aula[4],
                        "duracao": aula[5],
                        "maximo_alunos": aula[6],
                        "vagas_ocupadas": aula[7]
                    }
                    for aula in aulas
                ]
            }
        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def agendar_aula(self, token, id_aula):
        """Agenda uma nova aula para o aluno."""
        sucesso, user = self._verificar_autenticacao(token)
        if not sucesso:
            return {"sucesso": False, "mensagem": user}

        try:
            # Verificar se a sala existe
            aulas = self.planilha.ler_dados("Aulas!A2:H")
            linha_aula = None
            aulas_info = None
            for idx, aula in enumerate(aulas, start=2):
                if aula[0] == id_aula:
                    aulas_info = aula
                    linha_aula = idx
                    break
            if not aulas_info:
                return {"sucesso": False, "mensagem": "Sala não encontrada"}
            if aulas_info[6] <= aulas_info[7]:
                return {"sucesso": False, "mensagem": "Aula está lotada"}

            # Verificar se o aluno já tem aulas agendadas para essa aula
            agendamentos = self.planilha.ler_dados("Agendamentos!A2:F")
            if any(
                a[1] == user["cpf"] and a[3] == aulas_info[0]
                for a in agendamentos
            ):
                return {"sucesso": False, "mensagem": "Aluno já está inscrito nessa aula"}
            
            # Verificar cadastro aluno
            aluno = self.planilha.ler_dados(f"Alunos!A2:E")
            aluno_info = next((a for a in aluno if a[1] == user["cpf"]), None)
            if not aluno_info:
                return {"sucesso": False, "mensagem": "Aluno não encontrado"}

            limite_aulas = int(aluno_info[2])
            
            # Verificar limite de aulas por semana
            semana_alvo = datetime.strptime(aulas_info[1], "%d/%m/%Y").isocalendar().week

            agendamentos_semana = [
                a for a in agendamentos
                if a[1] == user["cpf"]
                and len(a) >= 5
                and datetime.strptime(a[4], "%d/%m/%Y").isocalendar().week == semana_alvo
            ]
            if len(agendamentos_semana) >= limite_aulas:
                return {"sucesso": False, "mensagem": "Limite de aulas da semana atingido"}

            # Verificar disponibilidade do horário na sala
            # aulas_horario = [a for a in aulas if a[1] == data and a[2] == horario and a[3] == sala_nome]
            # if aulas_horario:
            #     return {"sucesso": False, "mensagem": "Horário já ocupado nesta sala"}


            # Inserir aula
            nova_aula = [[
                str(uuid.uuid4()),
                user["cpf"], 
                user["nome"],  
                aulas_info[0],
                aulas_info[1],
                aulas_info[2],
                aulas_info[3],
                aulas_info[4],
                aulas_info[5]
            ]]
            sucesso, mensagem = self.planilha.inserir_dados("Agendamentos!A:I", nova_aula)
            
            if sucesso:
                atual = int(aulas_info[7]) if len(aulas_info) > 7 and aulas_info[7].isdigit() else 0
                self.planilha.atualizar_dados(f"Aulas!H{linha_aula}", [[str(atual + 1)]], "USER_ENTERED")
                return {"sucesso": True, "mensagem": "Aula agendada com sucesso"}
            return {"sucesso": False, "mensagem": mensagem}

        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def cancelar_agendamento(self, token, id_agendamento):
        """Cancela uma aula agendada."""
        sucesso, user = self._verificar_autenticacao(token)
        if not sucesso:
            return {"sucesso": False, "mensagem": user}

        cpf = user["cpf"]
        if not sucesso:
            return {"sucesso": False, "mensagem": cpf}

        try:
            # Buscar aula
            agendamentos = self.planilha.ler_dados("Agendamentos!A2:I")
            aulas = self.planilha.ler_dados("Aulas!A2:H")

            # Procura a linha e a info do agendamento com base no ID
            resultado = next(
                ((i + 2, a) for i, a in enumerate(agendamentos) if a[0] == id_agendamento),
                (None, None)
            )

            linha_agendamento, agendamento_info = resultado

            if not linha_agendamento:
                return {"sucesso": False, "mensagem": "Agendamento não encontrado"}

            if agendamento_info[1] != cpf:
                return {"sucesso": False, "mensagem": "Agendamento não pertence ao aluno logado"}

            # Procura a aula para reduzir o numero de vagas ocupadas

            aulas_info = None
            linha_aula = None
            for idx, aula in enumerate(aulas, start=2):
                if aula[0] == agendamento_info[3]:
                    aulas_info = aula
                    linha_aula = idx
                    break

            # Remover aula
            sucesso, mensagem = self.planilha.remover_dados("Agendamentos!A:I", linha_agendamento, "Agendamentos")

            if sucesso:
                atual = int(aulas_info[7]) if len(aulas_info) > 7 and aulas_info[7].isdigit() else 1
                self.planilha.atualizar_dados(f"Aulas!H{linha_aula}", [[str(atual - 1)]], "USER_ENTERED")
                return {"sucesso": True, "mensagem": "Agendamento cancelada com sucesso"}
            return {"sucesso": False, "mensagem": mensagem}

        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def listar_agendamentos(self, token):
        """Lista todas as aulas do aluno."""
        sucesso, user = self._verificar_autenticacao(token)
        if not sucesso:
            return {"sucesso": False, "mensagem": user}

        cpf = user["cpf"]
        if not sucesso:
            return {"sucesso": False, "mensagem": cpf}

        try:
            aulas = self.planilha.ler_dados("Agendamentos!A2:I")
            if not aulas:
                return {"sucesso": True, "aulas": []}
            aulas_aluno = [a for a in aulas if a[1] == cpf]
            
            return {
                "sucesso": True,
                "aulas": [
                    {
                        "id": aula[0],
                        "id_aula": aula[3],
                        "data": aula[4],
                        "horario": aula[5],
                        "modalidade": aula[6],
                        "professor": aula[7],
                        "duração": aula[8]
                    }
                    for aula in aulas_aluno
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
                dados.get("aulas_semana", alunos[aluno_index-2][3]),
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