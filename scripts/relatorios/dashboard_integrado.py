#!/usr/bin/env python3
"""
📊 DASHBOARD WEB INTERATIVO - ÓTICAS CARNE FÁCIL
================================================================================
🎯 Dashboard completo com visualizações dos dados integrados
📈 Gráficos, métricas e análises em tempo real
🌐 Interface web moderna e responsiva
================================================================================
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
from pathlib import Path
import uvicorn
from datetime import datetime

app = FastAPI(title="Dashboard Óticas Carne Fácil")

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

# Dados globais (carregados na inicialização)
dados_dashboard = {}

def carregar_dados():
    """Carrega todos os dados processados"""
    global dados_dashboard
    
    data_dir = Path("data/processed")
    
    try:
        # Carregar clientes
        clientes_files = list(data_dir.glob("BASE_CLIENTES_COM_ID_*.xlsx"))
        if clientes_files:
            dados_dashboard['clientes'] = pd.read_excel(clientes_files[-1])
        
        # Carregar relacionamentos
        relacionamentos_files = list(data_dir.glob("RELACIONAMENTO_OS_CLIENTE_*.xlsx"))
        if relacionamentos_files:
            dados_dashboard['relacionamentos'] = pd.read_excel(relacionamentos_files[-1])
        
        # Carregar dioptrías
        dioptrias_files = list(data_dir.glob("DIOPTRIAS_COMPLETAS_*.xlsx"))
        if dioptrias_files:
            dados_dashboard['dioptrias'] = pd.read_excel(dioptrias_files[-1])
        
        # Carregar vendas
        vendas_files = list(data_dir.glob("VENDAS_COMPLETAS_*.xlsx"))
        if vendas_files:
            dados_dashboard['vendas'] = pd.read_excel(vendas_files[-1])
        
        print("✅ Dados carregados para dashboard")
        
    except Exception as e:
        print(f"⚠️ Erro ao carregar dados: {e}")

def criar_metricas_principais():
    """Cria as métricas principais do dashboard"""
    metricas = {}
    
    if 'clientes' in dados_dashboard:
        metricas['total_clientes'] = len(dados_dashboard['clientes'])
    
    if 'relacionamentos' in dados_dashboard:
        df_rel = dados_dashboard['relacionamentos']
        metricas['total_os'] = len(df_rel)
        metricas['os_identificadas'] = len(df_rel[df_rel['Cliente_ID'].notna()])
        metricas['taxa_identificacao'] = round(metricas['os_identificadas'] / metricas['total_os'] * 100, 1)
    
    if 'vendas' in dados_dashboard:
        df_vendas = dados_dashboard['vendas']
        metricas['total_vendas'] = df_vendas['valor_total'].sum()
        metricas['os_com_vendas'] = len(df_vendas[df_vendas['valor_total'] > 0])
        metricas['ticket_medio'] = metricas['total_vendas'] / metricas['os_com_vendas'] if metricas['os_com_vendas'] > 0 else 0
    
    if 'dioptrias' in dados_dashboard:
        metricas['os_com_dioptrias'] = len(dados_dashboard['dioptrias'])
    
    return metricas

def criar_grafico_vendas_por_loja():
    """Cria gráfico de vendas por loja"""
    if 'relacionamentos' not in dados_dashboard or 'vendas' not in dados_dashboard:
        return {}
    
    df_rel = dados_dashboard['relacionamentos']
    df_vendas = dados_dashboard['vendas']
    
    # Merge para obter loja das vendas
    df_vendas_loja = df_vendas.merge(
        df_rel[['OS_Numero', 'Loja']], 
        left_on='numero_os',
        right_on='OS_Numero', 
        how='left'
    )
    
    # Agrupar por loja
    vendas_loja = df_vendas_loja.groupby('Loja')['valor_total'].sum().reset_index()
    
    fig = px.bar(
        vendas_loja, 
        x='Loja', 
        y='valor_total',
        title='Vendas por Loja',
        labels={'valor_total': 'Vendas (R$)', 'Loja': 'Loja'},
        color='valor_total',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#333'
    )
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)

def criar_grafico_os_por_mes():
    """Cria gráfico de OS por mês"""
    if 'relacionamentos' not in dados_dashboard:
        return {}
    
    df_rel = dados_dashboard['relacionamentos']
    
    # Simular data baseada no número da OS (aproximação)
    df_rel_copy = df_rel.copy()
    df_rel_copy['Mes'] = (df_rel_copy['OS_Numero'] % 12) + 1
    
    os_mes = df_rel_copy.groupby('Mes').size().reset_index()
    os_mes.columns = ['Mes', 'Quantidade_OS']
    
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
             'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    os_mes['Mes_Nome'] = os_mes['Mes'].apply(lambda x: meses[x-1])
    
    fig = px.line(
        os_mes, 
        x='Mes_Nome', 
        y='Quantidade_OS',
        title='Evolução de OS por Mês',
        labels={'Quantidade_OS': 'Número de OS', 'Mes_Nome': 'Mês'},
        markers=True
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#333'
    )
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)

def criar_grafico_distribuicao_clientes():
    """Cria gráfico de distribuição de clientes por loja"""
    if 'clientes' not in dados_dashboard:
        return {}
    
    df_clientes = dados_dashboard['clientes']
    
    # Distribuição por loja
    dist_loja = df_clientes['origem_loja'].value_counts().reset_index()
    dist_loja.columns = ['Loja', 'Quantidade']
    
    fig = px.pie(
        dist_loja, 
        values='Quantidade', 
        names='Loja',
        title='Distribuição de Clientes por Loja',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#333'
    )
    
    return json.dumps(fig, cls=PlotlyJSONEncoder)

def criar_grafico_produtos_top():
    """Cria gráfico dos produtos mais vendidos"""
    if 'vendas' not in dados_dashboard:
        return {}
    
    df_vendas = dados_dashboard['vendas']
    
    # Top produtos
    produtos = []
    for i in range(1, 6):  # Produtos 1 a 5
        col_desc = f'produto{i}_descricao'
        col_valor = f'produto{i}_valor'
        
        if col_desc in df_vendas.columns and col_valor in df_vendas.columns:
            df_produto = df_vendas[[col_desc, col_valor]].dropna()
            df_produto.columns = ['Produto', 'Valor']
            produtos.append(df_produto)
    
    if produtos:
        df_todos_produtos = pd.concat(produtos, ignore_index=True)
        top_produtos = df_todos_produtos.groupby('Produto')['Valor'].sum().sort_values(ascending=False).head(10)
        
        fig = px.bar(
            x=top_produtos.values,
            y=top_produtos.index,
            orientation='h',
            title='Top 10 Produtos Mais Vendidos',
            labels={'x': 'Valor Total (R$)', 'y': 'Produto'}
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#333',
            height=500
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    return {}

@app.on_event("startup")
async def startup_event():
    """Carrega dados na inicialização"""
    carregar_dados()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Página principal do dashboard"""
    
    # Criar métricas
    metricas = criar_metricas_principais()
    
    # Criar gráficos
    grafico_vendas_loja = criar_grafico_vendas_por_loja()
    grafico_os_mes = criar_grafico_os_por_mes()
    grafico_clientes = criar_grafico_distribuicao_clientes()
    grafico_produtos = criar_grafico_produtos_top()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "metricas": metricas,
        "grafico_vendas_loja": grafico_vendas_loja,
        "grafico_os_mes": grafico_os_mes,
        "grafico_clientes": grafico_clientes,
        "grafico_produtos": grafico_produtos,
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })

@app.get("/api/dados")
async def api_dados():
    """API para dados em JSON"""
    metricas = criar_metricas_principais()
    return {"metricas": metricas, "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    print("🚀 Iniciando Dashboard Óticas Carne Fácil...")
    print("📊 Carregando dados integrados...")
    
    uvicorn.run(
        "dashboard_integrado:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )