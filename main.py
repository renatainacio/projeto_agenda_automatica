from api_alunos import AlunoAPI
from planilha import PlanilhaService

def main():
    # Criar instância da API
    api = AlunoAPI()
    
    # Exemplo de login
    print("\n=== Testando Login ===")
    print("Tentando login com:")
    print("Telefone: (11)999999999")
    print("Senha: senha123")
    
    # # Verificar dados na planilha
    # planilha = PlanilhaService()
    # alunos = planilha.ler_dados("Alunos!A2:E")
    # print("\nDados encontrados na planilha:")
    # for aluno in alunos:
    #     print(f"CPF: {aluno[0]}")
    #     print(f"Nome: {aluno[1]}")
    #     print(f"Telefone: {aluno[2]}")
    #     print(f"Aulas por semana: {aluno[3]}")
    #     print(f"Senha: {aluno[4]}")
    #     print("-" * 30)
    
    # # Se não houver alunos, criar um aluno de teste
    # if not alunos:
    #     print("\nCriando aluno de teste...")
    #     novo_aluno = [
    #         ["123.456.789-00", "Aluno Teste", "(11)999999999", "2", "senha123"]
    #     ]
    #     sucesso, mensagem = planilha.inserir_dados("Alunos!A:E", novo_aluno)
    #     print(f"Resultado da criação: {mensagem}")
    
    resultado_login = api.login("(11)999999999", "senha123")
    print(f"\nResultado do login: {resultado_login}")
    
    if resultado_login["sucesso"]:
        token = resultado_login["token"]
        
        # Listar salas disponíveis
        print("\n=== Listando Salas Disponíveis ===")
        resultado_salas = api.listar_aulas()
        print(f"Salas disponíveis: {resultado_salas}")
        
        if resultado_salas["sucesso"] and resultado_salas["salas"]:
            sala = resultado_salas["salas"][0]  # Pega a primeira sala disponível
            
            # # Exemplo de agendamento de aula
            # print("\n=== Testando Agendamento de Aula ===")
            # resultado_agendamento = api.agendar_aula(
            #     token, 
            #     "10/02/2025", 
            #     "11:00",
            #     sala["nome"]
            # )
            # print(f"Resultado do agendamento: {resultado_agendamento}")
            
            # # Exemplo de listagem de aulas
            print("\n=== Testando Listagem de Aulas ===")
            resultado_listagem = api.listar_agendamentos(token)
            print(f"Resultado da listagem: {resultado_listagem}")
            
            # Exemplo de cancelamento de aula
            # print("\n=== Testando Cancelamento de Aula ===")
            # resultado_cancelamento = api.cancelar_aula(
            #     token, 
            #     "10/02/2025", 
            #     "11:00",
            #     sala["nome"]
            # )
            # print(f"Resultado do cancelamento: {resultado_cancelamento}")
        else:
            print("Nenhuma sala disponível encontrada")

if __name__ == "__main__":
    main() 