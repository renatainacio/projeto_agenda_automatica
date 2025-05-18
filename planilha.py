from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import jwt
import datetime
import os
import hashlib
import secrets
import json

load_dotenv()  # Carrega variáveis do .env

# ID da planilha
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "1cyXrNZ2b1fDiuG7MCOGNYvTjcOrMBee__QZEuO-fyZM")

# Escopos necessários
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Chave secreta para JWT
JWT_SECRET = os.getenv("JWT_SECRET", "sua_chave_secreta_aqui_123456@")

class PlanilhaService:
    def __init__(self):
        self.service = self._conectar_google_sheets()
        self.sheet_ids = self._obter_sheet_ids() 

    def _conectar_google_sheets(self):
        """Conecta ao Google Sheets usando service account."""
        try:
            creds_info = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
            creds = service_account.Credentials.from_service_account_info(
                creds_info,
                scopes=SCOPES
            )
            return build("sheets", "v4", credentials=creds)
        except Exception as e:
            print(f"Erro ao conectar: {str(e)}")
            return None

    def _obter_sheet_ids(self):
        try:
            metadata = self.service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
            sheet_ids = {
                sheet["properties"]["title"]: sheet["properties"]["sheetId"]
                for sheet in metadata.get("sheets", [])
            }
            return sheet_ids
        except Exception as e:
            print(f"Erro ao obter sheet IDs: {e}")
            return {}

    def _gerar_token(self, cpf, nome):
        """Gera um token JWT para o aluno."""
        payload = {
            'cpf': cpf,
            'nome': nome,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        self._salvar_token(cpf, token)
        return token


    def _buscar_token(self, token):
        dados = self.ler_dados("Tokens!A:B")
        for linha in dados[1:]:
            if len(linha) >= 2 and linha[1] == token:
                return linha[0]
        return None
    

    def _verificar_token(self, token):
        """Verifica se o token é válido."""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            return payload['cpf'], payload['nome']
        except:
            return None, None

    def _criptografar_senha(self, senha):
        """Criptografa a senha usando SHA-256 com salt."""
        salt = secrets.token_hex(16)
        senha_hash = hashlib.sha256((senha + salt).encode()).hexdigest()
        return f"{salt}${senha_hash}"

    def _verificar_senha(self, senha, senha_hash):
        """Verifica se a senha está correta."""
        salt, hash_armazenado = senha_hash.split('$')
        hash_calculado = hashlib.sha256((senha + salt).encode()).hexdigest()
        return hash_calculado == hash_armazenado

    def autenticar_aluno(self, cpf, senha):
        """Autentica um aluno e retorna um token."""
        try:
            # Buscar aluno pelo cpf
            alunos = self.ler_dados("Alunos!A2:D")
            for aluno in alunos:
                if len(aluno) >= 4 and aluno[1] == cpf:
                    if not self._verificar_senha(senha, aluno[3]):
                        return {"sucesso": False, "mensagem": "Senha incorreta"}
                    
                    token = self._gerar_token(cpf, aluno[0])
                    return {
                        "sucesso": True,
                        "token": token,
                        "aluno": {
                            "nome": aluno[0],
                            "cpf": aluno[1],
                            "atendimentos_semana": aluno[2]
                        }
                    }
            return {"sucesso": False, "mensagem": "Aluno não encontrado"}
        except Exception as e:
            return {"sucesso": False, "mensagem": str(e)}

    def ler_dados(self, range_name):
        """Lê dados de uma planilha."""
        try:
            sheet = self.service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=SPREADSHEET_ID, range=range_name)
                .execute()
            )
            return result.get("values", [])
        except HttpError as err:
            print(f"Erro ao ler dados: {err}")
            return []

    def inserir_dados(self, range_name, values):
        """Insere dados em uma planilha."""
        try:
            sheet = self.service.spreadsheets()
            body = {'values': values}
            result = (
                sheet.values()
                .append(
                    spreadsheetId=SPREADSHEET_ID,
                    range=range_name,
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body=body
                )
                .execute()
            )
            return True, "Dados inseridos com sucesso"
        except HttpError as err:
            return False, f"Erro ao inserir dados: {err}"

    def atualizar_dados(self, range_name, values, valueInputOption="RAW"):
        """Atualiza dados em uma planilha."""
        try:
            sheet = self.service.spreadsheets()
            body = {'values': values}
            result = (
                sheet.values()
                .update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=range_name,
                    valueInputOption=valueInputOption,
                    body=body
                )
                .execute()
            )
            return True, "Dados atualizados com sucesso"
        except HttpError as err:
            return False, f"Erro ao atualizar dados: {err}"

    def remover_dados(self, range_name, row_index, sheet_name):
        """Remove uma linha específica da planilha."""
        try:
            sheet = self.service.spreadsheets()
            request = {
                'requests': [{
                    'deleteDimension': {
                        'range': {
                            'sheetId': self.sheet_ids[sheet_name],
                            'dimension': 'ROWS',
                            'startIndex': row_index - 1,
                            'endIndex': row_index
                        }
                    }
                }]
            }
            result = sheet.batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body=request
            ).execute()
            return True, "Dados removidos com sucesso"
        except HttpError as err:
            return False, f"Erro ao remover dados: {err}"

    def _salvar_token(self, cpf, token):
        """Salva ou atualiza um token na aba 'Tokens'."""
        dados = self.ler_dados("Tokens!A:B")

        # Verifica se o cpf já existe
        for i, linha in dados[1:]: 
            if len(linha) >= 2 and linha[0] == cpf:
                # Atualiza o token na linha correspondente
                range_update = f"Tokens!B{i}"
                sucesso, msg = self.atualizar_dados(range_update, [[token]])
                return sucesso, "Token atualizado" if sucesso else msg

        # Insere nova linha
        sucesso, msg = self.inserir_dados("Tokens!A2", [[cpf, token]])
        return sucesso, "Token inserido" if sucesso else msg


    def verificar_autenticacao(self, token):
        """Verifica se o token é válido e retorna o cpf do aluno."""
        cpf, nome = self._verificar_token(token)
        if cpf and self._buscar_token(token) == cpf:
            return {
                    "cpf": cpf, 
                    "nome": nome
                }
        return None 