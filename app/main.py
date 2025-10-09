from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import pandas as pd
import io
from pathlib import Path

app = FastAPI(
    title="Sistema de Gestão de Óticas - Carne Fácil",
    description="Sistema para análise e normalização de dados de óticas",
    version="1.0.0"
)

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Página inicial do sistema"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Gestão de Óticas</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }
            .upload-area { background: #f8f9fa; padding: 30px; border-radius: 10px; margin: 20px 0; border: 2px dashed #dee2e6; }
            .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            .btn:hover { background: #0056b3; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
            .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏥 Sistema de Gestão de Óticas</h1>
            <p>Análise e normalização inteligente de dados de ordens de serviço</p>
        </div>
        
        <div class="upload-area">
            <h2>📊 Upload de Planilhas</h2>
            <form id="uploadForm" enctype="multipart/form-data">
                <input type="file" id="file" name="file" accept=".xlsx,.xls,.xlsm" multiple>
                <button type="submit" class="btn">Processar Planilhas</button>
            </form>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>👥 Clientes</h3>
                <p id="clientesCount">0 registros</p>
            </div>
            <div class="stat-card">
                <h3>📝 Ordens de Serviço</h3>
                <p id="osCount">0 registros</p>
            </div>
            <div class="stat-card">
                <h3>🔍 Duplicatas Encontradas</h3>
                <p id="duplicatesCount">0 registros</p>
            </div>
            <div class="stat-card">
                <h3>✅ Status</h3>
                <p id="status">Aguardando dados</p>
            </div>
        </div>
        
        <div id="detalhesProcessamento" style="display: none; margin: 20px 0;">
            <h2>📊 Detalhes do Processamento</h2>
            <div id="detalhesConteudo"></div>
        </div>
        
        <script>
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData();
                const files = document.getElementById('file').files;
                
                for (let file of files) {
                    formData.append('files', file);
                }
                
                document.getElementById('status').textContent = 'Processando...';
                
                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        document.getElementById('clientesCount').textContent = result.clientes + ' registros';
                        document.getElementById('osCount').textContent = result.ordens_servico + ' registros';
                        document.getElementById('duplicatesCount').textContent = result.duplicatas + ' registros';
                        document.getElementById('status').textContent = 'Processamento concluído!';
                        
                        // Mostrar detalhes por arquivo
                        if (result.detalhes_por_arquivo && result.detalhes_por_arquivo.length > 0) {
                            let detalhesHtml = '<table style="width: 100%; border-collapse: collapse; margin: 10px 0;">';
                            detalhesHtml += '<tr style="background: #f8f9fa;"><th style="padding: 10px; border: 1px solid #dee2e6;">Arquivo</th><th style="padding: 10px; border: 1px solid #dee2e6;">Linhas Total</th><th style="padding: 10px; border: 1px solid #dee2e6;">OS Lancaster</th><th style="padding: 10px; border: 1px solid #dee2e6;">OS OTM</th><th style="padding: 10px; border: 1px solid #dee2e6;">Total OS</th></tr>';
                            
                            result.detalhes_por_arquivo.forEach(arquivo => {
                                detalhesHtml += `<tr>
                                    <td style="padding: 10px; border: 1px solid #dee2e6;">${arquivo.nome}</td>
                                    <td style="padding: 10px; border: 1px solid #dee2e6; text-align: center;">${arquivo.linhas_total}</td>
                                    <td style="padding: 10px; border: 1px solid #dee2e6; text-align: center;">${arquivo.os_lancaster}</td>
                                    <td style="padding: 10px; border: 1px solid #dee2e6; text-align: center;">${arquivo.os_otm}</td>
                                    <td style="padding: 10px; border: 1px solid #dee2e6; text-align: center; font-weight: bold;">${arquivo.total_os}</td>
                                </tr>`;
                            });
                            
                            detalhesHtml += '</table>';
                            document.getElementById('detalhesConteudo').innerHTML = detalhesHtml;
                            document.getElementById('detalhesProcessamento').style.display = 'block';
                        }
                    } else {
                        document.getElementById('status').textContent = 'Erro: ' + result.detail;
                    }
                } catch (error) {
                    document.getElementById('status').textContent = 'Erro de conexão: ' + error.message;
                }
            });
        </script>
    </body>
    </html>
    """

@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    """Upload e processamento de planilhas"""
    try:
        results = {
            "clientes": 0,
            "ordens_servico": 0,
            "duplicatas": 0,
            "arquivos_processados": [],
            "detalhes_por_arquivo": []
        }
        
        for file in files:
            # Aceitar arquivos Excel (.xlsx, .xls, .xlsm)
            if not file.filename.lower().endswith(('.xlsx', '.xls', '.xlsm')):
                continue
                
            # Ler planilha com suporte a macros
            content = await file.read()
            try:
                # Para arquivos XLSM, usar engine='openpyxl' que suporta macros
                if file.filename.lower().endswith('.xlsm'):
                    df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
                else:
                    df = pd.read_excel(io.BytesIO(content))
            except Exception as e:
                continue
            
            # Extrair OS corretamente das colunas específicas
            os_count = 0
            detalhes_arquivo = {
                "nome": file.filename,
                "linhas_total": len(df),
                "os_lancaster": 0,
                "os_otm": 0
            }
            
            # Verificar coluna OS LANCASTER
            if 'OS LANCASTER' in df.columns:
                os_lancaster = pd.to_numeric(df['OS LANCASTER'], errors='coerce').dropna()
                detalhes_arquivo["os_lancaster"] = len(os_lancaster)
                os_count += len(os_lancaster)
            
            # Verificar coluna OS OTM
            if 'OS OTM' in df.columns:
                os_otm = pd.to_numeric(df['OS OTM'], errors='coerce').dropna()
                detalhes_arquivo["os_otm"] = len(os_otm)
                os_count += len(os_otm)
            
            # Se não encontrou colunas específicas, tentar outras variações
            if os_count == 0:
                colunas_os = [col for col in df.columns if 'OS' in str(col).upper()]
                for col in colunas_os:
                    valores_os = pd.to_numeric(df[col], errors='coerce').dropna()
                    os_count += len(valores_os)
            
            results["ordens_servico"] += os_count
            detalhes_arquivo["total_os"] = os_count
            results["detalhes_por_arquivo"].append(detalhes_arquivo)
            
            # Tentar identificar clientes (buscar colunas de nomes)
            colunas_nome = [col for col in df.columns if any(termo in col.lower() for termo in ['nome', 'cliente', 'paciente'])]
            if colunas_nome:
                nome_col = colunas_nome[0]
                clientes_unicos = df[nome_col].nunique()
                results["clientes"] += clientes_unicos
                
                # Detectar duplicatas potenciais
                total_nomes = len(df[nome_col].dropna())
                results["duplicatas"] += max(0, total_nomes - clientes_unicos)
            
            results["arquivos_processados"].append(file.filename)
            
            # Salvar arquivo processado
            save_path = Path(f"data/raw/{file.filename}")
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(content)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar arquivos: {str(e)}")

@app.get("/api/analyze/{file_id}")
async def analyze_file(file_id: str):
    """Análise detalhada de um arquivo específico"""
    # TODO: Implementar análise detalhada
    return {"message": f"Análise do arquivo {file_id} em desenvolvimento"}

@app.get("/api/deduplicate")
async def deduplicate_clients():
    """Executar processo de deduplicação"""
    # TODO: Implementar deduplicação inteligente
    return {"message": "Deduplicação em desenvolvimento"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)