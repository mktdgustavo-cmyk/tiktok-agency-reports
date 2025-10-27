#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador Automático de Relatórios de Agência
Desenvolvido para análise semanal de creators TikTok
"""

from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
import os
import pandas as pd
from datetime import datetime
import json
from analisador import AnalisadorRelatorio

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Extensões permitidas
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def limpar_arquivos_antigos():
    """Remove arquivos com mais de 30 dias"""
    import time
    agora = time.time()
    
    for pasta in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
        if os.path.exists(pasta):
            for arquivo in os.listdir(pasta):
                caminho = os.path.join(pasta, arquivo)
                if os.path.isfile(caminho):
                    # Remove se arquivo tem mais de 30 dias (2592000 segundos)
                    if agora - os.path.getmtime(caminho) > 2592000:
                        try:
                            os.remove(caminho)
                        except:
                            pass

@app.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Processa upload da planilha"""
    try:
        limpar_arquivos_antigos()
        
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Arquivo vazio'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Formato não suportado. Use XLSX, XLS ou CSV'}), 400
        
        # Salvar arquivo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_com_timestamp = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename_com_timestamp)
        file.save(filepath)
        
        # Processar planilha
        analisador = AnalisadorRelatorio(filepath)
        resultado = analisador.processar()
        
        if resultado['status'] == 'erro':
            return jsonify({'error': resultado['mensagem']}), 400
        
        # Gerar relatório HTML
        html_filename = f"relatorio_{timestamp}.html"
        html_path = os.path.join(app.config['OUTPUT_FOLDER'], html_filename)
        analisador.gerar_html(html_path)
        
        return jsonify({
            'status': 'sucesso',
            'mensagem': 'Relatório gerado com sucesso!',
            'dados': resultado['dados'],
            'html_url': f'/relatorio/{html_filename}',
            'pdf_url': f'/pdf/{html_filename}',
            'timestamp': timestamp
        })
    
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': f'Erro ao processar arquivo: {str(e)}'}), 500

@app.route('/relatorio/<filename>')
def visualizar_relatorio(filename):
    """Exibe relatório HTML"""
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        return send_file(filepath, mimetype='text/html')
    except Exception as e:
        return f"Erro ao carregar relatório: {str(e)}", 404

@app.route('/pdf/<html_filename>')
def gerar_pdf(html_filename):
    """Gera e retorna PDF do relatório"""
    try:
        from weasyprint import HTML
        
        html_path = os.path.join(app.config['OUTPUT_FOLDER'], html_filename)
        pdf_filename = html_filename.replace('.html', '.pdf')
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
        
        # Gerar PDF
        HTML(filename=html_path).write_pdf(pdf_path)
        
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'relatorio_agencia_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar PDF: {str(e)}'}), 500

@app.route('/health')
def health():
    """Endpoint de health check para Easypanel"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/historico')
def historico():
    """Página de histórico de relatórios"""
    try:
        relatorios = []
        output_folder = app.config['OUTPUT_FOLDER']
        
        if os.path.exists(output_folder):
            # Listar apenas arquivos HTML
            arquivos = [f for f in os.listdir(output_folder) if f.endswith('.html')]
            
            for arquivo in arquivos:
                caminho = os.path.join(output_folder, arquivo)
                # Pegar data de modificação
                timestamp = os.path.getmtime(caminho)
                data_criacao = datetime.fromtimestamp(timestamp)
                
                # Extrair período do nome do arquivo se possível
                # Formato esperado: relatorio_20251027_143045.html
                periodo = "N/D"
                try:
                    # Tentar extrair data do nome do arquivo
                    partes = arquivo.replace('relatorio_', '').replace('.html', '').split('_')
                    if len(partes) >= 1:
                        data_parte = partes[0]
                        if len(data_parte) == 8:  # YYYYMMDD
                            periodo = f"{data_parte[6:8]}/{data_parte[4:6]}/{data_parte[0:4]}"
                except:
                    pass
                
                relatorios.append({
                    'arquivo': arquivo,
                    'data_criacao': data_criacao.strftime('%d/%m/%Y %H:%M'),
                    'periodo': periodo,
                    'tamanho': os.path.getsize(caminho)
                })
            
            # Ordenar por data de criação (mais recente primeiro)
            relatorios.sort(key=lambda x: x['data_criacao'], reverse=True)
        
        return render_template('historico.html', relatorios=relatorios)
    
    except Exception as e:
        return f"Erro ao carregar histórico: {str(e)}", 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'Arquivo muito grande. Máximo: 16MB'}), 413

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    # Criar pastas se não existirem
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    # Rodar aplicação
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
