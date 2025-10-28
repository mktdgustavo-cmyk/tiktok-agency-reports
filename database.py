#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Banco de Dados - Supabase
Gerencia usuários e histórico de relatórios
"""

import os
from supabase import create_client, Client
from datetime import datetime
import bcrypt

class Database:
    """Gerenciador de banco de dados Supabase"""
    
    def __init__(self):
        """Inicializa conexão com Supabase"""
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            print("⚠️ Credenciais Supabase não configuradas!")
            self.supabase = None
        else:
            self.supabase: Client = create_client(url, key)
            print("✅ Conectado ao Supabase!")
    
    def is_connected(self):
        """Verifica se está conectado"""
        return self.supabase is not None
    
    # ==========================================
    # USUÁRIOS
    # ==========================================
    
    def criar_usuario(self, email, senha, tipo='creator', nome_display=None, criadores_gerenciados=None):
        """
        Cria um novo usuário
        
        Tipos:
        - 'creator': vê apenas seus dados
        - 'sub_agente': vê criadores que gerencia
        - 'admin': vê tudo
        """
        if not self.is_connected():
            return {'erro': 'Banco não conectado'}
        
        try:
            # Hashear senha
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            dados = {
                'email': email,
                'senha_hash': senha_hash,
                'tipo': tipo,
                'nome_display': nome_display or email.split('@')[0],
                'criadores_gerenciados': criadores_gerenciados or [],
                'criado_em': datetime.now().isoformat()
            }
            
            result = self.supabase.table('usuarios').insert(dados).execute()
            return {'sucesso': True, 'usuario': result.data[0]}
        
        except Exception as e:
            return {'erro': str(e)}
    
    def buscar_usuario_por_email(self, email):
        """Busca usuário por email"""
        if not self.is_connected():
            return None
        
        try:
            result = self.supabase.table('usuarios').select('*').eq('email', email).execute()
            return result.data[0] if result.data else None
        except:
            return None
    
    def verificar_senha(self, senha, senha_hash):
        """Verifica se senha está correta"""
        try:
            return bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8'))
        except:
            return False
    
    def autenticar(self, email, senha):
        """Autentica usuário"""
        usuario = self.buscar_usuario_por_email(email)
        
        if not usuario:
            return {'sucesso': False, 'erro': 'Usuário não encontrado'}
        
        if not self.verificar_senha(senha, usuario['senha_hash']):
            return {'sucesso': False, 'erro': 'Senha incorreta'}
        
        # Remover senha do retorno
        del usuario['senha_hash']
        
        return {'sucesso': True, 'usuario': usuario}
    
    # ==========================================
    # RELATÓRIOS
    # ==========================================
    
    def salvar_relatorio(self, periodo_inicio, periodo_fim, dados_criadores):
        """
        Salva dados do relatório no banco
        
        dados_criadores: lista de dicts com:
        - nome, diamantes, horas, batalhas, dias, status, etc.
        """
        if not self.is_connected():
            return {'erro': 'Banco não conectado'}
        
        try:
            registros = []
            
            for criador in dados_criadores:
                registros.append({
                    'periodo_inicio': periodo_inicio,
                    'periodo_fim': periodo_fim,
                    'creator_nome': criador['nome'],
                    'diamantes': criador['diamantes'],
                    'horas': criador['horas'],
                    'batalhas': criador['batalhas'],
                    'dias_validos': criador['dias'],
                    'perc_batalhas': criador['perc_bat'],
                    'diamantes_por_hora': criador['diam_hora'],
                    'status': criador['classificacao']['status'],
                    'motivo': criador['classificacao']['motivo'],
                    'is_top': criador['is_top'],
                    'data_criacao': datetime.now().isoformat()
                })
            
            # Inserir em lote
            result = self.supabase.table('relatorios').insert(registros).execute()
            return {'sucesso': True, 'total': len(registros)}
        
        except Exception as e:
            return {'erro': str(e)}
    
    def buscar_historico_creator(self, creator_nome, limite=10):
        """Busca histórico de um creator específico"""
        if not self.is_connected():
            return []
        
        try:
            result = self.supabase.table('relatorios')\
                .select('*')\
                .eq('creator_nome', creator_nome)\
                .order('data_criacao', desc=True)\
                .limit(limite)\
                .execute()
            
            return result.data
        except:
            return []
    
    def buscar_historico_completo(self, limite=20):
        """Busca histórico completo (admin)"""
        if not self.is_connected():
            return []
        
        try:
            result = self.supabase.table('relatorios')\
                .select('*')\
                .order('data_criacao', desc=True)\
                .limit(limite)\
                .execute()
            
            return result.data
        except:
            return []
    
    def buscar_ultimas_semanas_creator(self, creator_nome, n_semanas=4):
        """Busca últimas N semanas de um creator para gráficos"""
        if not self.is_connected():
            return []
        
        try:
            # Buscar registros únicos por período
            result = self.supabase.table('relatorios')\
                .select('periodo_inicio, periodo_fim, diamantes, horas, batalhas')\
                .eq('creator_nome', creator_nome)\
                .order('periodo_fim', desc=True)\
                .limit(n_semanas)\
                .execute()
            
            return result.data
        except:
            return []
    
    # ==========================================
    # ESTATÍSTICAS
    # ==========================================
    
    def estatisticas_creator(self, creator_nome):
        """Retorna estatísticas gerais de um creator"""
        if not self.is_connected():
            return None
        
        try:
            historico = self.buscar_historico_creator(creator_nome, limite=100)
            
            if not historico:
                return None
            
            total_diamantes = sum(r['diamantes'] for r in historico)
            total_horas = sum(r['horas'] for r in historico)
            media_diamantes = total_diamantes / len(historico)
            media_horas = total_horas / len(historico)
            
            # Contar status
            status_count = {}
            for r in historico:
                status = r['status']
                status_count[status] = status_count.get(status, 0) + 1
            
            return {
                'total_semanas': len(historico),
                'total_diamantes': total_diamantes,
                'total_horas': total_horas,
                'media_diamantes': round(media_diamantes, 2),
                'media_horas': round(media_horas, 2),
                'status_distribuicao': status_count,
                'melhor_semana': max(historico, key=lambda x: x['diamantes']),
                'pior_semana': min(historico, key=lambda x: x['diamantes'])
            }
        
        except Exception as e:
            print(f"Erro estatísticas: {e}")
            return None


# Instância global
db = Database()
