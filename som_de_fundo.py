import os, sys, json, threading, time, math, webbrowser, zipfile, tempfile, shutil
import pygame
import qrcode
from remote_control import RemoteControlServer
import customtkinter as ctk
from tkinter import filedialog, colorchooser, messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont

def mostrar_sobre():
    sobre_janela = ctk.CTkToplevel()
    sobre_janela.title("Sobre o Desenvolvedor")
    sobre_janela.geometry("500x400")
    sobre_janela.resizable(False, False)
    sobre_janela.transient(app)
    sobre_janela.grab_set()
    sobre_janela.lift()
    sobre_janela.focus_force()
    try:
        sobre_janela.attributes("-topmost", True)
        sobre_janela.after(300, lambda: sobre_janela.attributes("-topmost", False))
    except:
        pass
    
    main_frame = ctk.CTkFrame(sobre_janela, fg_color="transparent")
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)
    
    titulo = ctk.CTkLabel(main_frame, text="Sobre o Desenvolvedor", font=("Arial", 24, "bold"))
    titulo.pack(pady=(0, 20))
    
    avatar = ctk.CTkLabel(main_frame, text="👨‍💻", font=("Arial", 70))
    avatar.pack(pady=10)
    
    def pulsar_avatar():
        current_size = 70
        def aumentar():
            nonlocal current_size
            if current_size < 80:
                current_size += 2
                avatar.configure(font=("Arial", current_size))
                sobre_janela.after(20, aumentar)
            else:
                sobre_janela.after(20, diminuir)
        
        def diminuir():
            nonlocal current_size
            if current_size > 70:
                current_size -= 2
                avatar.configure(font=("Arial", current_size))
                sobre_janela.after(20, diminuir)
            else:
                sobre_janela.after(1500, pulsar_avatar)
        
        aumentar()
    
    pulsar_avatar()
    
    texto_sobre = ctk.CTkLabel(
        main_frame,
        text="Desenvolvido com carinho por Alan ❤️\n\n"
             "Siga-me nas redes sociais:",
        justify="center"
    )
    texto_sobre.pack(pady=10)
    
    links_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    links_frame.pack(pady=10)
    
    def criar_botao_link(text, url):
        btn = ctk.CTkButton(
            links_frame,
            text=text,
            command=lambda: webbrowser.open(url),
            fg_color="transparent",
            text_color=("#1a73e8", "#8ab4f8"),
            hover_color=("#e8f0fe", "#1a56db"),
            anchor="w"
        )
        btn.pack(fill="x", pady=2)
    
    criar_botao_link("📷 Instagram: @allan.psxd1", "https://instagram.com/allan.psxd1")
    criar_botao_link("▶️ YouTube: @alanPs", "https://www.youtube.com/@alanPs")
    criar_botao_link("▶️ YouTube: @alantecmoz", "https://www.youtube.com/@alantecmoz")
    criar_botao_link("💾 GitHub: alanxdpro/Som_de_fundo", "https://github.com/alanxdpro/Som_de_fundo")
    
    versao = ctk.CTkLabel(
        main_frame,
        text="Versão 1.1.0",
        text_color=("gray50", "gray70"),
        font=("Arial", 10)
    )
    versao.pack(side="bottom", pady=10)
    
    sobre_janela.update_idletasks()
    width = sobre_janela.winfo_width()
    height = sobre_janela.winfo_height()
    x = (sobre_janela.winfo_screenwidth() // 2) - (width // 2)
    y = (sobre_janela.winfo_screenheight() // 2) - (height // 2)
    sobre_janela.geometry(f'{width}x{height}+{x}+{y}')

BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
APP_NAME = "Som_de_fundo"
USER_DATA_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", APP_NAME)
CONFIG_FILE = os.path.join(USER_DATA_DIR, "config.json")
APP_PREFS_FILE = os.path.join(USER_DATA_DIR, "app_prefs.json")
SONS_DIR = os.path.join(USER_DATA_DIR, "sons")
PLAYLISTS_DIR = os.path.join(USER_DATA_DIR, "playlists")
ICONS_DIR = os.path.join(BASE_DIR, "icons")
FADE_MS = 800
CONFIG_VERSION = 2

os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(SONS_DIR, exist_ok=True)
os.makedirs(PLAYLISTS_DIR, exist_ok=True)
pygame.mixer.init()

def carregar_icone(nome_arquivo, tamanho=(20, 20)):
    """Carrega um ícone da pasta icons e redimensiona se necessário"""
    try:
        caminho = os.path.join(ICONS_DIR, nome_arquivo)
        if os.path.exists(caminho):
            img = Image.open(caminho)
            img = img.resize(tamanho, Image.Resampling.LANCZOS)
            return ctk.CTkImage(light_image=img, dark_image=img, size=tamanho)
    except:
        pass
    return None

config = {}
current_index = None
is_switching = threading.Lock()
music_start_time = None
timer_label = None
is_paused = False
pause_time = 0
master_volume = 1.0
current_playlist = "default"

remote_label = None
app_prefs = {"whatsapp_disable": False, "whatsapp_last": 0}

def carregar_prefs():
    global app_prefs
    try:
        if os.path.exists(APP_PREFS_FILE):
            with open(APP_PREFS_FILE, "r", encoding="utf-8") as f:
                app_prefs = json.load(f)
        else:
            app_prefs = {"whatsapp_disable": False, "whatsapp_last": 0, "appearance_mode": "dark"}
    except:
        app_prefs = {"whatsapp_disable": False, "whatsapp_last": 0, "appearance_mode": "dark"}
    try:
        if "appearance_mode" not in app_prefs:
            app_prefs["appearance_mode"] = "dark"
    except:
        pass

def salvar_prefs():
    try:
        with open(APP_PREFS_FILE, "w", encoding="utf-8") as f:
            json.dump(app_prefs, f, indent=4, ensure_ascii=False)
    except:
        pass

def aplicar_tema_prefs():
    try:
        mode = app_prefs.get("appearance_mode", "dark")
        ctk.set_appearance_mode(mode)
    except:
        pass

def mostrar_whatsapp_popup_se_preciso():
    try:
        if app_prefs.get("whatsapp_disable"):
            return
        ultimo = float(app_prefs.get("whatsapp_last", 0))
        if time.time() - ultimo >= 5*24*3600:
            mostrar_whatsapp_popup()
    except:
        pass

def mostrar_whatsapp_popup():
    link = "https://chat.whatsapp.com/LhrNYqFpfrJ0GXPHqvjW1A?mode=hqrt3"
    win = ctk.CTkToplevel(app)
    win.title("Grupo do WhatsApp")
    win.geometry("520x280")
    win.resizable(False, False)
    win.transient(app)
    win.grab_set()
    win.lift()
    win.focus_force()
    try:
        win.attributes("-topmost", True)
        win.after(300, lambda: win.attributes("-topmost", False))
    except:
        pass
    frame = ctk.CTkFrame(win, fg_color="transparent")
    frame.pack(expand=True, fill="both", padx=20, pady=20)
    ctk.CTkLabel(frame, text="Participe do grupo no WhatsApp para melhorias do aplicativo.", font=("Arial", 16, "bold")).pack(pady=(0,10))
    ctk.CTkLabel(frame, text=link, font=("Arial", 13)).pack(pady=6)
    row = ctk.CTkFrame(frame, fg_color="transparent")
    row.pack(pady=10)
    def entrar():
        webbrowser.open(link)
        app_prefs["whatsapp_last"] = time.time()
        salvar_prefs()
        win.destroy()
    def depois():
        app_prefs["whatsapp_last"] = time.time()
        salvar_prefs()
        win.destroy()
    def nunca():
        app_prefs["whatsapp_disable"] = True
        salvar_prefs()
        win.destroy()
    ctk.CTkButton(row, text="Entrar no grupo", fg_color="#16a34a", hover_color="#15803d", command=entrar).pack(side="left", padx=6)
    ctk.CTkButton(row, text="Depois", fg_color="#6b7280", hover_color="#4b5563", command=depois).pack(side="left", padx=6)
    ctk.CTkButton(row, text="Não mostrar novamente", fg_color="#ef4444", hover_color="#dc2626", command=nunca).pack(side="left", padx=6)
    win.update_idletasks()
    w = win.winfo_width()
    h = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (w // 2)
    y = (win.winfo_screenheight() // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

def _post_to_main(func, *args, **kwargs):
    try:
        app.after(0, lambda: func(*args, **kwargs))
    except:
        pass

def _run_on_main_and_wait(func, timeout=2.0, *args, **kwargs):
    ev = threading.Event()
    def runner():
        try:
            func(*args, **kwargs)
        finally:
            ev.set()
    try:
        app.after(0, runner)
        ev.wait(timeout)
    except:
        pass
    return ev.is_set()


def _show_error(title, err):
    try:
        msg = str(err) if err is not None else ""
        typ = type(err).__name__ if err is not None else "Erro"
        messagebox.showerror(title, f"{msg}\n\n{typ}")
    except:
        pass


def trocar_playlist_remoto(nova_playlist):
    global current_playlist, config
    parar_tudo()
    current_playlist = nova_playlist
    carregar_config()
    atualizar_estilos()
    atualizar_combo_playlists()
    try:
        recriar_botoes()
    except Exception:
        pass

def default_config():
    paleta_cores = [
        '#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#ef4444',
        '#f59e0b', '#ec4899', '#14b8a6', '#f97316', '#6366f1'
    ]
    
    return {
        "botoes": [
            {"nome": f"Botão {i+1}", "cor": paleta_cores[i], "arquivo": "", "icone": "", "volume": 1.0,
             "imagem": "", "imagem_cache": "", "texto_cor": "#ffffff"}
            for i in range(10)
        ],
        "atalhos_habilitados": True,
        "fade_in_ms": 800,
        "fade_out_ms": 800,
        "repeticao_habilitada": False,
        "master_volume": 1.0,
        "config_version": CONFIG_VERSION
    }

def carregar_config():
    global config, master_volume
    playlist_file = os.path.join(PLAYLISTS_DIR, f"{current_playlist}.json")
    
    if not os.path.exists(playlist_file):
        config = default_config()
        salvar_config()
    else:
        with open(playlist_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        changed = False
        try:
            v = int(config.get("config_version", 0))
        except:
            v = 0
        if v < CONFIG_VERSION:
            config["config_version"] = CONFIG_VERSION
            changed = True
        if "atalhos_habilitados" not in config:
            config["atalhos_habilitados"] = True
            changed = True
        if "fade_in_ms" not in config:
            config["fade_in_ms"] = 800
            changed = True
        if "fade_out_ms" not in config:
            config["fade_out_ms"] = 800
            changed = True
        if "repeticao_habilitada" not in config:
            config["repeticao_habilitada"] = False
            changed = True
        if "master_volume" not in config:
            config["master_volume"] = 1.0
            changed = True
        
        for idx, b in enumerate(config.get("botoes", [])):
            if "volume" not in b:
                b["volume"] = 1.0
                changed = True
            if "imagem" not in b:
                b["imagem"] = ""
                changed = True
            if "imagem_cache" not in b:
                b["imagem_cache"] = ""
                changed = True
            if "texto_cor" not in b:
                b["texto_cor"] = "#ffffff"
                changed = True
            try:
                expected = os.path.join(ICONS_DIR, current_playlist, f"btn{idx+1}.jpg")
                cache_ok = b.get("imagem_cache") and os.path.normpath(b.get("imagem_cache")) == os.path.normpath(expected) and os.path.exists(expected)
                if b.get("imagem") and not cache_ok:
                    processar_imagem_botao(idx, b.get("imagem"))
                    changed = True
                elif not b.get("imagem"):
                    b["imagem_cache"] = ""
                    changed = True
            except:
                pass
        
        if changed:
            salvar_config()
    
    master_volume = config.get("master_volume", 1.0)
    try:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(master_volume)
    except Exception:
        pass

def salvar_config():
    playlist_file = os.path.join(PLAYLISTS_DIR, f"{current_playlist}.json")
    config["master_volume"] = master_volume
    try:
        config["config_version"] = CONFIG_VERSION
    except:
        pass
    with open(playlist_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def listar_playlists():
    playlists = []
    for file in os.listdir(PLAYLISTS_DIR):
        if file.endswith(".json"):
            playlists.append(file.replace(".json", ""))
    return playlists if playlists else ["default"]

def trocar_playlist(nova_playlist):
    global current_playlist, config
    parar_tudo()
    current_playlist = nova_playlist
    carregar_config()
    atualizar_estilos()
    atualizar_combo_playlists()
    messagebox.showinfo("Playlist", f"Playlist '{nova_playlist}' carregada com sucesso!")
    try:
        recriar_botoes()
    except Exception:
        pass

def criar_nova_playlist():
    nome = simpledialog.askstring("Nova Playlist", "Digite o nome da nova playlist:")
    if nome:
        nome = nome.strip().replace(" ", "_")
        if nome:
            global current_playlist
            parar_tudo()
            current_playlist = nome
            global config
            config = default_config()
            salvar_config()
            atualizar_estilos()
            atualizar_combo_playlists()
            messagebox.showinfo("Playlist", f"Playlist '{nome}' criada com sucesso!")
            try:
                recriar_botoes()
            except Exception:
                pass

def duplicar_playlist():
    nome = simpledialog.askstring("Duplicar Playlist", f"Digite o nome para a cópia de '{current_playlist}':")
    if nome:
        nome = nome.strip().replace(" ", "_")
        if nome:
            nova_playlist_file = os.path.join(PLAYLISTS_DIR, f"{nome}.json")
            playlist_atual_file = os.path.join(PLAYLISTS_DIR, f"{current_playlist}.json")
            
            with open(playlist_atual_file, "r", encoding="utf-8") as f:
                config_copia = json.load(f)
            
            with open(nova_playlist_file, "w", encoding="utf-8") as f:
                json.dump(config_copia, f, indent=4, ensure_ascii=False)
            
            atualizar_combo_playlists()
            messagebox.showinfo("Playlist", f"Playlist duplicada como '{nome}'!")

def excluir_playlist():
    if current_playlist == "default":
        resposta = messagebox.askyesno("Limpar Cache", "A playlist 'default' não pode ser excluída.\n\nDeseja limpar o cache de ícones desta playlist?")
        if resposta:
            try:
                base = os.path.join(ICONS_DIR, current_playlist)
                if os.path.isdir(base):
                    for nome in os.listdir(base):
                        p = os.path.join(base, nome)
                        try:
                            if os.path.isfile(p):
                                os.remove(p)
                        except Exception:
                            pass
                    try:
                        os.rmdir(base)
                    except Exception:
                        pass
            except Exception:
                pass
            messagebox.showinfo("Cache", "Cache de ícones da playlist 'default' limpo!")
        return
    
    resposta = messagebox.askyesno("Excluir Playlist", f"Tem certeza que deseja excluir a playlist '{current_playlist}'?")
    if resposta:
        playlist_file = os.path.join(PLAYLISTS_DIR, f"{current_playlist}.json")
        if os.path.exists(playlist_file):
            os.remove(playlist_file)
        try:
            base = os.path.join(ICONS_DIR, current_playlist)
            if os.path.isdir(base):
                for nome in os.listdir(base):
                    p = os.path.join(base, nome)
                    try:
                        if os.path.isfile(p):
                            os.remove(p)
                    except Exception:
                        pass
                try:
                    os.rmdir(base)
                except Exception:
                    pass
        except Exception:
            pass
        trocar_playlist("default")
        messagebox.showinfo("Playlist", f"Playlist excluída com sucesso!")

def _play_file_loop(path, volume):
    global is_paused
    try:
        pygame.mixer.music.load(path)
        volume_final = volume * master_volume
        pygame.mixer.music.set_volume(volume_final)
        # Decidir se deve repetir baseado na configuração
        repetir = config.get("repeticao_habilitada", False)
        loops = -1 if repetir else 0
        pygame.mixer.music.play(loops=loops, fade_ms=config.get("fade_in_ms", FADE_MS))
        is_paused = False
    except Exception as e:
        _show_error("Erro de áudio", e)

def abrir_arquivo(index):
    """Abre a janela de seleção de arquivo para o botão especificado"""
    f = filedialog.askopenfilename(
        title=f"Selecionar som para {config['botoes'][index]['nome']}", 
        filetypes=[("Áudio", "*.mp3 *.wav *.ogg")]
    )
    if f:
        if validar_arquivo_audio(f):
            config["botoes"][index]["arquivo"] = f
            try:
                config["botoes"][index]["duracao"] = obter_duracao_musica(f)
            except:
                pass
            salvar_config()
            messagebox.showinfo("Sucesso", f"Arquivo adicionado ao botão {config['botoes'][index]['nome']}")

def resolve_audio_path(p):
    try:
        if p and os.path.exists(p):
            return p
        base = os.path.basename(p) if p else ""
        if base:
            candidate = os.path.join(SONS_DIR, base)
            if os.path.exists(candidate):
                return candidate
            for root, _, files in os.walk(SONS_DIR):
                for fn in files:
                    if fn.lower() == base.lower():
                        return os.path.join(root, fn)
    except Exception:
        pass
    return p

def tocar_som(index):
    global current_index
    botao = config["botoes"][index]
    caminho_orig = botao["arquivo"]
    caminho = resolve_audio_path(caminho_orig)
    if caminho != caminho_orig:
        config["botoes"][index]["arquivo"] = caminho
        salvar_config()
    if not caminho or not os.path.exists(caminho):
        resposta = messagebox.askyesno("Arquivo não encontrado", 
                                     f"Nenhum arquivo de som definido para este botão.\n\nDeseja adicionar um arquivo agora?")
        if resposta:
            abrir_arquivo(index)
        return
    if current_index == index and pygame.mixer.music.get_busy():
        return
    volume = botao.get("volume", 1.0)
    threading.Thread(target=_switch_music_thread, args=(index, caminho, volume), daemon=True).start()

def _switch_music_thread(index, caminho, volume):
    global current_index, music_start_time
    if not is_switching.acquire(blocking=False):
        return
    try:
        if pygame.mixer.music.get_busy():
            fade_out = config.get("fade_out_ms", FADE_MS)
            pygame.mixer.music.fadeout(fade_out)
            time.sleep(fade_out / 1000)
        _play_file_loop(caminho, volume)
        current_index = index
        music_start_time = time.time()
        atualizar_estilos()
        atualizar_timer()
    finally:
        is_switching.release()

# Controle remoto: estado para API
def get_remote_state():
    botoes = []
    for i, b in enumerate(config.get("botoes", [])):
        img_cache = b.get("imagem_cache")
        base_dir = os.path.join(ICONS_DIR, current_playlist)
        use_img = bool(img_cache and os.path.exists(img_cache) and os.path.normpath(img_cache).startswith(os.path.normpath(base_dir)))
        icon = f"/icon/{current_playlist}/{i+1}" if use_img else "/icon/_default"
        botoes.append({
            "index": i,
            "nome": b.get("nome", f"Botão {i+1}"),
            "cor": b.get("cor", "#2563eb"),
            "ativo": current_index == i,
            "icon": icon,
        })
    return {
        "playlist": current_playlist,
        "playlists": listar_playlists(),
        "botoes": botoes,
        "tocando": bool(pygame.mixer.music.get_busy()),
        "paused": is_paused,
        "master_volume": master_volume,
        "volume_percent": int(master_volume * 100),
    }

def obter_duracao_musica(caminho):
    try:
        sound = pygame.mixer.Sound(caminho)
        return int(sound.get_length())
    except:
        return 0

def validar_arquivo_audio(path):
    try:
        ext = os.path.splitext(path)[1].lower()
        if ext not in (".mp3", ".wav", ".ogg"):
            messagebox.showerror("Áudio", "Formato não suportado. Use .mp3, .wav ou .ogg.")
            return False
        try:
            size = os.path.getsize(path)
            mb = max(1, int(size / (1024 * 1024)))
            if size > 120 * 1024 * 1024:
                messagebox.showerror("Áudio", "O arquivo excede 120 MB. Por favor, use um áudio menor.")
                return False
            if size > 40 * 1024 * 1024:
                messagebox.showwarning("Áudio", f"Arquivo grande (~{mb} MB). Se o seu computador não for muito potente, pode haver pequenas travadinhas durante a reprodução. Isso é normal — prefira arquivos menores quando possível.")
        except Exception as e:
            _show_error("Erro ao verificar tamanho", e)
            return False
        try:
            pygame.mixer.Sound(path)
        except Exception as e:
            _show_error("Áudio não suportado", e)
            return False
        return True
    except Exception as e:
        _show_error("Erro ao validar áudio", e)
        return False

def formatar_tempo(segundos):
    minutos = int(segundos) // 60
    segundos = int(segundos) % 60
    return f"{minutos:02d}:{segundos:02d}"

def atualizar_timer():
    global music_start_time, timer_label, progressBar_musica
    if music_start_time and pygame.mixer.music.get_busy():
        elapsed = int(time.time() - music_start_time)
        
        if current_index is not None and "arquivo" in config["botoes"][current_index]:
            caminho = resolve_audio_path(config["botoes"][current_index]["arquivo"]) 
            nome_arquivo = os.path.basename(caminho) if caminho else ""
            nome_musica = os.path.splitext(nome_arquivo)[0] if nome_arquivo else ""
            
            if "duracao" not in config["botoes"][current_index]:
                duracao_total = obter_duracao_musica(caminho) if caminho and os.path.exists(caminho) else 0
                config["botoes"][current_index]["duracao"] = duracao_total
                try:
                    salvar_config()
                except:
                    pass
            else:
                duracao_total = config["botoes"][current_index]["duracao"]
            
            tempo_atual = formatar_tempo(elapsed)
            tempo_total = formatar_tempo(duracao_total) if duracao_total > 0 else "--:--"
            
            timer_label.configure(text=f" {nome_musica} | {tempo_atual} / {tempo_total}")
            progress = 0.0
            if duracao_total > 0:
                try:
                    progress = min(elapsed / duracao_total, 1.0)
                except Exception:
                    progress = 0.0
            progressBar_musica.set(progress)

        app.after(1000, atualizar_timer)
    elif timer_label:
        timer_label.configure(text="00:00 / 00:00")

def fade_in(step=0.0):
    if not is_paused and current_index is not None and pygame.mixer.music.get_busy():
        volume_botao = config["botoes"][current_index].get("volume", 1.0)
        target_volume = volume_botao * master_volume
        current_vol = min(step, target_volume)
        pygame.mixer.music.set_volume(current_vol)
        
        if current_vol < target_volume:
            app.after(30, lambda: fade_in(step + 0.05))

def pausar_retomar():
    global music_start_time, is_paused, current_index, pause_time
    
    if not is_paused and pygame.mixer.music.get_busy():
        fade_out_time = 500
        pygame.mixer.music.fadeout(fade_out_time)
        is_paused = True
        if music_start_time is not None:
            pause_time = time.time() - music_start_time
    elif is_paused and current_index is not None:
        botao = config["botoes"][current_index]
        caminho = resolve_audio_path(botao["arquivo"]) 
        volume = botao.get("volume", 1.0)
        
        pygame.mixer.music.stop()
        
        try:
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.set_volume(0)
            
            posicao_segundos = pause_time if pause_time is not None else 0
            # Respeitar configuração de repetição ao retomar
            repetir = config.get("repeticao_habilitada", False)
            loops = -1 if repetir else 0
            pygame.mixer.music.play(loops=loops, start=posicao_segundos)
            
            is_paused = False
            music_start_time = time.time() - posicao_segundos
            
            fade_in(0.0)
            
            atualizar_timer()
            
        except Exception as e:
            _show_error("Erro ao retomar", e)
            is_paused = True
    
    atualizar_estilos()

def reiniciar_musica():
    global music_start_time, is_paused, pause_time
    if current_index is None:
        return
    botao = config["botoes"][current_index]
    caminho = resolve_audio_path(botao["arquivo"]) 
    volume = botao.get("volume", 1.0)
    if not caminho or not os.path.exists(caminho):
        return
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(caminho)
        pygame.mixer.music.set_volume(0)
        repetir = config.get("repeticao_habilitada", False)
        loops = -1 if repetir else 0
        pygame.mixer.music.play(loops=loops, fade_ms=0)
        is_paused = False
        pause_time = 0
        music_start_time = time.time()
        fade_in(0.0)
        atualizar_timer()
        atualizar_estilos()
    except Exception as e:
        _show_error("Erro ao reiniciar", e)

def parar_tudo():
    global current_index, music_start_time, is_paused
    if pygame.mixer.music.get_busy() or is_paused:
        fade_out_time = 500
        pygame.mixer.music.fadeout(fade_out_time)
        is_paused = False
    music_start_time = None
    if timer_label:
        timer_label.configure(text="00:00 / 00:00")
    current_index = None
    atualizar_estilos()



def atualizar_volume_individual(index, volume):
    config["botoes"][index]["volume"] = volume
    if current_index == index and pygame.mixer.music.get_busy():
        volume_final = volume * master_volume
        pygame.mixer.music.set_volume(volume_final)
    salvar_config()

def atualizar_volume_master(volume):
    global master_volume
    master_volume = volume
    config["master_volume"] = volume
    if current_index is not None and pygame.mixer.music.get_busy():
        volume_botao = config["botoes"][current_index].get("volume", 1.0)
        volume_final = volume_botao * master_volume
        pygame.mixer.music.set_volume(volume_final)
    salvar_config()

def set_master_volume_smooth(target, duration_ms=500):
    try:
        target = max(0.0, min(1.0, float(target)))
    except:
        return
    current = float(master_volume)
    steps = max(1, int(duration_ms / 50))
    delta = (target - current) / steps
    def _step(i=0, v=current):
        nv = max(0.0, min(1.0, v + delta))
        atualizar_volume_master(nv)
        if i < steps - 1:
            app.after(50, lambda: _step(i+1, nv))
    _step()

def remote_set_master_volume(value):
    set_master_volume_smooth(value, 500)

def remote_delta_master_volume(delta):
    try:
        delta = float(delta)
    except:
        delta = 0.0
    set_master_volume_smooth(max(0.0, min(1.0, master_volume + delta)), 500)

animation_frames = {}

def criar_animacao_pulsacao(canvas_widget, index):
    def animar():
        if current_index == index:
            t = time.time() * 3
            escala = 1 + 0.05 * math.sin(t)
            opacity = 0.3 + 0.2 * math.sin(t)
            app.after(50, animar)
    animar()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Som de Fundo — Console Profissional")
app.geometry("1100x650")

try:
    ico_path = os.path.join(os.path.dirname(__file__), "icone.ico")
    if os.path.exists(ico_path):
        app.iconbitmap(ico_path)
    else:
        alt_ico = os.path.join(ICONS_DIR, "app_icon.ico")
        if os.path.exists(alt_ico):
            app.iconbitmap(alt_ico)
except:
    pass

carregar_config()
carregar_prefs()
aplicar_tema_prefs()
button_refs = []
volume_sliders = []

# Inicializar servidor de controle remoto
server = RemoteControlServer(
    port=5005,
    get_state=get_remote_state,
    play=tocar_som,
    stop=parar_tudo,
    pause=pausar_retomar,
    switch_playlist=trocar_playlist_remoto,
    post_to_main=_post_to_main,
    run_on_main_and_wait=_run_on_main_and_wait,
    set_volume=remote_set_master_volume,
    delta_volume=remote_delta_master_volume,
)

header_frame = ctk.CTkFrame(app, fg_color="transparent")
header_frame.pack(pady=20, fill="x", padx=20)

header = ctk.CTkLabel(header_frame, text="🎚️ SOM DE FUNDO PRO", font=("Arial Rounded MT Bold", 26))
header.pack(side="left", expand=True)

musica_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
musica_frame.pack(side="right", expand=True)


timer_label = ctk.CTkLabel(musica_frame, text="00:00 / 00:00", font=("Arial", 12), text_color="#9ca3af", anchor="e")
timer_label.pack(side="top", padx=20, pady=5)

progressBar_musica = ctk.CTkProgressBar(musica_frame, width=200)
progressBar_musica.pack(side="bottom", pady=10, padx=10)
progressBar_musica.set(0)

playlist_frame = ctk.CTkFrame(app, fg_color=("#e5e7eb", "#1e293b"), height=50)
playlist_frame.pack(fill="x", padx=20, pady=(0, 10))

ctk.CTkLabel(playlist_frame, text="📁 Playlist:", font=("Arial", 13, "bold")).pack(side="left", padx=(10, 5))

playlist_combo = ctk.CTkComboBox(playlist_frame, values=listar_playlists(), width=200,
                                  command=lambda choice: trocar_playlist(choice))
playlist_combo.set(current_playlist)
playlist_combo.pack(side="left", padx=5)

ctk.CTkButton(playlist_frame, text="➕ Nova", width=80, height=28,
              command=criar_nova_playlist).pack(side="left", padx=2)
ctk.CTkButton(playlist_frame, text="📋 Duplicar", width=90, height=28,
              command=duplicar_playlist).pack(side="left", padx=2)
ctk.CTkButton(playlist_frame, text="🗑️ Excluir", width=80, height=28, fg_color="#dc2626",
              command=excluir_playlist).pack(side="left", padx=2)

def atualizar_combo_playlists():
    playlists = listar_playlists()
    playlist_combo.configure(values=playlists)
    playlist_combo.set(current_playlist)

volume_master_frame = ctk.CTkFrame(playlist_frame, fg_color="transparent")
volume_master_frame.pack(side="right", padx=10)

ctk.CTkLabel(volume_master_frame, text="🔊 Volume Geral:", font=("Arial", 12, "bold")).pack(side="left", padx=5)

volume_master_label = ctk.CTkLabel(volume_master_frame, text="100%", width=45, font=("Arial", 11))
volume_master_label.pack(side="left", padx=5)

def on_master_volume_change(valor):
    volume_master_label.configure(text=f"{int(valor*100)}%")
    atualizar_volume_master(valor)

volume_master_slider = ctk.CTkSlider(volume_master_frame, from_=0, to=1, width=150,
                                     command=on_master_volume_change)
volume_master_slider.set(master_volume)
volume_master_slider.pack(side="left", padx=5)

panel = ctk.CTkFrame(app)
panel.pack(expand=True, fill="both", padx=20, pady=10)

def atualizar_estilos():
    for i, ref in enumerate(button_refs):
        cor = config["botoes"][i]["cor"]
        nome = config["botoes"][i]["nome"]
        ref.configure(fg_color=cor, text=quebrar_texto(nome))
        
        if current_index == i:
            ref.configure(border_color="#ffffff", border_width=3)
            cor_rgb = tuple(int(cor.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            cor_clara = f"#{min(cor_rgb[0]+30, 255):02x}{min(cor_rgb[1]+30, 255):02x}{min(cor_rgb[2]+30, 255):02x}"
            ref.configure(hover_color=cor_clara)
        else:
            ref.configure(border_color=cor, border_width=0)
            ref.configure(hover_color=cor)
    
    atualizar_texto_atalhos()

def _hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _lighten_hex(h, amt=30):
    r, g, b = _hex_to_rgb(h)
    return f"#{min(r+amt,255):02x}{min(g+amt,255):02x}{min(b+amt,255):02x}"

def _make_placeholder(size, cor):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    radius = max(10, size//12)
    fill = _lighten_hex(cor, 20)
    d.rounded_rectangle([0, 0, size-1, size-1], radius=radius, fill=fill, outline="#ffffff", width=max(2, size//40))
    return img

def _load_default_cover(size, cor):
    try:
        p = os.path.join(ICONS_DIR, "sem_capa.png")
        if os.path.exists(p):
            img = Image.open(p).convert("RGBA")
            img = img.resize((size, size), Image.Resampling.LANCZOS)
            mask = Image.new("L", (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([0, 0, size-1, size-1], radius=max(10, size//12), fill=255)
            img.putalpha(mask)
            return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
    except:
        pass
    imgp = _make_placeholder(size, cor)
    return ctk.CTkImage(light_image=imgp, dark_image=imgp, size=(size, size))

def quebrar_texto(texto, max_chars=12):
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
    
    return '\n'.join(linhas) if linhas else texto

def is_fullscreen_like():
    try:
        if app.attributes("-fullscreen"):
            return True
    except:
        pass
    try:
        sw, sh = app.winfo_screenwidth(), app.winfo_screenheight()
        ww, wh = app.winfo_width(), app.winfo_height()
        return ww >= sw - 50 and wh >= sh - 80
    except:
        return False

def criar_botoes():
    panel.grid_propagate(True)
    for i in range(2):
        panel.grid_rowconfigure(i, weight=1, uniform='row')
    for i in range(5):
        panel.grid_columnconfigure(i, weight=1, uniform='col')
    
    for i in range(10):
        frame = ctk.CTkFrame(panel, fg_color="transparent")
        frame.grid(row=i//5, column=i%5, padx=5, pady=5, sticky="nsew")
        frame.grid_propagate(True)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_columnconfigure(0, weight=1)
        
        base_texto = config["botoes"][i]["nome"]
        texto_botao = quebrar_texto(base_texto)
        
        img_cache = config["botoes"][i].get("imagem_cache", "")
        base_dir = os.path.join(ICONS_DIR, current_playlist)
        use_img = bool(img_cache and os.path.exists(img_cache) and os.path.normpath(img_cache).startswith(os.path.normpath(base_dir)))
        img_sz = 180 if is_fullscreen_like() else 120
        cover_sz = max(80, int(img_sz * 0.85))
        b = ctk.CTkButton(frame, 
                         text=texto_botao,
                         fg_color=config["botoes"][i]["cor"],
                         text_color=config["botoes"][i].get("texto_cor", "white"),
                         width=img_sz, 
                         height=cover_sz + 40, 
                         font=("Arial", 13, "bold"),
                         anchor="center",
                         corner_radius=8,
                         hover_color=config["botoes"][i]["cor"],
                         compound=("top" if use_img else None),
                         command=lambda i=i: tocar_som(i))
        b.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        if use_img:
            try:
                img = Image.open(img_cache).convert("RGBA")
                img = img.resize((cover_sz, cover_sz), Image.Resampling.LANCZOS)
                mask = Image.new("L", (cover_sz, cover_sz), 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle([0, 0, cover_sz-1, cover_sz-1], radius=max(10, cover_sz//12), fill=255)
                img.putalpha(mask)
                cimg = ctk.CTkImage(light_image=img, dark_image=img, size=(cover_sz, cover_sz))
                b.configure(image=cimg)
                b.image = cimg
            except:
                pass
        else:
            try:
                cimgp = _load_default_cover(cover_sz, config["botoes"][i]["cor"]) 
                b.configure(image=cimgp, compound="top")
                b.image = cimgp
            except:
                pass
        button_refs.append(b)
        
        volume_frame = ctk.CTkFrame(frame, fg_color=("#e5e7eb", "#1e1e1e"), height=30)
        volume_frame.grid(row=1, column=0, sticky="ew", padx=2, pady=(0, 2))
        
        volume_label = ctk.CTkLabel(volume_frame, text=f"{int(config['botoes'][i].get('volume', 1.0)*100)}%", 
                                     width=35, font=("Arial", 10))
        volume_label.pack(side="left", padx=2)
        
        def criar_callback(idx, lbl):
            def callback(valor):
                lbl.configure(text=f"{int(valor*100)}%")
                atualizar_volume_individual(idx, valor)
            return callback
        
        slider = ctk.CTkSlider(volume_frame, from_=0, to=1, width=100, height=12,
                               command=criar_callback(i, volume_label))
        slider.set(config["botoes"][i].get("volume", 1.0))
        slider.pack(side="left", padx=2, expand=True, fill="x")
        volume_sliders.append((slider, volume_label))

criar_botoes()
try:
    atualizar_estilos()
except Exception:
    pass

def recriar_botoes():
    for b in button_refs:
        try:
            b.destroy()
        except:
            pass
    button_refs.clear()
    volume_sliders.clear()
    criar_botoes()

def _ensure_icons_dir():
    try:
        base = os.path.join(ICONS_DIR, current_playlist)
        os.makedirs(base, exist_ok=True)
        return base
    except:
        return ICONS_DIR

def selecionar_imagem_botao(index, parent=None):
    _ensure_icons_dir()
    f = filedialog.askopenfilename(title=f"Selecionar imagem para {config['botoes'][index]['nome']}",
                                   filetypes=[("Imagens", "*.jpg *.jpeg *.png *.webp")])
    if not f:
        return
    try:
        if os.path.getsize(f) > 2 * 1024 * 1024:
            messagebox.showwarning("Imagem grande", "Limite de 2MB por imagem. Escolha outra.")
            return
    except:
        pass
    ok = processar_imagem_botao(index, f)
    if ok:
        salvar_config()
        recriar_botoes()
        if parent:
            parent.focus_force()

def remover_imagem_botao(index, parent=None):
    try:
        config["botoes"][index]["imagem"] = ""
        config["botoes"][index]["imagem_cache"] = ""
        salvar_config()
        recriar_botoes()
    except:
        pass
    if parent:
        parent.focus_force()

def processar_imagem_botao(index, path):
    try:
        img = Image.open(path).convert("RGB")
    except Exception as e:
        _show_error("Erro ao abrir imagem", e)
        return False
    w, h = img.size
    if min(w, h) < 140:
        messagebox.showwarning("Baixa resolução", "Imagem muito pequena, pode ficar borrada.")
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    small = img.resize((126, 126), Image.Resampling.LANCZOS)
    bg = Image.new("RGB", (140, 140), "#ffffff")
    bg.paste(small, (7, 7))
    try:
        draw = ImageDraw.Draw(bg)
        nome = config["botoes"][index]["nome"]
        texto = nome
        cor = config["botoes"][index].get("texto_cor", "#ffffff")
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        tw, th = draw.textsize(texto, font=font)
        x = (140 - tw) // 2
        y = 140 - th - 6
        shadow = (x+1, y+1)
        draw.text(shadow, texto, font=font, fill="#000000")
        draw.text((x, y), texto, font=font, fill=cor, stroke_width=2, stroke_fill="#000000")
    except:
        pass
    out_dir = _ensure_icons_dir()
    cache_name = f"btn{index+1}.jpg"
    out_path = os.path.join(out_dir, cache_name)
    try:
        bg.save(out_path, format="JPEG", quality=85, optimize=True)
    except Exception as e:
        _show_error("Erro ao salvar imagem", e)
        return False
    config["botoes"][index]["imagem"] = path
    config["botoes"][index]["imagem_cache"] = out_path
    return True

_last_fullscreen_like = None
_resize_rebuild_flag = False

def is_fullscreen_like():
    try:
        if app.attributes("-fullscreen"):
            return True
    except:
        pass
    try:
        sw, sh = app.winfo_screenwidth(), app.winfo_screenheight()
        ww, wh = app.winfo_width(), app.winfo_height()
        return ww >= sw - 50 and wh >= sh - 80
    except:
        return False

def _do_rebuild_buttons():
    global _resize_rebuild_flag
    _resize_rebuild_flag = False
    recriar_botoes()

def _on_app_resize(event=None):
    global _last_fullscreen_like, _resize_rebuild_flag
    cur = is_fullscreen_like()
    if cur != _last_fullscreen_like:
        _last_fullscreen_like = cur
        if not _resize_rebuild_flag:
            _resize_rebuild_flag = True
            try:
                app.after(300, _do_rebuild_buttons)
            except:
                pass

try:
    app.bind("<Configure>", _on_app_resize)
except:
    pass

 

def exportar_backup():
    try:
        parar_tudo()
    except Exception:
        pass
    backup_name = f"Som_de_fundo_backup_{time.strftime('%Y%m%d')}.zip"
    path = filedialog.asksaveasfilename(defaultextension=".zip", initialfile=backup_name,
                                        filetypes=[("Zip", "*.zip")], title="Salvar backup")
    if not path:
        return
    try:
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(USER_DATA_DIR):
                for fn in files:
                    fp = os.path.join(root, fn)
                    arc = os.path.relpath(fp, USER_DATA_DIR)
                    z.write(fp, arc)
            for file in os.listdir(PLAYLISTS_DIR):
                if file.endswith(".json"):
                    pl_name = file.replace(".json", "")
                    try:
                        with open(os.path.join(PLAYLISTS_DIR, file), "r", encoding="utf-8") as f:
                            pdata = json.load(f)
                        for b in pdata.get("botoes", []):
                            imgp = b.get("imagem") or ""
                            if imgp and os.path.exists(imgp):
                                z.write(imgp, os.path.join("images", pl_name, os.path.basename(imgp)))
                    except Exception:
                        pass
        messagebox.showinfo("Backup", "Backup exportado com sucesso!")
    except Exception as e:
        _show_error("Erro ao exportar backup", e)

def importar_backup():
    try:
        parar_tudo()
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
    except Exception:
        pass
    resposta = messagebox.askyesno("Importar Backup", "Para evitar arquivos bloqueados, feche o app antes de importar.\n\nDeseja continuar?")
    if not resposta:
        return
    path = filedialog.askopenfilename(filetypes=[("Zip", "*.zip")], title="Selecionar backup")
    if not path:
        return
    tmpdir = None
    try:
        tmpdir = tempfile.mkdtemp(prefix="Som_de_fundo_import_")
        with zipfile.ZipFile(path, "r") as z:
            z.extractall(tmpdir)
        for root, _, files in os.walk(tmpdir):
            for fn in files:
                src = os.path.join(root, fn)
                rel = os.path.relpath(src, tmpdir)
                dest = os.path.join(USER_DATA_DIR, rel)
                try:
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    if not os.path.exists(dest):
                        shutil.copy2(src, dest)
                    else:
                        try:
                            os.replace(src, dest)
                        except Exception:
                            pass
                except PermissionError:
                    pass
                except Exception:
                    pass
        for file in os.listdir(PLAYLISTS_DIR):
            if file.endswith(".json"):
                try:
                    pl_name = file.replace(".json", "")
                    ppath = os.path.join(PLAYLISTS_DIR, file)
                    with open(ppath, "r", encoding="utf-8") as f:
                        pdata = json.load(f)
                    changed = False
                    for b in pdata.get("botoes", []):
                        base = os.path.basename(b.get("imagem", "") or "")
                        if base:
                            new_img = os.path.join(USER_DATA_DIR, "images", pl_name, base)
                            if os.path.exists(new_img):
                                b["imagem"] = new_img
                                b["imagem_cache"] = ""
                                changed = True
                    if changed:
                        with open(ppath, "w", encoding="utf-8") as f:
                            json.dump(pdata, f, indent=4, ensure_ascii=False)
                except Exception:
                    pass
        carregar_config()
        try:
            recriar_botoes()
        except Exception:
            atualizar_estilos()
        messagebox.showinfo("Backup", "Backup importado com sucesso! Reinicie o aplicativo para aplicar totalmente.")
    except Exception as e:
        _show_error("Erro ao importar backup", e)
    finally:
        try:
            if tmpdir and os.path.isdir(tmpdir):
                shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass

def abrir_pasta_dados():
    try:
        if os.name == 'nt':
            os.startfile(USER_DATA_DIR)
        else:
            webbrowser.open(f"file://{os.path.abspath(USER_DATA_DIR)}")
    except Exception as e:
        _show_error("Erro ao abrir pasta de dados", e)

def abrir_config_janela():
    win = ctk.CTkToplevel(app)
    win.title("Configurações dos Botões")
    win.geometry("750x600")
    win.resizable(False, False)
    
    win.transient(app)
    win.grab_set()
    win.lift()
    win.focus_force()
    try:
        win.attributes("-topmost", True)
        win.after(300, lambda: win.attributes("-topmost", False))
    except:
        pass
    
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (750 // 2)
    y = (win.winfo_screenheight() // 2) - (600 // 2)
    win.geometry(f"750x600+{x}+{y}")
    
    def resetar_config():
        resposta = messagebox.askyesno(
            "Resetar Configurações",
            "Tem certeza que deseja resetar todas as configurações para o padrão?\n\nIsso irá remover todos os nomes, cores e arquivos de áudio configurados."
        )
        if resposta:
            global config, master_volume
            try:
                parar_tudo()
            except Exception:
                pass
            config = default_config()
            try:
                atualizar_volume_master(1.0)
            except Exception:
                master_volume = 1.0
                config["master_volume"] = 1.0
            # limpar cache de imagens da playlist atual
            try:
                base = os.path.join(ICONS_DIR, current_playlist)
                if os.path.isdir(base):
                    for nome in os.listdir(base):
                        p = os.path.join(base, nome)
                        try:
                            if os.path.isfile(p):
                                os.remove(p)
                        except Exception:
                            pass
            except Exception:
                pass
            salvar_config()
            try:
                recriar_botoes()
            except Exception:
                atualizar_estilos()
            for i, (slider, label) in enumerate(volume_sliders):
                try:
                    slider.set(1.0)
                    label.configure(text="100%")
                except Exception:
                    pass
            try:
                volume_master_slider.set(1.0)
                volume_master_label.configure(text="100%")
            except Exception:
                pass
            messagebox.showinfo("✅ Resetado", "Configurações resetadas com sucesso!")
            win.destroy()
    
    header_config = ctk.CTkFrame(win, fg_color="transparent", height=40)
    header_config.pack(fill="x", padx=10, pady=(10, 5))
    
    ctk.CTkLabel(header_config, text="⚙️ Configurações", font=("Arial", 18, "bold")).pack(side="left")
    
    ctk.CTkButton(header_config, text="🔄 Resetar Tudo", fg_color="#dc2626", hover_color="#b91c1c",
                  width=120, height=30, font=("Arial", 11, "bold"),
                  command=resetar_config).pack(side="right")

    canvas = ctk.CTkScrollableFrame(win, width=720, height=420)
    canvas.pack(padx=10, pady=(5, 5), fill="both", expand=True)

    entries = []
    
    atalhos_frame = ctk.CTkFrame(canvas, corner_radius=12, fg_color=("#f3f4f6", "#1e293b"))
    atalhos_frame.pack(pady=8, padx=10, fill="x")
    
    ctk.CTkLabel(atalhos_frame, text="⌨️ Atalhos de Teclado", font=("Arial", 16, "bold")).pack(anchor="w", pady=4, padx=8)
    
    atalhos_var = ctk.BooleanVar(value=config.get("atalhos_habilitados", True))
    atalhos_checkbox = ctk.CTkCheckBox(atalhos_frame, 
                                       text="Habilitar atalhos de teclado (Teclas 0-9)",
                                       variable=atalhos_var,
                                       font=("Arial", 12))
    atalhos_checkbox.pack(anchor="w", padx=10, pady=8)
    tema_frame = ctk.CTkFrame(canvas, corner_radius=12, fg_color=("#f3f4f6", "#1e293b"))
    tema_frame.pack(pady=8, padx=10, fill="x")
    ctk.CTkLabel(tema_frame, text="🎨 Tema", font=("Arial", 16, "bold")).pack(anchor="w", pady=4, padx=8)
    row_tema = ctk.CTkFrame(tema_frame, fg_color="transparent")
    row_tema.pack(fill="x", padx=10, pady=6)
    ctk.CTkLabel(row_tema, text="Aparência:", width=120).pack(side="left")
    appearance_combo = ctk.CTkComboBox(row_tema, values=["light", "dark"], width=140)
    appearance_combo.set(app_prefs.get("appearance_mode", "dark"))
    appearance_combo.pack(side="left", padx=(0, 20))
    
    fade_frame = ctk.CTkFrame(canvas, corner_radius=12, fg_color=("#f3f4f6", "#1e293b"))
    fade_frame.pack(pady=8, padx=10, fill="x")
    ctk.CTkLabel(fade_frame, text="🎵 Áudio (Fade)", font=("Arial", 16, "bold")).pack(anchor="w", pady=4, padx=8)
    fades_row = ctk.CTkFrame(fade_frame, fg_color="transparent")
    fades_row.pack(fill="x", padx=10, pady=6)
    ctk.CTkLabel(fades_row, text="Fade In (ms):", width=120).pack(side="left")
    fade_in_entry = ctk.CTkEntry(fades_row, width=100)
    fade_in_entry.insert(0, str(config.get("fade_in_ms", 800)))
    fade_in_entry.pack(side="left", padx=(0, 20))
    ctk.CTkLabel(fades_row, text="Fade Out (ms):", width=120).pack(side="left")
    fade_out_entry = ctk.CTkEntry(fades_row, width=100)
    fade_out_entry.insert(0, str(config.get("fade_out_ms", 800)))
    fade_out_entry.pack(side="left")

    # Opção de repetição do áudio (logo após Fade)
    repeticao_frame = ctk.CTkFrame(fade_frame, fg_color="transparent")
    repeticao_frame.pack(fill="x", padx=10, pady=(6, 6))
    ctk.CTkLabel(repeticao_frame, text="🔁 Repetição:", width=120).pack(side="left")
    repeticao_var = ctk.BooleanVar(value=config.get("repeticao_habilitada", False))
    repeticao_checkbox = ctk.CTkCheckBox(repeticao_frame, 
                                         text="Habilitar repetição do áudio (loop)",
                                         variable=repeticao_var,
                                         font=("Arial", 12))
    repeticao_checkbox.pack(side="left", padx=8)

    backup_frame = ctk.CTkFrame(canvas, corner_radius=12, fg_color=("#f3f4f6", "#1e293b"))
    backup_frame.pack(pady=8, padx=10, fill="x")
    ctk.CTkLabel(backup_frame, text="💾 Backup", font=("Arial", 16, "bold")).pack(anchor="w", pady=4, padx=8)
    row_backup = ctk.CTkFrame(backup_frame, fg_color="transparent")
    row_backup.pack(fill="x", padx=10, pady=6)
    ctk.CTkButton(row_backup, text="Exportar Backup", fg_color="#2563eb", hover_color="#1d4ed8",
                  command=exportar_backup).pack(side="left", padx=6)
    ctk.CTkButton(row_backup, text="Importar Backup", fg_color="#16a34a", hover_color="#15803d",
                  command=importar_backup).pack(side="left", padx=6)
    ctk.CTkButton(row_backup, text="Abrir Pasta de Dados", fg_color="#374151", hover_color="#1f2937",
                  command=abrir_pasta_dados).pack(side="left", padx=6)

    ctk.CTkLabel(canvas, text="🎚️ Configuração dos Botões", font=("Arial", 16, "bold")).pack(anchor="w", pady=(15, 5), padx=10)
    # Cores globais
    cores_globais_frame = ctk.CTkFrame(canvas, corner_radius=12, fg_color=("#f3f4f6", "#1e293b"))
    cores_globais_frame.pack(pady=8, padx=10, fill="x")
    ctk.CTkLabel(cores_globais_frame, text="🎨 Cores Globais", font=("Arial", 16, "bold")).pack(anchor="w", pady=4, padx=8)
    def aplicar_cor_todos():
        c = colorchooser.askcolor(title="Escolher cor para todos os botões")[1]
        if c:
            for i in range(len(config.get("botoes", []))):
                config["botoes"][i]["cor"] = c
            salvar_config()
            try:
                recriar_botoes()
            except Exception:
                atualizar_estilos()
    ctk.CTkButton(cores_globais_frame, text="Aplicar cor em todos", width=180, command=aplicar_cor_todos).pack(anchor="w", padx=10, pady=6)

    for i, b in enumerate(config["botoes"]):
        frame = ctk.CTkFrame(canvas, corner_radius=12)
        frame.pack(pady=8, padx=10, fill="x")

        ctk.CTkLabel(frame, text=f"🎵 {b['nome']}", font=("Arial", 16, "bold")).pack(anchor="w", pady=4, padx=8)

        nome = ctk.CTkEntry(frame, placeholder_text="Nome do botão (máx. 30 caracteres)")
        nome.insert(0, b["nome"])
        nome.pack(padx=10, pady=5, fill="x")
        
        aviso_label = ctk.CTkLabel(frame, text="", font=("Arial", 10), text_color="#e74c3c")
        aviso_label.pack(padx=10, pady=2, anchor="w")
        
        def validar_caracteres(event, nome_entry=nome, aviso=aviso_label):
            texto = nome_entry.get()
            num_chars = len(texto)
            if num_chars > 30:
                aviso.configure(text=f"⚠️ Limite excedido: {num_chars}/30 caracteres")
            else:
                aviso.configure(text=f"{num_chars}/30 caracteres")
        
        nome.bind("<KeyRelease>", validar_caracteres)
        validar_caracteres(None, nome, aviso_label)

        # emojis removidos

        ctk.CTkLabel(frame, text="Imagem", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
        cor_frame = ctk.CTkFrame(frame, fg_color=b["cor"], width=30, height=30, corner_radius=6)
        cor_label = ctk.CTkLabel(frame, text=b["cor"]) 
        row_img = ctk.CTkFrame(frame, fg_color="transparent")
        row_img.pack(padx=10, pady=5, fill="x")
        cor_frame.pack(in_=row_img, side="left")
        cor_label.pack(in_=row_img, side="left", padx=5)

        def escolher_cor_local(cor_frame=cor_frame, cor_label=cor_label, i=i):
            c = colorchooser.askcolor()[1]
            if c:
                config["botoes"][i]["cor"] = c
                cor_frame.configure(fg_color=c)
                cor_label.configure(text=c)
        ctk.CTkButton(row_img, text="🎨 Cor do Fundo", width=130, command=escolher_cor_local).pack(side="left", padx=8)
        def inserir_img_local(i=i):
            selecionar_imagem_botao(i, win)
        def remover_img_local(i=i):
            remover_imagem_botao(i, win)
        ctk.CTkButton(row_img, text="🖼️ Inserir Imagem", width=150, command=inserir_img_local).pack(side="left", padx=8)
        ctk.CTkButton(row_img, text="🗑️ Remover Imagem", width=150, fg_color="#ef4444", hover_color="#dc2626", command=remover_img_local).pack(side="left", padx=8)
        prev = ctk.CTkLabel(row_img, text="(prévia)")
        prev.pack(side="left", padx=8)
        img_cache = b.get("imagem_cache", "")
        if img_cache and os.path.exists(img_cache):
            try:
                imgp = Image.open(img_cache).resize((80,80), Image.Resampling.LANCZOS)
                prev_img = ctk.CTkImage(light_image=imgp, dark_image=imgp, size=(80,80))
                prev.configure(image=prev_img, text="")
                prev.image = prev_img
            except:
                pass
        def escolher_cor_texto(i=i):
            c = colorchooser.askcolor(title="Cor do texto do botão")[1]
            if c:
                config["botoes"][i]["texto_cor"] = c
        row_text = ctk.CTkFrame(frame, fg_color="transparent")
        row_text.pack(padx=10, pady=(2, 6), fill="x")
        ctk.CTkLabel(row_text, text="Cor do texto", width=120).pack(side="left")
        ctk.CTkButton(row_text, text="🅣 Cor do Texto", width=140, command=escolher_cor_texto).pack(side="left", padx=8)
        def escolher_som_local(i=i):
            f = filedialog.askopenfilename(title="Selecionar som", filetypes=[("Áudio", "*.mp3 *.wav *.ogg")])
            if f:
                if validar_arquivo_audio(f):
                    config["botoes"][i]["arquivo"] = f
                    try:
                        config["botoes"][i]["duracao"] = obter_duracao_musica(f)
                    except:
                        pass
                    salvar_config()
                    messagebox.showinfo("Som", f"Som selecionado para {config['botoes'][i]['nome']}")
        ctk.CTkLabel(frame, text="Áudio", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
        row_audio = ctk.CTkFrame(frame, fg_color="transparent")
        row_audio.pack(padx=10, pady=6, fill="x")
        ctk.CTkButton(row_audio, text="🎵 Escolher Som", width=150, command=escolher_som_local).pack(side="left", padx=0)
        arq = b.get("arquivo", "")
        ctk.CTkLabel(row_audio, text=(os.path.basename(arq) if arq else ""), font=("Arial", 11)).pack(side="left", padx=8)

        entries.append((i, nome))

    def salvar_tudo():
        for i, entry in entries:
            texto = entry.get()
            num_chars = len(texto)
            if num_chars > 30:
                messagebox.showerror("Erro", f"O botão '{config['botoes'][i]['nome']}' excede o limite de 30 caracteres ({num_chars} caracteres).\nPor favor, reduza o texto.")
                return
            config["botoes"][i]["nome"] = texto
        
        try:
            fi = int(fade_in_entry.get())
            fo = int(fade_out_entry.get())
            if fi < 0 or fo < 0:
                raise ValueError
            config["fade_in_ms"] = fi
            config["fade_out_ms"] = fo
        except Exception:
            messagebox.showerror("Erro", "Os valores de Fade In/Out devem ser números inteiros não negativos (em milissegundos).")
            return
        
        config["atalhos_habilitados"] = atalhos_var.get()
        # Salvar opção de repetição
        config["repeticao_habilitada"] = repeticao_var.get()
        app_prefs["appearance_mode"] = appearance_combo.get()
        salvar_prefs()
        aplicar_tema_prefs()
        
        salvar_config()
        atualizar_estilos()
        recriar_botoes()
        messagebox.showinfo("Configurações", "✅ Alterações salvas com sucesso!")
        win.destroy()

    rodape = ctk.CTkFrame(win, fg_color=("#e5e7eb", "#2b2b2b"), height=60)
    rodape.pack(fill="x", side="bottom", pady=0)
    rodape.pack_propagate(False)
    
    btn_frame = ctk.CTkFrame(rodape, fg_color="transparent")
    btn_frame.pack(expand=True)
    
    ctk.CTkButton(btn_frame, text="💾 Salvar", fg_color="#16a34a", hover_color="#15803d",
                  width=120, height=35, font=("Arial", 13, "bold"),
                  command=salvar_tudo).pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="❌ Cancelar", fg_color="#6b7280", hover_color="#4b5563",
                  width=120, height=35, font=("Arial", 13, "bold"),
                  command=win.destroy).pack(side="left", padx=5)

footer = ctk.CTkFrame(app, fg_color="transparent")
footer.pack(pady=15, fill="x", padx=10)

buttons_frame = ctk.CTkFrame(footer, fg_color="transparent")
buttons_frame.pack(side="left")

# Carregar ícones para os botões
icon_stop = carregar_icone("stop.png", (16, 16))
icon_pause = carregar_icone("pause.png", (16, 16))
icon_config = carregar_icone("config.png", (16, 16))

# Botão Parar com ícone
if icon_stop:
    btn_stop = ctk.CTkButton(buttons_frame, text=" Parar", image=icon_stop, 
                           fg_color="#e74c3c", hover_color="#c0392b", 
                           command=parar_tudo)
else:
    btn_stop = ctk.CTkButton(buttons_frame, text="⏹️ Parar", fg_color="#e74c3c", hover_color="#c0392b", 
                           command=parar_tudo)
btn_stop.pack(side="left", padx=5)

# Botão Pausar/Retomar com ícone
if icon_pause:
    btn_pause = ctk.CTkButton(buttons_frame, text=" Pausar/Retomar", image=icon_pause,
                            fg_color="#f39c12", hover_color="#d35400", 
                            command=pausar_retomar)
else:
    btn_pause = ctk.CTkButton(buttons_frame, text="⏯️ Pausar/Retomar", fg_color="#f39c12", hover_color="#d35400", 
                            command=pausar_retomar)
btn_pause.pack(side="left", padx=5)

# Botão Configurar com ícone
if icon_config:
    btn_config = ctk.CTkButton(buttons_frame, text=" Configurar", image=icon_config,
                              fg_color="#2563eb", hover_color="#1d4ed8", 
                              command=abrir_config_janela)
else:
    btn_config = ctk.CTkButton(buttons_frame, text="⚙️ Configurar", fg_color="#2563eb", hover_color="#1d4ed8", 
                              command=abrir_config_janela)
btn_config.pack(side="left", padx=5)

def abrir_controle_remoto():
    abrir_controle_remoto_info()

btn_remote = ctk.CTkButton(buttons_frame, text="🌐 Controle Remoto", fg_color="#10b981", hover_color="#059669",
                           command=abrir_controle_remoto)
btn_remote.pack(side="left", padx=5)

def abrir_pasta_sons():
    try:
        if os.name == 'nt':
            os.startfile(SONS_DIR)
        else:
            webbrowser.open(f"file://{os.path.abspath(SONS_DIR)}")
    except Exception as e:
        _show_error("Erro ao abrir pasta", e)

ctk.CTkButton(buttons_frame, text="Abrir Pasta Sons", fg_color="#374151", hover_color="#1f2937", 
              command=abrir_pasta_sons).pack(side="left", padx=5)

sobre_frame = ctk.CTkFrame(footer, fg_color="transparent")
sobre_frame.pack(side="right")

ctk.CTkButton(sobre_frame, text="ℹ️ Sobre", 
              fg_color="transparent", 
              text_color=("#4b5563", "#9ca3af"),
              hover_color=("#f3f4f6", "#1f2937"),
              border_width=1,
              border_color=("#e5e7eb", "#374151"),
              command=mostrar_sobre).pack(side="right", padx=5)

shortcuts_label = ctk.CTkLabel(footer, text="", font=("Arial", 11), text_color="#9ca3af")
shortcuts_label.pack(side="right", padx=20)

remote_label = ctk.CTkLabel(footer, text="Controle Remoto: desligado", font=("Arial", 11), text_color="#9ca3af")
remote_label.pack(side="right", padx=10)
remote_led = ctk.CTkLabel(footer, text="●", font=("Arial", 12), text_color="#ef4444")
remote_led.pack(side="right")

def abrir_controle_remoto_info():
    win = ctk.CTkToplevel(app)
    win.title("Controle Remoto")
    win.geometry("520x560")
    win.resizable(False, False)
    win.transient(app)
    win.grab_set()
    win.lift()
    win.focus_force()
    try:
        win.attributes("-topmost", True)
        win.after(300, lambda: win.attributes("-topmost", False))
    except:
        pass
    url = server.get_url()
    top = ctk.CTkFrame(win, fg_color="transparent")
    top.pack(expand=True, fill="both", padx=20, pady=20)
    ctk.CTkLabel(top, text="Acesse pelo celular", font=("Arial", 18, "bold")).pack(pady=(0,10))
    url_label = ctk.CTkLabel(top, text=url, font=("Arial", 14))
    url_label.pack(pady=6)
    pin_label = ctk.CTkLabel(top, text=f"PIN: {server.get_pin()}", font=("Arial", 14, "bold"))
    pin_label.pack(pady=6)

    status_row = ctk.CTkFrame(top, fg_color="transparent")
    status_row.pack(pady=6)
    status_text = ctk.CTkLabel(status_row, text="", font=("Arial", 12))
    status_text.pack(side="left", padx=6)
    status_led = ctk.CTkLabel(status_row, text="●", font=("Arial", 12))
    status_led.pack(side="left")
    conn_label = ctk.CTkLabel(status_row, text="Conectados: 0", font=("Arial", 12))
    conn_label.pack(side="left", padx=6)
    row = ctk.CTkFrame(top, fg_color="transparent")
    row.pack(pady=8)
    ctk.CTkButton(row, text="Abrir no Navegador", fg_color="#2563eb", hover_color="#1d4ed8",
                  command=lambda: webbrowser.open(url)).pack(side="left", padx=4)
    ctk.CTkButton(row, text="Copiar URL", fg_color="#374151", hover_color="#1f2937",
                  command=lambda: (app.clipboard_clear(), app.clipboard_append(url))).pack(side="left", padx=4)
    def regenerar():
        server.regenerate_pin()
        pin_label.configure(text=f"PIN: {server.get_pin()}")
        if remote_label:
            remote_label.configure(text=f"Controle Remoto: {server.get_url()}  PIN: {server.get_pin()}")
        render_qr()
    ctk.CTkButton(row, text="Trocar PIN", fg_color="#f59e0b", hover_color="#d97706",
                  command=regenerar).pack(side="left", padx=4)
    ctrl_row = ctk.CTkFrame(top, fg_color="transparent")
    ctrl_row.pack(pady=8)

    def ligar_servidor():
        server.start()
        pin_label.configure(text=f"PIN: {server.get_pin()}")
        url_label.configure(text=server.get_url())
        atualizar_status_servidor(True)
        atualizar_status_local(True)
        conn_label.configure(text=f"Conectados: {server.get_connections_count()} \u200b")

    def desligar_servidor():
        server.stop()
        atualizar_status_servidor(False)
        atualizar_status_local(False)
        conn_label.configure(text="Conectados: 0")

    ctk.CTkButton(ctrl_row, text="Ligar Servidor", fg_color="#10b981", hover_color="#059669",
                  command=ligar_servidor).pack(side="left", padx=4)
    ctk.CTkButton(ctrl_row, text="Desligar Servidor", fg_color="#ef4444", hover_color="#dc2626",
                  command=desligar_servidor).pack(side="left", padx=4)
    qr_frame = ctk.CTkFrame(top)
    qr_frame.pack(pady=8)
    qr_label = ctk.CTkLabel(qr_frame, text="")
    qr_label.pack()
    def render_qr():
        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        img = img.resize((200, 200), Image.Resampling.LANCZOS)
        qr_img = ctk.CTkImage(light_image=img, dark_image=img, size=(200,200))
        qr_label.configure(image=qr_img)
        qr_label.image = qr_img
    render_qr()
    
    def atualizar_status_local(ligado):
        status_text.configure(text=("Servidor ligado" if ligado else "Servidor desligado"))
        try:
            status_led.configure(text_color=("#10b981" if ligado else "#ef4444"))
        except Exception:
            pass
    
    def monitor():
        try:
            atualizar_status_local(server.is_running())
            conn_label.configure(text=f"Conectados: {server.get_connections_count()} \u200b")
        finally:
            win.after(1500, monitor)
    atualizar_status_local(server.is_running())
    monitor()
    win.update_idletasks()
    w = win.winfo_width()
    h = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (w // 2)
    y = (win.winfo_screenheight() // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

def regenerar_pin():
    server.regenerate_pin()
    atualizar_status_servidor(server.is_running())

def atualizar_status_servidor(ligado):
    if remote_label:
        if ligado:
            remote_label.configure(text=f"Controle Remoto: {server.get_url()}  PIN: {server.get_pin()}")
        else:
            remote_label.configure(text=f"Controle Remoto: desligado")
    try:
        remote_led.configure(text_color="#10b981" if ligado else "#ef4444")
    except Exception:
        pass

def _monitorizar_servidor_footer():
    try:
        atualizar_status_servidor(server.is_running())
    finally:
        app.after(2000, _monitorizar_servidor_footer)

def atualizar_texto_atalhos():
    if config.get("atalhos_habilitados", True):
        shortcuts_label.configure(text="⌨️ Atalhos: Teclas 1-0 para reproduzir os botões")
    else:
        shortcuts_label.configure(text="⌨️ Atalhos: Desabilitados", text_color="#6b7280")

def on_key(event):
    if not config.get("atalhos_habilitados", True):
        return
    if event.char.isdigit():
        tecla = int(event.char)
        # Mapear teclas 1-0 para botões 0-9
        if tecla == 0:
            index = 9  # Tecla 0 = Botão 10
        else:
            index = tecla - 1  # Tecla 1 = Botão 1, Tecla 2 = Botão 2, etc.
        
        if index < len(button_refs):
            tocar_som(index)
    elif event.keysym == 'space':
        parar_tudo()
    elif event.char.lower() == 'r':
        reiniciar_musica()

app.bind("<Key>", on_key)

app.protocol("WM_DELETE_WINDOW", lambda: (pygame.mixer.music.stop(), app.destroy()))
atualizar_estilos()
atualizar_texto_atalhos()
def _start_remote():
    _monitorizar_servidor_footer()
app.after(2000, mostrar_whatsapp_popup_se_preciso)
app.mainloop()
