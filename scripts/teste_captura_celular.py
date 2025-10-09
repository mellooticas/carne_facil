#!/usr/bin/env python3
"""
Teste de Captura do Campo CELULAR
Vamos verificar se agora estamos pegando o campo correto! 😄
"""

import pandas as pd
from pathlib import Path
import re

def identificar_campos_teste(arquivo_path):
    """Identifica campos usando a mesma lógica do consolidador"""
    
    try:
        # Carregar arquivo
        engine = 'openpyxl' if arquivo_path.suffix.lower() in ['.xlsx', '.xlsm'] else None
        excel_file = pd.ExcelFile(arquivo_path, engine=engine)
        
        # Encontrar sheet principal
        sheet_principal = None
        for sheet_name in ['base_clientes_OS', 'base', 'dados']:
            if sheet_name in excel_file.sheet_names:
                sheet_principal = sheet_name
                break
        
        if not sheet_principal:
            sheet_principal = excel_file.sheet_names[0]
        
        df_original = pd.read_excel(arquivo_path, sheet_name=sheet_principal, engine=engine)
        
        # Identificar campos (mesma lógica do consolidador)
        campos = {}
        
        # Primeiro, buscar campos específicos com prioridade
        for col in df_original.columns:
            col_lower = str(col).lower().strip()
            
            # CELULAR tem prioridade absoluta sobre TELEFONE
            if any(termo in col_lower for termo in ['celular:', 'celular']) and 'celular' not in campos:
                campos['celular'] = col
        
        # Depois buscar outros campos
        for col in df_original.columns:
            col_lower = str(col).lower().strip()
            
            if any(termo in col_lower for termo in ['nome:', 'nome', 'cliente', 'paciente']) and 'nome' not in campos:
                campos['nome'] = col
            elif any(termo in col_lower for termo in ['cpf']) and 'cpf' not in campos:
                campos['cpf'] = col
            elif any(termo in col_lower for termo in ['rg']) and 'rg' not in campos:
                campos['rg'] = col
            elif 'celular' not in campos and any(termo in col_lower for termo in ['telefone:', 'telefone', 'fone']):
                campos['celular'] = col
            elif any(termo in col_lower for termo in ['email:', 'email', 'e-mail']) and 'email' not in campos:
                campos['email'] = col
            elif any(termo in col_lower for termo in ['end:', 'endereco', 'endereço', 'endereco:', 'endereço:']) and 'endereco' not in campos:
                campos['endereco'] = col
        
        return campos, df_original
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return {}, None

def limpar_celular_sp(celular):
    """Mesma função do consolidador"""
    if not celular or str(celular).strip() == '' or pd.isna(celular):
        return None
    
    cel_str = re.sub(r'[^\d]', '', str(celular))
    
    if len(cel_str) < 9:
        return None
    
    if len(cel_str) == 9:
        cel_str = '11' + cel_str
    elif len(cel_str) == 10:
        cel_str = '11' + cel_str
    elif len(cel_str) == 11 and cel_str.startswith('1'):
        pass
    elif len(cel_str) == 11 and not cel_str.startswith('11'):
        cel_str = '11' + cel_str[2:]
    elif len(cel_str) == 13 and cel_str.startswith('55'):
        cel_str = '11' + cel_str[4:]
    elif len(cel_str) > 11:
        cel_str = '11' + cel_str[-9:]
    
    if len(cel_str) == 11 and cel_str.startswith('11') and cel_str[2] == '9':
        return f"(11) {cel_str[2:7]}-{cel_str[7:]}"
    
    return None

def testar_captura_celular():
    """Testa a captura do campo celular"""
    
    print("📱 TESTE DE CAPTURA DO CAMPO CELULAR")
    print("=" * 60)
    print("🎯 Verificando se agora pegamos o campo 'CELULAR:' corretamente")
    print("=" * 60)
    
    arquivo_teste = Path("data/raw/OS NOVA - mesa01.xlsm")
    
    if not arquivo_teste.exists():
        print(f"❌ Arquivo não encontrado: {arquivo_teste}")
        return
    
    # Identificar campos
    campos, df = identificar_campos_teste(arquivo_teste)
    
    print(f"📋 CAMPOS IDENTIFICADOS:")
    print("-" * 60)
    
    for campo_padrao, coluna_original in campos.items():
        print(f"✅ {campo_padrao:<12} → '{coluna_original}'")
    
    # Testar especificamente o celular
    if 'celular' in campos:
        campo_celular = campos['celular']
        print(f"\n🎉 SUCESSO! Campo celular encontrado: '{campo_celular}'")
        print("-" * 60)
        
        # Pegar algumas amostras
        celulares_originais = df[campo_celular].dropna().head(10).tolist()
        
        print(f"📱 AMOSTRAS DO CAMPO CELULAR (originais):")
        for i, celular in enumerate(celulares_originais, 1):
            print(f"   {i:2d}. {celular}")
        
        print(f"\n📱 AMOSTRAS APÓS VALIDAÇÃO SP:")
        for i, celular in enumerate(celulares_originais, 1):
            celular_formatado = limpar_celular_sp(celular)
            status = "✅" if celular_formatado else "❌"
            print(f"   {i:2d}. {status} '{celular}' → '{celular_formatado}'")
        
        # Estatísticas
        total_celulares = len(df[campo_celular].dropna())
        celulares_validos = 0
        
        for celular in df[campo_celular].dropna():
            if limpar_celular_sp(celular):
                celulares_validos += 1
        
        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   📱 Total de celulares não vazios: {total_celulares}")
        print(f"   ✅ Celulares válidos SP: {celulares_validos}")
        print(f"   📈 Taxa de validação: {(celulares_validos/total_celulares*100):.1f}%")
        
    else:
        print(f"\n❌ Campo celular NÃO encontrado!")
        print(f"💡 Campos disponíveis: {list(campos.keys())}")
        
        # Mostrar todas as colunas para debug
        print(f"\n🔍 TODAS AS COLUNAS DISPONÍVEIS:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. '{col}'")

if __name__ == "__main__":
    testar_captura_celular()