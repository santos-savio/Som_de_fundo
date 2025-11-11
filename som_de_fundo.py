import os, json, threading, time
import pygame
import customtkinter as ctk
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageTk

# ----------------------------------------
CONFIG_FILE = "config.json"
SONS_DIR = "sons"
ICONS_DIR = "icons"
FADE_MS = 800
# ----------------------------------------

os.makedirs(SONS_DIR, exist_ok=True)
os.makedirs(ICONS_DIR, exist_ok=True)
pygame.mixer.init()

config = {}
current_index = None
is_switching = threading.Lock()
music_start_time = None  # Tempo de início da música
timer_label = None  # Label do contador

# ---------- Configuração padrão ----------
def default_config():
    # Paleta de cores variada
    paleta_cores = [
        '#3b82f6',  # primaria_azul
        '#8b5cf6',  # secundaria_roxo
        '#06b6d4',  # destaque_ciano
        '#10b981',  # sucesso_verde
        '#ef4444',  # alerta_vermelho
        '#f59e0b',  # aviso_laranja
        '#ec4899',  # destaque_rosa
        '#14b8a6',  # teal
        '#f97316',  # laranja_quente
        '#6366f1'   # indigo
    ]
    
    return {
        "botoes": [
            {"nome": f"Botão {i+1}", "cor": paleta_cores[i], "arquivo": "", "icone": ""}
            for i in range(10)
        ],
        "atalhos_habilitados": True  # Atalhos de teclado habilitados por padrão
    }

def carregar_config():
    global config
    if not os.path.exists(CONFIG_FILE):
        config = default_config()
        salvar_config()
    else:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        # Garante que a configuração de atalhos existe
        if "atalhos_habilitados" not in config:
            config["atalhos_habilitados"] = True
            salvar_config()

def salvar_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# ---------- Áudio ----------
def _play_file_loop(path):
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1, fade_ms=FADE_MS)
    except Exception as e:
        messagebox.showerror("Erro de áudio", f"Falha ao tocar: {e}")

def tocar_som(index):
    global current_index
    botao = config["botoes"][index]
    caminho = botao["arquivo"]
    if not caminho or not os.path.exists(caminho):
        messagebox.showwarning("Aviso", "Escolha um arquivo de som para este botão.")
        return
    if current_index == index and pygame.mixer.music.get_busy():
        return
    threading.Thread(target=_switch_music_thread, args=(index, caminho), daemon=True).start()

def _switch_music_thread(index, caminho):
    global current_index, music_start_time
    if not is_switching.acquire(blocking=False):
        return
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(FADE_MS)
            time.sleep(FADE_MS / 1000)
        _play_file_loop(caminho)
        current_index = index
        music_start_time = time.time()  # Registra o tempo de início
        atualizar_estilos()
        atualizar_timer()  # Inicia a atualização do timer
    finally:
        is_switching.release()

