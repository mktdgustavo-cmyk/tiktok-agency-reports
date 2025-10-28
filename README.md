# 🚀 OLAH AGÊNCIA - SISTEMA DE RELATÓRIOS v3.0

Sistema automatizado de análise de desempenho para creators TikTok com IA integrada.

---

## ✨ **NOVIDADES VERSÃO 3.0**

### 🤖 **IA com Claude**
- Insights personalizados gerados automaticamente
- Recomendações práticas baseadas nos dados
- Observações críticas para ações imediatas

### 🏅 **Tratamento Especial para Top Creators**
- Tops com 60%+ indicadores OK não vão para vermelho
- Classificação inteligente baseada em performance
- Regra 80/20 aplicada automaticamente

### 🎨 **Identidade Visual OLAH**
- Paleta de cores da marca (Lima, Fúcsia, Violeta, Laranja)
- Tipografia oficial (Headline Gothic, Archivo)
- Elementos gráficos característicos

### 🌙 **Modo Escuro**
- Toggle entre modo claro e escuro
- Preferência salva no navegador

---

## 🔧 **CONFIGURAÇÃO NO EASYPANEL**

### **1. Adicionar API Key do Claude**

1. Acesse seu app no Easypanel
2. Vá em **"Environment Variables"**
3. Adicione uma nova variável:
   - **Nome:** `ANTHROPIC_API_KEY`
   - **Valor:** Sua chave da Anthropic (começa com `sk-ant-api03-...`)
4. Clique em **"Save"**
5. **Rebuild** a aplicação

### **2. Obter API Key**

1. Acesse: https://console.anthropic.com/
2. Crie uma conta (se não tiver)
3. Vá em **"API Keys"**
4. Clique em **"Create Key"**
5. Copie a chave gerada

**Custo:** ~$0.003 por relatório (~R$0.015)

---

## 📊 **FUNCIONALIDADES**

### **Upload e Processamento**
- ✅ Suporte para XLSX, XLS, CSV
- ✅ Validação automática de dados
- ✅ Conversão de duração (texto → horas)
- ✅ Tratamento de valores inválidos

### **Análise Inteligente**
- ✅ Cálculo automático de todas as métricas
- ✅ Aplicação de metas e alertas
- ✅ Identificação de Top 20% (Pareto)
- ✅ **Classificação especial para tops**
- ✅ **Insights gerados por IA**

### **Relatórios**
- ✅ HTML responsivo com identidade OLAH
- ✅ Sumário executivo com totais
- ✅ Destaques 80/20
- ✅ Alertas vermelhos (ação imediata)
- ✅ Atenções (monitoramento)
- ✅ **Recomendações práticas (IA)**
- ✅ **Observações críticas (IA)**
- ✅ Tabela detalhada por criador
- ✅ Exportação em PDF

### **Histórico**
- ✅ Página dedicada com todos os relatórios
- ✅ Retenção de 30 dias
- ✅ Limpeza automática

---

## 📋 **MÉTRICAS E METAS**

| Métrica | 🟢 Ideal | 🟡 Atenção | 🔴 Alerta |
|---------|----------|------------|-----------|
| Diamantes/semana | ≥ 12.500 | 3.000 - 12.499 | < 3.000 |
| Horas de live | ≥ 25h | 20h - 24h | < 20h |
| Dias válidos | ≥ 3 | 2 | < 2 |
| Batalhas | ≥ 20 | 5 - 19 | < 5 |
| % Batalhas | ≥ 50% | 20% - 49% | < 20% |

### **Regra Especial: Top Creators**
- **Se TOP 20% + 60% indicadores OK** → 🟡 Atenção (não 🔴)
- Exemplo: ciganamariaddolores1 (top 1) com 3/5 OK = 🟡

---

## 🎨 **IDENTIDADE VISUAL**

### **Cores**
- **Lima:** `#E4FF1A` (principal)
- **Fúcsia:** `#FF006B`
- **Violeta:** `#8B00FF`
- **Laranja:** `#FF5C00`
- **Preto:** `#2D2D2D`
- **Branco:** `#F5F5F5`

### **Tipografia**
- **Títulos:** Headline Gothic ATF Rough
- **Corpo:** Archivo
- **Destaques:** Swanky and Moo Moo

---

## 🚀 **USO**

### **1. Preparar Planilha**
Colunas obrigatórias:
- Nome do criador
- Diamantes
- Duração da LIVE
- Dias válidos de início de LIVE
- Batalhas
- Diamantes obtidos de batalhas

### **2. Fazer Upload**
1. Acesse a aplicação
2. Arraste a planilha ou clique para selecionar
3. Aguarde o processamento
4. Visualize o relatório gerado

### **3. Exportar**
- **Imprimir:** Ctrl+P
- **PDF:** Botão "Baixar PDF"
- **Histórico:** Ver relatórios anteriores

---

## 📞 **SUPORTE**

**Contato Técnico:** 11 99761-2998  
**Desenvolvido para:** OLAH Agência de Creators

---

## 🔐 **SEGURANÇA**

- ✅ API Key armazenada como variável de ambiente (segura)
- ✅ Validação de arquivos
- ✅ Sanitização de nomes
- ✅ Limite de 16MB por upload
- ✅ Dados temporários (30 dias)

---

## 📝 **CHANGELOG**

### **v3.0 (atual)**
- 🤖 Integração com Claude API
- 🏅 Classificação especial para tops
- 🎨 Identidade visual OLAH
- 🌙 Modo escuro
- ✨ Insights gerados por IA

### **v2.1**
- 🐛 Correção de NaN no JSON
- 📂 Histórico de relatórios
- ⏱️ Retenção de 30 dias
- 🎯 Barra de ações

### **v2.0**
- 📊 Relatórios HTML completos
- 📄 Exportação em PDF
- 📈 Análise Pareto 80/20
- 🎯 Metas e alertas automáticos

---

## 🔜 **PRÓXIMOS PASSOS**

- [ ] Painel individual para creators (com login)
- [ ] Dashboard interativo com gráficos
- [ ] Comparativo entre semanas
- [ ] Notificações automáticas (email/Slack)
- [ ] API REST para integrações

---

**Desenvolvido com ⚡ pela OLAH Agência de Creators**
