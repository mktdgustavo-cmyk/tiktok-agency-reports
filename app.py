#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OLAH Agência - Sistema de Relatórios v3.0
Com autenticação, banco de dados e painéis individuais
"""

from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from analisador import AnalisadorRelatorio
from database import db
from auth import User
import os
from datetime import datetime, timedelta
import json

# Configuração do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'olah-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Criar pastas se não existirem
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('static/img', exist_ok=True)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """Carrega usuário pelo ID"""
    if not db.is_connected():
        return None
    
    try:
        result = db.supabase.table('usuarios').select('*').eq('id', int(user_id)).execute()
        if result.data:
            return User(result.data[0])
    except:
        pass
    return None

# ==========================================
# ROTAS DE AUTENTICAÇÃO
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('painel'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if not db.is_connected():
            return render_template('login.html', error='Banco de dados não conectado. Entre em contato com o suporte.')
        
        resultado = db.autenticar(email, senha)
        
        if resultado['sucesso']:
            user = User(resultado['usuario'])
            login_user(user, remember=True)
            return redirect(url_for('painel'))
        else:
            return render_template('login.html', error=resultado['erro'])
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    return redirect(url_for('login'))

# ==========================================
# PAINEL INDIVIDUAL
# ==========================================

@app.route('/painel')
@login_required
def painel():
    """Painel individual do creator/sub-agente/admin"""
    
    if not db.is_connected():
        return render_template('error.html', error='Banco de dados não conectrado')
    
    # Admins vão para o painel de upload
    if current_user.is_admin():
        return redirect(url_for('index'))
    
    # Creators e sub-agentes veem seus dados
    if current_user.is_creator():
        creator_nome = current_user.email.split('@')[0]
        
        # Buscar histórico
        historico = db.buscar_historico_creator(creator_nome, limite=10)
        
        # Buscar estatísticas
        stats = db.estatisticas_creator(creator_nome)
        
        if not stats:
            return render_template('painel_creator.html', 
                                 user=current_user,
                                 stats={'total_semanas': 0, 'total_diamantes': 0, 'total_horas': 0, 'media_diamantes': 0, 'media_horas': 0, 'melhor_semana': {'diamantes': 0, 'periodo_inicio': 'N/D'}},
                                 historico=[],
                                 labels=[],
                                 data=[])
        
        # Preparar dados do gráfico
        ultimas_semanas = db.buscar_ultimas_semanas_creator(creator_nome, n_semanas=8)
        ultimas_semanas.reverse()  # Mais antiga primeiro
        
        labels = [f"{s['periodo_inicio']}" for s in ultimas_semanas]
        data = [s['diamantes'] for s in ultimas_semanas]
        
        return render_template('painel_creator.html',
                             user=current_user,
                             stats=stats,
                             historico=historico,
                             labels=labels,
                             data=data)
    
    # Sub-agentes (futuro)
    return render_template('error.html', error='Tipo de usuário não suportado ainda')

# ==========================================
# PAINEL ADMIN (UPLOAD)
# ==========================================

@app.route('/')
@login_required
def index():
    """Página principal - upload de planilhas (apenas admins)"""
    if not current_user.is_admin():
        return redirect(url_for('painel'))
    
    return render_template('index.html', user=current_user)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    """Processa upload de planilha (apenas admins)"""
    if not current_user.is_admin():
        return jsonify({'erro': 'Acesso negado'}), 403
    
    if 'file' not in request.files:
        return jsonify({'erro': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'erro': 'Nenhum arquivo selecionado'}), 400
    
    if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
        return jsonify({'erro': 'Formato inválido. Use XLSX, XLS ou CSV'}), 400
    
    try:
        # Salvar arquivo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_final = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename_final)
        file.save(filepath)
        
        # Processar
        analisador = AnalisadorRelatorio(filepath)
        resultado = analisador.processar()
        
        if resultado['status'] == 'erro':
            return jsonify({'erro': resultado['mensagem']}), 400
        
        # Gerar HTML
        output_filename = f"relatorio_{timestamp}.html"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        analisador.gerar_html(output_path)
        
        # Salvar no banco de dados
        if db.is_connected():
            periodo = analisador.dados_agregados.get('periodo', '')
            if ' a ' in periodo:
                periodo_inicio, periodo_fim = periodo.split(' a ')
            else:
                periodo_inicio = periodo_fim = datetime.now().strftime('%Y-%m-%d')
            
            db.salvar_relatorio(
                periodo_inicio=periodo_inicio,
                periodo_fim=periodo_fim,
                dados_criadores=analisador.criadores
            )
            print("✅ Dados salvos no Supabase!")
        
        return jsonify({
            'sucesso': True,
            'html_url': f'/relatorio/{output_filename}',
            'pdf_url': f'/pdf/{output_filename}'
        })
    
    except Exception as e:
        print(f"Erro no upload: {e}")
        return jsonify({'erro': str(e)}), 500

# ==========================================
# VISUALIZAÇÃO DE RELATÓRIOS
# ==========================================

@app.route('/relatorio/<filename>')
@login_required
def ver_relatorio(filename):
    """Visualiza relatório gerado (apenas admins)"""
    if not current_user.is_admin():
        return redirect(url_for('painel'))
    
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return "Relatório não encontrado", 404
    
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    return html_content

@app.route('/historico')
@login_required
def historico():
    """Lista histórico de relatórios (apenas admins)"""
    if not current_user.is_admin():
        return redirect(url_for('painel'))
    
    try:
        arquivos = []
        output_dir = app.config['OUTPUT_FOLDER']
        
        for filename in os.listdir(output_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(output_dir, filename)
                stat = os.stat(filepath)
                
                arquivos.append({
                    'nome': filename,
                    'data_criacao': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M'),
                    'tamanho': f"{stat.st_size / 1024:.1f} KB",
                    'url': f'/relatorio/{filename}'
                })
        
        # Ordenar por data (mais recente primeiro)
        arquivos.sort(key=lambda x: x['data_criacao'], reverse=True)
        
        return render_template('historico.html', arquivos=arquivos, user=current_user)
    
    except Exception as e:
        return f"Erro ao listar histórico: {e}", 500

@app.route('/pdf/<filename>')
@login_required
def download_pdf(filename):
    """Gera e baixa PDF do relatório (apenas admins)"""
    if not current_user.is_admin():
        return jsonify({'erro': 'Acesso negado'}), 403
    
    try:
        from weasyprint import HTML
        
        html_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        # Verificar se arquivo HTML existe
        if not os.path.exists(html_path):
            return f"Relatório HTML não encontrado: {filename}", 404
        
        pdf_path = html_path.replace('.html', '.pdf')
        
        # Gerar PDF
        HTML(html_path).write_pdf(pdf_path)
        
        return send_file(pdf_path, as_attachment=True, download_name=filename.replace('.html', '.pdf'))
    
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        return f"Erro ao gerar PDF: {e}", 500

# ==========================================
# LIMPEZA AUTOMÁTICA
# ==========================================

def limpar_arquivos_antigos():
    """Remove arquivos com mais de 30 dias"""
    limite = datetime.now() - timedelta(days=30)
    
    for pasta in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
        if not os.path.exists(pasta):
            continue
            
        for filename in os.listdir(pasta):
            filepath = os.path.join(pasta, filename)
            
            if os.path.isfile(filepath):
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if mtime < limite:
                    os.remove(filepath)
                    print(f"🗑️ Arquivo removido: {filename}")

# Executar limpeza ao iniciar
limpar_arquivos_antigos()

# ==========================================
# HEALTH CHECK
# ==========================================

@app.route('/health')
def health():
    """Endpoint de health check"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if db.is_connected() else 'disconnected'
    })

# ==========================================
# INICIALIZAÇÃO
# ==========================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
