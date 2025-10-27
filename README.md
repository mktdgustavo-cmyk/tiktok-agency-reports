# 📊 Gerador Automático de Relatórios - Agência

Sistema web para análise automática de dados de creators TikTok, gerando relatórios visuais em HTML e PDF.

## ✨ Funcionalidades

- 📤 **Upload de planilhas** (XLSX, XLS, CSV)
- 🔍 **Análise automática** seguindo métricas da agência
- 📊 **Relatório visual HTML** com dashboard interativo
- 📥 **Exportação em PDF** com um clique
- 🎯 **Identificação automática** de alertas e destaques
- 🔄 **Análise Pareto 80/20** dos melhores performers

## 🚀 Deploy no Easypanel

### Opção 1: Deploy via GitHub (Recomendado)

1. **Criar repositório no GitHub:**
   - Crie um repositório novo no GitHub
   - Suba todos os arquivos deste projeto

2. **No Easypanel:**
   - Clique em **"+ Create"**
   - Selecione **"App"**
   - Escolha **"Deploy from GitHub"**
   - Conecte seu repositório
   - Configure:
     - **Name:** `gerador-relatorios`
     - **Port:** `5000`
     - **Build Method:** `Dockerfile`

3. **Variáveis de ambiente (opcional):**
   ```
   PORT=5000
   ```

4. **Deploy:**
   - Clique em **"Deploy"**
   - Aguarde o build (primero deploy pode levar 5-10 min)

### Opção 2: Deploy via Dockerfile direto

1. No Easypanel, crie uma nova aplicação
2. Cole o Dockerfile completo
3. Configure a porta: `5000`
4. Deploy!

## 📦 Estrutura do Projeto

```
relatorio-agencia-app/
│
├── app.py                  # Backend Flask (servidor web)
├── analisador.py           # Engine de análise de dados
├── requirements.txt        # Dependências Python
├── Dockerfile             # Configuração Docker
├── .dockerignore          # Arquivos ignorados no build
│
├── templates/
│   └── index.html         # Interface de upload
│
├── uploads/               # Planilhas enviadas (temporário)
└── outputs/               # Relatórios gerados (temporário)
```

## 🔧 Desenvolvimento Local

### Pré-requisitos
- Python 3.11+
- pip

### Instalação

1. **Clone o repositório:**
```bash
git clone <seu-repo>
cd relatorio-agencia-app
```

2. **Crie ambiente virtual:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale dependências:**
```bash
pip install -r requirements.txt
```

4. **Rode a aplicação:**
```bash
python app.py
```

5. **Acesse:**
```
http://localhost:5000
```

## 📋 Como Usar

1. **Acesse a interface web** (URL do Easypanel ou localhost:5000)
2. **Faça upload** da planilha de dados dos creators
3. **Aguarde o processamento** (geralmente 5-15 segundos)
4. **Visualize o relatório** HTML ou baixe em PDF

## 📊 Formato da Planilha

A planilha deve conter as seguintes colunas (nomes podem variar):

| Coluna Obrigatória | Variações Aceitas |
|-------------------|-------------------|
| Nome do criador | Nome, Criador, Streamer |
| Diamantes | Diamantes Totais, Total Diamantes |
| Duração da LIVE | Horas, Tempo de Live |
| Dias válidos | Dias válidos de início de LIVE |
| Batalhas | Qtd Batalhas, Total Batalhas |
| Diamantes de batalhas | Diamantes obtidos de batalhas |

**Exemplo de formato de duração:** `52h 26m 44s`

## 🎯 Métricas Analisadas

O sistema analisa automaticamente:

- 💎 **Diamantes totais** (meta: ≥ 12.500 / alerta: < 3.000)
- ⏰ **Horas de live** (meta: ≥ 25h / alerta: < 20h)
- 📅 **Dias válidos** (meta: ≥ 3 / alerta: < 2)
- ⚔️ **Batalhas** (meta: ≥ 20 / alerta: < 5)
- 📊 **% Diamantes em batalhas** (meta: ≥ 50% / alerta: < 20%)

### Status por Criador

- 🟢 **Verde:** Meta ideal atingida
- 🟡 **Amarelo:** Atenção necessária
- 🔴 **Vermelho:** Alerta crítico - ação imediata

## 🔒 Segurança

- Arquivos são automaticamente deletados após 1 hora
- Limite de upload: 16MB
- Formatos aceitos: `.xlsx`, `.xls`, `.csv`

## 🐛 Troubleshooting

### Erro ao gerar PDF
- Verifique se as dependências do WeasyPrint foram instaladas
- No Dockerfile, as libs necessárias já estão incluídas

### Upload falha
- Verifique o formato do arquivo
- Confirme que a planilha tem as colunas obrigatórias
- Tamanho máximo: 16MB

### Porta em uso (desenvolvimento local)
```bash
# Mude a porta no app.py ou use variável de ambiente
PORT=8000 python app.py
```

## 📝 Logs e Monitoramento

No Easypanel, acesse:
- **Logs:** Aba "Logs" da aplicação
- **Health check:** `/health` endpoint

## 🔄 Atualizações

Para atualizar a aplicação no Easypanel:

1. **Via GitHub:**
   - Faça push das alterações
   - Easypanel faz rebuild automático

2. **Manual:**
   - Clique em "Rebuild" no Easypanel

## 🤝 Suporte

Em caso de problemas:
1. Verifique os logs no Easypanel
2. Confirme que o Dockerfile buildou corretamente
3. Teste localmente primeiro

## 📜 Licença

Uso interno - Agência Olah

---

**Desenvolvido para análise semanal de creators TikTok** 🚀
