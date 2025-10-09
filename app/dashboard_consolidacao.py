#!/usr/bin/env python3
"""
Dashboard Web Interativo para Resultados da Consolidação
Mostra todos os arquivos, resultados e estatísticas
"""

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

app = FastAPI(title="Dashboard - Consolidação por Loja")

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

# Montar arquivos estáticos se existir
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except:
    pass

@app.get("/", response_class=HTMLResponse)
async def dashboard_principal(request: Request):
    """Dashboard principal com todos os resultados"""
    
    # Carregar dados do dashboard
    dashboard_file = Path("data/processed/dashboard_consolidacao_por_loja.xlsx")
    
    if not dashboard_file.exists():
        return templates.TemplateResponse("dashboard_vazio.html", {
            "request": request,
            "message": "Execute primeiro a consolidação por loja para ver os resultados!"
        })
    
    try:
        # Carregar dados
        excel_file = pd.ExcelFile(dashboard_file)
        
        # Dashboard principal
        df_dashboard = pd.read_excel(dashboard_file, sheet_name='Dashboard_Principal')
        
        # Resumo por loja
        df_resumo_loja = pd.read_excel(dashboard_file, sheet_name='Resumo_Por_Loja')
        
        # Estatísticas gerais
        df_stats = pd.read_excel(dashboard_file, sheet_name='Estatisticas_Gerais')
        
        # Qualidade de dados
        df_qualidade = None
        try:
            df_qualidade = pd.read_excel(dashboard_file, sheet_name='Qualidade_Dados')
        except:
            pass
        
        # Preparar dados para template
        arquivos_data = df_dashboard.to_dict('records')
        
        # Calcular métricas gerais
        total_arquivos = len(arquivos_data)
        arquivos_sucesso = len([a for a in arquivos_data if a['status'] == 'sucesso'])
        arquivos_erro = len([a for a in arquivos_data if a['status'] == 'erro'])
        
        # Calcular totais
        total_originais = sum(a.get('registros_originais', 0) for a in arquivos_data)
        total_consolidados = sum(a.get('registros_consolidados', 0) for a in arquivos_data)
        total_duplicatas = sum(a.get('duplicatas_encontradas', 0) for a in arquivos_data)
        total_os = sum(a.get('total_os', 0) for a in arquivos_data)
        
        # Taxa de redução
        taxa_reducao = 0
        if total_originais > 0:
            taxa_reducao = ((total_originais - total_consolidados) / total_originais) * 100
        
        # Dados por loja
        lojas_data = df_resumo_loja.reset_index().to_dict('records')
        
        # Top arquivos com mais duplicatas
        top_duplicatas = sorted(arquivos_data, key=lambda x: x.get('duplicatas_encontradas', 0), reverse=True)[:5]
        
        # Qualidade de dados por campo
        qualidade_por_campo = {}
        if df_qualidade is not None:
            for campo in ['nome', 'cpf', 'celular', 'email', 'endereco']:
                dados_campo = df_qualidade[df_qualidade['campo'] == campo]
                if not dados_campo.empty:
                    total_preenchidos = dados_campo['preenchidos'].sum()
                    total_registros = dados_campo['total'].sum()
                    percentual = (total_preenchidos / total_registros * 100) if total_registros > 0 else 0
                    qualidade_por_campo[campo] = {
                        'preenchidos': total_preenchidos,
                        'total': total_registros,
                        'percentual': round(percentual, 1)
                    }
        
        return templates.TemplateResponse("dashboard_consolidacao.html", {
            "request": request,
            "arquivos": arquivos_data,
            "lojas": lojas_data,
            "top_duplicatas": top_duplicatas,
            "qualidade_campos": qualidade_por_campo,
            "metricas": {
                "total_arquivos": total_arquivos,
                "arquivos_sucesso": arquivos_sucesso,
                "arquivos_erro": arquivos_erro,
                "total_originais": total_originais,
                "total_consolidados": total_consolidados,
                "total_duplicatas": total_duplicatas,
                "total_os": total_os,
                "taxa_reducao": round(taxa_reducao, 1)
            },
            "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })
        
    except Exception as e:
        return templates.TemplateResponse("dashboard_erro.html", {
            "request": request,
            "erro": str(e)
        })

@app.get("/loja/{loja_nome}", response_class=HTMLResponse)
async def detalhes_loja(request: Request, loja_nome: str):
    """Detalhes específicos de uma loja"""
    
    dashboard_file = Path("data/processed/dashboard_consolidacao_por_loja.xlsx")
    
    if not dashboard_file.exists():
        return templates.TemplateResponse("dashboard_vazio.html", {
            "request": request,
            "message": "Execute primeiro a consolidação por loja!"
        })
    
    try:
        df_dashboard = pd.read_excel(dashboard_file, sheet_name='Dashboard_Principal')
        arquivos_loja = df_dashboard[df_dashboard['loja'] == loja_nome].to_dict('records')
        
        if not arquivos_loja:
            return templates.TemplateResponse("loja_nao_encontrada.html", {
                "request": request,
                "loja_nome": loja_nome
            })
        
        # Calcular totais da loja
        total_arquivos = len(arquivos_loja)
        total_originais = sum(a.get('registros_originais', 0) for a in arquivos_loja)
        total_consolidados = sum(a.get('registros_consolidados', 0) for a in arquivos_loja)
        total_duplicatas = sum(a.get('duplicatas_encontradas', 0) for a in arquivos_loja)
        total_os = sum(a.get('total_os', 0) for a in arquivos_loja)
        
        return templates.TemplateResponse("detalhes_loja.html", {
            "request": request,
            "loja_nome": loja_nome,
            "arquivos": arquivos_loja,
            "totais": {
                "arquivos": total_arquivos,
                "originais": total_originais,
                "consolidados": total_consolidados,
                "duplicatas": total_duplicatas,
                "os": total_os
            }
        })
        
    except Exception as e:
        return templates.TemplateResponse("dashboard_erro.html", {
            "request": request,
            "erro": str(e)
        })

@app.get("/api/dados")
async def api_dados():
    """API para dados em JSON"""
    
    dashboard_file = Path("data/processed/dashboard_consolidacao_por_loja.xlsx")
    
    if not dashboard_file.exists():
        return {"erro": "Dashboard não encontrado"}
    
    try:
        df_dashboard = pd.read_excel(dashboard_file, sheet_name='Dashboard_Principal')
        df_resumo = pd.read_excel(dashboard_file, sheet_name='Resumo_Por_Loja')
        
        return {
            "arquivos": df_dashboard.to_dict('records'),
            "resumo_lojas": df_resumo.reset_index().to_dict('records'),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"erro": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando Dashboard de Consolidação por Loja")
    print("📊 Acesse: http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)