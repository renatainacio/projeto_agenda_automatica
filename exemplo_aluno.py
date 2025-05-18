from aluno_service import AlunoService

def main():
    # Criar instância do serviço
    aluno_service = AlunoService()
    
    # Exemplo de criação de aluno
    print("\n=== Criando Aluno ===")
    resultado_criacao = aluno_service.criar_aluno(
        nome="João Silva",
        cpf="99999999999",
        atendimentos_semana=2,
        senha="senha123"
    )
    print(f"Resultado da criação: {resultado_criacao}")
    
    # Exemplo de listagem de alunos
    print("\n=== Listando Alunos ===")
    resultado_listagem = aluno_service.listar_alunos()
    print(f"Resultado da listagem: {resultado_listagem}")
    
    # Exemplo de busca de aluno
    print("\n=== Buscando Aluno ===")
    resultado_busca = aluno_service.buscar_aluno("99999999999")
    print(f"Resultado da busca: {resultado_busca}")
    
    # Exemplo de edição de aluno
    print("\n=== Editando Aluno ===")
    resultado_edicao = aluno_service.editar_aluno(
        cpf="(11)977884455",
        dados={
            "nome": "João Silva Atualizado",
            "atendimentos_semana": 3,
            "senha": "nova_senha123"
        }
    )
    print(f"Resultado da edição: {resultado_edicao}")

if __name__ == "__main__":
    main() 