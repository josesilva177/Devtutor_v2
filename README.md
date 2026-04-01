# DevTutor 

**Tutor de programação com Inteligência Artificial — local e online**

DevTutor é uma aplicação web que utiliza modelos de linguagem de grande escala (LLMs) para responder a dúvidas de programação em tempo real. Suporta dois modos de inferência: um modelo local via [LM Studio](https://lmstudio.ai) e um modelo remoto via [API da OpenAI](https://platform.openai.com).

---

## Funcionalidades

- **Modo local** — inferência com o modelo DeepSeek Coder via LM Studio (sem internet, sem custos)
- **Modo online** — inferência com GPT-3.5 Turbo via API da OpenAI
- **Sistema de autenticação** — registo, login e sessões seguras
- **Histórico de conversas** — guardado por utilizador na base de dados
- **Interface dark mode** — design clean e confortável para programadores
- **API REST** — backend Flask com endpoints documentados

---

## Tecnologias utilizadas

| Camada | Tecnologia |
|---|---|
| Backend | Python 3 + Flask |
| Base de dados | SQLite |
| Frontend | HTML5, CSS3, JavaScript |
| IA local | LM Studio + DeepSeek Coder |
| IA remota | OpenAI API (GPT-3.5 Turbo) |
| Segurança | SHA-256, Flask Sessions, CORS |

---

## Estrutura do projeto

```
devtutor/
├── app.py          # Servidor Flask — rotas e lógica principal
├── database.py     # Acesso à base de dados SQLite
├── config.py       # Configuração de variáveis de ambiente
├── index.html      # Interface principal da aplicação
├── login.html      # Página de autenticação e registo
├── .env            # Variáveis de ambiente (não incluído no repositório)
└── devtutor.db     # Base de dados SQLite (gerada automaticamente)
```

---

## Instalação e execução

### Pré-requisitos

- Python 3.10 ou superior
- pip
- (Opcional) LM Studio para o modo local
- (Opcional) Chave de API da OpenAI para o modo online

### Passos

**1. Clonar o repositório**
```bash
git clone https://github.com/SEU-UTILIZADOR/devtutor.git
cd devtutor
```

**2. Instalar as dependências**
```bash
pip install flask flask-cors requests python-dotenv
```

**3. Configurar as variáveis de ambiente**

Criar um ficheiro `.env` na raiz do projeto:
```env
OPENAI_API_KEY=sk-...        # necessário apenas para o modo online
SECRET_KEY=uma-chave-secreta
LM_STUDIO_URL=http://localhost:1234/v1/chat/completions
```

**4. (Opcional) Configurar o modo local**

- Instalar o [LM Studio](https://lmstudio.ai)
- Descarregar o modelo **DeepSeek Coder** (versão GGUF)
- Iniciar o servidor local do LM Studio na porta `1234`

**5. Iniciar a aplicação**
```bash
python app.py
```

Aceder a [http://localhost:5000](http://localhost:5000) no navegador.

---

## Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/auth/register` | Criar nova conta |
| `POST` | `/auth/login` | Autenticar utilizador |
| `POST` | `/auth/logout` | Encerrar sessão |
| `GET` | `/auth/me` | Verificar sessão ativa |
| `POST` | `/analyze` | Enviar pergunta para a IA |
| `GET` | `/history` | Obter histórico de conversas |
| `DELETE` | `/history/<id>` | Eliminar item do histórico |
| `DELETE` | `/history/clear` | Limpar todo o histórico |
| `GET` | `/health` | Estado dos serviços |

### Exemplo de pedido à rota `/analyze`

```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "O que é uma lista em Python?", "mode": "local"}'
```

### Resposta esperada

```json
{
  "success": true,
  "analysis": "Uma lista em Python é uma estrutura de dados...",
  "provider": "LM Studio (Local)",
  "model": "deepseek-coder",
  "response_time": "4.2s",
  "tokens_used": 312
}
```

---

## Arquitetura do sistema

```
Navegador (HTML/JS)
        │
        │  HTTP / Fetch API
        ▼
┌─────────────────────────────────────┐
│           Servidor Flask            │
│  ┌──────────┐  ┌────────────────┐  │
│  │   Auth   │  │ Motor análise  │  │
│  └──────────┘  └────────────────┘  │
│        │              │            │
└────────│──────────────│────────────┘
         │              │
    ┌────▼────┐    ┌────▼──────────────────┐
    │ SQLite  │    │  Modo local           │
    │ users   │    │  LM Studio:1234       │
    │ history │    ├───────────────────────┤
    └─────────┘    │  Modo online          │
                   │  api.openai.com       │
                   └───────────────────────┘
```

---

## Segurança

- As palavras-passe são armazenadas com hash **SHA-256** (nunca em texto simples)
- As sessões são assinadas criptograficamente com `SECRET_KEY`
- O histórico de cada utilizador é isolado por `user_id`
- As entradas são validadas e normalizadas no lado do servidor
- Em produção, recomenda-se substituir SHA-256 por **bcrypt** ou **Argon2**

---

## Melhorias previstas

- [ ] Hash de palavras-passe com bcrypt/Argon2
- [ ] Janela de contexto nas conversas (enviar histórico no prompt)
- [ ] Suporte a múltiplos modelos locais
- [ ] Rate limiting na API
- [ ] Interface Progressive Web App (PWA)
- [ ] Streaming de respostas em tempo real (Server-Sent Events)

---

## Projeto académico

Este projeto foi desenvolvido no âmbito da **Prova de Aptidão Profissional (PAP)** do Curso Profissional de Técnico de Gestão e Programação de Sistemas Informáticos (TGPSI) na Escola Básica e Secundária de Fajões.

**Autor:** José Carlos da Silva Neto  
**Orientadora:** Professora Teresa Gonçalves  
**Ano letivo:** 2025/2026

---

## Licença

Este projeto foi desenvolvido para fins académicos. Podes utilizá-lo e modificá-lo livremente para aprendizagem.
