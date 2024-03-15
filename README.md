# Agenda Online

Plataforma para gerenciamento de compromissos com notificações via WhatsApp.

Este projeto é um sistema de agendamento online que permite aos usuários marcar, visualizar, editar e excluir compromissos. Utiliza **Flask** como framework backend em **Python**, **PostgreSQL** para gerenciamento de banco de dados e **JQuery** para melhor interatividade no frontend. As notificações dos compromissos são enviadas via WhatsApp utilizando a API do WhatsApp Business.

## 🛠 Ferramentas e Versões Utilizadas

- **Python**: `3.8.10`
- **Flask**: `2.0.1`
- **PostgreSQL**: `13`
- **JQuery**: `3.5.1`
- **psycopg2**: `2.8.6` (PostgreSQL adapter for Python)
- **python-dotenv**: `0.19.0` (Para gerenciar variáveis de ambiente)

## 🚀 Configuração Inicial

### Pré-Requisitos

- Python 3.8 ou superior instalado.
- PostgreSQL instalado.
- Um banco de dados em branco criado no PostgreSQL.

### Instalação e Execução

##### Clone o repositório:
```bash
git clone https://github.com/Rafael-720/Agenda-lembrete.git
```

## 💬 Uso da API Oficial do WhatsApp Cloud

Este projeto utiliza a API Oficial do WhatsApp Cloud para enviar notificações de compromissos. É necessário configurar a integração com a API do WhatsApp e cadastrar templates de mensagens no painel do WhatsApp Business API.

### Configuração da API do WhatsApp

1. Crie uma conta no Facebook Business Manager: Siga as instruções para configurar uma conta de negócios se você ainda não possui uma.
   
2. Configure o WhatsApp Business API: Dentro do Business Manager, navegue até a seção de configurações do WhatsApp e siga o processo para conectar sua conta do WhatsApp.

3. Obtenha as credenciais da API: Após a configuração, você receberá um `token` e um `WABA ID` que são necessários para enviar mensagens através da API.

### Cadastramento de Templates de Mensagem

1. Acesse o Painel do WhatsApp Business API: Navegue até a seção de gerenciamento de mensagens.

2. Crie Templates de Mensagem: Cada template de mensagem precisa ser aprovado pelo WhatsApp antes de ser usado. Siga as diretrizes do WhatsApp para criar e submeter seus templates para aprovação.

3. Use os Templates Aprovados no Projeto: Uma vez aprovados, você pode utilizar os nomes dos templates no seu código para enviar notificações de compromissos.

### 🛠 Configuração do Projeto para Enviar Notificações

Após ter suas credenciais da API e templates de mensagem aprovados, você precisa configurá-los no seu projeto:

1. Adicione suas Credenciais ao Arquivo .env: Inclua seu WA_TOKEN e WAID (WhatsApp Business Account ID) no arquivo .env na raiz do seu projeto.

```bash 
WA_TOKEN=seu_token_aqui
WAID=seu_waba_id_aqui
```
2. Modifique o Código para Usar os Templates: No código que envia as mensagens WhatsApp, referencie os nomes dos templates de mensagem aprovados ao construir o payload da requisição.

## 📡 Configuração do Webhook para Notificações do WhatsApp

O webhook é essencial para a interação em tempo real com a API do WhatsApp Cloud, permitindo receber notificações de eventos como mensagens recebidas, entregues, lidas, entre outros. Este projeto inclui a implementação de um webhook para esses propósitos.

### Configurando o Webhook

1. **Definindo o Endpoint do Webhook**: O arquivo `webhook.py` contém a implementação do webhook. Certifique-se de que o endpoint `/verify_token` esteja configurado para permitir a validação do webhook com a API do WhatsApp.

