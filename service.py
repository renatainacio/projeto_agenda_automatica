from planilha import PlanilhaService
import hashlib
import secrets

class Service:
    def __init__(self):
        self.planilha = PlanilhaService()

    def _criptografar_senha(self, senha):
        """Criptografa a senha usando SHA-256 com salt."""
        salt = secrets.token_hex(16)
        senha_hash = hashlib.sha256((senha + salt).encode()).hexdigest()
        return f"{salt}${senha_hash}"

    def listar_clientes(self):
        """Lista todos os clientes cadastrados."""
        try:
            clientes = self.planilha.ler_dados("Clientes!A2:D")
            return {
                "sucesso": True,
                "clientes": [
                    {
                        "nome": cliente[0],
                        "cpf": cliente[1],
                        "atendimentos_semana": cliente[2]
                    }
                    for cliente in clientes
                ]
            }
        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def buscar_cliente(self, cpf):
        """Busca um cliente específico pelo cpf."""
        try:
            clientes = self.planilha.ler_dados("Clientes!A2:D")
            cliente = next((a for a in clientes if a[1] == cpf), None)
            
            if cliente:
                return {
                    "sucesso": True,
                    "cliente": {
                        "nome": cliente[0],
                        "cpf": cliente[1],
                        "atendimentos_semana": cliente[2]
                    }
                }
            return {"sucesso": False, "mensagem": "Cliente não encontrado"}
        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def criar_cliente(self, nome, cpf, atendimentos_semana, senha):
        """Cria um novo cliente."""
        try:
            # Validar dados
            if not nome or not cpf or not atendimentos_semana or not senha:
                return {"sucesso": False, "mensagem": "Todos os campos são obrigatórios"}

            # Verificar se o cpf já está cadastrado
            clientes = self.planilha.ler_dados("Clientes!A2:D")
            if any(a[1] == cpf for a in clientes):
                return {"sucesso": False, "mensagem": "CPF já cadastrado"}

            # Criptografar senha
            senha_hash = self._criptografar_senha(senha)

            # Preparar dados
            novo_cliente = [[nome, cpf, str(atendimentos_semana), senha_hash]]
            
            # Inserir na planilha
            sucesso, mensagem = self.planilha.inserir_dados("Clientes!A:D", novo_cliente)
            
            if sucesso:
                return {"sucesso": True, "mensagem": "Cliente cadastrado com sucesso"}
            return {"sucesso": False, "mensagem": mensagem}

        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def editar_cliente(self, cpf, dados):
        """Edita os dados de um cliente existente."""
        try:
            # Buscar cliente
            clientes = self.planilha.ler_dados("Clientes!A2:D")
            cliente_index = None
            
            for i, cliente in enumerate(clientes):
                if cliente[1] == cpf:
                    cliente_index = i + 2
                    break

            if not cliente_index:
                return {"sucesso": False, "mensagem": "Cliente não encontrado"}

            # Preparar dados atualizados
            dados_atualizados = [
                dados.get("nome", clientes[cliente_index-2][0]),
                dados.get("cpf", clientes[cliente_index-2][1]),
                dados.get("atendimentos_semana", clientes[cliente_index-2][2]),
                clientes[cliente_index-2][3]  # Manter a senha atual
            ]

            # Se uma nova senha foi fornecida, criptografá-la
            if "senha" in dados:
                dados_atualizados[3] = self._criptografar_senha(dados["senha"])

            # Atualizar na planilha
            sucesso, mensagem = self.planilha.atualizar_dados(
                f"Clientes!A{cliente_index}:D{cliente_index}",
                [dados_atualizados]
            )
            
            if sucesso:
                return {"sucesso": True, "mensagem": "Cliente atualizado com sucesso"}
            return {"sucesso": False, "mensagem": mensagem}

        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def excluir_cliente(self, cpf):
        """Exclui um cliente."""
        try:
            # Buscar cliente
            clientes = self.planilha.ler_dados("Clientes!A2:D")
            cliente_index = None
            
            for i, cliente in enumerate(clientes):
                if cliente[1] == cpf:
                    cliente_index = i + 2
                    break

            if not cliente_index:
                return {"sucesso": False, "mensagem": "Cliente não encontrado"}

            # Remover cliente
            sucesso, mensagem = self.planilha.remover_dados("Clientes!A:D", cliente_index, "Clientes")
            
            if sucesso:
                return {"sucesso": True, "mensagem": "Cliente excluído com sucesso"}
            return {"sucesso": False, "mensagem": mensagem}

        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)} 