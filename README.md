# 🎓 Verificador de Segurança para Exames Supervisionados

Este script Python detecta telas secundárias e verifica serviços/aplicativos que podem ser prejudiciais durante exames supervisionados no computador.

## 🔧 Funcionalidades

- ✅ **Detecção de Telas Secundárias**: Identifica se há monitores adicionais conectados
- ✅ **Verificação de Processos Suspeitos**: Lista aplicativos que podem ajudar em fraudes
- ✅ **Detecção de Aplicativos de IA**: Identifica assistentes de IA e ferramentas similares  
- ✅ **Análise de Serviços**: Verifica serviços do Windows que podem ser problemáticos
- ✅ **Relatório Detalhado**: Gera relatório em JSON com todas as informações
- ✅ **Score de Risco**: Calcula nível de risco do sistema para o exame

## 🚨 O que o script detecta

### Aplicativos de IA
- ChatGPT, Claude, Bard, Copilot, Cortana
- GitHub Copilot, Tabnine, Codeium
- Google Translate, DeepL, Grammarly

### Ferramentas Problemáticas
- **Acesso Remoto**: TeamViewer, AnyDesk, VNC
- **Comunicação**: Teams, Discord, Zoom, Skype  
- **Navegadores**: Chrome, Firefox, Edge (podem acessar IA online)
- **Gravação/Screenshot**: OBS, Bandicam, Lightshot
- **Calculadoras Avançadas**: Wolfram, Mathematica, GeoGebra

### Verificações de Hardware
- **Telas Múltiplas**: Detecta monitores secundários
- **Resolução Virtual**: Verifica se há área de desktop estendida

## 📦 Instalação

1. **Clone ou baixe o projeto**
```bash
cd c:\Users\seu_usuario\Desktop\DEV_LUCAS\tcc
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

## 🚀 Como Usar

### Executar Verificação Completa
```bash
python script_verification.py
```

### Exemplo de Uso em Código
```python
from script_verification import ExamSecurityVerifier

# Criar verificador
verifier = ExamSecurityVerifier()

# Gerar relatório
report = verifier.generate_report()

# Verificar se há telas secundárias
if report["screen_verification"]["has_secondary_screens"]:
    print("⚠️ ATENÇÃO: Telas múltiplas detectadas!")

# Salvar relatório
verifier.save_report(report, "meu_relatorio.json")
```

## 📊 Exemplo de Saída

```
============================================================
🎓 VERIFICADOR DE SEGURANÇA PARA EXAMES SUPERVISIONADOS
============================================================
🔍 Iniciando verificação de segurança para exame...
📺 Verificando telas secundárias...
⚙️  Analisando processos em execução...
🚨 Verificando aplicativos suspeitos...

========================================
📊 RESUMO DA VERIFICAÇÃO
========================================
🖥️  Telas detectadas: 2
⚠️  Tela secundária: SIM - CRÍTICO!
🔍 Processos suspeitos: 15
⚙️  Serviços suspeitos: 8
🤖 Apps de IA: 3
📈 Score de risco: 45.2%

🚨 PROCESSOS SUSPEITOS DETECTADOS:
  • chrome.exe (PID: 1234) - MÉDIO
  • teams.exe (PID: 5678) - MÉDIO
  • copilot.exe (PID: 9012) - ALTO

🤖 APLICATIVOS DE IA DETECTADOS:
  • GitHub Copilot (PID: 3456)
  • Cortana (PID: 7890)

========================================
💡 RECOMENDAÇÕES
========================================
  ❌ CRÍTICO: Desconecte todas as telas secundárias antes do exame
  ⚠️  Feche 26 aplicativos/serviços suspeitos identificados
  🔴 ALTO RISCO: Muitos aplicativos suspeitos detectados - reinicie o sistema
  ✅ Feche todos os navegadores web
  ✅ Desabilite conexões de rede desnecessárias
  ✅ Feche aplicativos de comunicação (Teams, Discord, etc.)
  ✅ Desabilite assistentes de IA (Copilot, Cortana, etc.)

📄 Relatório salvo em: exam_security_report_20250828_160245.json

========================================
🔴 STATUS: NÃO APROVADO PARA EXAME - Telas múltiplas detectadas
============================================================
```

## 📋 Interpretação dos Resultados

### Status do Sistema
- 🟢 **APROVADO**: Sistema seguro para exame
- 🟠 **RISCO MÉDIO**: Alguns itens suspeitos detectados
- 🟡 **RISCO ALTO**: Muitos aplicativos problemáticos
- 🔴 **NÃO APROVADO**: Telas múltiplas ou risco crítico

### Níveis de Risco
- **ALTO**: Aplicativos de IA, acesso remoto, ferramentas de fraude
- **MÉDIO**: Navegadores, comunicação, ferramentas de produtividade  
- **BAIXO**: Aplicativos diversos que podem ser problemáticos

## 🔧 Personalização

Você pode modificar as listas de aplicativos suspeitos editando as variáveis no início da classe `ExamSecurityVerifier`:

```python
self.suspicious_processes = {
    # Adicione seus próprios aplicativos aqui
    "meu_app_suspeito", "outro_app"
}
```

## ⚙️ Métodos de Detecção de Telas

O script usa 3 métodos diferentes para máxima compatibilidade:

1. **Win32API EnumDisplayDevices**: Método principal e mais preciso
2. **System Metrics**: Fallback usando métricas virtuais do Windows
3. **Tkinter**: Última alternativa se outros métodos falharem

## 📄 Arquivos Gerados

- `exam_security_report_YYYYMMDD_HHMMSS.json`: Relatório detalhado em JSON
- Contém todas as informações sobre processos, serviços e hardware detectados

## 🔒 Segurança e Privacidade

- O script apenas **lê** informações do sistema
- Não modifica, instala ou remove nenhum software
- Não envia dados para servidores externos
- Todas as informações permanecem locais

## 🐛 Solução de Problemas

### Erro de Permissão
Execute como Administrador se houver problemas de acesso

### Módulos Não Encontrados
```bash
pip install --upgrade -r requirements.txt
```

### Script Não Detecta Telas Múltiplas
- Verifique se os drivers de vídeo estão atualizados
- Teste desconectar e reconectar o monitor secundário
- Execute como Administrador

## 📝 Licença

Este projeto é de uso educacional para sistemas de exames supervisionados.

---

**⚠️ IMPORTANTE**: Este script deve ser usado apenas em sistemas próprios ou com autorização. Sempre respeite políticas de privacidade e segurança da instituição.
