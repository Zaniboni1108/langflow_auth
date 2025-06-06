import os
import json
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# 1) Ajuste aqui as scopes que seu Langflow vai usar:
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
]

# 2) Aponte para o JSON de "Desktop App" que você baixou do Google Cloud
CLIENT_SECRET_FILE = r"caminho do client_secret"

# Nome do token que vai ser gravado localmente
TOKEN_PATH = "token.json"

def get_user_email(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get("https://openidconnect.googleapis.com/v1/userinfo", headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        return user_info.get("email")
    return None

def main():
    creds = None

    # Se já existe token.json, tenta carregar e, se tiver refresh_token, renovar se expirado
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())
        print(f"\nToken salvo em '{TOKEN_PATH}'.\n")
    else:
        print("Já existe um token válido em disco (token.json).")

    creds_json = json.loads(creds.to_json())
    creds_json["type"] = "authorized_user"

    # Pega o e-mail da conta e adiciona no campo 'account'
    email = get_user_email(creds.token)
    if email:
        creds_json["account"] = email
    else:
        creds_json["account"] = ""

    # Salvar o JSON com o campo "type" e "account"
    with open(TOKEN_PATH, "w", encoding="utf-8") as token_file:
        json.dump(creds_json, token_file, indent=2, ensure_ascii=False)
    
    print(json.dumps(creds_json, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
