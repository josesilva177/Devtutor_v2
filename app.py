from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import requests
import time
import os
from datetime import datetime
from config import Config
from database import init_db, create_user, login_user, save_history, get_history, delete_history_item, clear_all_history


OPENAI_API_KEY = Config.OPENAI_API_KEY
if not Config.OPENAI_API_KEY:
    print(" ERRO: OPENAI_API_KEY não definida!")

LM_STUDIO_URL = Config.LM_STUDIO_URL
LM_MODEL = "deepseek-coder"

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-3.5-turbo"

NIM_API_KEY = Config.NIM_API_KEY
NIM_URL = Config.NIM_URL
NIM_MODEL = Config.NIM_MODEL

def analyze_with_nim(code):
    try:
        start_time = time.time()
        prompt = f"""Como tutor de programação responda essa pergunta: {code}"""
        response = requests.post(
            NIM_URL,
            headers={
                "Authorization": f"Bearer {NIM_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": NIM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1024,
                "temperature": 0.7
            },
            timeout=60
        )
        elapsed = time.time() - start_time
        if response.status_code == 200:
            result = response.json()
            analysis = result["choices"][0]["message"]["content"]
            tokens = result.get("usage", {}).get("total_tokens", 0)
            return {
                "success": True,
                "analysis": analysis,
                "provider": f"NVIDIA NIM ({NIM_MODEL})",
                "model": NIM_MODEL,
                "response_time": f"{elapsed:.1f}s",
                "tokens_used": tokens,
            }
        error_msg = response.text[:200] if response.text else "Sem detalhes"
        return {"success": False, "error": f"NIM erro {response.status_code}", "provider": "NVIDIA NIM", "details": error_msg}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "NVIDIA NIM demorou muito (>60s)", "provider": "NVIDIA NIM"}
    except Exception as e:
        return {"success": False, "error": f"Erro NIM: {str(e)}", "provider": "NVIDIA NIM"}


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "devtutor-secret-key-2024")
CORS(app, supports_credentials=True)

# Inicializa a base de dados ao arrancar
init_db()


def get_current_user():
    """Retorna o utilizador da sessão ou None"""
    return session.get("user")


def require_login():
    """Retorna erro se não estiver autenticado"""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "Não autenticado. Faça login primeiro."}), 401
    return None


# ============================================
# IAs (igual ao original)
# ============================================

def analyze_with_local(code):
    try:
        start_time = time.time()
        prompt = f"""Como tutor de programação responda essa pergunta: {code}"""
        response = requests.post(
            LM_STUDIO_URL,
            json={"messages": [{"role": "user", "content": prompt}]},
            timeout=300
        )
        elapsed = time.time() - start_time
        if response.status_code == 200:
            result = response.json()
            analysis = result["choices"][0]["message"]["content"]
            tokens = result.get("usage", {}).get("total_tokens", 0)
            return {
                "success": True, "analysis": analysis,
                "provider": "LM Studio (Local)", "model": LM_MODEL,
                "response_time": f"{elapsed:.1f}s", "tokens_used": tokens,
            }
        return {"success": False, "error": f"LM Studio erro {response.status_code}", "provider": "LM Studio", "response_time": f"{elapsed:.1f}s"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "LM Studio demorou muito (>300s)", "provider": "LM Studio"}
    except Exception as e:
        return {"success": False, "error": f"Erro LM Studio: {str(e)}", "provider": "LM Studio"}


def analyze_with_openai(code):
    try:
        start_time = time.time()
        prompt = f"""Como tutor de programação responda essa pergunta: {code}"""
        response = requests.post(
            OPENAI_URL,
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={"model": OPENAI_MODEL, "messages": [{"role": "user", "content": prompt}]},
            timeout=30
        )
        elapsed = time.time() - start_time
        if response.status_code == 200:
            result = response.json()
            analysis = result["choices"][0]["message"]["content"]
            tokens = result["usage"]["total_tokens"]
            cost = tokens * 0.0000015
            return {
                "success": True, "analysis": analysis,
                "provider": "OpenAI GPT-3.5", "model": OPENAI_MODEL,
                "response_time": f"{elapsed:.1f}s", "tokens_used": tokens,
                "cost": f"${cost:.4f}"
            }
        error_msg = response.text[:200] if response.text else "Sem detalhes"
        return {"success": False, "error": f"OpenAI erro {response.status_code}", "provider": "OpenAI", "details": error_msg}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "OpenAI demorou muito (>30s)", "provider": "OpenAI"}
    except Exception as e:
        return {"success": False, "error": f"Erro OpenAI: {str(e)}", "provider": "OpenAI"}


# ============================================
# ROTAS ESTÁTICAS
# ============================================

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)


# ============================================
# ROTAS DE AUTENTICAÇÃO
# ============================================

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({"success": False, "error": "Preencha todos os campos"}), 400
    if len(password) < 6:
        return jsonify({"success": False, "error": "A palavra-passe deve ter pelo menos 6 caracteres"}), 400
    if len(username) < 3:
        return jsonify({"success": False, "error": "O nome de utilizador deve ter pelo menos 3 caracteres"}), 400

    ok, msg = create_user(username, email, password)
    if ok:
        return jsonify({"success": True, "message": msg})
    return jsonify({"success": False, "error": msg}), 400


