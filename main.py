import requests
import time
import os
import threading
from flask import Flask

# Servidor Web mínimo para satisfazer o Render (plano Free Web Service)
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Robô de Ofertas Mercado Livre está rodando com sucesso!", 200
@app.route('/rodar')
def rodar_manual():
    # Chame aqui a sua função de buscar ofertas
    buscar_e_enviar_ofertas()
    return "Busca executada com sucesso!"

def rodar_servidor_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Configurações obtidas das Variáveis de Ambiente
MEU_LINK_AFILIADO = os.getenv("MEU_LINK_AFILIADO", "https://meli.la/1GyJx4Y")
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
ID_GRUPO_WHATSAPP = os.getenv("ID_GRUPO_WHATSAPP")
INSTANCIA_WHATSAPP = "promo_bot"

TERMO_BUSCA = "smartphone"
produtos_postados = set()

def buscar_promocoes_ml(query):
    url = f"https://api.mercadolivre.com/sites/MLB/search?q={query}&limit=10"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        resposta = requests.get(url, headers=headers, timeout=10)
        if resposta.status_code == 200:
            return resposta.json().get("results", [])
    except Exception as e:
        print(f"Aviso ao consultar Mercado Livre: {e}")
    return []

def enviar_mensagem_whatsapp(texto):
    if not EVOLUTION_API_URL or not ID_GRUPO_WHATSAPP:
        print("Erro: Variáveis do WhatsApp não configuradas.")
        return
        
    endpoint = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCIA_WHATSAPP}"
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "number": ID_GRUPO_WHATSAPP,
        "options": {
            "delay": 1200,
            "presence": "composing"
        },
        "text": texto
    }
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
        if response.status_code in [200, 201]:
            print("Mensagem enviada com sucesso para o WhatsApp!")
        else:
            print(f"Erro ao enviar mensagem: {response.text}")
    except Exception as e:
        print(f"Erro na ligação com WhatsApp: {e}")

def loop_do_robo():
    print("Robô de Ofertas iniciado...")
    while True:
        try:
            produtos = buscar_promocoes_ml(TERMO_BUSCA)
            if produtos:
                for item in produtos:
                    item_id = item.get("id")
                    if item_id in produtos_postados:
                        continue
                        
                    titulo = item.get("title")
                    preco_original = item.get("original_price")
                    preco_atual = item.get("price")
                    
                    if preco_original and preco_original > preco_atual:
                        desconto = int(((preco_original - preco_atual) / preco_original) * 100)
                        
                        mensagem = (
                            f"🔥 *OFERTA IMPERDÍVEL NO MERCADO LIVRE!* ({desconto}% OFF)\n\n"
                            f"📦 *{titulo}*\n"
                            f"❌ De: R$ {preco_original:.2f}\n"
                            f"✅ *Por: R$ {preco_atual:.2f}*\n\n"
                            f"🛒 *Compre pelo link:* {MEU_LINK_AFILIADO}"
                        )
                        
                        print(f"Nova promoção encontrada: {titulo}")
                        enviar_mensagem_whatsapp(mensagem)
                        produtos_postados.add(item_id)
                        time.sleep(30)
        except Exception as e:
            print(f"Erro no loop do robô: {e}")
            
        print("Aguardando 15 minutos para a próxima busca...")
        time.sleep(900)

if __name__ == "__main__":
    # Inicia a busca contínua em segundo plano
    threading.Thread(target=loop_do_robo, daemon=True).start()
    # Inicia o servidor web na porta exigida pelo Render
    rodar_servidor_web()
