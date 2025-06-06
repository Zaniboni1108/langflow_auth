# README

## Descrição
Este repositório contém dois scripts Python relacionados à autenticação OAuth do Google:

1. **generate_token.py**: Script que cria ou atualiza um arquivo token.json usando fluxo de autenticação OAuth local no navegador. Este arquivo é utilizado para autenticar aplicações que acessam APIs do Google (por exemplo, Google Drive).
2. **google_oauth_component.py**: Componente customizado para Langflow que carrega credenciais do Google a partir de um arquivo token.json pré-gerado, sem abrir o navegador.

---

## Pré-requisitos
- Python 3.7 ou superior
- Conta no Google Cloud com credenciais de tipo Desktop App (arquivo JSON)
- Dependências Python (instaláveis via pip):
  ```
  pip install --upgrade google-auth google-auth-oauthlib
  ```

> Nota: Se usar um ambiente virtual (virtualenv, venv, conda etc.), ative-o antes de instalar as dependências.

---

## Estrutura dos arquivos

```
.
├── generate_token.py
├── google_oauth_component.py
└── README.md
```

---

## 1. Gerar o arquivo token.json (generate_token.py)

### Descrição
Este script executa o fluxo OAuth 2.0 do Google para Desktop App, abrindo o navegador para autenticação, e salva o resultado em um arquivo token.json local. O token.json contém campos como access_token e refresh_token, necessários para autorizar chamadas às APIs do Google.

### Configuração
1. Defina as scopes que sua aplicação precisará modificando a variável SCOPES (lista de URLs). Exemplo:
   ```python
   SCOPES = [
       'https://www.googleapis.com/auth/drive',
   ]
   ```
2. Aponte para o arquivo de credenciais JSON (Desktop App) obtido no Console do Google Cloud:
   ```python
   CLIENT_SECRET_FILE = r'caminho/para/seu/credentials.json'
   ```
3. Opcional: o nome do arquivo onde o token será salvo. Padrão: token.json.
   ```python
   TOKEN_PATH = 'token.json'
   ```

### Uso
```bash
python generate_token.py
```
- Será aberto automaticamente o navegador para você escolher sua conta Google e autorizar o acesso.
- Após aprovação, o script salva o arquivo token.json no mesmo diretório.
- Caso já exista um token.json válido, exibirá mensagem informando que não há necessidade de novo login.

### Saída
- Um arquivo token.json contendo as credenciais JSON com access_token, refresh_token, expiry etc.
- Exibição do conteúdo JSON das credenciais no console para conferência.

---

## 2. Componente Langflow: GoogleOAuthToken (google_oauth_component.py)

### Descrição
Este componente para Langflow carrega credenciais do Google a partir de um arquivo token.json pré-existente, sem necessidade de abrir o navegador. Ideal para fluxos em produção ou servidores sem interface gráfica.

### Uso
1. Copie o conteudo arquivo google_oauth_component.py.
2. No painel do Langflow, adicione o componente 'New Custom Component' e em Code cole o coteudo do google_oauth_component.py e Salve.
3. Configure os seguintes campos no componente:
   - Scopes: lista de scopes separados por vírgula. Exemplo:
     ```
     https://www.googleapis.com/auth/drive.readonly, https://www.googleapis.com/auth/drive.activity.readonly
     ```
   - Credentials File: faça upload do arquivo de credenciais OAuth (credentials.json).
   - Token File (token.json): faça upload do arquivo token.json gerado pelo script anterior.

4. Conecte a saída Output para o próximo nó em seu fluxo Langflow, que receberá as credenciais JSON como objeto Data.

### Funcionamento interno
- validate_scopes: verifica se as scopes passadas estão no formato correto (URLs válidas).
- Se o usuário forneceu um token_file (token.json), carrega as credenciais:
  - Caso o token esteja expirado mas contenha refresh_token, faz creds.refresh(Request()) e atualiza em memória.
  - Se o carregamento for bem-sucedido e as credenciais forem válidas, retorna o JSON de credenciais.
- Se não houver token_file ou ele for inválido/expirado sem possibilidade de refresh, dispara erro orientando a gerar um novo token.json.

---

## Exemplo de Execução (Fluxo Completo)

1. Gere o token.json rodando generate_token.py:
   ```bash
   python generate_token.py
   ```
2. Copie token.json para o ambiente onde roda o Langflow.
3. No Langflow, arraste e configure o componente Google OAuth Token (via token.json), apontando para:
   - Scopes desejadas.
   - credentials.json (Desktop App).
   - token.json gerado.
4. Conecte a saída do componente para autenticar chamadas às APIs do Google.

---

## Dependências Pip
```bash
pip install --upgrade google-auth google-auth-oauthlib
```

---

## Observações
- Se seu fluxo precisar de outras APIs, adicione as scopes correspondentes.
- Mantenha seu credentials.json (Desktop App) seguro e não compartilhe publicamente.
- Não versionar token.json em repositórios públicos, pois contém tokens de acesso/atualização.

---

## Licença
MIT License
