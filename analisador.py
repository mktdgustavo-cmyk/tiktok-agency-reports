#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Engine de Análise de Relatórios
Segue todas as regras do manual_metricas_agencia_v2.md
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime

class AnalisadorRelatorio:
    """
    Analisador de dados de creators seguindo as métricas e regras da agência
    """
    
    # Metas e alertas (seção 2 do manual)
    METAS = {
        'diamantes': {'ideal': 12500, 'alerta': 3000},
        'horas': {'ideal': 25, 'alerta': 20},
        'dias': {'ideal': 3, 'alerta': 2},
        'batalhas': {'ideal': 20, 'alerta': 5},
        'perc_batalhas': {'ideal': 50, 'alerta': 20}
    }
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        self.dados_agregados = {}
        
    def converter_duracao_para_horas(self, duracao_str):
        """Converte duração (ex: '52h 26m 44s') para horas decimais"""
        if pd.isna(duracao_str) or duracao_str == 0:
            return 0.0
        
        duracao_str = str(duracao_str)
        horas = 0.0
        
        # Extrair horas
        h_match = re.search(r'(\d+)h', duracao_str)
        if h_match:
            horas += float(h_match.group(1))
        
        # Extrair minutos
        m_match = re.search(r'(\d+)m', duracao_str)
        if m_match:
            horas += float(m_match.group(1)) / 60.0
        
        # Extrair segundos
        s_match = re.search(r'(\d+)s', duracao_str)
        if s_match:
            horas += float(s_match.group(1)) / 3600.0
        
        return round(horas, 2)
    
    def mapear_colunas(self):
        """Mapeia colunas da planilha para nomes internos"""
        mapeamento = {
            'Nome do criador': 'streamer_nome',
            'Nome': 'streamer_nome',
            'Criador': 'streamer_nome',
            'Diamantes': 'diamantes_total',
            'Diamantes Totais': 'diamantes_total',
            'Duração da LIVE': 'duracao_live',
            'Horas': 'duracao_live',
            'Dias válidos de início de LIVE': 'dias_live_validos',
            'Dias': 'dias_live_validos',
            'Batalhas': 'batalhas_qtd',
            'Diamantes obtidos de batalhas': 'diamantes_batalhas',
            'Período dos dados': 'periodo'
        }
        
        # Tentar mapear colunas
        colunas_renomeadas = {}
        for col in self.df.columns:
            if col in mapeamento:
                colunas_renomeadas[col] = mapeamento[col]
        
        self.df.rename(columns=colunas_renomeadas, inplace=True)
        
        # Verificar colunas obrigatórias
        colunas_obrigatorias = ['streamer_nome', 'diamantes_total', 'duracao_live']
        colunas_faltando = [c for c in colunas_obrigatorias if c not in self.df.columns]
        
        if colunas_faltando:
            raise ValueError(f"Colunas obrigatórias faltando: {', '.join(colunas_faltando)}")
    
    def processar(self):
        """Processa a planilha e retorna dados analisados"""
        try:
            # Ler arquivo
            if self.filepath.endswith('.csv'):
                self.df = pd.read_csv(self.filepath)
            else:
                self.df = pd.read_excel(self.filepath, sheet_name=0)
            
            # Mapear colunas
            self.mapear_colunas()
            
            # Processar dados
            self.df['horas_live'] = self.df['duracao_live'].apply(self.converter_duracao_para_horas)
            self.df['diamantes_total'] = self.df['diamantes_total'].fillna(0)
            self.df['batalhas_qtd'] = self.df.get('batalhas_qtd', pd.Series([0] * len(self.df))).fillna(0)
            self.df['diamantes_batalhas'] = self.df.get('diamantes_batalhas', pd.Series([0] * len(self.df))).fillna(0)
            self.df['dias_live_validos'] = self.df.get('dias_live_validos', pd.Series([0] * len(self.df))).fillna(0)
            
            # Calcular métricas
            self.df['diamantes_por_hora'] = self.df.apply(
                lambda row: round(row['diamantes_total'] / max(row['horas_live'], 0.01), 2), 
                axis=1
            )
            self.df['perc_batalhas'] = self.df.apply(
                lambda row: round((row['diamantes_batalhas'] / max(row['diamantes_total'], 1)) * 100, 1), 
                axis=1
            )
            
            # Aplicar status
            self.df['status_diamantes'] = self.df['diamantes_total'].apply(self.get_status_diamantes)
            self.df['status_horas'] = self.df['horas_live'].apply(self.get_status_horas)
            self.df['status_dias'] = self.df['dias_live_validos'].apply(self.get_status_dias)
            self.df['status_batalhas'] = self.df['batalhas_qtd'].apply(self.get_status_batalhas)
            self.df['status_perc_bat'] = self.df['perc_batalhas'].apply(self.get_status_perc_batalhas)
            
            # Classificar criadores
            self.df['alertas'] = self.df.apply(lambda row: self.classificar_criador(row)[0], axis=1)
            self.df['atencoes'] = self.df.apply(lambda row: self.classificar_criador(row)[1], axis=1)
            
            # Calcular agregados
            self.calcular_agregados()
            
            # Extrair período
            self.extrair_periodo()
            
            return {
                'status': 'sucesso',
                'dados': self.dados_agregados
            }
        
        except Exception as e:
            return {
                'status': 'erro',
                'mensagem': str(e)
            }
    
    def get_status_diamantes(self, valor):
        if valor >= self.METAS['diamantes']['ideal']:
            return '🟢'
        elif valor >= self.METAS['diamantes']['alerta']:
            return '🟡'
        else:
            return '🔴'
    
    def get_status_horas(self, valor):
        if valor >= self.METAS['horas']['ideal']:
            return '🟢'
        elif valor >= self.METAS['horas']['alerta']:
            return '🟡'
        else:
            return '🔴'
    
    def get_status_dias(self, valor):
        if valor >= self.METAS['dias']['ideal']:
            return '🟢'
        elif valor == self.METAS['dias']['alerta']:
            return '🟡'
        else:
            return '🔴'
    
    def get_status_batalhas(self, valor):
        if valor >= self.METAS['batalhas']['ideal']:
            return '🟢'
        elif valor >= self.METAS['batalhas']['alerta']:
            return '🟡'
        else:
            return '🔴'
    
    def get_status_perc_batalhas(self, valor):
        if valor >= self.METAS['perc_batalhas']['ideal']:
            return '🟢'
        elif valor >= self.METAS['perc_batalhas']['alerta']:
            return '🟡'
        else:
            return '🔴'
    
    def classificar_criador(self, row):
        """Classifica criador em alertas e atenções"""
        alertas = []
        atencoes = []
        
        # Alertas vermelhos (críticos)
        if row['diamantes_total'] < self.METAS['diamantes']['alerta']:
            alertas.append(f"< 3.000 diamantes ({int(row['diamantes_total'])})")
        
        if row['dias_live_validos'] < self.METAS['dias']['alerta']:
            alertas.append(f"< 2 dias válidos ({int(row['dias_live_validos'])})")
        
        if row['batalhas_qtd'] < self.METAS['batalhas']['alerta']:
            alertas.append(f"< 5 batalhas ({int(row['batalhas_qtd'])})")
        
        if row['perc_batalhas'] < self.METAS['perc_batalhas']['alerta']:
            alertas.append(f"% batalhas < 20% ({row['perc_batalhas']}%)")
        
        # Atenções (abaixo da meta ideal, mas não crítico)
        if row['diamantes_total'] >= self.METAS['diamantes']['alerta'] and row['diamantes_total'] < self.METAS['diamantes']['ideal']:
            atencoes.append(f"Abaixo da meta ideal em diamantes ({int(row['diamantes_total'])})")
        
        if row['horas_live'] >= self.METAS['horas']['alerta'] and row['horas_live'] < self.METAS['horas']['ideal']:
            atencoes.append(f"Horas entre 20-25h ({row['horas_live']}h)")
        elif row['horas_live'] < self.METAS['horas']['alerta'] and row['horas_live'] > 0:
            alertas.append(f"< 20h de live ({row['horas_live']}h)")
        
        if row['perc_batalhas'] >= self.METAS['perc_batalhas']['alerta'] and row['perc_batalhas'] < self.METAS['perc_batalhas']['ideal']:
            atencoes.append(f"% batalhas entre 20-50% ({row['perc_batalhas']}%)")
        
        if row['dias_live_validos'] == self.METAS['dias']['alerta']:
            atencoes.append(f"Apenas 2 dias válidos")
        
        if row['batalhas_qtd'] >= self.METAS['batalhas']['alerta'] and row['batalhas_qtd'] < self.METAS['batalhas']['ideal']:
            atencoes.append(f"Batalhas entre 5-20 ({int(row['batalhas_qtd'])})")
        
        return alertas, atencoes
    
    def calcular_agregados(self):
        """Calcula dados agregados da agência"""
        total_diamantes = int(self.df['diamantes_total'].sum())
        total_horas = round(self.df['horas_live'].sum(), 2)
        n_criadores = len(self.df)
        
        # Médias
        media_dph = round(total_diamantes / max(total_horas, 0.01), 2)
        media_diam_criador = int(total_diamantes / max(n_criadores, 1))
        media_horas_criador = round(total_horas / max(n_criadores, 1), 2)
        media_perc_batalhas = round(self.df['perc_batalhas'].mean(), 1)
        media_batalhas = round(self.df['batalhas_qtd'].mean(), 1)
        media_dias = round(self.df['dias_live_validos'].mean(), 1)
        
        # Contadores de status
        criadores_alertas = self.df[self.df['alertas'].apply(len) > 0]
        criadores_atencoes = self.df[self.df['atencoes'].apply(len) > 0]
        criadores_atencoes = criadores_atencoes[~criadores_atencoes['streamer_nome'].isin(criadores_alertas['streamer_nome'])]
        
        n_alertas = len(criadores_alertas)
        n_atencoes = len(criadores_atencoes)
        n_oks = n_criadores - n_alertas - n_atencoes
        
        # Pareto 80/20
        df_sorted = self.df.sort_values('diamantes_total', ascending=False).reset_index(drop=True)
        n_top_20 = max(1, int(n_criadores * 0.20))
        top_pareto = df_sorted.head(n_top_20)
        perc_pareto = round(top_pareto['diamantes_total'].sum() / max(total_diamantes, 1) * 100, 1)
        
        # Status da agência
        status_diam_ag = self.get_status_diamantes(media_diam_criador)
        status_horas_ag = self.get_status_horas(media_horas_criador)
        status_perc_bat_ag = self.get_status_perc_batalhas(media_perc_batalhas)
        status_bat_ag = self.get_status_batalhas(media_batalhas)
        status_dias_ag = self.get_status_dias(media_dias)
        
        # Preparar top pareto
        top_pareto_list = []
        for idx, row in top_pareto.iterrows():
            perc_individual = round((row['diamantes_total'] / max(total_diamantes, 1)) * 100, 1)
            top_pareto_list.append({
                'nome': row['streamer_nome'],
                'diamantes': int(row['diamantes_total']),
                'percentual': perc_individual
            })
        
        # Preparar alertas
        alertas_list = []
        for idx, row in criadores_alertas.iterrows():
            if len(row['alertas']) > 0:
                alertas_list.append({
                    'nome': row['streamer_nome'],
                    'motivos': row['alertas']
                })
        
        # Preparar atenções
        atencoes_list = []
        for idx, row in criadores_atencoes.iterrows():
            if len(row['atencoes']) > 0:
                atencoes_list.append({
                    'nome': row['streamer_nome'],
                    'motivos': row['atencoes']
                })
        
        # Preparar tabela de criadores (top 50)
        tabela_criadores = []
        for idx, row in df_sorted.head(50).iterrows():
            tabela_criadores.append({
                'nome': row['streamer_nome'],
                'diamantes': int(row['diamantes_total']),
                'horas': row['horas_live'],
                'diam_hora': row['diamantes_por_hora'],
                'perc_bat': row['perc_batalhas'],
                'batalhas': int(row['batalhas_qtd']),
                'dias': int(row['dias_live_validos']),
                'st_diam': row['status_diamantes'],
                'st_horas': row['status_horas'],
                'st_perc_bat': row['status_perc_bat'],
                'st_bats': row['status_batalhas'],
                'st_dias': row['status_dias'],
                'nota': self.gerar_nota(row)
            })
        
        self.dados_agregados = {
            'n_criadores': n_criadores,
            'total_diamantes': total_diamantes,
            'total_horas': total_horas,
            'media_dph': media_dph,
            'media_diam_criador': media_diam_criador,
            'media_horas_criador': media_horas_criador,
            'media_perc_batalhas': media_perc_batalhas,
            'media_batalhas': media_batalhas,
            'media_dias': media_dias,
            'n_alertas': n_alertas,
            'n_atencoes': n_atencoes,
            'n_oks': n_oks,
            'n_top': n_top_20,
            'perc_pareto': perc_pareto,
            'status_diam_ag': status_diam_ag,
            'status_horas_ag': status_horas_ag,
            'status_perc_bat_ag': status_perc_bat_ag,
            'status_bat_ag': status_bat_ag,
            'status_dias_ag': status_dias_ag,
            'top_pareto': top_pareto_list,
            'alertas': alertas_list,
            'atencoes': atencoes_list,
            'tabela_criadores': tabela_criadores,
            'criadores_ocultos': max(0, n_criadores - 50)
        }
    
    def gerar_nota(self, row):
        """Gera nota contextual para o criador"""
        notas = []
        
        if row['diamantes_total'] >= 12500 and len(row['alertas']) == 0:
            notas.append("Performance excelente")
        elif row['diamantes_total'] < 100:
            notas.append("Crítico - urgente")
        elif len(row['alertas']) > 3:
            notas.append("Múltiplos problemas")
        
        if row['diamantes_por_hora'] > 1000:
            notas.append("Alta eficiência")
        elif row['diamantes_por_hora'] < 100:
            notas.append("Baixa conversão")
        
        if row['batalhas_qtd'] == 0:
            notas.append("Sem batalhas")
        elif row['batalhas_qtd'] >= 50:
            notas.append("Muito ativo em batalhas")
        
        if row['dias_live_validos'] <= 1:
            notas.append("Quase inativo")
        elif row['dias_live_validos'] >= 6:
            notas.append("Muito consistente")
        
        return " · ".join(notas) if notas else "—"
    
    def extrair_periodo(self):
        """Extrai período dos dados"""
        if 'periodo' in self.df.columns:
            periodo = self.df['periodo'].iloc[0]
            if pd.notna(periodo):
                self.dados_agregados['periodo'] = str(periodo)
                return
        
        # Fallback: usar data atual
        hoje = datetime.now()
        self.dados_agregados['periodo'] = f"{hoje.strftime('%Y-%m-%d')} (data do upload)"
    
    def gerar_html(self, output_path):
        """Gera arquivo HTML do relatório"""
        from jinja2 import Template
        
        # Extrair nome do arquivo
        arquivo_nome = os.path.basename(output_path)
        
        # Template HTML (inline por simplicidade)
        template_html = self.get_template_html()
        
        template = Template(template_html)
        html_content = template.render(arquivo_nome=arquivo_nome, **self.dados_agregados)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def get_template_html(self):
        """Retorna template HTML do relatório"""
        # Vou usar o mesmo HTML que gerei antes, mas como template Jinja2
        return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório Semanal - Agência</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; line-height: 1.6; color: #1a1a1a; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h1 { font-size: 32px; margin-bottom: 10px; color: #000; border-bottom: 3px solid #ff0050; padding-bottom: 10px; }
        .meta-info { font-size: 14px; color: #666; margin-bottom: 30px; padding: 10px; background: #f9f9f9; border-radius: 6px; }
        h2 { font-size: 24px; margin-top: 40px; margin-bottom: 20px; color: #000; }
        .summary-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 10px; margin-bottom: 30px; }
        .summary-box ul { list-style: none; font-size: 16px; }
        .summary-box li { margin: 10px 0; padding-left: 10px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; }
        thead { background: #2c3e50; color: white; }
        th { padding: 12px 8px; text-align: left; font-weight: 600; }
        td { padding: 10px 8px; border-bottom: 1px solid #e0e0e0; }
        tbody tr:hover { background: #f5f5f5; }
        .text-right { text-align: right; }
        .text-center { text-align: center; }
        .alert-box { padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid; }
        .alert-red { background: #ffebee; border-color: #c62828; color: #c62828; }
        .alert-yellow { background: #fff9e6; border-color: #f57c00; color: #e65100; }
        .creator-name { font-weight: 600; color: #000; }
        .motivo-list { list-style: none; font-size: 13px; color: #555; margin-top: 5px; }
        .motivo-list li { padding-left: 15px; position: relative; }
        .motivo-list li:before { content: "→"; position: absolute; left: 0; }
        .pareto-list { list-style: none; counter-reset: pareto-counter; }
        .pareto-list li { counter-increment: pareto-counter; padding: 10px; margin: 8px 0; background: #f9f9f9; border-radius: 6px; display: flex; justify-content: space-between; }
        .pareto-list li:before { content: counter(pareto-counter) ". "; font-weight: 700; color: #667eea; margin-right: 10px; }
        .footer-note { margin-top: 40px; padding-top: 20px; border-top: 2px solid #e0e0e0; text-align: center; color: #666; font-size: 13px; }
    </style>
</head>
<body>
    <!-- Barra de Ações Fixa -->
    <div style="position: sticky; top: 0; z-index: 1000; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <div style="display: flex; gap: 10px;">
            <button onclick="window.print()" style="padding: 10px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: all 0.3s ease;">
                🖨️ Imprimir
            </button>
            <a href="/pdf/{{ arquivo_nome }}" download style="padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; text-decoration: none; transition: all 0.3s ease;">
                📥 Baixar PDF
            </a>
        </div>
        <div style="display: flex; gap: 10px;">
            <a href="/historico" style="padding: 10px 20px; background: white; color: #667eea; border: 2px solid #667eea; border-radius: 8px; font-weight: 600; text-decoration: none; display: flex; align-items: center; gap: 8px; transition: all 0.3s ease;">
                📂 Histórico
            </a>
            <a href="/" style="padding: 10px 20px; background: white; color: #667eea; border: 2px solid #667eea; border-radius: 8px; font-weight: 600; text-decoration: none; display: flex; align-items: center; gap: 8px; transition: all 0.3s ease;">
                ← Voltar
            </a>
        </div>
    </div>
    
    <div class="container">
        <h1>📊 Relatório Semanal — Agência</h1>
        
        <div class="meta-info">
            <span><strong>Período:</strong> {{ periodo }}</span> ·
            <span><strong>Criadores analisados:</strong> {{ n_criadores }}</span>
        </div>

        <div class="summary-box">
            <h2 style="color: white; margin-top: 0;">📌 Sumário Executivo</h2>
            <ul>
                <li><strong>💎 Diamantes totais:</strong> {{ "{:,}".format(total_diamantes).replace(",", ".") }}</li>
                <li><strong>⏱️ Horas totais:</strong> {{ total_horas }}h · <strong>Eficiência média:</strong> {{ media_dph }} diam/h</li>
                <li><strong>📊 Média por criador:</strong> {{ "{:,}".format(media_diam_criador).replace(",", ".") }} diamantes · {{ media_horas_criador }}h</li>
                <li><strong>🎯 Top {{ n_top }}</strong> criadores gerando <strong>{{ perc_pareto }}%</strong> dos diamantes</li>
                <li><strong>🔴 Alertas:</strong> {{ n_alertas }} · <strong>🟡 Atenções:</strong> {{ n_atencoes }} · <strong>🟢 OKs:</strong> {{ n_oks }}</li>
            </ul>
        </div>

        <h2>🏢 Painel da Agência</h2>
        <table>
            <thead>
                <tr>
                    <th>Métrica</th>
                    <th class="text-right">Valor Médio</th>
                    <th class="text-right">Meta Ideal</th>
                    <th class="text-right">Alerta</th>
                    <th class="text-center">Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Diamantes</strong></td>
                    <td class="text-right">{{ "{:,}".format(media_diam_criador).replace(",", ".") }}</td>
                    <td class="text-right">≥ 12.500</td>
                    <td class="text-right">&lt; 3.000</td>
                    <td class="text-center">{{ status_diam_ag }}</td>
                </tr>
                <tr>
                    <td><strong>Horas</strong></td>
                    <td class="text-right">{{ media_horas_criador }}h</td>
                    <td class="text-right">≥ 25h</td>
                    <td class="text-right">&lt; 20h</td>
                    <td class="text-center">{{ status_horas_ag }}</td>
                </tr>
                <tr>
                    <td><strong>% em Batalhas</strong></td>
                    <td class="text-right">{{ media_perc_batalhas }}%</td>
                    <td class="text-right">≥ 50%</td>
                    <td class="text-right">&lt; 20%</td>
                    <td class="text-center">{{ status_perc_bat_ag }}</td>
                </tr>
                <tr>
                    <td><strong>Batalhas</strong></td>
                    <td class="text-right">{{ media_batalhas }}</td>
                    <td class="text-right">≥ 20</td>
                    <td class="text-right">&lt; 5</td>
                    <td class="text-center">{{ status_bat_ag }}</td>
                </tr>
                <tr>
                    <td><strong>Dias válidos</strong></td>
                    <td class="text-right">{{ media_dias }}</td>
                    <td class="text-right">≥ 3</td>
                    <td class="text-right">&lt; 2</td>
                    <td class="text-center">{{ status_dias_ag }}</td>
                </tr>
            </tbody>
        </table>

        <h2>🏅 Destaques 80/20</h2>
        <ol class="pareto-list">
            {% for criador in top_pareto %}
            <li>
                <span class="pareto-name">{{ criador.nome }}</span>
                <span>{{ "{:,}".format(criador.diamantes).replace(",", ".") }} diamantes ({{ criador.percentual }}%)</span>
            </li>
            {% endfor %}
        </ol>

        {% if alertas %}
        <h2>🚨 Alertas Vermelhos</h2>
        <p style="color: #c62828; font-weight: 600; margin-bottom: 15px;">{{ n_alertas }} criadores em situação crítica</p>
        <div style="max-height: 600px; overflow-y: auto; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px;">
            {% for alerta in alertas %}
            <div class="alert-box alert-red">
                <div class="creator-name">{{ alerta.nome }}</div>
                <ul class="motivo-list">
                    {% for motivo in alerta.motivos %}
                    <li>{{ motivo }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if atencoes %}
        <h2>⚠️ Atenções</h2>
        <p style="color: #e65100; font-weight: 600; margin-bottom: 15px;">{{ n_atencoes }} criadores precisando de orientação</p>
        {% for atencao in atencoes %}
        <div class="alert-box alert-yellow">
            <div class="creator-name">{{ atencao.nome }}</div>
            <ul class="motivo-list">
                {% for motivo in atencao.motivos %}
                <li>{{ motivo }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endfor %}
        {% endif %}

        <h2>👤 Visão Detalhada por Criador (Top 50)</h2>
        <div style="overflow-x: auto;">
            <table style="font-size: 12px;">
                <thead>
                    <tr>
                        <th>Criador</th>
                        <th class="text-right">Diamantes</th>
                        <th class="text-right">Horas</th>
                        <th class="text-right">Diam/h</th>
                        <th class="text-right">%Bat</th>
                        <th class="text-right">Bats</th>
                        <th class="text-right">Dias</th>
                        <th class="text-center">St(Diam)</th>
                        <th class="text-center">St(Horas)</th>
                        <th class="text-center">St(%Bat)</th>
                        <th class="text-center">St(Bats)</th>
                        <th class="text-center">St(Dias)</th>
                        <th>Notas</th>
                    </tr>
                </thead>
                <tbody>
                    {% for criador in tabela_criadores %}
                    <tr>
                        <td class="creator-name">{{ criador.nome }}</td>
                        <td class="text-right">{{ "{:,}".format(criador.diamantes).replace(",", ".") }}</td>
                        <td class="text-right">{{ criador.horas }}</td>
                        <td class="text-right">{{ criador.diam_hora }}</td>
                        <td class="text-right">{{ criador.perc_bat }}%</td>
                        <td class="text-right">{{ criador.batalhas }}</td>
                        <td class="text-right">{{ criador.dias }}</td>
                        <td class="text-center">{{ criador.st_diam }}</td>
                        <td class="text-center">{{ criador.st_horas }}</td>
                        <td class="text-center">{{ criador.st_perc_bat }}</td>
                        <td class="text-center">{{ criador.st_bats }}</td>
                        <td class="text-center">{{ criador.st_dias }}</td>
                        <td>{{ criador.nota }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% if criadores_ocultos > 0 %}
        <p style="margin-top: 20px; color: #666; font-size: 14px;">
            <em>Nota: {{ criadores_ocultos }} criadores não exibidos na tabela.</em>
        </p>
        {% endif %}

        <div class="footer-note">
            <p><strong>Relatório baseado em {{ n_criadores }} criadores</strong></p>
            <p>Gerado em: {{ periodo }}</p>
        </div>
    </div>
</body>
</html>"""
