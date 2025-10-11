#!/usr/bin/env python3
"""
📊 DASHBOARD SIMPLIFICADO - ÓTICAS CARNE FÁCIL
================================================================================
🎯 Dashboard básico com métricas principais
📈 Sem gráficos complexos para evitar erros
🌐 Interface web funcional
================================================================================
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from pathlib import Path
import uvicorn
from datetime import datetime

app = FastAPI(title="Dashboard Óticas Carne Fácil - Simplificado")

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

# Dados globais
dados_dashboard = {}

def carregar_dados_simples():
    """Carrega dados básicos"""
    global dados_dashboard
    
    data_dir = Path("data/processed")
    
    try:
        # Carregar clientes
        clientes_files = list(data_dir.glob("BASE_CLIENTES_COM_ID_*.xlsx"))
        if clientes_files:
            dados_dashboard['clientes'] = pd.read_excel(clientes_files[-1])
            print(f"✅ {len(dados_dashboard['clientes'])} clientes carregados")
        
        # Carregar relacionamentos
        relacionamentos_files = list(data_dir.glob("RELACIONAMENTO_OS_CLIENTE_*.xlsx"))
        if relacionamentos_files:
            dados_dashboard['relacionamentos'] = pd.read_excel(relacionamentos_files[-1])
            print(f"✅ {len(dados_dashboard['relacionamentos'])} relacionamentos carregados")
        
        # Carregar vendas
        vendas_files = list(data_dir.glob("VENDAS_COMPLETAS_*.xlsx"))
        if vendas_files:
            dados_dashboard['vendas'] = pd.read_excel(vendas_files[-1])
            print(f"✅ {len(dados_dashboard['vendas'])} vendas carregadas")
        
        # Carregar dioptrías
        dioptrias_files = list(data_dir.glob("DIOPTRIAS_COMPLETAS_*.xlsx"))
        if dioptrias_files:
            dados_dashboard['dioptrias'] = pd.read_excel(dioptrias_files[-1])
            print(f"✅ {len(dados_dashboard['dioptrias'])} dioptrías carregadas")
        
        print("✅ Dados carregados com sucesso")
        
    except Exception as e:
        print(f"⚠️ Erro ao carregar dados: {e}")

def criar_metricas_simples():
    """Cria métricas básicas"""
    metricas = {}
    
    try:
        if 'clientes' in dados_dashboard:
            metricas['total_clientes'] = len(dados_dashboard['clientes'])
        
        if 'relacionamentos' in dados_dashboard:
            df_rel = dados_dashboard['relacionamentos']
            metricas['total_os'] = len(df_rel)
            metricas['os_identificadas'] = len(df_rel[df_rel['Cliente_ID'].notna()])
            metricas['taxa_identificacao'] = round(metricas['os_identificadas'] / metricas['total_os'] * 100, 1) if metricas['total_os'] > 0 else 0
        
        if 'vendas' in dados_dashboard:
            df_vendas = dados_dashboard['vendas']
            metricas['total_vendas'] = df_vendas['valor_total'].sum()
            metricas['os_com_vendas'] = len(df_vendas[df_vendas['valor_total'] > 0])
            metricas['ticket_medio'] = metricas['total_vendas'] / metricas['os_com_vendas'] if metricas['os_com_vendas'] > 0 else 0
        
        if 'dioptrias' in dados_dashboard:
            metricas['os_com_dioptrias'] = len(dados_dashboard['dioptrias'])
        
    except Exception as e:
        print(f"⚠️ Erro ao criar métricas: {e}")
        metricas = {
            'total_clientes': 0,
            'total_os': 0,
            'os_identificadas': 0,
            'taxa_identificacao': 0,
            'total_vendas': 0,
            'os_com_vendas': 0,
            'ticket_medio': 0,
            'os_com_dioptrias': 0
        }
    
    return metricas

@app.on_event("startup")
async def startup_event():
    """Carrega dados na inicialização"""
    print("🚀 Iniciando Dashboard Simplificado...")
    carregar_dados_simples()

@app.get("/", response_class=HTMLResponse)
async def dashboard_simples(request: Request):
    """Dashboard simplificado"""
    metricas = criar_metricas_simples()
    
    return templates.TemplateResponse("dashboard_simples.html", {
        "request": request,
        "metricas": metricas,
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })

@app.get("/status")
async def status():
    """Status da aplicação"""
    return {
        "status": "ok",
        "dados_carregados": list(dados_dashboard.keys()),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Iniciando Dashboard Simplificado...")
    
    uvicorn.run(
        "dashboard_simples:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )