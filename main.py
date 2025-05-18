from api_alunos import AlunoAPI
from planilha import PlanilhaService

def main():
    # Criar instância da API
    api = AlunoAPI()
    
    # Exemplo de login
    print("\n=== Testando Login ===")
    print("Tentando login com:")
    print("cpf: 99999999999")
    print("Senha: senha123")
    
    resultado_login = api.login("99999999999", "senha123")
    print(f"\nResultado do login: {resultado_login}")
    
    if resultado_login["sucesso"]:
        token = resultado_login["token"]
        
        # Listar atendimentos disponíveis
        print("\n=== Listando Atendimentos Disponíveis ===")
        atendimentos = api.listar_atendimentos()
        print(f"Atendimentos disponíveis: {atendimentos}")
        
        if resultado_salas["sucesso"] and resultado_salas["salas"]:
            sala = resultado_salas["salas"][0]  # Pega a primeira sala disponível
            
            # # Exemplo de listagem de atendimentos
            print("\n=== Testando Listagem de Atendimentos ===")
            resultado_listagem = api.listar_agendamentos(token)
            print(f"Resultado da listagem: {resultado_listagem}")
            
        else:
            print("Nenhum atendimento disponível encontrado")

if __name__ == "__main__":
    main() 