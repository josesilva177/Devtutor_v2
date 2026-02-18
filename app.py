"""
TUTOR DE CÓDIGO - SISTEMA HÍBRIDO IA
Modo Local: LM Studio | Modo Online: OpenAI GPT-3.5
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import time
import os
from datetime import datetime

# ============================================
# CONFIGURAÇÃO - COLE SUA CHAVE OPENAI AQUI ↓
# ============================================

# CHAVE OPENAI 
OPENAI_API_KEY = "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"


# Configurações LM Studio (Local)
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
LM_MODEL = "deepseek-coder"

# Configurações OpenAI (Online)
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-3.5-turbo"


app = Flask(__name__)
CORS(app)

# ============================================
# FUNÇÕES DE ANÁLISE SEPARADAS
# ============================================

def analyze_with_local(code):
    """Usa LM Studio local"""
    try:
        start_time = time.time()
        
        prompt = f"""Como tutor de programação responda essa pergunta: {code}"""

        print(f"    Enviando para LM Studio...")
        
        response = requests.post(
            LM_STUDIO_URL,
            json={
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=300
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            analysis = result["choices"][0]["message"]["content"]
            tokens = result.get("usage", {}).get("total_tokens", 0)
            
            print(f"    LM Studio respondeu em {elapsed:.1f}s")
            
            return {
                "success": True,
                "analysis": analysis,
                "provider": "LM Studio (Local)",
                "model": LM_MODEL,
                "response_time": f"{elapsed:.1f}s",
                "tokens_used": tokens,
            }
        else:
            print(f"    LM Studio erro {response.status_code}")
            return {
                "success": False,
                "error": f"LM Studio erro {response.status_code}",
                "provider": "LM Studio",
                "response_time": f"{elapsed:.1f}s"
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "LM Studio demorou muito (>120s)",
            "provider": "LM Studio"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro LM Studio: {str(e)}",
            "provider": "LM Studio"
        }


def analyze_with_openai(code):
    """Usa OpenAI GPT-3.5 online"""
    try:
        start_time = time.time()
        
        prompt = f"""Como tutor de programação responda essa pergunta: {code}"""

        print(f"    Enviando para OpenAI...")

        response = requests.post(
            OPENAI_URL,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": OPENAI_MODEL,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            analysis = result["choices"][0]["message"]["content"]
            tokens = result["usage"]["total_tokens"]
            cost = tokens * 0.0000015
            
            print(f"    OpenAI respondeu em {elapsed:.1f}s")
            print(f"    {tokens} tokens (~${cost:.4f})")
            
            return {
                "success": True,
                "analysis": analysis,
                "provider": "OpenAI GPT-3.5",
                "model": OPENAI_MODEL,
                "response_time": f"{elapsed:.1f}s",
                "tokens_used": tokens,
                "cost": f"${cost:.4f}",
                "note": f"~{tokens} tokens utilizados"
            }
            
        else:
            print(f"    OpenAI erro {response.status_code}")
            error_msg = response.text[:200] if response.text else "Sem detalhes"
            return {
                "success": False,
                "error": f"OpenAI erro {response.status_code}",
                "provider": "OpenAI",
                "details": error_msg
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "OpenAI demorou muito (>30s)",
            "provider": "OpenAI"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro OpenAI: {str(e)}",
            "provider": "OpenAI"
        }


# ============================================
# ROTAS DO SISTEMA
# ============================================

@app.route('/')
def serve_index():
    """Serve o arquivo index.html"""
    return send_from_directory('.', 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """Serve outros arquivos estáticos"""
    return send_from_directory('.', filename)


@app.route('/health')
def health_check():
    """Verifica saúde de todos os serviços"""
    services = {
        "flask": " Online",
        "lm_studio": " Offline",
        "openai": " Offline"
    }

    # Testar LM Studio
    try:
        lm_test = requests.get("http://localhost:1234/v1/models", timeout=5)
        services["lm_studio"] = " Online" if lm_test.status_code == 200 else " Offline"
    except:
        services["lm_studio"] = " Offline"

    # Testar OpenAI
    try:
        test_response = requests.post(
            OPENAI_URL,
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": OPENAI_MODEL,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1
            },
            timeout=5
        )
        services["openai"] = " Online" if test_response.status_code == 200 else " Offline"
    except:
        services["openai"] = " Offline"

    return jsonify({
        **services,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "system": "Tutor de Código Híbrido",
        "modes_available": ["local", "online"]
    })


@app.route('/analyze', methods=['POST'])
def analyze_code():
    """Rota principal - escolhe a melhor IA"""
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        mode = data.get('mode', 'local')  # local, online

        if not code:
            return jsonify({"success": False, "error": "Código vazio"}), 400
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}]  Nova análise")
        print(f"   Modo: {mode.upper()}")
        print(f"   Tamanho: {len(code)} caracteres")
        
        result = None
        
        # LÓGICA DE ESCOLHA
        if mode == 'local':
            print("    Usando IA Local (LM Studio)...")
            result = analyze_with_local(code)
            
        elif mode == 'online':
            print("    Usando IA Online (OpenAI)...")
            result = analyze_with_openai(code)
        
        else:
            return jsonify({"success": False, "error": "Modo inválido. Use 'local' ou 'online'"}), 400
        
        # Log final
        if result and result.get('success'):
            provider = result.get('provider', 'IA')
            time_taken = result.get('response_time', 'N/A')
            print(f"   {provider} - {time_taken}")
        elif result:
            print(f"    {result.get('provider', 'Sistema')} falhou")
        
        return jsonify(result) if result else jsonify({
            "success": False,
            "error": "Erro no processamento"
        })
        
    except Exception as e:
        print(f"Erro na rota /analyze: {e}")
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500


@app.route('/system/info')
def system_info():
    """Informações do sistema"""
    return jsonify({
        "system": "Tutor de Código Híbrido - PAP",
        "version": "1.0",
        "author": "Seu Nome",
        "architecture": {
            "local": "LM Studio + DeepSeek Coder",
            "online": "OpenAI GPT-3.5 Turbo API",
            "modes": ["auto", "local", "online"]
        },
        "cost_estimation": {
            "local": "Gratuito (offline)",
            "online": "~$0.0015 por 1000 tokens (GPT-3.5)"
        },
        "api_endpoints": {
            "web_interface": "GET /",
            "analyze_code": "POST /analyze",
            "health_check": "GET /health",
            "system_info": "GET /system/info"
        }
    })


# ============================================
# CONFIGURAÇÃO INICIAL
# ============================================

def check_initial_config():
    """Verifica configurações iniciais"""
    print("\nVerificando configuração...")

    # Verificar chave OpenAI
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-...":
        print("  AVISO: Chave OpenAI não configurada")
        print("   O modo 'online' não funcionará")
    else:
        print("OpenAI configurado")

    # Verificar arquivo index.html
    if not os.path.exists('index.html'):
        print("index.html não encontrado na pasta")
    else:
        print(" Frontend encontrado")

    # Verificar LM Studio
    try:
        requests.get("http://localhost:1234/v1/models", timeout=3)
        print(" LM Studio detectado")
    except:
        print("  LM Studio não está respondendo")
        print("   Execute LM Studio e inicie o servidor local")


# ============================================
# INICIAR SERVIDOR
# ============================================

if __name__ == '__main__':
    check_initial_config()

    print("\n" + "=" * 60)
    print("SISTEMA PRONTO PARA USO")
    print("=" * 60)
    print("Endpoints:")
    print(f"  • Interface:  http://localhost:5000/")
    print(f"  • API:        http://localhost:5000/analyze")
    print(f"  • Saúde:      http://localhost:5000/health")
    print(f"  • Info:       http://localhost:5000/system/info")
    print("\n ")
    print("\nTeste rápido:")
    print("  . Acesse http://localhost:5000/")
    print("=" * 60 + "\n")

    app.run(
        host='0.0.0.0',  # Aceita conexões de qualquer interface
        port=5000,
        debug=True,
        threaded=True
    )
