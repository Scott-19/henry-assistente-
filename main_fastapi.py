# Henry Assistente Financeiro - Versão 1.1 (FastAPI)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests
import os
from datetime import datetime

app = FastAPI(
    title="Henry Assistente Financeiro",
    description="Sistema de análise financeira com IA para Moçambique",
    version="1.1"
)

# Configuração CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

# Database em memória (mesmo da v1.0)
negocios = {}
transacao_id_counter = 1

# Modelos Pydantic
class NegocioCreate(BaseModel):
    nome: str
    setor: str = "Geral"
    localizacao: str = "Maputo"

class TransacaoCreate(BaseModel):
    valor: float
    tipo: str
    categoria: str = "outros"
    descricao: str = ""

# Rotas principais
@app.get("/")
async def home():
    return {
        "message": "💰 Henry Assistente Financeiro 1.1",
        "version": "1.1",
        "status": "online",
        "framework": "FastAPI"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.1",
        "deepseek_configurado": bool(DEEPSEEK_API_KEY),
        "total_negocios": len(negocios),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/criar-negocio", response_model=dict)
async def criar_negocio(negocio: NegocioCreate):
    try:
        negocio_id = str(len(negocios) + 1)
        negocios[negocio_id] = {
            'id': negocio_id,
            'nome': negocio.nome,
            'setor': negocio.setor,
            'localizacao': negocio.localizacao,
            'transacoes': [],
            'criado_em': datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "negocio_id": negocio_id,
            "message": "✅ Negócio criado com sucesso!",
            "negocio": negocios[negocio_id]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/adicionar-transacao/{negocio_id}", response_model=dict)
async def adicionar_transacao(negocio_id: str, transacao: TransacaoCreate):
    try:
        if negocio_id not in negocios:
            raise HTTPException(status_code=404, detail="Negócio não encontrado")
        
        global transacao_id_counter
        nova_transacao = {
            'id': transacao_id_counter,
            'valor': transacao.valor,
            'tipo': transacao.tipo,
            'categoria': transacao.categoria,
            'descricao': transacao.descricao,
            'data': datetime.now().isoformat()
        }
        
        negocios[negocio_id]['transacoes'].append(nova_transacao)
        transacao_id_counter += 1
        
        return {
            "success": True,
            "transacao_id": nova_transacao['id'],
            "message": f"✅ {transacao.tipo.title()} de {transacao.valor} MT registrada!",
            "total_transacoes": len(negocios[negocio_id]['transacoes'])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analise-financeira/{negocio_id}")
async def analise_financeira(negocio_id: str):
    try:
        if negocio_id not in negocios:
            raise HTTPException(status_code=404, detail="Negócio não encontrado")
        
        negocio = negocios[negocio_id]
        transacoes = negocio['transacoes']
        
        # Cálculos financeiros
        vendas = sum(t['valor'] for t in transacoes if t['tipo'] == 'venda')
        custos = sum(t['valor'] for t in transacoes if t['tipo'] == 'custo')
        lucro = vendas - custos
        margem = (lucro / vendas * 100) if vendas > 0 else 0
        
        # Análise básica (por enquanto)
        analise_basica = f"📊 Análise 1.1 | Lucro: {lucro} MT | Margem: {margem:.1f}%"
        
        return {
            "negocio": negocio['nome'],
            "versao": "1.1",
            "relatorio_financeiro": {
                "receitas": vendas,
                "despesas": custos,
                "resultado_liquido": lucro,
                "margem_rentabilidade": f"{margem:.1f}%",
                "saude_financeira": "✅ Saudável" if margem > 20 else "⚠️ Atenção" if margem > 0 else "🔴 Crítica"
            },
            "analise": analise_basica,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/negocios")
async def listar_negocios():
    return {
        "versao": "1.1",
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
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)