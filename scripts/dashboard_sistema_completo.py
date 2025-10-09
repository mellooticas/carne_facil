#!/usr/bin/env python3
"""
Dashboard Unificado - Sistema Completo de Clientes + OS
Visualização integrada das duas bases criadas
"""

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import pandas as pd
from pathlib import Path
import uvicorn

app = FastAPI(title="Sistema Óticas - Dashboard Completo")
templates = Jinja2Templates(directory="app/templates")

class DashboardSistemaCompleto:
    def __init__(self):
        self.carregar_dados()
    
    def carregar_dados(self):
        """Carrega as bases de dados"""
        data_dir = Path("data/processed")
        
        # Carregar base de clientes
        arquivo_clientes = None
        for arquivo in data_dir.glob("BASE_CLIENTES_MASTER_*.xlsx"):
            if not arquivo_clientes or arquivo.stat().st_mtime > arquivo_clientes.stat().st_mtime:
                arquivo_clientes = arquivo
        
        # Carregar base de OS
        arquivo_os = None
        for arquivo in data_dir.glob("BASE_ORDENS_SERVICO_*.xlsx"):
            if not arquivo_os or arquivo.stat().st_mtime > arquivo_os.stat().st_mtime:
                arquivo_os = arquivo
        
        if arquivo_clientes:
            self.df_clientes = pd.read_excel(arquivo_clientes, sheet_name='Base_Clientes_Master')
            self.stats_clientes = pd.read_excel(arquivo_clientes, sheet_name='Estatisticas_Por_Loja')
            print(f"✅ Clientes carregados: {arquivo_clientes.name}")
        else:
            self.df_clientes = pd.DataFrame()
            self.stats_clientes = pd.DataFrame()
        
        if arquivo_os:
            self.df_os = pd.read_excel(arquivo_os, sheet_name='Base_OS_Completa')
            self.df_os_com_cliente = pd.read_excel(arquivo_os, sheet_name='OS_Com_Cliente')
            self.stats_os = pd.read_excel(arquivo_os, sheet_name='Estatisticas_Por_Loja')
            print(f"✅ OS carregadas: {arquivo_os.name}")
        else:
            self.df_os = pd.DataFrame()
            self.df_os_com_cliente = pd.DataFrame()
            self.stats_os = pd.DataFrame()
    
    def get_resumo_geral(self):
        """Resumo geral do sistema"""
        total_clientes = len(self.df_clientes)
        total_os = len(self.df_os)
        os_com_cliente = len(self.df_os_com_cliente) if not self.df_os_com_cliente.empty else 0
        
        # Clientes com mais dados
        clientes_cpf = self.df_clientes['cpf'].notna().sum() if not self.df_clientes.empty else 0
        clientes_celular = self.df_clientes['celular'].notna().sum() if not self.df_clientes.empty else 0
        clientes_email = self.df_clientes['email'].notna().sum() if not self.df_clientes.empty else 0
        
        # OS com dados
        os_com_valor = self.df_os['valor_os'].notna().sum() if not self.df_os.empty else 0
        os_com_data = self.df_os['data_os'].notna().sum() if not self.df_os.empty else 0
        
        return {
            'total_clientes': total_clientes,
            'total_os': total_os,
            'os_com_cliente': os_com_cliente,
            'taxa_identificacao': (os_com_cliente / total_os * 100) if total_os > 0 else 0,
            'clientes_cpf': clientes_cpf,
            'clientes_celular': clientes_celular,
            'clientes_email': clientes_email,
            'os_com_valor': os_com_valor,
            'os_com_data': os_com_data,
            'qualidade_cpf': (clientes_cpf / total_clientes * 100) if total_clientes > 0 else 0,
            'qualidade_celular': (clientes_celular / total_clientes * 100) if total_clientes > 0 else 0,
            'qualidade_email': (clientes_email / total_clientes * 100) if total_clientes > 0 else 0,
            'qualidade_valor': (os_com_valor / total_os * 100) if total_os > 0 else 0,
            'qualidade_data': (os_com_data / total_os * 100) if total_os > 0 else 0
        }
    
    def get_analise_por_loja(self):
        """Análise detalhada por loja"""
        if self.df_clientes.empty or self.df_os.empty:
            return []
        
        # Lojas nos clientes
        lojas_clientes = self.df_clientes.groupby('origem_loja').agg({
            'nome_completo': 'count',
            'cpf': lambda x: x.notna().sum(),
            'celular': lambda x: x.notna().sum(),
            'email': lambda x: x.notna().sum()
        }).rename(columns={'nome_completo': 'total_clientes'})
        
        # Lojas nas OS
        lojas_os = self.df_os.groupby('loja_os').agg({
            'numero_os': 'count',
            'cliente_id': lambda x: x.notna().sum(),
            'valor_os': lambda x: x.notna().sum()
        }).rename(columns={'numero_os': 'total_os'})
        
        # Combinar dados
        analise = []
        for loja in set(list(lojas_clientes.index) + list(lojas_os.index)):
            info_loja = {
                'loja': loja,
                'clientes': lojas_clientes.loc[loja]['total_clientes'] if loja in lojas_clientes.index else 0,
                'os': lojas_os.loc[loja]['total_os'] if loja in lojas_os.index else 0,
                'cpf_pct': (lojas_clientes.loc[loja]['cpf'] / lojas_clientes.loc[loja]['total_clientes'] * 100) if loja in lojas_clientes.index and lojas_clientes.loc[loja]['total_clientes'] > 0 else 0,
                'celular_pct': (lojas_clientes.loc[loja]['celular'] / lojas_clientes.loc[loja]['total_clientes'] * 100) if loja in lojas_clientes.index and lojas_clientes.loc[loja]['total_clientes'] > 0 else 0,
                'email_pct': (lojas_clientes.loc[loja]['email'] / lojas_clientes.loc[loja]['total_clientes'] * 100) if loja in lojas_clientes.index and lojas_clientes.loc[loja]['total_clientes'] > 0 else 0
            }
            analise.append(info_loja)
        
        return sorted(analise, key=lambda x: x['clientes'], reverse=True)
    
    def get_clientes_top(self, limit=10):
        """Top clientes por número de OS"""
        if self.df_os_com_cliente.empty:
            return []
        
        clientes_os = self.df_os_com_cliente.groupby('cliente_id').agg({
            'numero_os': 'count',
            'nome_cliente': 'first',
            'cpf_cliente': 'first',
            'celular_cliente': 'first',
            'valor_os': lambda x: x.sum() if x.notna().any() else 0
        }).rename(columns={'numero_os': 'total_os'})
        
        clientes_os = clientes_os.sort_values('total_os', ascending=False).head(limit)
        
        return [
            {
                'nome': row['nome_cliente'],
                'cpf': row['cpf_cliente'],
                'celular': row['celular_cliente'],
                'total_os': row['total_os'],
                'valor_total': row['valor_os']
            }
            for _, row in clientes_os.iterrows()
        ]
    
    def get_os_recentes(self, limit=10):
        """OS mais recentes"""
        if self.df_os.empty:
            return []
        
        # Filtrar OS com data válida
        df_com_data = self.df_os[self.df_os['data_os'].notna()].copy()
        
        if df_com_data.empty:
            return []
        
        # Converter data para datetime para ordenação
        df_com_data['data_sort'] = pd.to_datetime(df_com_data['data_os'], format='%d/%m/%Y', errors='coerce')
        df_recentes = df_com_data.sort_values('data_sort', ascending=False).head(limit)
        
        return [
            {
                'numero_os': row['numero_os'],
                'data_os': row['data_os'],
                'nome_cliente': row.get('nome_cliente', row.get('nome_informado', 'N/A')),
                'loja': row['loja_os'],
                'valor': row.get('valor_os', 0) or 0
            }
            for _, row in df_recentes.iterrows()
        ]

