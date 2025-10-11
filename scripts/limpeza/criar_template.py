#!/usr/bin/env python3
"""
📋 GERADOR DE TEMPLATE EXCEL PADRONIZADO
================================================================================
🎯 Cria arquivo Excel modelo com estrutura padronizada
📊 Use este template para organizar os dados antes de processar
🔧 Garante consistência e elimina problemas de estrutura
================================================================================
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def criar_template_padronizado():
    """Cria template Excel com estrutura padronizada"""
    
    # Definir colunas padronizadas
    colunas_padronizadas = [
        # Identificação da OS
        'OS_NUMERO',
        'LOJA',
        'SISTEMA',
        'DATA_OS',
        'CONSULTOR',
        
        # Dados do Cliente
        'CLIENTE_NOME',
        'CLIENTE_CPF',
        'CLIENTE_RG',
        'CLIENTE_NASCIMENTO',
        'CLIENTE_CELULAR',
        'CLIENTE_EMAIL',
        'CLIENTE_ENDERECO',
        'CLIENTE_CEP',
        'CLIENTE_BAIRRO',
        
        # Dioptrías Olho Direito (OD)
        'ESF_OD',
        'CIL_OD',
        'EIXO_OD',
        'DNP_OD',
        'ALTURA_OD',
        'ADICAO_OD',
        
        # Dioptrías Olho Esquerdo (OE)
        'ESF_OE',
        'CIL_OE',
        'EIXO_OE',
        'DNP_OE',
        'ALTURA_OE',
        'ADICAO_OE',
        
        # Medidas da Armação
        'PONTE',
        'HORIZONTAL',
        'VERTICAL',
        'DIAG_MAIOR',
        
        # Produtos (até 5 produtos por OS)
        'PRODUTO_1_CODIGO',
        'PRODUTO_1_DESCRICAO',
        'PRODUTO_1_VALOR',
        
        'PRODUTO_2_CODIGO',
        'PRODUTO_2_DESCRICAO',
        'PRODUTO_2_VALOR',
        
        'PRODUTO_3_CODIGO',
        'PRODUTO_3_DESCRICAO',
        'PRODUTO_3_VALOR',
        
        'PRODUTO_4_CODIGO',
        'PRODUTO_4_DESCRICAO',
        'PRODUTO_4_VALOR',
        
        'PRODUTO_5_CODIGO',
        'PRODUTO_5_DESCRICAO',
        'PRODUTO_5_VALOR',
        
        # Vendas e Pagamentos
        'COD_TRELLO',
        'VALOR_TOTAL',
        'PAGAMENTO_1',
        'SINAL_1',
        'PAGAMENTO_2',
        'SINAL_2',
        'VALOR_RESTANTE'
    ]
    
    # Criar DataFrame exemplo
    dados_exemplo = []
    
    # Linha 1 - Exemplo MAUA
    exemplo_1 = {
        'OS_NUMERO': 4001,
        'LOJA': 'MAUA',
        'SISTEMA': 'LANCASTER',
        'DATA_OS': '01/10/2024',
        'CONSULTOR': 'BETH',
        
        'CLIENTE_NOME': 'JOÃO DA SILVA',
        'CLIENTE_CPF': '12345678901',
        'CLIENTE_RG': '123456789',
        'CLIENTE_NASCIMENTO': '15/05/1980',
        'CLIENTE_CELULAR': '11999887766',
        'CLIENTE_EMAIL': 'joao@email.com',
        'CLIENTE_ENDERECO': 'RUA DAS FLORES, 123',
        'CLIENTE_CEP': '12345678',
        'CLIENTE_BAIRRO': 'CENTRO',
        
        'ESF_OD': -2.50,
        'CIL_OD': -1.25,
        'EIXO_OD': 90,
        'DNP_OD': 32,
        'ALTURA_OD': 18,
        'ADICAO_OD': 2.00,
        
        'ESF_OE': -2.75,
        'CIL_OE': -1.50,
        'EIXO_OE': 85,
        'DNP_OE': 30,
        'ALTURA_OE': 17,
        'ADICAO_OE': 2.00,
        
        'PONTE': 18,
        'HORIZONTAL': 52,
        'VERTICAL': 38,
        'DIAG_MAIOR': 55,
        
        'PRODUTO_1_CODIGO': 'ARM001',
        'PRODUTO_1_DESCRICAO': 'ARMACAO TITANIO',
        'PRODUTO_1_VALOR': 350.00,
        
        'PRODUTO_2_CODIGO': 'LEN001',
        'PRODUTO_2_DESCRICAO': 'LENTE MULTIFOCAL',
        'PRODUTO_2_VALOR': 450.00,
        
        'COD_TRELLO': 'TRL123',
        'VALOR_TOTAL': 800.00,
        'PAGAMENTO_1': 'DINHEIRO',
        'SINAL_1': 200.00,
        'PAGAMENTO_2': 'CARTAO',
        'SINAL_2': 600.00,
        'VALOR_RESTANTE': 0.00
    }
    
    # Linha 2 - Exemplo SAO_MATEUS
    exemplo_2 = {
        'OS_NUMERO': 5001,
        'LOJA': 'SAO_MATEUS',
        'SISTEMA': 'LANCASTER',
        'DATA_OS': '02/10/2024',
        'CONSULTOR': 'MARIA',
        
        'CLIENTE_NOME': 'ANA MARIA SANTOS',
        'CLIENTE_CPF': '98765432100',
        'CLIENTE_RG': '987654321',
        'CLIENTE_NASCIMENTO': '20/08/1975',
        'CLIENTE_CELULAR': '11888776655',
        'CLIENTE_EMAIL': 'ana@email.com',
        'CLIENTE_ENDERECO': 'AV. PRINCIPAL, 456',
        'CLIENTE_CEP': '87654321',
        'CLIENTE_BAIRRO': 'JARDIM',
        
        'ESF_OD': -1.75,
        'CIL_OD': -0.75,
        'EIXO_OD': 180,
        'DNP_OD': 31,
        'ALTURA_OD': 19,
        'ADICAO_OD': '',
        
        'ESF_OE': -1.50,
        'CIL_OE': -0.50,
        'EIXO_OE': 175,
        'DNP_OE': 29,
        'ALTURA_OE': 18,
        'ADICAO_OE': '',
        
        'PONTE': 16,
        'HORIZONTAL': 50,
        'VERTICAL': 36,
        'DIAG_MAIOR': 53,
        
        'PRODUTO_1_CODIGO': 'ARM002',
        'PRODUTO_1_DESCRICAO': 'ARMACAO ACETATO',
        'PRODUTO_1_VALOR': 280.00,
        
        'PRODUTO_2_CODIGO': 'LEN002',
        'PRODUTO_2_DESCRICAO': 'LENTE SIMPLES',
        'PRODUTO_2_VALOR': 180.00,
        
        'COD_TRELLO': 'TRL456',
        'VALOR_TOTAL': 460.00,
        'PAGAMENTO_1': 'PIX',
        'SINAL_1': 460.00,
        'VALOR_RESTANTE': 0.00
    }
    
    # Adicionar exemplos às linhas
    for col in colunas_padronizadas:
        if col not in exemplo_1:
            exemplo_1[col] = ''
        if col not in exemplo_2:
            exemplo_2[col] = ''
    
    dados_exemplo = [exemplo_1, exemplo_2]
    
    # Criar DataFrame
    df_template = pd.DataFrame(dados_exemplo, columns=colunas_padronizadas)
    
    # Salvar template
    output_dir = Path("data/templates")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    template_file = output_dir / f"TEMPLATE_PADRONIZADO_{timestamp}.xlsx"
    
    with pd.ExcelWriter(template_file, engine='openpyxl') as writer:
        # Sheet com exemplos
        df_template.to_excel(writer, sheet_name='DADOS_EXEMPLO', index=False)
        
        # Sheet vazia para preenchimento
        df_vazio = pd.DataFrame(columns=colunas_padronizadas)
        df_vazio.to_excel(writer, sheet_name='DADOS_NOVOS', index=False)
        
        # Sheet com documentação
        doc_data = []
        doc_data.append(['CAMPO', 'DESCRIÇÃO', 'EXEMPLO'])
        doc_data.append(['OS_NUMERO', 'Número único da Ordem de Serviço', '4001'])
        doc_data.append(['LOJA', 'Nome da loja (MAUA, SAO_MATEUS, RIO_PEQUENO)', 'MAUA'])
        doc_data.append(['SISTEMA', 'Sistema usado (LANCASTER, OTM)', 'LANCASTER'])
        doc_data.append(['CLIENTE_NOME', 'Nome completo do cliente', 'JOÃO DA SILVA'])
        doc_data.append(['CLIENTE_CPF', 'CPF sem pontuação', '12345678901'])
        doc_data.append(['ESF_OD', 'Grau esférico olho direito', '-2.50'])
        doc_data.append(['CIL_OD', 'Grau cilíndrico olho direito', '-1.25'])
        doc_data.append(['PRODUTO_1_CODIGO', 'Código do produto 1', 'ARM001'])
        doc_data.append(['VALOR_TOTAL', 'Valor total da venda', '800.00'])
        
        df_doc = pd.DataFrame(doc_data[1:], columns=doc_data[0])
        df_doc.to_excel(writer, sheet_name='DOCUMENTACAO', index=False)
    
    print(f"📋 TEMPLATE CRIADO COM SUCESSO!")
    print("=" * 80)
    print(f"📁 Arquivo: {template_file}")
    print(f"📊 {len(colunas_padronizadas)} colunas padronizadas")
    print(f"📄 3 sheets: DADOS_EXEMPLO, DADOS_NOVOS, DOCUMENTACAO")
    print("\n💡 COMO USAR:")
    print("1. Use a sheet DADOS_NOVOS para inserir dados")
    print("2. Siga os exemplos da sheet DADOS_EXEMPLO")
    print("3. Consulte a DOCUMENTACAO para detalhes dos campos")
    print("4. Salve o arquivo em data/raw/ e execute recalcular_tudo.py")

if __name__ == "__main__":
    criar_template_padronizado()