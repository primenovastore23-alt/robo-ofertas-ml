import os
import time
import json
import urllib.request
import threading
from flask import Flask

app = Flask(__name__)

# Configurações obtidas das Variáveis de Ambiente no Render
EVOLUTION_API_URL = os.environ.get("EVOLUTION_API_URL", "").strip().rstrip("/")
EVOLUTION_API_KEY = os.environ.get("EVOLUTION_API_KEY", "").strip()
ID_GRUPO_WHATSAPP = os.environ.get("ID_GRUPO_WHATSAPP", "").strip()
NOME_INSTANCIA = os.environ.get("NOME_INSTANCIA", "promo_bot").strip()

AFFILIATE_LINK = "https://meli.la/1GyJx4Y"

OFERTAS_BACKUP = [
    {"title": "Smartphone Samsung Galaxy S23 5G 256GB", "price": 2899.00, "original_price": 4499.00},
    {"title": "Smartphone Motorola Edge 40 Neo 256GB", "price": 1699.00, "original_price": 2799.00},
    {"title": "Smartphone Xiaomi Redmi Note 13 256GB", "price": 1249.00, "original_price": 1999.00},
    {"title": "Smartphone Apple iPhone 13 128GB", "price": 3699.00, "original_price": 5499.00}
]

def buscar_e_enviar_ofertas():
    print("🔎 [ROBÔ] Iniciando busca por ofertas no Mercado Livre...")
    
    url_ml = "https://api.mercadolibre.com/sites/MLB/search?q=celular&limit=5"
    results = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    
    try:
        req = urllib.request.Request(url_ml, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            results = data.get("results", [])
            print(f"📦 [ROBÔ] Total de produtos da API: {len(results)}")
    except Exception as e:
        print(f"⚠️ [ROBÔ] API bloqueou ({e}). Usando lista de ofertas selecionadas!")
        results = OFERTAS_BACKUP

    for item in results[:5]:
        preco_atual = item.get("price", 0)
        preco_original = item.get("original_price")
        
        if not preco_original or preco_original <= preco_atual:
            preco_original = preco_atual * 1.25

        titulo = item.get("title", "Smartphone em Promoção")
        desconto = int(((preco_original - preco_atual) / preco_original) * 100)
        
        mensagem = (
            f"🔥 *OFERTA IMPERDÍVEL!*\n\n"
            f"📱 *{titulo}*\n"
            f"❌ De: R$ {preco_original:,.2f}\n"
            f"✅ *Por: R$ {preco_atual:,.2f}* ({desconto}% OFF)\n\n"
            f"🛒 *Compre aqui:* {AFFILIATE_LINK}"
        )
        
        print(f"🚀 [ROBÔ] Enviando oferta para o WhatsApp: {titulo[:30]}...")
        
        # Constrói o endpoint limpo garantindo a rota /message/sendText/{instancia}
        endpoint = f"{EVOLUTION_API_URL}/message/sendText/{NOME_INSTANCIA}"
        
        payload = json.dumps({
            "number": ID_GRUPO_WHATSAPP,
            "text": mensagem
        }).encode('utf-8')
        
        req_api = urllib.request.Request(
            endpoint,
            data=payload,
            headers={
                "apikey": EVOLUTION_API_KEY,
                "Content-Type": "application/json"
            },
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req_api, timeout=15) as res_api:
                res_body = res_api.read().decode('utf-8')
                print(f"📡 [ROBÔ] Sucesso! Resposta da Evolution API ({res_api.status}): {res_body}")
        except Exception as err_api:
            print(f"❌ [ROBÔ] Erro ao enviar para Evolution API (URL tentada: {endpoint}): {err_api}")
        
        time.sleep(5)

def loop_automatico():
    time.sleep(10)
    while True:
        try:
            buscar_e_enviar_ofertas()
        except Exception as e:
            print(f"❌ [ROBÔ] Erro no loop: {e}")
        time.sleep(900)

threading.Thread(target=loop_automatico, daemon=True).start()

@app.route("/")
def home():
    return "Robô de Ofertas do Mercado Livre está Ativo e Rodando!"

@app.route("/rodar")
def rodar_manual():
    print("⚡ [ROBÔ] Disparo manual acionado via rota /rodar!")
    threading.Thread(target=buscar_e_enviar_ofertas).start()
    return "Busca e envio iniciados com sucesso! Verifique os logs do Render e o seu grupo do WhatsApp."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
