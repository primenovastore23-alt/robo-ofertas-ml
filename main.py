import requests
import time
import os

# Configurações obtidas das Variáveis de Ambiente do Render
MEU_LINK_AFILIADO = os.getenv("MEU_LINK_AFILIADO", "https://meli.la/1GyJx4Y")
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
ID_GRUPO_WHATSAPP = os.getenv("ID_GRUPO_WHATSAPP")
INSTANCIA_WHATSAPP = "promo_bot"

TERMO_BUSCA = "oferta do dia"
produtos_postados = set()

def buscar_promocoes_ml(query):
    url = f"https://api.mercadolivre.com/sites/MLB/search?q={query}&limit=10"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        return resposta.json().get("results", [])
    return []

def enviar_mensagem_whatsapp(texto):
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
        response = requests.post(endpoint, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            print("Mensagem enviada com sucesso para o WhatsApp!")
        else:
            print(f"Erro ao enviar: {response.text}")
    except Exception as e:
        print(f"Erro na ligação: {e}")

def executar_bot():
    print("Robô de Ofertas iniciado...")
    produtos = buscar_promocoes_ml(TERMO_BUSCA)
    
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
            
            print(f"Nova promoção: {titulo}")
            enviar_mensagem_whatsapp(mensagem)
            produtos_postados.add(item_id)
            time.sleep(30)

if __name__ == "__main__":
    while True:
        executar_bot()
        print("Aguardando 15 minutos para a próxima busca...")
        time.sleep(900)
