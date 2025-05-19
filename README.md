# Sistema de Agendamento de Atendimentos de Fisioterapia

Este sistema permite gerenciar clientes e agendamentos de agendamentos de fisioterapia usando o Google Sheets como banco de dados.

## Requisitos

- Python 3.8 ou superior
- Conta Google com acesso ao Google Sheets
- Credenciais do Google Cloud Platform
- https://docs.google.com/spreadsheets/d/1cyXrNZ2b1fDiuG7MCOGNYvTjcOrMBee__QZEuO-fyZM/edit?gid=1480663513#gid=1480663513 (planilha)

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITORIO]
cd agenda_pilates
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as credenciais do Google:
   - Acesse o [Google Cloud Console](https://console.cloud.google.com)
   - Crie um novo projeto
   - Ative a API do Google Sheets
   - Crie uma conta de serviço
   - Baixe o arquivo JSON das credenciais
   - Renomeie o arquivo para `credentials.json` e coloque na raiz do projeto

5. Configure a planilha do Google Sheets:
   - Crie uma nova planilha
   - Crie as seguintes abas:
     - `Clientes`: Nome, CPF, Atendimentos por Semana, Senha
     - `Atendimentos`: CPF, Data, Horário, Sala, Status, Fisio
     - `Salas`: Nome da Sala, Fisio
   - Compartilhe a planilha com o email da conta de serviço
   - Copie o ID da planilha da URL e atualize no arquivo `planilha.py`

## Estrutura do Projeto

```
agenda_pilates/
├── planilha.py          # Serviço base para interação com o Google Sheets
├── service.py     # Serviço para gerenciamento de clientes
├── api.py        # API para operações dos clientes
├── exemplo_cliente.py     # Exemplos de uso do serviço de clientes
├── requirements.txt     # Dependências do projeto
├── credentials.json     # Credenciais do Google (não versionado)
└── README.md           # Este arquivo
```

## Uso

### Gerenciamento de Clientes

```python
from service import Service

# Criar instância do serviço
service = Service()

# Cadastrar cliente
resultado = service.criar_cliente(
    nome="João Silva",
    cpf="99999999999",
    atendimentos_semana=2,
    senha="senha123"
)

# Listar clientes
clientes = service.listar_clientes()

# Buscar clientes
cliente = service.buscar_cliente("99999999999")

# Editar cliente
service.editar_cliente(
    cpf="99999999999",
    dados={
        "nome": "Novo Nome",
        "atendimentos_semana": 3,
        "senha": "nova_senha"
    }
)

# Excluir cliente
service.excluir_cliente("99999999999")
```

### Agendamento de Atendimentos

```python
from api import API

# Criar instância da API
api = API()

# Login
resultado = api.login("99999999999", "senha123")
token = resultado["token"]

# Agendar atendimento
api.agendar_atendimento(token, "01/01/2024", "10:00", "Sala 1")

# Listar agendamentos
agendamentos = api.listar_agendamentos(token)

# Cancelar agendamento
api.cancelar_agendamento(token, "01/01/2024", "10:00", "Sala 1")
```

## Segurança

- Senhas são criptografadas usando SHA-256 com salt
- Tokens JWT são usados para autenticação
- Validação de dados em todas as operações
- Verificação de duplicidade de cpf
- Limite de atendimentos por semana

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes. 