import json
import time
import logging
import os
import sys
from datetime import datetime

import psutil
import requests

# --- Windows APIs ---
import win32gui
import win32process

# --- Selenium attach ao Chrome com DevTools ---
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import WebDriverException

# ------------- Util -------------
def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def now_iso():
    return datetime.utcnow().isoformat() + "Z"

# ------------- Janela ativa -------------
def get_active_window_info():
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return None, None, None
    title = win32gui.GetWindowText(hwnd)
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid)
        pname = proc.name()
    except Exception:
        pname = None
        pid = None
    return hwnd, pname, title

# ------------- Selenium/CDP -------------
class ChromeAttach:
    def __init__(self, debug_addr):
        self.debug_addr = debug_addr
        self.driver = None

    def connect(self):
        if self.driver:
            return
        opts = ChromeOptions()
        # Conecta em uma instância existente do Chrome com DevTools
        opts.debugger_address = self.debug_addr
        try:
            self.driver = webdriver.Chrome(options=opts)
        except WebDriverException as e:
            raise RuntimeError(f"Falha ao anexar ao Chrome: {e}")

    def get_tabs(self):
        if not self.driver:
            return []
        return self.driver.window_handles

    def get_tab_title(self):
        if not self.driver:
            return None
        try:
            return self.driver.title or ""
        except Exception:
            return ""

    def get_tab_url(self):
        if not self.driver:
            return None
        try:
            return self.driver.current_url or ""
        except Exception:
            return ""

    def switch_to(self, handle):
        self.driver.switch_to.window(handle)

# ------------- Lógica principal -------------
def url_is_allowed(url, allowed_prefixes):
    if not url:
        return False
    url_lower = url.lower()
    for p in allowed_prefixes:
        if url_lower.startswith(p.lower()):
            return True
    return False

def title_is_allowed(title, browsers_allowed_markers):
    if not title:
        return False
    # Estratégia simples: permitir quando o título aparenta ser da plataforma (fallback)
    return any(marker.lower() in title.lower() for marker in browsers_allowed_markers)

def send_alert(server_url, student_id, reason, extra=None):
    payload = {
        "student_id": student_id,
        "timestamp": now_iso(),
        "reason": reason,
        "extra": extra or {}
    }
    try:
        resp = requests.post(server_url, json=payload, timeout=5)
        logging.info(f"Alerta enviado: {payload} | resp={resp.status_code}")
    except Exception as e:
        logging.error(f"Falha ao enviar alerta: {e}")

def main():
    cfg = load_config()
    setup_logging(cfg.get("log_file", "monitor.log"))

    student_id = cfg["student_id"]
    allowed_domains = cfg["exam_domains"]
    poll = float(cfg.get("poll_interval_sec", 1.0))
    server_url = cfg["server_url"]
    browsers_allowed = [x.lower() for x in cfg.get("browsers_allowed", ["chrome.exe", "msedge.exe"])]
    chrome_debug_addr = cfg.get("chrome_debug_address", "127.0.0.1:9222")

    # Para fallback por título (quando não der pra pegar URL real),
    # considere adicionar um marcador do domínio no título (se aplicável).
    title_markers = [u.replace("https://", "").replace("http://", "").split("/")[0] for u in allowed_domains]

    # Tenta conectar ao Chrome (URL real)
    chrome = ChromeAttach(chrome_debug_addr)
    cdp_ok = True
    try:
        chrome.connect()
        logging.info(f"Conectado ao Chrome em {chrome_debug_addr}")
    except Exception as e:
        logging.warning(f"CDP indisponível, usando fallback por título. Detalhe: {e}")
        cdp_ok = False

    last_state_ok = None  # pra evitar alertar em loop quando estado não muda

    while True:
        _, proc_name, active_title = get_active_window_info()
        proc_name = (proc_name or "").lower()

        # Está em um navegador permitido?
        in_browser = proc_name in browsers_allowed

        state_ok = False
        current_url = None

        if in_browser and cdp_ok:
            # Tente achar a aba do Chrome que corresponde ao título ativo
            matched = False
            try:
                handles = chrome.get_tabs()
                for h in handles:
                    try:
                        chrome.switch_to(h)
                        t = chrome.get_tab_title()
                        # Se o título da janela ativa bate com o da aba, assumimos que é a aba focada
                        if t and active_title and t.strip() == active_title.strip():
                            current_url = chrome.get_tab_url()
                            matched = True
                            break
                    except Exception:
                        continue
            except Exception as e:
                logging.warning(f"Erro ao iterar abas: {e}")
                matched = False

            if matched:
                state_ok = url_is_allowed(current_url, allowed_domains)
            else:
                # Se não achou a aba pelo título, último recurso: checa URL da aba atual do driver
                try:
                    current_url = chrome.get_tab_url()
                    state_ok = url_is_allowed(current_url, allowed_domains)
                except Exception:
                    state_ok = False

        else:
            # Fallback: não deu pra usar CDP/URL real, valida por título
            # (menos seguro, mas melhor que nada)
            if in_browser:
                state_ok = any(marker in (active_title or "").lower() for marker in [m.lower() for m in title_markers])
            else:
                state_ok = False

        # Dispara alerta se saiu do permitido
        if state_ok is False and last_state_ok is not False:
            reason = "left_exam_context"
            extra = {
                "proc": proc_name,
                "active_title": active_title,
                "url": current_url
            }
            logging.warning(f"[VIOLAÇÃO] Saiu da aba/sistema: {extra}")
            send_alert(server_url, student_id, reason, extra)

        last_state_ok = state_ok
        time.sleep(poll)

if __name__ == "__main__":
    main()
