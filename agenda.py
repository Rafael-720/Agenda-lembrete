from flask import Flask, render_template, request, redirect, url_for, jsonify  # Importe jsonify para criar respostas JSON
import psycopg2
from dotenv import load_dotenv
import os  # Importar o módulo os
import requests  # Importar o módulo requests
import json  # Importar o módulo json
from datetime import datetime


app = Flask(__name__)

# Carregando variáveis de ambiente do arquivo .env no mesmo diretório
load_dotenv()

# Obtendo o token da API do WhatsApp a partir das variáveis de ambiente
wa_token = os.getenv('WA_TOKEN')
waid_token = os.getenv('WAID')

#numero_principal
marco = '' #coloque aqui seu numero do whatsapp exemplo: +5521982111111

COMPROMISSOS = {
    'NOVO_MARCO': 'novo_compromisso_marco',
    'NOVO_CLIENTE': 'novo_compromisso_cliente',
    'ALTERAR_MARCO': 'alterar_compromisso_marco',
    'ALTERAR_CLIENTE': 'alterar_compromisso_cliente',
    'EXCLUIR_MARCO': 'excluir_compromisso_marco',
    'EXCLUIR_CLIENTE': 'excluir_compromisso_cliente'
}





# Função para se conectar ao banco de dados
def connect_db():
    conn = psycopg2.connect(
        database="postgres", #nome do banco
        user="postgres",
        password="12345678",
        host="localhost",
        port="5432"
    )
    return conn

# Rota para a página inicial
@app.route('/')
def index():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM compromissos;")
    compromissos_raw = cur.fetchall()


    # Formatar as datas e os horários
    compromissos = []
    for c in compromissos_raw:
        nao_notificar_checked = True if c[7] == 'N/A' else False
        if nao_notificar_checked:
            whatsapp_cliente = 'N/A'
        else:
            whatsapp_cliente = formatar_whatsapp(c[7])
        formatted_compromisso = {
            'id': c[0],
            'titulo': c[1],
            'data_hora_inicio': c[2].strftime('%d/%m/%Y'),
            'data_hora_inicio_editar': c[2].strftime('%Y-%m-%dT%H:%M'),
            'data_hora_fim_editar': c[3].strftime('%Y-%m-%dT%H:%M'),
            'hora_inicio': c[2].strftime('%H:%M'),
            'data_hora_fim': c[3].strftime('%d/%m/%Y'),
            'hora_fim': c[3].strftime('%H:%M'),
            'assunto': c[4],
            'projeto': c[5],
            'participante': c[6],
            'whatsapp_cliente': whatsapp_cliente,
            'nao_notificar_checked': nao_notificar_checked
        }
        compromissos.append(formatted_compromisso)

    # Buscar projetos distintos
    cur.execute("SELECT DISTINCT projeto FROM compromissos;")
    projetos_distintos = [row[0] for row in cur.fetchall()]

    # Obter as datas e horários indisponíveis
    cur.execute("SELECT data_hora_inicio, data_hora_fim FROM compromissos;")
    datas_indisponiveis_raw = cur.fetchall()
    
    # Aqui, você pode formatar 'datas_indisponiveis_raw' da forma que for mais conveniente para o seu front-end
    datas_indisponiveis = [ {"inicio": inicio.strftime('%Y-%m-%dT%H:%M'), "fim": fim.strftime('%Y-%m-%dT%H:%M')} for inicio, fim in datas_indisponiveis_raw]


    cur.close()
    conn.close()
    return render_template('index.html', compromissos=compromissos, datas_indisponiveis=datas_indisponiveis, projetos_distintos=projetos_distintos)

