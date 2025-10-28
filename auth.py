#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Autenticação
Flask-Login + Supabase
"""

from flask_login import UserMixin

class User(UserMixin):
    """Classe de usuário para Flask-Login"""
    
    def __init__(self, user_data):
        """
        user_data: dict do Supabase com:
        - id, email, tipo, nome_display, criadores_gerenciados
        """
        self.id = str(user_data['id'])
        self.email = user_data['email']
        self.tipo = user_data['tipo']
        self.nome_display = user_data.get('nome_display', self.email.split('@')[0])
        self.criadores_gerenciados = user_data.get('criadores_gerenciados', [])
    
    def is_admin(self):
        """Verifica se é admin"""
        return self.tipo == 'admin'
    
    def is_sub_agente(self):
        """Verifica se é sub-agente"""
        return self.tipo == 'sub_agente'
    
    def is_creator(self):
        """Verifica se é creator"""
        return self.tipo == 'creator'
    
    def pode_ver_creator(self, creator_nome):
        """Verifica se pode ver dados de um creator específico"""
        if self.is_admin():
            return True
        
        if self.is_sub_agente():
            return creator_nome in self.criadores_gerenciados
        
        if self.is_creator():
            # Creator só vê seus próprios dados
            # Verificar se o email corresponde ao username
            return creator_nome.lower() in self.email.lower()
        
        return False
    
    def get_criadores_permitidos(self):
        """Retorna lista de creators que pode visualizar"""
        if self.is_admin():
            return None  # None = todos
        
        if self.is_sub_agente():
            return self.criadores_gerenciados
        
        if self.is_creator():
            # Tentar extrair username do email
            return [self.email.split('@')[0]]
        
        return []
