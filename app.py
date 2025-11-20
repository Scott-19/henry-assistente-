from flask import Flask, jsonify, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ================= CONFIGURAÇÃO =================
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
print(f"💰 Henry Assistente Financeiro - DeepSeek: {'✅' if DEEPSEEK_API_KEY else '❌'}")

# Database em memória
negocios = {}
transacao_id_counter = 1

# ================= SERVIÇO FINANCEIRO DEEPSEEK =================
def analisar_financas(dados_negocio):
    """Análise financeira especializada com DeepSeek"""
    if not DEEPSEEK_API_KEY:
        return "🔧 Configure DEEPSEEK_API_KEY no Render"
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        prompt = f"""
        Você é o HENRY, assistente financeiro especializado em Moçambique.
        
        ANALISE FINANCEIRA DO NEGÓCIO:
        💼 Nome: {dados_negocio['nome']}
        🏢 Setor: {dados_negocio['setor']}
        📍 Local: {dados_negocio['localizacao']}
        
        DADOS FINANCEIROS:
        💰 Vendas Totais: {dados_negocio['vendas_total']} MT
        💸 Custos Totais: {dados_negocio['custos_total']} MT
        💵 Lucro Líquido: {dados_negocio['lucro_liquido']} MT
        📈 Margem de Lucro: {dados_negocio['margem_lucro']}
        📊 Transações: {dados_negocio['total_transacoes']}
        
        FORNEÇA ANÁLISE FINANCEIRA ESPECIALIZADA:
        1. 📊 DIAGNÓSTICO FINANCEIRO (Saúde do negócio)
        2. 💡 OPORTUNIDADES DE OTIMIZAÇÃO
        3. ⚠️ ALERTAS DE RISCO FINANCEIRO
        4. 🎯 ESTRATÉGIAS PARA MOÇAMBIQUE
        
        Seja prático, use termos financeiros e foque em resultados.
        """
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "Você é HENRY, assistente financeiro moçambicano especializado em análise financeira, fluxo de caixa e otimização de negócios. Seja técnico porém acessível."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 1200
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        return response.json()['choices'][0]['message']['content']
        
    except Exception as e:
        return f"📊 Análise Financeira Básica | Lucro: {dados_negocio['lucro_liquido']} MT | Margem: {dados_negocio['margem_lucro']}"

# ================= ROTAS FINANCEIRAS =================
@app.route('/')
def home():
    return jsonify({
        "message": "💰 Henry Assistente Financeiro - ONLINE!",
        "status": "✅ Operacional",
        "servico": "Análise Financeira com IA",
        "pais": "Moçambique 🇲🇿",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "servico": "Assistente Financeiro",
        "deepseek_configurado": bool(DEEPSEEK_API_KEY),
        "total_negocios": len(negocios),
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
            "message": "✅ Negócio cadastrado para análise financeira!",
            "negocio": negocios[negocio_id]
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/adicionar-transacao/<negocio_id>', methods=['POST'])
def adicionar_transacao(negocio_id):
    try:
        if negocio_id not in negocios:
            return jsonify({"error": "❌ Negócio não encontrado"}), 404
        
        data = request.get_json() or {}
        global transacao_id_counter
        
        transacao = {
            'id': transacao_id_counter,
            'valor': float(data.get('valor', 0)),
            'tipo': data.get('tipo', 'venda'),
            'categoria': data.get('categoria', 'outros'),
            'descricao': data.get('descricao', ''),
            'data': datetime.now().isoformat()
        }
        
        negocios[negocio_id]['transacoes'].append(transacao)
        transacao_id_counter += 1
        
        return jsonify({
            "success": True,
            "transacao_id": transacao['id'],
            "message": f"✅ Transação financeira registrada!",
            "tipo": transacao['tipo'],
            "valor": transacao['valor'],
            "total_transacoes": len(negocios[negocio_id]['transacoes'])
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/analise-financeira/<negocio_id>')
def analise_financeira(negocio_id):
    try:
        if negocio_id not in negocios:
            return jsonify({"error": "❌ Negócio não encontrado"}), 404
        
        negocio = negocios[negocio_id]
        transacoes = negocio['transacoes']
        
        # Cálculos financeiros
        vendas = sum(t['valor'] for t in transacoes if t['tipo'] == 'venda')
        custos = sum(t['valor'] for t in transacoes if t['tipo'] == 'custo')
        lucro = vendas - custos
        margem = (lucro / vendas * 100) if vendas > 0 else 0
        
        dados_analise = {
            'nome': negocio['nome'],
            'setor': negocio['setor'],
            'localizacao': negocio['localizacao'],
            'vendas_total': vendas,
            'custos_total': custos,
            'lucro_liquido': lucro,
            'margem_lucro': f"{margem:.1f}%",
            'total_transacoes': len(transacoes)
        }
        
        # Análise financeira com IA
        analise_ia = analisar_financas(dados_analise)
        
        return jsonify({
            "negocio": negocio['nome'],
            "relatorio_financeiro": {
                "receitas": vendas,
                "despesas": custos,
                "resultado_liquido": lucro,
                "margem_rentabilidade": f"{margem:.1f}%",
                "saude_financeira": "✅ Saudável" if margem > 20 else "⚠️ Atenção" if margem > 0 else "🔴 Crítica",
                "transacoes_analisadas": len(transacoes)
            },
            "analise_especializada": analise_ia,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/negocios')
def listar_negocios():
    return jsonify({
        "total_negocios": len(negocios),
        "negocios": [
            {
                "id": negocio_id,
                "nome": negocio['nome'],
                "setor": negocio['setor'],
                "transacoes": len(negocio['transacoes'])
            }
            for negocio_id, negocio in negocios.items()
        ]
    })

if __name__ == '__main__':
    print("💰 Henry Assistente Financeiro Iniciado!")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)