# Rota para inserir um novo compromisso
@app.route('/inserir_compromisso', methods=['POST'])
def inserir_compromisso():
    titulo = request.form['titulo']
    data_hora_inicio = request.form['data_hora_inicio']
    data_hora_fim = request.form['data_hora_fim_completa']
    assunto = request.form['assunto']
    projeto = request.form['projeto']
    participante = request.form['participante']


    # Verificar se o checkbox 'nao_notificar' foi marcado
    nao_notificar = request.form.get('nao_notificar', 'off') == 'on' # 'on' se marcado, 'off' se não marcado


    if nao_notificar:
        whatsapp_cliente = 'N/A'  # Definir como "Não se aplica"
    else:
        whatsapp_cliente = request.form['whatsapp_cliente']
        whatsapp_cliente = whatsapp_cliente.replace(" ", "").replace("(", "").replace(")", "").replace("-", "")

   

    conn = connect_db()
    cur = conn.cursor()
    
    # Verificar se o horário está disponível
    cur.execute("""
    SELECT COUNT(*) FROM compromissos WHERE 
    (data_hora_inicio <= %s AND data_hora_fim >= %s) OR
    (data_hora_inicio <= %s AND data_hora_fim >= %s) OR
    (data_hora_inicio >= %s AND data_hora_fim <= %s);
    """, (data_hora_inicio, data_hora_inicio, data_hora_fim, data_hora_fim, data_hora_inicio, data_hora_fim))
    
    overlap_count = cur.fetchone()[0]

    if overlap_count == 0:
        # Insira o novo compromisso se o horário estiver disponível
        cur.execute("INSERT INTO compromissos (titulo, data_hora_inicio, data_hora_fim, assunto, projeto, participante, whatsapp_cliente) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                    (titulo, data_hora_inicio, data_hora_fim, assunto, projeto, participante, whatsapp_cliente))
        conn.commit()
        cur.close()
        conn.close()

        # Convertendo as strings para objetos datetime
        dt_inicio = datetime.fromisoformat(data_hora_inicio)
        dt_fim = datetime.fromisoformat(data_hora_fim)

        # Formatando os objetos datetime
        dia_inicio_format = dt_inicio.strftime('%d/%m/%Y')
        hora_inicio_format = dt_inicio.strftime('%H:%M')
        hora_fim_format = dt_fim.strftime('%H:%M')


        if not nao_notificar:
            # Notifique sobre o novo compromisso
            notificar_novo_compromisso(dia_inicio_format, hora_inicio_format, assunto, participante, COMPROMISSOS['NOVO_MARCO'], marco)#marco
            notificar_novo_compromisso(dia_inicio_format, hora_inicio_format, assunto, participante, COMPROMISSOS['NOVO_CLIENTE'], whatsapp_cliente)#cliente
        



        return redirect(url_for('index'))
    else:
        # Retornar uma mensagem de erro se o horário não estiver disponível
        cur.close()
        conn.close()
        return "Horário não disponível", 400



    


# Rota para excluir um compromisso
@app.route('/excluir_compromisso/<int:compromisso_id>')
def excluir_compromisso(compromisso_id):
    

    # Conecte ao banco de dados e obtenha as informações do compromisso
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM compromissos WHERE id = %s;", (compromisso_id,))
    compromisso = cur.fetchone()

    # Extraia os detalhes do compromisso
    if compromisso:
        data_hora_inicio = compromisso[2]
        data_hora_fim = compromisso[3]
        assunto = compromisso[4]
        participante = compromisso[6]
        whatsapp_cliente = compromisso[7]

        # Formatando os objetos datetime
        dia_inicio_format = data_hora_inicio.strftime('%d/%m/%Y')
        hora_inicio_format = data_hora_inicio.strftime('%H:%M')
        hora_fim_format = data_hora_fim.strftime('%H:%M')

        # Verificar se o whatsapp_cliente é "N/A" ou algum valor que indique que não se aplica
        if whatsapp_cliente not in ["N/A"]:
            # Notifique sobre a exclusão do compromisso
            notificar_novo_compromisso(dia_inicio_format, hora_inicio_format, assunto, participante, COMPROMISSOS['EXCLUIR_MARCO'], marco)#marco
            notificar_novo_compromisso(dia_inicio_format, hora_inicio_format, assunto, participante, COMPROMISSOS['EXCLUIR_CLIENTE'], whatsapp_cliente)#cliente




        # Agora, exclua o compromisso
        cur.execute("DELETE FROM compromissos WHERE id = %s;", (compromisso_id,))
        conn.commit()
        
    else:
        print("Compromisso não encontrado")
        
    cur.close()
    conn.close()
    
    return redirect(url_for('index'))


    



# Rota para salvar as alterações após a edição de um compromisso
@app.route('/salvar_edicao/', methods=['POST'])
def salvar_edicao():
    
    compromisso_id = request.form['compromissoId']
    novo_titulo = request.form['tituloEditar']
    novo_data_hora_inicio = request.form['data_hora_inicioEditar']
    novo_data_hora_fim = request.form['data_hora_fim_completaEditar']
    novo_assunto = request.form['assuntoEditar']
    novo_projeto = request.form['projetoEditar']
    novo_participante = request.form['participanteEditar']
    
    conn = connect_db()
    cur = conn.cursor()


   
    # Verificar se o checkbox 'nao_notificarEditar' foi marcado
    nao_notificar = request.form.get('nao_notificar', 'off') == 'on'

    if nao_notificar:
        novo_whatsapp_cliente = 'N/A'  # Definir como "Não se aplica"  
    else:
        # Removendo a formatação do número do WhatsApp antes de salvar no banco de dados
        novo_whatsapp_cliente = desformatar_whatsapp(request.form['whatsapp_clienteEditar'])



    

     # Verificar se o horário está disponível
    cur.execute("""
    SELECT COUNT(*) FROM compromissos WHERE 
    ((data_hora_inicio <= %s AND data_hora_fim >= %s) OR
    (data_hora_inicio <= %s AND data_hora_fim >= %s) OR
    (data_hora_inicio >= %s AND data_hora_fim <= %s)) AND
    id != %s;
    """, (novo_data_hora_inicio, novo_data_hora_inicio, novo_data_hora_fim, novo_data_hora_fim, novo_data_hora_inicio, novo_data_hora_fim, compromisso_id))
    
    overlap_count = cur.fetchone()[0]

    if overlap_count == 0:
        # Altere o compromisso se o horário estiver disponível
        cur.execute("UPDATE compromissos SET titulo = %s, data_hora_inicio = %s, data_hora_fim = %s, assunto = %s, projeto = %s, participante = %s, whatsapp_cliente = %s WHERE id = %s;",
                    (novo_titulo, novo_data_hora_inicio, novo_data_hora_fim, novo_assunto, novo_projeto, novo_participante, novo_whatsapp_cliente, compromisso_id))
        conn.commit()
        cur.close()
        conn.close()
        
        # Convertendo as strings para objetos datetime
        dt_inicio = datetime.fromisoformat(novo_data_hora_inicio)
        dt_fim = datetime.fromisoformat(novo_data_hora_fim)

        # Formatando os objetos datetime
        dia_inicio_format = dt_inicio.strftime('%d/%m/%Y')
        hora_inicio_format = dt_inicio.strftime('%H:%M')
        hora_fim_format = dt_fim.strftime('%H:%M')

        if not nao_notificar:
            # Chame a função do webhook para notificar sobre o novo compromisso
            notificar_novo_compromisso(dia_inicio_format, hora_inicio_format, novo_assunto, novo_participante, COMPROMISSOS['ALTERAR_MARCO'], marco)#marco
            notificar_novo_compromisso(dia_inicio_format, hora_inicio_format, novo_assunto, novo_participante, COMPROMISSOS['ALTERAR_CLIENTE'], novo_whatsapp_cliente)#cliente
       

        return redirect(url_for('index'))
    else:   
        # Retornar uma mensagem de erro se o horário não estiver disponível
        cur.close()
        conn.close()
        return "Horário não disponível", 400

        

def formatar_whatsapp(numero):
    # Verificar se o número já está formatado
    if "(" in numero and ")" in numero and "-" in numero:
        return numero
    
    # Remover o +55 do início, se presente
    if numero.startswith('+55'):
        numero = numero[3:]
    
    # Inserir os parênteses, espaço e traço
    return "({}) {}-{}".format(numero[:2], numero[2:7], numero[7:])


def desformatar_whatsapp(numero_formatado):
    # Remover todos os caracteres não numéricos
    numero = ''.join(filter(str.isdigit, numero_formatado))
    # Adicionar o prefixo +55
    return '+55' + numero






# Função para notificar sobre o novo compromisso via webhook 1-participante|2- assunto|3- data|4- hora
def notificar_novo_compromisso(data_hora_inicio, data_hora_fim, assunto, participante, modelo, numero):
    #marco: novo_compromisso_marco | alterar_compromisso_marco | excluir_compromisso_marco
    #cliente: novo_compromisso_cliente | alterar_compromisso_cliente | excluir_compromisso_cliente





    # Carregar variáveis de ambiente do arquivo .env
    #load_dotenv()

    url = 'http://localhost:5000/send_message'
    headers = {'Content-Type': 'application/json'}

    # Configurar cabeçalhos da API
    #headers = {
    #    'Content-Type': 'application/json',
    #    'Authorization': f"Bearer {os.getenv('WA_TOKEN')}"
    #}
    


    # Payload da mensagem (Dados da mensagem)
    payload = {
        "to": numero, #+5521982181146
        "template_name": modelo,  # Este é o nome do modelo aprovado alerta|alterar_compromisso|excluir_compromisso
        "components": [
            {
                "type": "body",
                "parameters": [
                    {
                        "type": "text",
                        "text": participante  # participante {{1}}
                    },
                    {
                        "type": "text",
                        "text": assunto  # assunto {{2}}
                    },
                    {
                        "type": "text",
                        "text": data_hora_inicio  # data {{3}}
                    },
                    {
                        "type": "text",
                        "text": data_hora_fim  # hora {{4}}
                    }
                ]
            }
        ]
    }

    

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("Notificação enviada com sucesso!")
    else:
        print("Falha ao enviar a notificação. {response.content}")


#@app.route('/verify_token', methods=['GET'])
#def verificar_token():
#    mode = request.args.get('hub.mode', '')
#    challenge = request.args.get('hub.challenge', '')
#    verify_token = request.args.get('hub.verify_token', '')

    # Substitua 'SEU_TOKEN_DE_VERIFICACAO' pelo token que você configurou na API
#    if mode == 'subscribe' and verify_token == wa_token:
#        return challenge, 200  # Retorne o valor de 'hub.challenge' para validar
#    else:
#        print("Token de verificação inválido")
#        return "Token de verificação inválido", 403



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
