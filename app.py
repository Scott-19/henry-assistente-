# ================= PROMPT PERSONALIZADO =================
@app.route('/perguntar-henry', methods=['POST'])
def perguntar_henry():
    """Permite fazer perguntas personalizadas ao Henry"""
    try:
        data = request.get_json() or {}
        pergunta = data.get('pergunta', '')
        negocio_id = data.get('negocio_id', '1')
        
        if not pergunta:
            return jsonify({"error": "❌ Forneça uma pergunta"}), 400
        
        if not DEEPSEEK_API_KEY:
            return jsonify({"error": "🔧 DeepSeek não configurado"}), 500
        
        # Buscar dados do negócio se fornecido
        dados_negocio = {}
        if negocio_id in negocios:
            negocio = negocios[negocio_id]
            transacoes = negocio['transacoes']
            vendas = sum(t['valor'] for t in transacoes if t['tipo'] == 'venda')
            custos = sum(t['valor'] for t in transacoes if t['tipo'] == 'custo')
            
            dados_negocio = {
                'nome': negocio['nome'],
                'vendas': vendas,
                'custos': custos,
                'lucro': vendas - custos
            }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        prompt = f"""
        Você é o HENRY, assistente financeiro especializado em Moçambique.
        
        DADOS DO NEGÓCIO (se disponível):
        {dados_negocio}
        
        PERGUNTA DO USUÁRIO:
        {pergunta}
        
        Forneça uma resposta prática, focada em finanças e negócios em Moçambique.
        Seja direto e use exemplos concretos quando possível.
        """
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "Você é HENRY, assistente financeiro moçambicano. Responda de forma prática e focada em ações."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        resposta = response.json()['choices'][0]['message']['content']
        
        return jsonify({
            "pergunta": pergunta,
            "resposta": resposta,
            "negocio_id": negocio_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500