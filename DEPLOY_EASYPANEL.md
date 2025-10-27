# 🚀 Guia Rápido - Deploy no Easypanel

## Passo a Passo Completo

### 1️⃣ Preparar o Repositório GitHub

```bash
# Na sua máquina local, crie um novo repositório
mkdir gerador-relatorios-agencia
cd gerador-relatorios-agencia

# Copie todos os arquivos do projeto para esta pasta

# Inicialize o Git
git init
git add .
git commit -m "Initial commit: Gerador de Relatórios"

# Crie um repositório no GitHub e suba o código
git remote add origin https://github.com/SEU-USUARIO/SEU-REPO.git
git branch -M main
git push -u origin main
```

### 2️⃣ Deploy no Easypanel

1. **Acesse seu Easypanel**
   - URL: `https://seu-easypanel.com`

2. **Criar Nova Aplicação**
   - Clique em **"+ Create"**
   - Selecione **"App"**

3. **Configurar Source**
   - Source: **"GitHub"**
   - Repository: `seu-usuario/gerador-relatorios-agencia`
   - Branch: `main`

4. **Configurações da App**
   ```
   Name: gerador-relatorios
   Build Type: Dockerfile
   Port: 5000
   ```

5. **Deploy**
   - Clique em **"Create"**
   - Aguarde o build (5-10 minutos no primeiro deploy)

### 3️⃣ Configurar Domínio (Opcional)

No Easypanel:
1. Vá em **"Domains"**
2. Adicione seu domínio: `relatorios.suaagencia.com`
3. Configure DNS apontando para o IP do Easypanel

### 4️⃣ Testar a Aplicação

1. Acesse a URL fornecida pelo Easypanel
2. Faça upload de uma planilha de teste
3. Verifique se o relatório é gerado corretamente

---

## ⚡ Deploy Rápido (Sem GitHub)

Se preferir deploy direto sem GitHub:

1. **No Easypanel:**
   - Clique em **"+ Create" → "App"**
   - Source: **"Dockerfile"**
   - Cole o conteúdo completo do Dockerfile
   - Port: `5000`
   - Click **"Create"**

2. **Upload dos arquivos:**
   - Use SFTP/SCP para enviar os arquivos para:
   - `/app/` no container

**Nota:** Esta opção é mais manual e não tem auto-deploy.

---

## 🔍 Verificar Status

Após deploy, verifique:

### Health Check
```bash
curl https://sua-url.easypanel.io/health
# Deve retornar: {"status":"ok","timestamp":"..."}
```

### Logs em Tempo Real
No Easypanel:
- Aba **"Logs"** → Ver logs da aplicação
- Procure por: `* Running on http://0.0.0.0:5000`

---

## 🛠️ Troubleshooting

### Build falha
- Verifique se o Dockerfile está correto
- Logs geralmente mostram o erro específico

### App não responde
- Confirme que a porta 5000 está configurada
- Verifique os logs por erros

### Erro ao gerar PDF
- Dependências do WeasyPrint devem estar no Dockerfile
- Se persistir, rode: `docker logs <container-id>`

---

## 📊 Recursos da Aplicação

Após deploy, você terá:
- ✅ Interface web para upload
- ✅ Processamento automático
- ✅ Geração de HTML
- ✅ Exportação em PDF
- ✅ Limpeza automática de arquivos (1h)

---

## 🔐 Variáveis de Ambiente (Opcional)

Caso queira customizar:

```env
PORT=5000                    # Porta da aplicação
MAX_CONTENT_LENGTH=16777216  # 16MB limite de upload
```

Configure em: **Settings → Environment Variables** no Easypanel

---

## 🎯 URLs Importantes

Após deploy, você terá acesso a:
- `/` → Interface de upload
- `/health` → Health check
- `/upload` → Endpoint de upload (POST)
- `/relatorio/<id>` → Visualizar relatório
- `/pdf/<id>` → Download PDF

---

## 📱 Acesso Móvel

A interface é responsiva! Funciona em:
- 📱 Smartphones
- 💻 Tablets
- 🖥️ Desktop

---

**Pronto! Seu gerador de relatórios está no ar! 🎉**
