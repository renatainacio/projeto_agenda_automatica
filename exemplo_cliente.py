from service import Service

def main():
    # Criar instância do serviço
    service = Service()
    
    # Exemplo de criação de cliente
    print("\n=== Criando Cliente ===")
    resultado_criacao = service.criar_cliente(
        nome="João Silva",
        cpf="99999999999",
        atendimentos_semana=2,
        senha="senha123"
    )
    print(f"Resultado da criação: {resultado_criacao}")
    
    # Exemplo de listagem de clientes
    print("\n=== Listando Clientes ===")
    resultado_listagem = service.listar_clientes()
    print(f"Resultado da listagem: {resultado_listagem}")
    
    # Exemplo de busca de cliente
    print("\n=== Buscando Cliente ===")
    resultado_busca = service.buscar_cliente("99999999999")
    print(f"Resultado da busca: {resultado_busca}")
    
    # Exemplo de edição de cliente
    print("\n=== Editando Cliente ===")
    resultado_edicao = service.editar_cliente(
        cpf="99999999999",
        dados={
            "nome": "João Silva Atualizado",
            "atendimentos_semana": 3,
            "senha": "nova_senha123"
        }
    )
    print(f"Resultado da edição: {resultado_edicao}")

if __name__ == "__main__":
    main() 