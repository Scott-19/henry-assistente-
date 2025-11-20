# HENRY BUSINESS - COM DEEPSEEK INTEGRADO
from flask import Flask, jsonify, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ================= CONFIGURAÇÃO =================
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
print(f"🔑 DeepSeek Configurado: {'✅' if DEEPSEEK_API_KEY else '❌'}")

# Database em memória
negocios = {}
transacao_id_counter = 1

# ================= SERVIÇO DEEPSEEK =================
def analisar_com_deepseek(dados_negocio):
    """Análise com IA - mas funciona mesmo se API falhar"""
    if not DEEPSEEK_API_KEY:
        return "🔧 Configure a DEEPSEEK_API_KEY no Render"
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        prompt = f"""
        Analise este negócio de Moçambique:

        NEGÓCIO: {dados_negocio['nome']}
        SETOR: {dados_negocio['setor']}
        LOCAL: {dados_negocio['localizacao']}

        DADOS:
        - Vendas: {dados_negocio['vendas_total']} MT
        - Custos: {dados_negocio['custos_total']} MT  
        - Lucro: {dados_negocio['lucro_liquido']} MT
        - Margem: {dados_negocio['margem_lucro']}

        Forneça análise prática em português.
        """
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system", 
                    "content": "Você é Henry, assistente empresarial moçambicano. Seja prático e direto."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 800
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        return response.json()['choices'][0]['message']['content']
        
    except Exception as e:
        # Fallback - análise básica se API falhar
        return f"📊 Análise Básica: Lucro {dados_negocio['lucro_liquido']} MT | Margem {dados_negocio['margem_lucro']} | Saúde: {dados_negocio['saude']}"

# ================= ROTAS PRINCIPAIS =================
@app.route('/')
def home():
    return jsonify({
        "message": "🚀 Henry Business Assistant - COM IA!",
        "status": "✅ Operacional", 
        "deepseek": "✅ Integrado" if DEEPSEEK_API_KEY else "⏳ Configurar",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "deepseek_configurado": bool(DEEPSEEK_API_KEY),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/criar-negocio', methods=['POST'])
def criar_negocio():
    try:
        data = request.get_json() or {}
        
        negocio_id = str(len(negocios) + 1)
        negocios[negocio_id] = {
            'id': negocio_id,
            'nome': data.get('nome', 'Meu Negócio'),
            'setor': data.get('setor', 'Geral'),
            'localizacao': data.get('localizacao', 'Maputo'),
            'transacoes': [],
            'criado_em': datetime.now().isoformat()
        }
        
        return jsonify({
            "success": True,
            "negocio_id": negocio_id,
            "message": "✅ Negócio criado!"
        })
        
    except Exception:
        return jsonify({"success": False, "message": "Erro ao criar negócio"}), 500

@app.route('/adicionar-transacao/<negocio_id>', methods=['POST'])
def adicionar_transacao(negocio_id):
    try:
        if negocio_id not in negocios:
            return jsonify({"error": "Negócio não encontrado"}), 404
        
        data = request.get_json() or {}
        global transacao_id_counter
        
        transacao = {
            'id': transacao_id_counter,
            'valor': float(data.get('valor', 0)),
            'tipo': data.get('tipo', 'venda'),
            'categoria': data.get('categoria', 'outros'),
            'data': datetime.now().isoformat()
        }
        
        negocios[negocio_id]['transacoes'].append(transacao)
        transacao_id_counter += 1
        
        return jsonify({
            "success": True,
            "message": f"✅ Transação de {transacao['valor']} MT registrada!"
        })
        
    except Exception:
        return jsonify({"success": False, "message": "Erro na transação"}), 500

@app.route('/analisar/<negocio_id>')
def analisar_negocio(negocio_id):
    try:
        if negocio_id not in negocios:
            return jsonify({"error": "Negócio não encontrado"}), 404
        
        negocio = negocios[negocio_id]
        transacoes = negocio['transacoes']
        
        # Cálculos básicos
        vendas = sum(t['valor'] for t in transacoes if t['tipo'] == 'venda')
        custos = sum(t['valor'] for t in transacoes if t['tipo'] == 'custo')
        lucro = vendas - custos
        margem = (lucro / vendas * 100) if vendas > 0 else 0
        saude = "✅ Boa" if margem > 20 else "⚠️ Atenção" if margem > 0 else "🔴 Crítica"
        
        dados_analise = {
            'nome': negocio['nome'],
            'setor': negocio['setor'],
            'localizacao': negocio['localizacao'],
            'vendas_total': vendas,
            'custos_total': custos,
            'lucro_liquido': lucro,
            'margem_lucro': f"{margem:.1f}%",
            'saude': saude
        }
        
        # Análise com IA
        analise_ia = analisar_com_deepseek(dados_analise)
        
        return jsonify({
            "negocio": negocio['nome'],
            "analise_basica": {
                "vendas_total": vendas,
                "custos_total": custos,
                "lucro_liquido": lucro,
                "margem_lucro": f"{margem:.1f}%",
                "saude": saude
            },
            "analise_ia": analise_ia
        })
        
    except Exception as e:
        return jsonify({"error": "Erro na análise"}), 500

if __name__ == '__main__':
    print("🚀 Henry com DeepSeek Integrado!")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