# Instância global do dashboard
dashboard = DashboardSistemaCompleto()

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Página principal do dashboard"""
    resumo = dashboard.get_resumo_geral()
    analise_lojas = dashboard.get_analise_por_loja()
    clientes_top = dashboard.get_clientes_top()
    os_recentes = dashboard.get_os_recentes()
    
    return templates.TemplateResponse("dashboard_sistema_completo.html", {
        "request": request,
        "resumo": resumo,
        "analise_lojas": analise_lojas,
        "clientes_top": clientes_top,
        "os_recentes": os_recentes
    })

@app.get("/clientes")
async def api_clientes():
    """API para buscar clientes"""
    if dashboard.df_clientes.empty:
        return {"error": "Base de clientes não carregada"}
    
    return {
        "total": len(dashboard.df_clientes),
        "clientes": dashboard.df_clientes.head(100).to_dict('records')
    }

@app.get("/os")
async def api_os():
    """API para buscar OS"""
    if dashboard.df_os.empty:
        return {"error": "Base de OS não carregada"}
    
    return {
        "total": len(dashboard.df_os),
        "os": dashboard.df_os.head(100).to_dict('records')
    }

# Criar template se não existir
def criar_template():
    """Cria template HTML se não existir"""
    templates_dir = Path("app/templates")
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    template_file = templates_dir / "dashboard_sistema_completo.html"
    
    if not template_file.exists():
        html_content = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema Óticas - Dashboard Completo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; text-align: center; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
        .metric-card h3 { color: #667eea; margin-bottom: 10px; }
        .metric-value { font-size: 2.5em; font-weight: bold; color: #2c3e50; margin: 10px 0; }
        .metric-subtitle { color: #666; font-size: 0.9em; }
        .section { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .section h2 { color: #2c3e50; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #667eea; }
        .table { width: 100%; border-collapse: collapse; }
        .table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        .table th { background: #f8f9fa; color: #2c3e50; font-weight: bold; }
        .table tbody tr:hover { background: #f8f9fa; }
        .progress-bar { background: #e9ecef; border-radius: 10px; height: 20px; overflow: hidden; margin: 5px 0; }
        .progress-fill { background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; border-radius: 10px; transition: width 0.3s ease; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-warning { background: #fff3cd; color: #856404; }
        .badge-info { background: #d1ecf1; color: #0c5460; }
        .two-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
        @media (max-width: 768px) { .two-columns { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏪 Sistema de Gestão de Óticas</h1>
            <p>Dashboard Completo - Clientes & Ordens de Serviço</p>
        </div>

        <!-- Métricas Principais -->
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>👥 Total de Clientes</h3>
                <div class="metric-value">{{ "{:,}".format(resumo.total_clientes) }}</div>
                <div class="metric-subtitle">Clientes únicos cadastrados</div>
            </div>
            <div class="metric-card">
                <h3>📋 Total de OS</h3>
                <div class="metric-value">{{ "{:,}".format(resumo.total_os) }}</div>
                <div class="metric-subtitle">Ordens de serviço processadas</div>
            </div>
            <div class="metric-card">
                <h3>🔗 Taxa Identificação</h3>
                <div class="metric-value">{{ "{:.1f}%".format(resumo.taxa_identificacao) }}</div>
                <div class="metric-subtitle">OS com cliente identificado</div>
            </div>
            <div class="metric-card">
                <h3>📱 Qualidade Celular</h3>
                <div class="metric-value">{{ "{:.1f}%".format(resumo.qualidade_celular) }}</div>
                <div class="metric-subtitle">Clientes com celular válido</div>
            </div>
        </div>

        <!-- Qualidade dos Dados -->
        <div class="section">
            <h2>📊 Qualidade dos Dados</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <div>
                    <strong>CPF:</strong> {{ "{:,}".format(resumo.clientes_cpf) }} clientes ({{ "{:.1f}%".format(resumo.qualidade_cpf) }})
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {{ resumo.qualidade_cpf }}%"></div>
                    </div>
                </div>
                <div>
                    <strong>Celular:</strong> {{ "{:,}".format(resumo.clientes_celular) }} clientes ({{ "{:.1f}%".format(resumo.qualidade_celular) }})
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {{ resumo.qualidade_celular }}%"></div>
                    </div>
                </div>
                <div>
                    <strong>Email:</strong> {{ "{:,}".format(resumo.clientes_email) }} clientes ({{ "{:.1f}%".format(resumo.qualidade_email) }})
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {{ resumo.qualidade_email }}%"></div>
                    </div>
                </div>
                <div>
                    <strong>OS com Valor:</strong> {{ "{:,}".format(resumo.os_com_valor) }} OS ({{ "{:.1f}%".format(resumo.qualidade_valor) }})
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {{ resumo.qualidade_valor }}%"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Análise por Loja -->
        <div class="section">
            <h2>🏪 Análise por Loja</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Loja</th>
                        <th>Clientes</th>
                        <th>OS</th>
                        <th>% CPF</th>
                        <th>% Celular</th>
                        <th>% Email</th>
                    </tr>
                </thead>
                <tbody>
                    {% for loja in analise_lojas %}
                    <tr>
                        <td><strong>{{ loja.loja }}</strong></td>
                        <td>{{ "{:,}".format(loja.clientes) }}</td>
                        <td>{{ "{:,}".format(loja.os) }}</td>
                        <td>
                            <span class="badge {% if loja.cpf_pct >= 70 %}badge-success{% elif loja.cpf_pct >= 50 %}badge-warning{% else %}badge-info{% endif %}">
                                {{ "{:.1f}%".format(loja.cpf_pct) }}
                            </span>
                        </td>
                        <td>
                            <span class="badge {% if loja.celular_pct >= 90 %}badge-success{% elif loja.celular_pct >= 70 %}badge-warning{% else %}badge-info{% endif %}">
                                {{ "{:.1f}%".format(loja.celular_pct) }}
                            </span>
                        </td>
                        <td>
                            <span class="badge {% if loja.email_pct >= 60 %}badge-success{% elif loja.email_pct >= 40 %}badge-warning{% else %}badge-info{% endif %}">
                                {{ "{:.1f}%".format(loja.email_pct) }}
                            </span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- Top Clientes e OS Recentes -->
        <div class="two-columns">
            <div class="section">
                <h2>🌟 Top Clientes por OS</h2>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Cliente</th>
                            <th>CPF</th>
                            <th>OS</th>
                            <th>Valor Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for cliente in clientes_top %}
                        <tr>
                            <td><strong>{{ cliente.nome[:30] }}...</strong></td>
                            <td>{{ cliente.cpf or "N/A" }}</td>
                            <td><span class="badge badge-info">{{ cliente.total_os }}</span></td>
                            <td>R$ {{ "{:,.2f}".format(cliente.valor_total or 0) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2>📅 OS Recentes</h2>
                <table class="table">
                    <thead>
                        <tr>
                            <th>OS #</th>
                            <th>Data</th>
                            <th>Cliente</th>
                            <th>Valor</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for os in os_recentes %}
                        <tr>
                            <td><strong>{{ os.numero_os or "N/A" }}</strong></td>
                            <td>{{ os.data_os or "N/A" }}</td>
                            <td>{{ (os.nome_cliente or "N/A")[:20] }}...</td>
                            <td>R$ {{ "{:,.2f}".format(os.valor or 0) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div style="text-align: center; margin-top: 30px; padding: 20px; color: #666;">
            <p>✅ Sistema completo operacional | Base de Clientes + Ordens de Serviço integradas</p>
        </div>
    </div>
</body>
</html>'''
        
        template_file.write_text(html_content, encoding='utf-8')

if __name__ == "__main__":
    criar_template()
    print("🚀 Iniciando Dashboard do Sistema Completo...")
    print("🌐 URL: http://localhost:8005")
    uvicorn.run(app, host="0.0.0.0", port=8005)