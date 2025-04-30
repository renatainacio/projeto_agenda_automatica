from planilha import PlanilhaService
from datetime import datetime, timedelta
import json

class AlunoAPI:
    def __init__(self):
        self.planilha = PlanilhaService()

    def login(self, telefone, senha):
        """Realiza o login do aluno e retorna o token."""
        return self.planilha.autenticar_aluno(telefone, senha)

    def _verificar_autenticacao(self, token):
        """Verifica se o token é válido."""
        cpf = self.planilha.verificar_autenticacao(token)
        if not cpf:
            return False, "Token inválido ou expirado"
        return True, cpf

    def listar_salas(self):
        """Lista todas as salas disponíveis."""
        try:
            salas = self.planilha.ler_dados("Salas!A2:B")
            return {
                "sucesso": True,
                "salas": [
                    {
                        "nome": sala[0],
                        "professor": sala[1]
                    }
                    for sala in salas
                ]
            }
        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def agendar_aula(self, token, data, horario, sala_nome):
        """Agenda uma nova aula para o aluno."""
        sucesso, cpf = self._verificar_autenticacao(token)
        if not sucesso:
            return {"sucesso": False, "mensagem": cpf}

        try:
            # Verificar se a sala existe
            salas = self.planilha.ler_dados("Salas!A2:B")
            sala_info = next((s for s in salas if s[0] == sala_nome), None)
            if not sala_info:
                return {"sucesso": False, "mensagem": "Sala não encontrada"}

            # Verificar se o aluno já tem aulas agendadas para o dia
            aulas = self.planilha.ler_dados("Aulas!A2:F")
            aulas_dia = [a for a in aulas if a[0] == cpf and a[1] == data]
            
            # Verificar limite de aulas por semana
            aluno = self.planilha.ler_dados(f"Alunos!A2:E")
            aluno_info = next((a for a in aluno if a[0] == cpf), None)
            if not aluno_info:
                return {"sucesso": False, "mensagem": "Aluno não encontrado"}

            limite_aulas = int(aluno_info[3])
            
            # Contar aulas da semana
            data_obj = datetime.strptime(data, "%d/%m/%Y")
            inicio_semana = data_obj - timedelta(days=data_obj.weekday())
            fim_semana = inicio_semana + timedelta(days=6)
            
            aulas_semana = [a for a in aulas if a[0] == cpf and 
                          inicio_semana <= datetime.strptime(a[1], "%d/%m/%Y") <= fim_semana]
            
            if len(aulas_semana) >= limite_aulas:
                return {"sucesso": False, "mensagem": "Limite de aulas da semana atingido"}

            # Verificar disponibilidade do horário na sala
            aulas_horario = [a for a in aulas if a[1] == data and a[2] == horario and a[3] == sala_nome]
            if aulas_horario:
                return {"sucesso": False, "mensagem": "Horário já ocupado nesta sala"}

            # Inserir aula
            nova_aula = [[cpf, data, horario, sala_nome, "Agendada", sala_info[1]]]  # Adiciona o professor
            sucesso, mensagem = self.planilha.inserir_dados("Aulas!A:F", nova_aula)
            
            if sucesso:
                return {"sucesso": True, "mensagem": "Aula agendada com sucesso"}
            return {"sucesso": False, "mensagem": mensagem}

        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def cancelar_aula(self, token, data, horario, sala_nome):
        """Cancela uma aula agendada."""
        sucesso, cpf = self._verificar_autenticacao(token)
        if not sucesso:
            return {"sucesso": False, "mensagem": cpf}

        try:
            # Buscar aula
            aulas = self.planilha.ler_dados("Aulas!A2:F")
            aula_index = None
            
            for i, aula in enumerate(aulas):
                if aula[0] == cpf and aula[1] == data and aula[2] == horario and aula[3] == sala_nome:
                    aula_index = i + 2  # +2 porque a contagem começa em 1 e pula o cabeçalho
                    break

            if not aula_index:
                return {"sucesso": False, "mensagem": "Aula não encontrada"}

            # Remover aula
            sucesso, mensagem = self.planilha.remover_dados("Aulas!A:F", aula_index, "Aulas")
            
            if sucesso:
                return {"sucesso": True, "mensagem": "Aula cancelada com sucesso"}
            return {"sucesso": False, "mensagem": mensagem}

        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def listar_aulas(self, token):
        """Lista todas as aulas do aluno."""
        sucesso, cpf = self._verificar_autenticacao(token)
        if not sucesso:
            return {"sucesso": False, "mensagem": cpf}

        try:
            aulas = self.planilha.ler_dados("Aulas!A2:F")
            if not aulas:
                return {"sucesso": True, "aulas": []}
                
            aulas_aluno = [a for a in aulas if a[0] == cpf]
            
            return {
                "sucesso": True,
                "aulas": [
                    {
                        "data": aula[1],
                        "horario": aula[2],
                        "sala": aula[3],
                        "status": aula[4],
                        "professor": aula[5] if len(aula) > 5 else ""
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
                dados.get("telefone", alunos[aluno_index-2][2]),
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