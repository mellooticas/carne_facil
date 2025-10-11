#!/usr/bin/env python3
"""
GERADOR DE RELATÓRIO EXECUTIVO
Consolida dados de todas as lojas e gera relatório completo
Uso: python relatorio_executivo.py
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import os

class RelatorioExecutivo:
    def __init__(self):
        self.pasta_vendas = Path("data/vendas_processadas")
        self.pasta_relatorios = Path("data/relatorios_executivos")
        self.pasta_relatorios.mkdir(exist_ok=True)
    
    def consolidar_todas_vendas(self):
        """Consolida vendas de todas as lojas processadas"""
        print("📊 CONSOLIDANDO VENDAS DE TODAS AS LOJAS...")
        print("=" * 60)
        
        arquivos_vendas = list(self.pasta_vendas.glob("VENDAS_*.xlsx"))
        print(f"📂 Encontrados {len(arquivos_vendas)} arquivos de vendas")
        
        if not arquivos_vendas:
            print("❌ Nenhum arquivo de vendas encontrado")
            return None
        
        todas_vendas = []
        resumo_arquivos = {}
        
        for arquivo in arquivos_vendas:
            try:
                df = pd.read_excel(arquivo)
                todas_vendas.append(df)
                
                # Extrair informações do nome do arquivo
                nome = arquivo.stem
                partes = nome.split('_')
                if len(partes) >= 4:
                    loja = partes[1]
                    ano = partes[2]
                    mes = partes[3]
                    
                    chave = f"{loja}_{ano}_{mes}"
                    resumo_arquivos[chave] = {
                        'arquivo': arquivo.name,
                        'loja': loja,
                        'periodo': f"{ano}_{mes}",
                        'vendas': len(df)
                    }
                    
                print(f"   ✅ {arquivo.name}: {len(df)} vendas")
                
            except Exception as e:
                print(f"   ❌ {arquivo.name}: Erro - {e}")
        
        if todas_vendas:
            df_consolidado = pd.concat(todas_vendas, ignore_index=True)
            print(f"\n📈 CONSOLIDAÇÃO CONCLUÍDA:")
            print(f"   💰 Total de vendas: {len(df_consolidado):,}")
            print(f"   🏪 Lojas processadas: {len(df_consolidado['loja'].unique())}")
            
            return df_consolidado, resumo_arquivos
        
        return None, None
    
    def gerar_relatorio_completo(self):
        """Gera relatório executivo completo"""
        print("🚀 GERANDO RELATÓRIO EXECUTIVO COMPLETO")
        print("=" * 80)
        
        # Consolidar dados
        df_vendas, resumo_arquivos = self.consolidar_todas_vendas()
        
        if df_vendas is None:
            print("❌ Não foi possível consolidar os dados")
            return
        
        # Preparar dados
        df_vendas['data'] = pd.to_datetime(df_vendas['data'])
        df_vendas['mes'] = df_vendas['data'].dt.strftime('%Y-%m')
        df_vendas['dia_semana'] = df_vendas['data'].dt.day_name()
        
        # Gerar arquivo Excel consolidado
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_excel = self.pasta_relatorios / f"RELATORIO_EXECUTIVO_{timestamp}.xlsx"
        
        with pd.ExcelWriter(arquivo_excel, engine='openpyxl') as writer:
            # Aba 1: Todas as vendas
            df_vendas.to_excel(writer, sheet_name='VENDAS_CONSOLIDADAS', index=False)
            
            # Aba 2: Resumo por loja
            resumo_loja = df_vendas.groupby('loja').agg({
                'numero_venda': 'count',
                'valor_venda': ['sum', 'mean'],
                'entrada': 'sum'
            }).round(2)
            resumo_loja.columns = ['qtd_vendas', 'valor_total', 'valor_medio', 'entrada_total']
            resumo_loja = resumo_loja.reset_index()
            resumo_loja.to_excel(writer, sheet_name='RESUMO_POR_LOJA', index=False)
            
            # Aba 3: Resumo por mês
            resumo_mensal = df_vendas.groupby(['loja', 'mes']).agg({
                'numero_venda': 'count',
                'valor_venda': 'sum',
                'entrada': 'sum'
            }).round(2).reset_index()
            resumo_mensal.to_excel(writer, sheet_name='RESUMO_MENSAL', index=False)
            
            # Aba 4: Top clientes geral
            top_clientes = df_vendas.groupby(['loja', 'cliente']).agg({
                'numero_venda': 'count',
                'valor_venda': 'sum'
            }).round(2).reset_index().sort_values('valor_venda', ascending=False).head(100)
            top_clientes.to_excel(writer, sheet_name='TOP_CLIENTES', index=False)
            
            # Aba 5: Formas de pagamento
            formas_pgto = df_vendas.groupby(['loja', 'forma_pgto']).agg({
                'numero_venda': 'count',
                'valor_venda': 'sum'
            }).round(2).reset_index().sort_values('valor_venda', ascending=False)
            formas_pgto.to_excel(writer, sheet_name='FORMAS_PAGAMENTO', index=False)
            
            # Aba 6: Arquivos processados
            df_arquivos = pd.DataFrame(resumo_arquivos.values())
            df_arquivos.to_excel(writer, sheet_name='ARQUIVOS_PROCESSADOS', index=False)
        
        print(f"💾 RELATÓRIO EXCEL GERADO: {arquivo_excel}")
        
        # Gerar relatório em texto
        self.gerar_relatorio_texto(df_vendas, resumo_arquivos, timestamp)
        
        # Gerar dashboards visuais (se matplotlib disponível)
        try:
            self.gerar_dashboards(df_vendas, timestamp)
        except ImportError:
            print("⚠️ Matplotlib não disponível - dashboards visuais não gerados")
        
        return arquivo_excel
    
    def gerar_relatorio_texto(self, df_vendas, resumo_arquivos, timestamp):
        """Gera relatório em formato texto"""
        arquivo_texto = self.pasta_relatorios / f"RELATORIO_EXECUTIVO_{timestamp}.txt"
        
        with open(arquivo_texto, 'w', encoding='utf-8') as f:
            f.write("🏪 RELATÓRIO EXECUTIVO - SISTEMA DE VENDAS ÓTICAS\n")
            f.write("=" * 80 + "\n")
            f.write(f"📅 Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n\n")
            
            # Resumo geral
            total_vendas = len(df_vendas)
            valor_total = df_vendas['valor_venda'].sum()
            entrada_total = df_vendas['entrada'].sum()
            lojas = df_vendas['loja'].unique()
            
            f.write("📊 RESUMO GERAL\n")
            f.write("-" * 40 + "\n")
            f.write(f"💰 Total de vendas: {total_vendas:,}\n")
            f.write(f"💵 Valor total: R$ {valor_total:,.2f}\n")
            f.write(f"🏧 Entradas total: R$ {entrada_total:,.2f}\n")
            f.write(f"📈 Média por venda: R$ {valor_total/total_vendas:,.2f}\n")
            f.write(f"🏪 Lojas ativas: {len(lojas)}\n")
            f.write(f"📋 Lojas: {', '.join(sorted(lojas))}\n\n")
            
            # Período
            periodo_inicio = df_vendas['data'].min().strftime('%d/%m/%Y')
            periodo_fim = df_vendas['data'].max().strftime('%d/%m/%Y')
            dias_periodo = (df_vendas['data'].max() - df_vendas['data'].min()).days + 1
            
            f.write("📅 PERÍODO ANALISADO\n")
            f.write("-" * 40 + "\n")
            f.write(f"🗓️ Início: {periodo_inicio}\n")
            f.write(f"🗓️ Fim: {periodo_fim}\n")
            f.write(f"📆 Total de dias: {dias_periodo}\n")
            f.write(f"📊 Média vendas/dia: {total_vendas/dias_periodo:.1f}\n\n")
            
            # Resumo por loja
            f.write("🏪 PERFORMANCE POR LOJA\n")
            f.write("-" * 40 + "\n")
            resumo_loja = df_vendas.groupby('loja').agg({
                'numero_venda': 'count',
                'valor_venda': ['sum', 'mean'],
                'entrada': 'sum'
            }).round(2)
            
            for loja in sorted(lojas):
                dados = resumo_loja.loc[loja]
                qtd = dados[('numero_venda', 'count')]
                valor_total_loja = dados[('valor_venda', 'sum')]
                valor_medio = dados[('valor_venda', 'mean')]
                entrada_loja = dados[('entrada', 'sum')]
                
                f.write(f"\n🏢 {loja}:\n")
                f.write(f"   💰 Vendas: {qtd:,}\n")
                f.write(f"   💵 Faturamento: R$ {valor_total_loja:,.2f}\n")
                f.write(f"   📈 Ticket médio: R$ {valor_medio:,.2f}\n")
                f.write(f"   🏧 Entradas: R$ {entrada_loja:,.2f}\n")
                f.write(f"   📊 % do total: {(valor_total_loja/valor_total)*100:.1f}%\n")
            
            # Top formas de pagamento
            f.write("\n💳 TOP FORMAS DE PAGAMENTO\n")
            f.write("-" * 40 + "\n")
            formas = df_vendas.groupby('forma_pgto').agg({
                'numero_venda': 'count',
                'valor_venda': 'sum'
            }).sort_values('valor_venda', ascending=False).head(10)
            
            for forma, dados in formas.iterrows():
                f.write(f"{forma}: {dados['numero_venda']} vendas (R$ {dados['valor_venda']:,.2f})\n")
            
            # Arquivos processados
            f.write(f"\n📂 ARQUIVOS PROCESSADOS ({len(resumo_arquivos)})\n")
            f.write("-" * 40 + "\n")
            for arquivo, dados in resumo_arquivos.items():
                f.write(f"✅ {dados['arquivo']}: {dados['vendas']} vendas\n")
        
        print(f"📄 RELATÓRIO TEXTO GERADO: {arquivo_texto}")
    
    def gerar_dashboards(self, df_vendas, timestamp):
        """Gera dashboards visuais (requer matplotlib)"""
        import matplotlib.pyplot as plt
        
        plt.style.use('default')
        
        # Dashboard 1: Vendas por loja
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('📊 Dashboard Executivo - Vendas por Loja', fontsize=16, fontweight='bold')
        
        # Gráfico 1: Vendas por loja (quantidade)
        vendas_loja = df_vendas.groupby('loja')['numero_venda'].count()
        axes[0,0].bar(vendas_loja.index, vendas_loja.values)
        axes[0,0].set_title('Quantidade de Vendas por Loja')
        axes[0,0].set_ylabel('Número de Vendas')
        
        # Gráfico 2: Faturamento por loja
        faturamento_loja = df_vendas.groupby('loja')['valor_venda'].sum()
        axes[0,1].bar(faturamento_loja.index, faturamento_loja.values)
        axes[0,1].set_title('Faturamento por Loja (R$)')
        axes[0,1].set_ylabel('Valor Total (R$)')
        
        # Gráfico 3: Ticket médio por loja
        ticket_medio = df_vendas.groupby('loja')['valor_venda'].mean()
        axes[1,0].bar(ticket_medio.index, ticket_medio.values)
        axes[1,0].set_title('Ticket Médio por Loja (R$)')
        axes[1,0].set_ylabel('Valor Médio (R$)')
        
        # Gráfico 4: Distribuição de formas de pagamento
        top_formas = df_vendas['forma_pgto'].value_counts().head(8)
        axes[1,1].pie(top_formas.values, labels=top_formas.index, autopct='%1.1f%%')
        axes[1,1].set_title('Distribuição Formas de Pagamento')
        
        plt.tight_layout()
        arquivo_dashboard1 = self.pasta_relatorios / f"DASHBOARD_LOJAS_{timestamp}.png"
        plt.savefig(arquivo_dashboard1, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Dashboard 2: Vendas temporais
        fig, axes = plt.subplots(2, 1, figsize=(15, 10))
        fig.suptitle('📈 Dashboard Temporal - Evolução das Vendas', fontsize=16, fontweight='bold')
        
        # Vendas por dia
        vendas_dia = df_vendas.groupby('data')['valor_venda'].sum().sort_index()
        axes[0].plot(vendas_dia.index, vendas_dia.values, marker='o', linewidth=2)
        axes[0].set_title('Faturamento Diário')
        axes[0].set_ylabel('Valor (R$)')
        axes[0].grid(True, alpha=0.3)
        
        # Vendas por mês e loja
        vendas_mes_loja = df_vendas.groupby(['mes', 'loja'])['valor_venda'].sum().unstack(fill_value=0)
        vendas_mes_loja.plot(kind='bar', ax=axes[1], stacked=True)
        axes[1].set_title('Faturamento Mensal por Loja')
        axes[1].set_ylabel('Valor (R$)')
        axes[1].legend(title='Loja')
        axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        arquivo_dashboard2 = self.pasta_relatorios / f"DASHBOARD_TEMPORAL_{timestamp}.png"
        plt.savefig(arquivo_dashboard2, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 DASHBOARDS GERADOS:")
        print(f"   📈 {arquivo_dashboard1}")
        print(f"   📅 {arquivo_dashboard2}")

def main():
    print("📊 GERADOR DE RELATÓRIO EXECUTIVO")
    print("=" * 50)
    
    relatorio = RelatorioExecutivo()
    arquivo_gerado = relatorio.gerar_relatorio_completo()
    
    if arquivo_gerado:
        print(f"\n🎉 RELATÓRIO EXECUTIVO CONCLUÍDO!")
        print(f"📂 Pasta: {relatorio.pasta_relatorios}")
        print(f"📄 Arquivo principal: {arquivo_gerado.name}")
    else:
        print(f"\n❌ Falha na geração do relatório")

if __name__ == "__main__":
    main()