import os
import json
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from langflow.custom import Component
from langflow.io import FileInput, MultilineInput, Output
from langflow.schema import Data


class GoogleOAuthToken(Component):
    display_name = "Google OAuth Token (via token.json)"
    description = "Carrega credenciais do Google a partir de um token.json fornecido, sem abrir navegador."
    documentation: str = "https://developers.google.com/identity/protocols/oauth2/web-server?hl=pt-br#python_1"
    icon = "Google"
    name = "GoogleOAuthToken"

    inputs = [
        MultilineInput(
            name="scopes",
            display_name="Scopes",
            info="Informe a lista de scopes (separadas por vírgula) que seu Langflow precisará.",
            required=True,
            value=(
                "https://www.googleapis.com/auth/drive.readonly,\n"
                "https://www.googleapis.com/auth/drive.activity.readonly"
            ),
        ),
        FileInput(
            name="oauth_credentials",
            display_name="Credentials File",
            info="Selecione o arquivo JSON de credenciais OAuth (por exemplo, credentials.json).",
            file_types=["json"],
            required=True,
        ),
        FileInput(
            name="token_file",
            display_name="Token File (token.json)",
            info=(
                "Envie aqui um token.json previamente gerado (contendo access_token e refresh_token). "
                "O componente vai carregá-lo sem abrir navegador."
            ),
            file_types=["json"],
            required=False,
        ),
    ]

    outputs = [
        Output(display_name="Output", name="output", method="build_output"),
    ]

    def validate_scopes(self, scopes: str):
        pattern = (
            r"^(https:\/\/(www\.googleapis\.com\/auth\/[\w\.\-]+"
            r"|mail\.google\.com\/"
            r"|www\.google\.com\/calendar\/feeds"
            r"|www\.google\.com\/m8\/feeds))"
            r"(,\s*https:\/\/(www\.googleapis\.com\/auth\/[\w\.\-]+"
            r"|mail\.google\.com\/"
            r"|www\.google\.com\/calendar\/feeds"
            r"|www\.google\.com\/m8\/feeds))*$"
        )
        if not re.match(pattern, scopes):
            raise ValueError(
                "Formato inválido para scopes. Certifique-se de passar URLs separadas por vírgula, sem aspas extras."
            )

    def build_output(self) -> Data:
        # 1) Valida formato das scopes
        self.validate_scopes(self.scopes)
        user_scopes = [s.strip() for s in self.scopes.split(",") if s.strip()]
        if not user_scopes:
            raise ValueError("Scopes não podem ficar vazias. Preencha corretamente o campo Scopes.")

        SCOPES = user_scopes
        creds = None

        # 2) Se o usuário enviou um token_file (token.json), carregamos dele:
        if self.token_file:
            token_path = self.token_file
            try:
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            except Exception as exc:
                raise ValueError(f"Falha ao carregar token.json: {exc}") from exc

            # Se o token estiver expirado, tentamos refresh (caso tenha refresh_token dentro)
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    # (Opcional) Se quiser sobrescrever o token.json fornecido, poderia gravar de volta:
                    # with open(token_path, "w", encoding="utf-8") as f:
                    #     f.write(creds.to_json())
                except Exception:
                    # Se não for possível refresh, consideramos inválido
                    raise ValueError(
                        "O token.json fornecido está expirado e não pôde ser atualizado. "
                        "Por favor, gere um novo token.json."
                    )

            # Se carregamos e o creds está válido agora, retornamos imediatamente
            if creds and creds.valid:
                creds_json = json.loads(creds.to_json())
                if "type" not in creds_json:
                    creds_json["type"] = "authorized_user"
                return Data(data=creds_json)


            # Caso contrário, cai em erro abaixo

        # 3) Se não houver token_file ou não conseguiu carregar credenciais válidas
        raise ValueError(
            "Nenhum token.json válido foi fornecido. Por favor:\n"
            "1) Gere um token.json localmente usando OAuth (run_local_server() em sua máquina ou fluxo manual).\n"
            "2) Faça o upload deste token.json neste campo.\n"
            "3) Execute novamente o componente para que ele carregue as credenciais."
        )
