from flask import Flask, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

wa_token = os.getenv('WA_TOKEN')
waid_token = os.getenv('WAID')

@app.route('/send_message', methods=['POST'])
def send_message():
    message_data = request.json

    # Configurar cabeçalhos da API
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {wa_token}"
    }


    # Validação do payload
    if not message_data or 'to' not in message_data or 'body' not in message_data:
        print("Payload inválido.")
        return "Payload inválido", 400

    # Defina um esquema padrão para o payload baseado nos dados recebidos.
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": message_data['to'],
        "type": "template",
        "template": {
            "name": message_data['template_name'],
            "language": {
                "code": "pt_BR"
            },
            "components": message_data['components']
        }
    }

    

    response = requests.post(
        f"https://graph.facebook.com/v17.0/{waid_token}/messages",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        print("Notificação enviada com sucesso!")
    else:
        print("Falha ao enviar a notificação. {response.content}")



@app.route('/verify_token', methods=['GET'])
def verificar_token():
    mode = request.args.get('hub.mode', '')
    challenge = request.args.get('hub.challenge', '')
    verify_token = request.args.get('hub.verify_token', '')

    # Substitua 'SEU_TOKEN_DE_VERIFICACAO' pelo token que você configurou na API
    if mode == 'subscribe' and verify_token == wa_token:
        return challenge, 200  # Retorne o valor de 'hub.challenge' para validar
    else:
        print("Token de verificação inválido")
        return "Token de verificação inválido", 403

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
