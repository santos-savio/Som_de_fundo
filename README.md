# 🎵 Aplicativo de Som de Fundo

Console simples e leve para tocar fundos musicais em cultos e eventos, desenvolvido com Python e CustomTkinter.

🔊 **Download (32 MB) — Nova Versão:**  
[📥 Clique para baixar](https://drive.google.com/file/d/1rO-22uEjcUjhtLAQ94sp_NV64Xvn9Jjb/view?usp=sharing)

## 🚀 Recursos

- Interface moderna e responsiva
- 10 botões personalizáveis com cor e imagem
- Atalhos de teclado (0–9)
- Aparência com modos `light` e `dark`
- Timer e barra de progresso com cálculo de duração
- Controle remoto via navegador com PIN

## 🆕 Novidades (v1.1.0)

- Aparência simplificada: opção apenas de `light`/`dark`
- Validação de áudio: aviso a partir de 40 MB e limite máximo 120 MB
- Cache de duração salvo no JSON da playlist
- Barra de progresso protegida contra divisão por zero
- Capas reduzidas no controle remoto para melhor visualização
- Imagens renderizadas com `CTkImage` (melhor HiDPI)

## 🛠️ Pré‑requisitos

- Python 3.8+
- Dependências em `requirements.txt`:
  - `customtkinter`, `pillow`, `pygame`, `flask`, `qrcode`

## ⚙️ Instalação

```bash
git clone https://github.com/alanxdpro/Som_de_fundo.git
cd Som_de_fundo
pip install -r requirements.txt
```

## ▶️ Execução

```bash
python som_de_fundo.py
```

## 🌐 Controle Remoto

- Abra “Controle Remoto” no app para ver URL e PIN.
- Acesse pelo celular/computador na mesma rede e digite o PIN.

## 🎨 Aparência

- Em “Configurar” → “Tema”, escolha `Aparência: light` ou `Aparência: dark`.

## 🔉 Áudio e Duração

- Formatos suportados: `.mp3`, `.wav`, `.ogg`.
- Arquivos acima de 40 MB mostram aviso amigável; acima de 120 MB são bloqueados.
- A duração calculada é salva na playlist para evitar reprocessamento.

## 📦 Criando um Executável

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icone.ico som_de_fundo.py
```

## 🗂️ Observações de Versionamento

- `.gitignore` ignora dados locais (preferências, playlists de uso, cache de ícones e sons). Ajuste conforme sua necessidade.

## � Publicar uma Nova Versão

- Atualize a versão no app (janela Sobre) e confirme alterações com Git:
  - `git fetch origin && git checkout -B main && git pull --rebase origin main`
  - `git add -A`
  - `git commit -m "Release 1.1.0: melhorias e correções"`
  - `git push -u origin main`
- Crie uma tag para a versão:
  - `git tag -a v1.1.0 -m "Som_de_fundo 1.1.0"`
  - `git push origin v1.1.0`
- No GitHub, vá em Releases → “Draft a new release”:
  - Tag: `v1.1.0`, Target: `main`
  - Título: `Som de Fundo 1.1.0`
  - Descreva as novidades e fixes
  - Opcional: anexe o executável gerado pelo PyInstaller

## �📝 Licença

Projeto sob Licença MIT — veja [LICENSE](LICENSE).

---

Desenvolvido com ❤️ por [@allan.psxd1]