def atualizar_timer():
    """Atualiza o contador de tempo da música"""
    global music_start_time, timer_label
    if music_start_time and pygame.mixer.music.get_busy():
        elapsed = int(time.time() - music_start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        timer_label.configure(text=f"⏱️ {minutes:02d}:{seconds:02d}")
        # Agenda a próxima atualização em 1 segundo
        app.after(1000, atualizar_timer)
    elif timer_label:
        timer_label.configure(text="")

def parar_tudo():
    global current_index, music_start_time
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(FADE_MS)
    music_start_time = None  # Reseta o timer
    if timer_label:
        timer_label.configure(text="")  # Limpa o display
    current_index = None
    atualizar_estilos()

# ---------- UI ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Som de Fundo — Console Profissional")
app.geometry("1000x600")

carregar_config()
button_refs = []

# --- Cabeçalho ---
header_frame = ctk.CTkFrame(app, fg_color="transparent")
header_frame.pack(pady=20, fill="x", padx=20)

header = ctk.CTkLabel(header_frame, text="🎧 SOM DE FUNDO", font=("Arial Rounded MT Bold", 26))
header.pack(side="left", expand=True)

# --- Timer discreto no canto superior direito ---
timer_label = ctk.CTkLabel(header_frame, text="", font=("Arial", 18), text_color="#9ca3af")
timer_label.pack(side="right", padx=30
)

# --- Painel de botões ---
panel = ctk.CTkFrame(app)
panel.pack(expand=True, fill="both", padx=20, pady=10)

def atualizar_estilos():
    for i, ref in enumerate(button_refs):
        cor = config["botoes"][i]["cor"]
        nome = config["botoes"][i]["nome"]
        ref.configure(fg_color=cor, text=nome)
        if current_index == i:
            ref.configure(border_color="white", border_width=3)
        else:
            # Define a borda com a mesma cor do botão para ficar invisível
            ref.configure(border_color=cor, border_width=0)
    # Atualiza o texto de atalhos
    atualizar_texto_atalhos()


def quebrar_texto(texto, max_chars=12):
    """Quebra o texto de forma inteligente para caber no botão"""
    palavras = texto.split()
    linhas = []
    linha_atual = []
    
    for palavra in palavras:
        teste = ' '.join(linha_atual + [palavra])
        if len(teste) <= max_chars:
            linha_atual.append(palavra)
        else:
            if linha_atual:
                linhas.append(' '.join(linha_atual))
            linha_atual = [palavra]
    
    if linha_atual:
        linhas.append(' '.join(linha_atual))
    
    # Se não houver quebras, retorna o texto original
    return '\n'.join(linhas) if linhas else texto

def criar_botoes():
    # Configuração do grid para ser responsivo
    panel.grid_propagate(True)
    for i in range(2):  # 2 linhas
        panel.grid_rowconfigure(i, weight=1, uniform='row')
    for i in range(5):  # 5 colunas
        panel.grid_columnconfigure(i, weight=1, uniform='col')
    
    for i in range(10):
        # Cria um frame para conter o botão e melhorar o layout
        frame = ctk.CTkFrame(panel, fg_color="transparent")
        frame.grid(row=i//5, column=i%5, padx=5, pady=5, sticky="nsew")
        frame.grid_propagate(True)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Quebra o texto de forma inteligente
        texto_botao = quebrar_texto(config["botoes"][i]["nome"])
        
        # Criando um botão com melhor contraste visual
        b = ctk.CTkButton(frame, 
                         text=texto_botao,
                         fg_color=config["botoes"][i]["cor"],
                         text_color="white",  # Texto branco para melhor contraste
                         width=140, 
                         height=80, 
                         font=("Arial", 13, "bold"),  # Fonte um pouco maior
                         anchor="center",
                         corner_radius=8,
                         hover_color=config["botoes"][i]["cor"],  # Mantém a cor no hover
                         command=lambda i=i: tocar_som(i))
        b.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        button_refs.append(b)

criar_botoes()

# --- Rodapé ---
footer = ctk.CTkFrame(app, fg_color="transparent")
footer.pack(pady=15)

# Botões de ação
buttons_frame = ctk.CTkFrame(footer, fg_color="transparent")
buttons_frame.pack(side="left")

ctk.CTkButton(buttons_frame, text="⏹ Parar", fg_color="#e74c3c", command=parar_tudo).pack(side="left", padx=10)
ctk.CTkButton(buttons_frame, text="⚙️ Configurar", fg_color="#2563eb", command=lambda: abrir_config_janela()).pack(side="left", padx=10)

# Texto de atalhos
shortcuts_label = ctk.CTkLabel(footer, text="", font=("Arial", 11), text_color="#9ca3af")
shortcuts_label.pack(side="right", padx=20)

def atualizar_texto_atalhos():
    """Atualiza o texto de atalhos baseado na configuração"""
    if config.get("atalhos_habilitados", True):
        shortcuts_label.configure(text="⌨️ Atalhos: Teclas 0-9 para reproduzir os botões")
    else:
        shortcuts_label.configure(text="⌨️ Atalhos: Desabilitados", text_color="#6b7280")

# --- Tela de configuração (CustomTkinter moderna) ---
def abrir_config_janela():
    win = ctk.CTkToplevel(app)
    win.title("Configurações dos Botões")
    win.geometry("650x550")  # Tamanho reduzido
    win.resizable(False, False)  # Impede redimensionamento
    
    # Configurações para manter a janela na frente
    win.transient(app)  # Define a janela como filha da janela principal
    win.grab_set()  # Torna a janela modal (bloqueia interação com a janela principal)
    win.lift()  # Traz a janela para frente
    win.focus_force()  # Força o foco na janela
    
    # Centraliza a janela na tela
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (650 // 2)
    y = (win.winfo_screenheight() // 2) - (550 // 2)
    win.geometry(f"650x550+{x}+{y}")
    
    def resetar_config():
        """Reseta todas as configurações para o padrão"""
        resposta = messagebox.askyesno(
            "Resetar Configurações",
            "Tem certeza que deseja resetar todas as configurações para o padrão?\n\nIsso irá remover todos os nomes, cores e arquivos de áudio configurados."
        )
        if resposta:
            global config
            config = default_config()
            salvar_config()
            atualizar_estilos()
            messagebox.showinfo("✅ Resetado", "Configurações resetadas com sucesso!\nFeche e abra a janela de configurações novamente para ver as mudanças.")
            win.destroy()
    
    # Cabeçalho com botão de reset no canto superior direito
    header_config = ctk.CTkFrame(win, fg_color="transparent", height=40)
    header_config.pack(fill="x", padx=10, pady=(10, 5))
    
    ctk.CTkLabel(header_config, text="⚙️ Configurações", font=("Arial", 18, "bold")).pack(side="left")
    
    ctk.CTkButton(header_config, text="🔄 Resetar Tudo", fg_color="#dc2626", hover_color="#b91c1c",
                  width=120, height=30, font=("Arial", 11, "bold"),
                  command=resetar_config).pack(side="right")

    # Frame principal com scroll
    canvas = ctk.CTkScrollableFrame(win, width=620, height=380)
    canvas.pack(padx=10, pady=(5, 5), fill="both", expand=True)

    entries = []
    
    # --- Seção de Atalhos de Teclado ---
    atalhos_frame = ctk.CTkFrame(canvas, corner_radius=12, fg_color="#1e293b")
    atalhos_frame.pack(pady=8, padx=10, fill="x")
    
    ctk.CTkLabel(atalhos_frame, text="⌨️ Atalhos de Teclado", font=("Arial", 16, "bold")).pack(anchor="w", pady=4, padx=8)
    
    # Checkbox para habilitar/desabilitar atalhos
    atalhos_var = ctk.BooleanVar(value=config.get("atalhos_habilitados", True))
    atalhos_checkbox = ctk.CTkCheckBox(atalhos_frame, 
                                       text="Habilitar atalhos de teclado (Teclas 0-9)",
                                       variable=atalhos_var,
                                       font=("Arial", 12))
    atalhos_checkbox.pack(anchor="w", padx=10, pady=8)
    
    # --- Seção de Botões ---
    ctk.CTkLabel(canvas, text="🎵 Configuração dos Botões", font=("Arial", 16, "bold")).pack(anchor="w", pady=(15, 5), padx=10)

    for i, b in enumerate(config["botoes"]):
        frame = ctk.CTkFrame(canvas, corner_radius=12)
        frame.pack(pady=8, padx=10, fill="x")

        ctk.CTkLabel(frame, text=f"🎚️ {b['nome']}", font=("Arial", 16, "bold")).pack(anchor="w", pady=4, padx=8)

        # Nome
        nome = ctk.CTkEntry(frame, placeholder_text="Nome do botão (máx. 15 caracteres)")
        nome.insert(0, b["nome"])
        nome.pack(padx=10, pady=5, fill="x")
        
        # Label de aviso sobre o limite
        aviso_label = ctk.CTkLabel(frame, text="", font=("Arial", 10), text_color="#e74c3c")
        aviso_label.pack(padx=10, pady=2, anchor="w")
        
        # Função para validar o número de caracteres
        def validar_caracteres(event, nome_entry=nome, aviso=aviso_label):
            texto = nome_entry.get()
            num_chars = len(texto)
            if num_chars > 15:
                aviso.configure(text=f"⚠️ Limite excedido: {num_chars}/15 caracteres")
            else:
                aviso.configure(text=f"{num_chars}/15 caracteres")
        
        nome.bind("<KeyRelease>", validar_caracteres)
        # Chama a validação inicial
        validar_caracteres(None, nome, aviso_label)

        # Cor
        cor_frame = ctk.CTkFrame(frame, fg_color=b["cor"], width=30, height=30, corner_radius=6)
        cor_frame.pack(padx=10, pady=5, side="left")
        cor_label = ctk.CTkLabel(frame, text=b["cor"])
        cor_label.pack(padx=5, side="left")

        def escolher_cor_local(cor_frame=cor_frame, cor_label=cor_label, i=i):
            c = colorchooser.askcolor()[1]
            if c:
                config["botoes"][i]["cor"] = c
                cor_frame.configure(fg_color=c)
                cor_label.configure(text=c)
        ctk.CTkButton(frame, text="🎨 Escolher Cor", width=130, command=escolher_cor_local).pack(side="left", padx=8)

        # Arquivo de áudio
        def escolher_som_local(i=i):
            f = filedialog.askopenfilename(title="Selecionar som", filetypes=[("Áudio", "*.mp3 *.wav *.ogg")])
            if f:
                config["botoes"][i]["arquivo"] = f
                messagebox.showinfo("Som", f"Som selecionado para {config['botoes'][i]['nome']}")
        ctk.CTkButton(frame, text="🎵 Escolher Som", width=150, command=escolher_som_local).pack(side="right", padx=10)

        entries.append((i, nome))

    def salvar_tudo():
        # Valida se algum nome excede 15 caracteres
        for i, entry in entries:
            texto = entry.get()
            num_chars = len(texto)
            if num_chars > 15:
                messagebox.showerror("Erro", f"O botão '{config['botoes'][i]['nome']}' excede o limite de 15 caracteres ({num_chars} caracteres).\nPor favor, reduza o texto.")
                return
            config["botoes"][i]["nome"] = texto
        
        # Salva a configuração dos atalhos
        config["atalhos_habilitados"] = atalhos_var.get()
        
        salvar_config()
        atualizar_estilos()
        messagebox.showinfo("Configurações", "Alterações salvas com sucesso!")
        win.destroy()

    # Rodapé da janela - fixo na parte inferior
    rodape = ctk.CTkFrame(win, fg_color="#2b2b2b", height=60)
    rodape.pack(fill="x", side="bottom", pady=0)
    rodape.pack_propagate(False)  # Mantém altura fixa
    
    # Botoes centralizados no rodapé
    btn_frame = ctk.CTkFrame(rodape, fg_color="transparent")
    btn_frame.pack(expand=True)
    
    ctk.CTkButton(btn_frame, text="✔️ Salvar", fg_color="#16a34a", hover_color="#15803d",
                  width=120, height=35, font=("Arial", 13, "bold"),
                  command=salvar_tudo).pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="❌ Cancelar", fg_color="#6b7280", hover_color="#4b5563",
                  width=120, height=35, font=("Arial", 13, "bold"),
                  command=win.destroy).pack(side="left", padx=5)

# --- Atalhos do teclado ---
def on_key(event):
    # Verifica se os atalhos estão habilitados
    if config.get("atalhos_habilitados", True) and event.char.isdigit():
        idx = (int(event.char) - 1) % 10
        tocar_som(idx)
app.bind("<Key>", on_key)

app.protocol("WM_DELETE_WINDOW", lambda: (pygame.mixer.music.stop(), app.destroy()))
atualizar_estilos()
atualizar_texto_atalhos()  # Atualiza o texto de atalhos na inicialização
app.mainloop()