@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    user, msg = login_user(username, password)
    if user:
        # Guardar na sessão (sem a password hash)
        session['user'] = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
        return jsonify({
            "success": True,
            "message": msg,
            "user": session['user']
        })
    return jsonify({"success": False, "error": msg}), 401


@app.route('/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Sessão terminada"})


@app.route('/auth/me')
def me():
    user = get_current_user()
    if user:
        return jsonify({"success": True, "user": user})
    return jsonify({"success": False, "error": "Não autenticado"}), 401


# ============================================
# ROTA PRINCIPAL DE ANÁLISE (com histórico)
# ============================================

@app.route('/analyze', methods=['POST'])
def analyze_code():
    # Verificar autenticação
    auth_error = require_login()
    if auth_error:
        return auth_error

    user = get_current_user()

    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        mode = data.get('mode', 'local')

        if not code:
            return jsonify({"success": False, "error": "Pergunta vazia"}), 400

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 👤 {user['username']} | Modo: {mode.upper()} | {len(code)} chars")

        if mode == 'local':
            result = analyze_with_local(code)
        elif mode == 'online':
            result = analyze_with_openai(code)
        elif mode == 'nim':
            result = analyze_with_nim(code)
        else:
            return jsonify({"success": False, "error": "Modo inválido. Use 'local' ou 'online'"}), 400

        # Guardar no histórico se a resposta foi bem-sucedida
        if result and result.get('success'):
            save_history(
                user_id=user['id'],
                question=code,
                answer=result.get('analysis', ''),
                provider=result.get('provider', ''),
                mode=mode,
                response_time=result.get('response_time', ''),
                tokens_used=result.get('tokens_used', 0)
            )

        return jsonify(result) if result else jsonify({"success": False, "error": "Erro no processamento"})

    except Exception as e:
        print(f"Erro na rota /analyze: {e}")
        return jsonify({"success": False, "error": f"Erro interno: {str(e)}"}), 500


# ============================================
# ROTAS DO HISTÓRICO
# ============================================

@app.route('/history', methods=['GET'])
def get_user_history():
    auth_error = require_login()
    if auth_error:
        return auth_error

    user = get_current_user()
    history = get_history(user['id'])
    return jsonify({"success": True, "history": history, "total": len(history)})


@app.route('/history/<int:item_id>', methods=['DELETE'])
def delete_history(item_id):
    auth_error = require_login()
    if auth_error:
        return auth_error

    user = get_current_user()
    delete_history_item(item_id, user['id'])
    return jsonify({"success": True, "message": "Item apagado"})


@app.route('/history/clear', methods=['DELETE'])
def clear_history():
    auth_error = require_login()
    if auth_error:
        return auth_error

    user = get_current_user()
    clear_all_history(user['id'])
    return jsonify({"success": True, "message": "Histórico limpo"})


# ============================================
# ROTAS DE SISTEMA (iguais ao original)
# ============================================

@app.route('/health')
def health_check():
    services = {"flask": " Online", "lm_studio": " Offline", "openai": " Offline"}
    try:
        lm_test = requests.get("http://localhost:1234/v1/models", timeout=5)
        services["lm_studio"] = " Online" if lm_test.status_code == 200 else " Offline"
    except:
        pass
    try:
        test_response = requests.post(
            OPENAI_URL,
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={"model": OPENAI_MODEL, "messages": [{"role": "user", "content": "test"}], "max_tokens": 1},
            timeout=5
        )
        services["openai"] = " Online" if test_response.status_code == 200 else " Offline"
    except:
        pass
    return jsonify({**services, "timestamp": datetime.now().strftime("%H:%M:%S"), "system": "DevTutor"})


@app.route('/system/info')
def system_info():
    return jsonify({
        "system": "DevTutor - Tutor de Código",
        "version": "2.0",
        "features": ["login", "registo", "histórico de conversas", "IA local", "IA online"],
        "api_endpoints": {
            "register": "POST /auth/register",
            "login": "POST /auth/login",
            "logout": "POST /auth/logout",
            "me": "GET /auth/me",
            "analyze": "POST /analyze",
            "history": "GET /history",
            "delete_item": "DELETE /history/<id>",
            "clear_history": "DELETE /history/clear",
            "health": "GET /health"
        }
    })


# ============================================
# INICIAR SERVIDOR
# ============================================

def check_initial_config():
    print("\nVerificando configuração...")
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-...":
        print("    AVISO: Chave OpenAI não configurada")
    else:
        print(" OpenAI configurado")
    if not os.path.exists('index.html'):
        print("  index.html não encontrado")
    else:
        print(" Frontend encontrado")
    try:
        requests.get("http://localhost:1234/v1/models", timeout=3)
        print(" LM Studio detectado")
    except:
        print("    LM Studio não está a responder")


if __name__ == '__main__':
    check_initial_config()
    print(f"  • Interface:  http://localhost:5000/")
    print(f"  • API:        http://localhost:5000/analyze")
    print(f"  • Saúde:      http://localhost:5000/health")
    print("=" * 60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)