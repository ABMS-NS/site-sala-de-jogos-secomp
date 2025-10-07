# 🎮 SECOMP - Sala de Jogos Leaderboard

Sistema de ranking para a sala de jogos da SECOMP com interface web em modo escuro e persistência via GitHub API.

## 📋 Funcionalidades

- **Home/Leaderboard**: Exibe ranking completo com destaque para o Top 3
- **Login de Administrador**: Acesso protegido por senha
- **Painel Admin**: Cadastro de jogadores e gerenciamento de pontos
- **Persistência via GitHub**: Dados salvos em repositório GitHub via API
- **Modo Escuro**: Interface totalmente em modo escuro

## 🚀 Como Configurar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Criar Token do GitHub

1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token (classic)"
3. Selecione o escopo `repo` (acesso completo ao repositório)
4. Copie o token gerado

### 3. Criar Repositório no GitHub

1. Crie um novo repositório (pode ser privado)
2. Crie um arquivo `leaderboard.json` com o conteúdo inicial:
```json
{
  "players": {}
}
```

### 4. Configurar no Streamlit Cloud (Recomendado)

1. Acesse: https://streamlit.io/cloud
2. Conecte seu repositório do GitHub
3. Em **Settings → Secrets**, adicione:

```toml
# GitHub API
GITHUB_TOKEN = "seu_token_do_github_aqui"
GITHUB_REPO = "usuario/repositorio"
GITHUB_FILE = "leaderboard.json"

# Credenciais de Admin
[ADMINS]
admin = "secomp2024"
organizador = "jogos123"
```

4. Deploy!

### 5. Configurar Localmente (Desenvolvimento)

Edite o arquivo `.env`:

```bash
GITHUB_TOKEN=seu_token_aqui
GITHUB_REPO=usuario/repositorio
GITHUB_FILE=leaderboard.json

ADMIN1_USER=admin
ADMIN1_PASS=secomp2024
ADMIN2_USER=organizador
ADMIN2_PASS=jogos123
```

### 5. Executar a Aplicação

```bash
streamlit run app.py
```

## 🔐 Credenciais de Admin (Hardcoded)

- **Usuário 1**: `admin` / Senha: `secomp2024`
- **Usuário 2**: `organizador` / Senha: `jogos123`

Para alterar, edite a variável `ADMIN_CREDENTIALS` no arquivo `app.py`.

## 📂 Estrutura do Projeto

```
.
├── app.py                 # Aplicação principal
├── requirements.txt       # Dependências Python
├── .env.example          # Exemplo de configuração
├── .gitignore            # Arquivos ignorados pelo Git
├── README.md             # Este arquivo
└── models/               # Modelos (não utilizados nesta versão)
    ├── __init__.py
    ├── adms.py
    ├── pessoa_ranking.py
    └── ranking.py
```

## 🎯 Como Usar

### Para Participantes

1. Acesse a página inicial
2. Visualize o ranking em tempo real
3. Veja sua posição e pontuação

### Para Administradores

1. Clique em "🔐 Área de Administrador"
2. Faça login com as credenciais
3. Use a aba "Cadastrar/Editar" para adicionar novos jogadores
4. Use a aba "Gerenciar Pontos" para atualizar pontuações
5. Os dados são salvos automaticamente no GitHub

## 🛠️ Tecnologias

- **Streamlit**: Framework web em Python
- **GitHub API**: Persistência de dados
- **Requests**: Comunicação HTTP
- **JSON**: Formato de dados

## 📝 Notas

- Os dados são salvos no GitHub em tempo real
- Cada atualização gera um commit no repositório
- O modo escuro é forçado via CSS customizado
- A interface é responsiva e funciona em dispositivos móveis

## 🐛 Solução de Problemas

**Erro 401 (Unauthorized)**: Verifique se o token do GitHub está correto e tem permissões de `repo`.

**Erro 404 (Not Found)**: Verifique se o repositório e o arquivo existem e se o formato está correto (`usuario/repo`).

**Dados não salvam**: Certifique-se de que o arquivo `leaderboard.json` existe no repositório.