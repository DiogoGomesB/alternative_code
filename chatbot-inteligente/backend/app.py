from flask import Flask, request, jsonify, session
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
app.secret_key = 'Sua API key aqui!'  # Mude para algo seguro

# Configurar o CORS
CORS(app, origins="*")

def chat_with_huggingface(messages):
    """
    Usa a API gratuita da Hugging Face - sem necessidade de token
    """
    # Pega apenas a última mensagem do usuário para simplificar
    last_user_message = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            last_user_message = msg["content"]
            break
    
    # URL da API - usando um modelo conversacional gratuito
    url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
    
    payload = {
        "inputs": last_user_message,
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0.7,
            "do_sample": True,
            "pad_token_id": 50256
        }
    }
    
    try:
        # Primeira tentativa
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 503:
            # Modelo ainda carregando, espera um pouco
            print("Modelo carregando, aguardando...")
            time.sleep(10)
            response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                
                # Remove a entrada original da resposta
                if last_user_message in generated_text:
                    assistant_response = generated_text.replace(last_user_message, "").strip()
                else:
                    assistant_response = generated_text.strip()
                
                # Se ficou muito curto, usa uma resposta padrão
                if len(assistant_response) < 3:
                    assistant_response = "Interessante! Pode me contar mais sobre isso?"
                
                return assistant_response
            
        # Se chegou até aqui, algo deu errado
        return "Desculpe, estou tendo dificuldades para responder agora. Tente novamente!"
        
    except requests.exceptions.Timeout:
        return "A resposta está demorando mais que o esperado. Tente novamente!"
    except Exception as e:
        print(f"Erro na API: {e}")
        return "Ops! Algo deu errado. Tente reformular sua pergunta."

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "Mensagem não pode ser vazia"}), 400

    # Recupera histórico da sessão (limitando a 10 mensagens para não sobrecarregar)
    messages = session.get("messages", [])
    
    # Adiciona a mensagem do usuário ao histórico
    messages.append({"role": "user", "content": user_message})
    
    # Mantém apenas as últimas 10 mensagens
    if len(messages) > 10:
        messages = messages[-10:]

    try:
        # Chama a API da Hugging Face
        assistant_message = chat_with_huggingface(messages)
        
        # Adiciona resposta do assistente ao histórico
        messages.append({"role": "assistant", "content": assistant_message})
        session["messages"] = messages

        return jsonify({"reply": assistant_message})
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("messages", None)
    return jsonify({"message": "Histórico resetado"})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "OK", 
        "message": "API funcionando com Hugging Face!",
        "ai_provider": "Hugging Face (microsoft/DialoGPT-medium)"
    })
    
if __name__ == "__main__":
    app.run(debug=True)