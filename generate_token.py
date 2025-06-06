import os
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# 1) Ajuste aqui as scopes que seu Langflow vai usar:
SCOPES = [
    "https://www.googleapis.com/auth/drive",
]

# 2) Aponte para o JSON de "Desktop App" que você baixou do Google Cloud
CLIENT_SECRET_FILE = r"caminho para o client_secret"

# Nome do token que vai ser gravado localmente
TOKEN_PATH = "token.json"

def main():
    creds = None

    # Se já existe token.json, tenta carregar e, se tiver refresh_token, renovar se expirado
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Cria o fluxo a partir do seu credentials.json (Desktop App)
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)

            # run_local_server vai:
            #   1) abrir seu navegador padrão no Google de autenticação,
            #   2) subir um mini-servidor em localhost:<porta aleatória>
            #   3) receber o callback automático (http://localhost:<porta>/?code=…)
            creds = flow.run_local_server(port=0)

        # Salva o novo token.json (contendo access_token e refresh_token)
        with open(TOKEN_PATH, "w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())
        print(f"\nToken salvo em '{TOKEN_PATH}'.\n")
    else:
        print("Já existe um token válido em disk (token.json).")

    # Remova se não quiser ver o JSON; aqui só mostramos no console para você conferir
    creds_json = json.loads(creds.to_json())
    print(json.dumps(creds_json, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
