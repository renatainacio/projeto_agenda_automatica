from planilha import PlanilhaService
import hashlib
import secrets

class AlunoService:
    def __init__(self):
        self.planilha = PlanilhaService()

    def _criptografar_senha(self, senha):
        """Criptografa a senha usando SHA-256 com salt."""
        salt = secrets.token_hex(16)
        senha_hash = hashlib.sha256((senha + salt).encode()).hexdigest()
        return f"{salt}${senha_hash}"

    def listar_alunos(self):
        """Lista todos os alunos cadastrados."""
        try:
            alunos = self.planilha.ler_dados("Alunos!A2:D")
            return {
                "sucesso": True,
                "alunos": [
                    {
                        "nome": aluno[0],
                        "cpf": aluno[1],
                        "aulas_semana": aluno[2]
                    }
                    for aluno in alunos
                ]
            }
        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def buscar_aluno(self, cpf):
        """Busca um aluno específico pelo cpf."""
        try:
            alunos = self.planilha.ler_dados("Alunos!A2:D")
            aluno = next((a for a in alunos if a[1] == cpf), None)
            
            if aluno:
                return {
                    "sucesso": True,
                    "aluno": {
                        "nome": aluno[0],
                        "cpf": aluno[1],
                        "aulas_semana": aluno[2]
                    }
                }
            return {"sucesso": False, "mensagem": "Aluno não encontrado"}
        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def criar_aluno(self, nome, cpf, aulas_semana, senha):
        """Cria um novo aluno."""
        try:
            # Validar dados
            if not nome or not cpf or not aulas_semana or not senha:
                return {"sucesso": False, "mensagem": "Todos os campos são obrigatórios"}

            # Verificar se o cpf já está cadastrado
            alunos = self.planilha.ler_dados("Alunos!A2:D")
            if any(a[1] == cpf for a in alunos):
                return {"sucesso": False, "mensagem": "CPF já cadastrado"}

            # Criptografar senha
            senha_hash = self._criptografar_senha(senha)

            # Preparar dados
            novo_aluno = [[nome, cpf, str(aulas_semana), senha_hash]]
            
            # Inserir na planilha
            sucesso, mensagem = self.planilha.inserir_dados("Alunos!A:D", novo_aluno)
            
            if sucesso:
                return {"sucesso": True, "mensagem": "Aluno cadastrado com sucesso"}
            return {"sucesso": False, "mensagem": mensagem}

        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def editar_aluno(self, cpf, dados):
        """Edita os dados de um aluno existente."""
        try:
            # Buscar aluno
            alunos = self.planilha.ler_dados("Alunos!A2:D")
            aluno_index = None
            
            for i, aluno in enumerate(alunos):
                if aluno[1] == cpf:
                    aluno_index = i + 2
                    break

            if not aluno_index:
                return {"sucesso": False, "mensagem": "Aluno não encontrado"}

            # Preparar dados atualizados
            dados_atualizados = [
                dados.get("nome", alunos[aluno_index-2][0]),
                dados.get("cpf", alunos[aluno_index-2][1]),
                dados.get("aulas_semana", alunos[aluno_index-2][2]),
                alunos[aluno_index-2][3]  # Manter a senha atual
            ]

            # Se uma nova senha foi fornecida, criptografá-la
            if "senha" in dados:
                dados_atualizados[3] = self._criptografar_senha(dados["senha"])

            # Atualizar na planilha
            sucesso, mensagem = self.planilha.atualizar_dados(
                f"Alunos!A{aluno_index}:D{aluno_index}",
                [dados_atualizados]
            )
            
            if sucesso:
                return {"sucesso": True, "mensagem": "Aluno atualizado com sucesso"}
            return {"sucesso": False, "mensagem": mensagem}

        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def excluir_aluno(self, telefone):
        """Exclui um aluno."""
        try:
            # Buscar aluno
            alunos = self.planilha.ler_dados("Alunos!A2:D")
            aluno_index = None
            
            for i, aluno in enumerate(alunos):
                if aluno[1] == telefone:
                    aluno_index = i + 2
                    break

            if not aluno_index:
                return {"sucesso": False, "mensagem": "Aluno não encontrado"}

            # Remover aluno
            sucesso, mensagem = self.planilha.remover_dados("Alunos!A:D", aluno_index, "Alunos")
            
            if sucesso:
                return {"sucesso": True, "mensagem": "Aluno excluído com sucesso"}
            return {"sucesso": False, "mensagem": mensagem}

        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)} 