2. **Verificação do Webhook com a API do WhatsApp**: Para que o WhatsApp verifique e valide seu webhook, é necessário retornar um `challenge` quando a API do WhatsApp envia uma solicitação GET para o seu endpoint `/verify_token`. O código necessário já está implementado:

   ```python
   @app.route('/verify_token', methods=['GET'])
   def verificar_token():
       mode = request.args.get('hub.mode', '')
       challenge = request.args.get('hub.challenge', '')
       verify_token = request.args.get('hub.verify_token', '')

       if mode == 'subscribe' and verify_token == os.getenv('WA_TOKEN'):
           return challenge, 200
       else:
           print("Token de verificação inválido")
           return "Token de verificação inválido", 403
   ```


 **Envio de Mensagens:** Para enviar mensagens via WhatsApp, utilize o endpoint /send_message, que prepara e envia uma requisição à API do WhatsApp Cloud:

```python
@app.route('/send_message', methods=['POST'])
def send_message():
    # Implementação para enviar mensagens
```
Certifique-se de configurar corretamente os cabeçalhos e o payload conforme a documentação da API do WhatsApp.


### Testando o Webhook
Para testar se o seu webhook está corretamente configurado e funcionando com a API do WhatsApp Cloud:

1. **Envie uma Solicitação de Teste:** Use ferramentas como Postman ou cURL para enviar uma solicitação POST ao seu endpoint /send_message e verifique se a mensagem é recebida pelo destinatário.

2. **Verifique as Respostas do Webhook:** Envie mensagens para o seu número do WhatsApp Business e observe se os eventos correspondentes são recebidos pelo seu webhook, verificando os logs do servidor Flask.

### Ferramentas e Recursos Úteis

- **Flask**: [Documentação oficial do Flask](https://flask.palletsprojects.com/)
- **WhatsApp Business API**: [Documentação oficial da API do WhatsApp](https://developers.facebook.com/docs/whatsapp)

Ao seguir estas instruções, você poderá configurar e testar o webhook em seu projeto, permitindo uma integração eficiente com a API do WhatsApp Cloud para o envio de notificações e o processamento de mensagens recebidas.


## 🗄 Configuração do Banco de Dados

Este projeto utiliza PostgreSQL como sistema de gerenciamento de banco de dados. Siga as instruções abaixo para criar e configurar o banco de dados necessário para o projeto.

### Criação do Banco de Dados e Tabela

1. Acesse o terminal do PostgreSQL:
Abra o terminal do PostgreSQL com o comando psql ou através do seu cliente de banco de dados preferido.

2. Crie o Banco de Dados (se ainda não tiver criado):

```bash
CREATE DATABASE nome_do_seu_banco;
```
3. Crie a Tabela compromissos:
Execute o seguinte comando SQL para criar a tabela compromissos:

```bash
CREATE TABLE compromissos (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    data_hora_inicio TIMESTAMP NOT NULL,
    data_hora_fim TIMESTAMP NOT NULL,
    assunto VARCHAR(255) NOT NULL,
    projeto VARCHAR(255) NOT NULL,
    participante VARCHAR(255) NOT NULL,
    whatsapp_cliente VARCHAR(20) NOT NULL
);
```

## Backend

Instale as dependências

```bash
pip install -r requirements.txt
```

Inicie a aplicação Flask:

```bash
flask run
```

## Endpoints da API

`GET /compromissos:` Lista todos os compromissos.

`POST /compromissos:` Cadastra um novo compromisso.

`PUT /compromissos/:id:` Atualiza um compromisso existente pelo ID.

`DELETE /compromissos/:id:` Exclui um compromisso pelo ID.

## Principais Funcionalidades

`Agendamento de Compromissos`: Permite marcar novos compromissos, especificando detalhes como título, data, hora e participantes.

`Visualização de Compromissos`: Exibe todos os compromissos agendados em um formato fácil de visualizar.

`Edição e Exclusão de Compromissos`: Oferece opções para modificar ou remover compromissos existentes.

`Notificações via WhatsApp`: Envia notificações automáticas via WhatsApp para os participantes do compromisso, lembrando-os da data e hora agendadas.











