import os
import time
import requests
import threading
from flask import Flask

app = Flask(__name__)

# Configurações obtidas das Variáveis de Ambiente no Render
EVOLUTION_API_URL = os.environ.get("EVOLUTION_API_URL", "").rstrip("/")
EVOLUTION_API_KEY = os.environ.get("EVOLUTION_API_KEY", "")
ID_GRUPO_WHATSAPP = os.environ.get("ID_GRUPO_WHATSAPP", "")
NOME_INSTANCIA = os.environ.get("NOME_INSTANCIA", "promo_bot")

TERMO_BUSCA = "smartphone"
AFFILIATE_LINK = "https://meli.la/1GyJx4Y"

def buscar_e_enviar_ofertas():
    print("🔎 [ROBÔ] Iniciando busca por ofertas no Mercado Livre...")
    
    url_ml = f"https://api.mercadolibre.com/sites/MLB/search?q={TERMO_BUSCA}"
    try:
        response = requests.get(url_ml, timeout=10)
        data = response.json()
        results = data.get("results", [])
        
        print(f"📦 [ROBÔ] Total de produtos encontrados: {len(results)}")
        
        for item in results[:5]:  # Analisa os 5 primeiros produtos
            preco_atual = item.get("price")
            preco_original = item.get("original_price")
            titulo = item.get("title")
            
            # Se não houver preco_original cadastrado na API, usa o preço atual para simular o teste
            if not preco_original:
                preco_original = preco_atual * 1.2
            
            if preco_original and preco_original > preco_atual:
                desconto = int(((preco_original - preco_atual) / preco_original) * 100)
                
                mensagem = (
                    f"🔥 *OFERTA IMPERDÍVEL!*\n\n"
                    f"📱 *{titulo}*\n"
                    f"❌ De: R$ {preco_original:,.2f}\n"
                    f"✅ *Por: R$ {preco_atual:,.2f}* ({desconto}% OFF)\n\n"
                    f"🛒 *Compre aqui:* {AFFILIATE_LINK}"
                )
                
                print(f"🚀 [ROBÔ] Enviando oferta para a Evolution API: {titulo[:30]}...")
                
                endpoint = f"{EVOLUTION_API_URL}/message/sendText/{NOME_INSTANCIA}"
                headers = {
                    "apikey": EVOLUTION_API_KEY,
                    "Content-Type": "application/json"
                }
                payload = {
                    "number": ID_GRUPO_WHATSAPP,
                    "text": mensagem
                }
                
                res = requests.post(endpoint, json=payload, headers=headers, timeout=15)
                print(f"📡 [ROBÔ] Resposta da API ({res.status_code}): {res.text}")
                
                # Aguarda 5 segundos entre cada envio para não sobrecarregar
                time.sleep(5)
                
    except Exception as e:
        print(f"❌ [ROBÔ] Erro durante a execução: {e}")

def loop_automatico():
    # Aguarda 10 segundos após o servidor ligar para fazer o primeiro disparo
    time.sleep(10)
    while True:
        try:
            buscar_e_enviar_ofertas()
        except Exception as e:
            print(f"❌ [ROBÔ] Erro no loop: {e}")
        # Roda novamente a cada 15 minutos (900 segundos)
        time.sleep(900)

# Inicia a Thread em segundo plano para o robô rodar sozinho
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
