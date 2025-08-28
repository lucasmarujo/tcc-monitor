import psutil
import win32api
import win32gui
import win32process
import json
import re
import os
from datetime import datetime
from typing import List, Dict, Tuple


class ExamSecurityVerifier:
    def __init__(self):
        # Lista de aplicativos de IA e ferramentas problemáticas para exames
        self.suspicious_processes = {
            # Assistentes de IA
            "chatgpt", "claude", "bard", "copilot", "cortana", "siri",
            "alexa", "google assistant", "openai", "anthropic",
            
            # Editores com IA
            "cursor", "github copilot", "tabnine", "codeium", "codey",
            "vscode", "visual studio", "intellij", "pycharm", "webstorm",
            
            # Ferramentas de tradução e pesquisa
            "google translate", "deepl", "translator", "linguee",
            "grammarly", "quillbot", "paraphraser",
            
            # Navegadores (podem acessar IA online)
            "chrome", "firefox", "edge", "safari", "opera", "brave",
            
            # Ferramentas de comunicação
            "teams", "zoom", "skype", "discord", "slack", "whatsapp",
            "telegram", "messenger", "signal",
            
            # Ferramentas de screenshot/gravação
            "snipping tool", "lightshot", "greenshot", "obs", "bandicam",
            "camtasia", "screenpresso", "sharex",
            
            # Ferramentas de acesso remoto
            "teamviewer", "anydesk", "remote desktop", "vnc", "parsec",
            "chrome remote desktop", "logmein", "splashtop",
            
            # Calculadoras avançadas
            "wolfram", "mathematica", "matlab", "octave", "geogebra",
            "desmos", "symbolab",
            
            # Desenvolvimento/IDEs
            "android studio", "xcode", "eclipse", "netbeans", "atom",
            "sublime text", "notepad++", "vim", "emacs"
        }
        
        # Serviços suspeitos
        self.suspicious_services = {
            "cortana", "search", "windows search", "indexing service",
            "teamviewer", "anydesk", "chrome remote desktop",
            "nvidia geforce experience", "amd software",
            "steam", "origin", "epic games", "battle.net",
            "dropbox", "onedrive", "google drive", "icloud"
        }
        
        # Extensões de arquivos problemáticas
        self.suspicious_files = {
            ".exe", ".msi", ".bat", ".cmd", ".ps1", ".vbs", ".js"
        }

    def detect_secondary_screens(self) -> Dict:
        """
        Detecta telas secundárias no sistema usando múltiplas abordagens
        """
        try:
            monitors = []
            method_used = "unknown"
            
            # Método 1: Usar Win32 API para enumerar displays
            try:
                import win32con
                
                # Enumerar todos os dispositivos de display
                device_index = 0
                while True:
                    try:
                        device = win32api.EnumDisplayDevices(None, device_index)
                        if device:
                            # Obter informações do monitor
                            try:
                                settings = win32api.EnumDisplaySettings(device.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
                                if settings:
                                    monitors.append({
                                        "device_name": device.DeviceName,
                                        "device_string": device.DeviceString,
                                        "left": settings.Position_x,
                                        "top": settings.Position_y,
                                        "width": settings.PelsWidth,
                                        "height": settings.PelsHeight,
                                        "bits_per_pixel": settings.BitsPerPel,
                                        "frequency": settings.DisplayFrequency,
                                        "is_primary": settings.Position_x == 0 and settings.Position_y == 0
                                    })
                            except:
                                # Se não conseguir obter settings, adiciona informação básica
                                monitors.append({
                                    "device_name": device.DeviceName,
                                    "device_string": device.DeviceString,
                                    "info": "Active display device detected"
                                })
                        else:
                            break
                        device_index += 1
                    except:
                        break
                
                method_used = "Win32API EnumDisplayDevices"
                
            except ImportError:
                pass
            
            # Método 2: Usar métricas do sistema se o método 1 falhou
            if not monitors:
                try:
                    # Obter informações do desktop virtual
                    virtual_screen_x = win32api.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
                    virtual_screen_y = win32api.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
                    virtual_screen_width = win32api.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
                    virtual_screen_height = win32api.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
                    
                    primary_width = win32api.GetSystemMetrics(0)  # SM_CXSCREEN
                    primary_height = win32api.GetSystemMetrics(1)  # SM_CYSCREEN
                    
                    # Se a tela virtual é maior que a primária, há monitores secundários
                    has_multiple = (virtual_screen_width > primary_width or 
                                  virtual_screen_height > primary_height or
                                  virtual_screen_x != 0 or virtual_screen_y != 0)
                    
                    monitors.append({
                        "type": "primary",
                        "width": primary_width,
                        "height": primary_height,
                        "left": 0,
                        "top": 0
                    })
                    
                    if has_multiple:
                        monitors.append({
                            "type": "virtual_screen_info",
                            "virtual_left": virtual_screen_x,
                            "virtual_top": virtual_screen_y,
                            "virtual_width": virtual_screen_width,
                            "virtual_height": virtual_screen_height,
                            "indicates_multiple_monitors": True
                        })
                    
                    method_used = "Win32API System Metrics"
                    
                except Exception as e:
                    return {
                        "error": f"Erro ao usar métricas do sistema: {str(e)}",
                        "total_monitors": 0,
                        "has_secondary_screens": False
                    }
            
            # Método 3: Fallback usando tkinter se disponível
            if not monitors:
                try:
                    import tkinter as tk
                    root = tk.Tk()
                    
                    screen_width = root.winfo_screenwidth()
                    screen_height = root.winfo_screenheight()
                    
                    monitors.append({
                        "type": "tkinter_screen",
                        "width": screen_width,
                        "height": screen_height,
                        "method": "tkinter fallback"
                    })
                    
                    root.destroy()
                    method_used = "Tkinter fallback"
                    
                except Exception:
                    pass
            
            # Determinar se há telas secundárias
            has_secondary = False
            total_monitors = 0
            
            if method_used == "Win32API EnumDisplayDevices":
                # Contar dispositivos ativos (não incluindo dispositivos desconectados)
                active_monitors = [m for m in monitors if m.get("width", 0) > 0]
                total_monitors = len(active_monitors)
                has_secondary = total_monitors > 1
                
            elif method_used == "Win32API System Metrics":
                # Verificar se há indicação de múltiplos monitores
                has_secondary = any(m.get("indicates_multiple_monitors", False) for m in monitors)
                total_monitors = 2 if has_secondary else 1
                
            else:
                total_monitors = len(monitors)
                has_secondary = False  # Método fallback não detecta múltiplos monitores
            
            primary_monitor = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
            
            result = {
                "total_monitors": total_monitors,
                "has_secondary_screens": has_secondary,
                "primary_resolution": f"{primary_monitor[0]}x{primary_monitor[1]}",
                "all_monitors": monitors,
                "detection_method": method_used,
                "warning": "TELAS MÚLTIPLAS DETECTADAS!" if has_secondary else "Apenas uma tela detectada",
                "virtual_screen_info": {
                    "x": win32api.GetSystemMetrics(76),
                    "y": win32api.GetSystemMetrics(77), 
                    "width": win32api.GetSystemMetrics(78),
                    "height": win32api.GetSystemMetrics(79)
                }
            }
            
            return result
            
        except Exception as e:
            # Último recurso: tentar detectar pelo menos informações básicas
            try:
                primary_width = win32api.GetSystemMetrics(0)
                primary_height = win32api.GetSystemMetrics(1)
                virtual_width = win32api.GetSystemMetrics(78)
                virtual_height = win32api.GetSystemMetrics(79)
                
                has_multiple = virtual_width > primary_width or virtual_height > primary_height
                
                return {
                    "error": f"Erro na detecção avançada: {str(e)}",
                    "total_monitors": 2 if has_multiple else 1,
                    "has_secondary_screens": has_multiple,
                    "primary_resolution": f"{primary_width}x{primary_height}",
                    "virtual_resolution": f"{virtual_width}x{virtual_height}",
                    "method": "basic_fallback",
                    "warning": "POSSÍVEL TELA MÚLTIPLA DETECTADA!" if has_multiple else "Uma tela detectada"
                }
            except:
                return {
                    "error": f"Erro completo ao detectar telas: {str(e)}",
                    "total_monitors": 0,
                    "has_secondary_screens": False
                }

    def get_running_processes(self) -> List[Dict]:
        """
        Obtém todos os processos em execução
        """
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'memory_info']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'exe': pinfo['exe'],
                    'cmdline': ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else '',
                    'memory_mb': round(pinfo['memory_info'].rss / 1024 / 1024, 2)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        return processes

    def get_running_services(self) -> List[Dict]:
        """
        Obtém todos os serviços em execução
        """
        services = []
        for service in psutil.win_service_iter():
            try:
                service_info = service.as_dict()
                if service_info['status'] == 'running':
                    services.append({
                        'name': service_info['name'],
                        'display_name': service_info['display_name'],
                        'status': service_info['status'],
                        'start_type': service_info['start_type']
                    })
            except Exception:
                pass
        
        return services

    def check_suspicious_processes(self, processes: List[Dict]) -> List[Dict]:
        """
        Verifica processos suspeitos
        """
        suspicious = []
        
        for process in processes:
            process_name = process['name'].lower()
            process_exe = (process['exe'] or '').lower()
            process_cmdline = process['cmdline'].lower()
            
            for suspicious_name in self.suspicious_processes:
                if (suspicious_name in process_name or 
                    suspicious_name in process_exe or 
                    suspicious_name in process_cmdline):
                    
                    suspicious.append({
                        **process,
                        'reason': f'Processo suspeito detectado: {suspicious_name}',
                        'risk_level': self._get_risk_level(suspicious_name)
                    })
                    break
        
        return suspicious

    def check_suspicious_services(self, services: List[Dict]) -> List[Dict]:
        """
        Verifica serviços suspeitos
        """
        suspicious = []
        
        for service in services:
            service_name = service['name'].lower()
            display_name = service['display_name'].lower()
            
            for suspicious_name in self.suspicious_services:
                if suspicious_name in service_name or suspicious_name in display_name:
                    suspicious.append({
                        **service,
                        'reason': f'Serviço suspeito: {suspicious_name}',
                        'risk_level': self._get_risk_level(suspicious_name)
                    })
                    break
        
        return suspicious

    def _get_risk_level(self, name: str) -> str:
        """
        Determina o nível de risco baseado no nome do processo/serviço
        """
        high_risk = ["teamviewer", "anydesk", "remote", "chatgpt", "claude", "copilot"]
        medium_risk = ["chrome", "firefox", "teams", "discord", "obs"]
        
        name_lower = name.lower()
        
        if any(hr in name_lower for hr in high_risk):
            return "ALTO"
        elif any(mr in name_lower for mr in medium_risk):
            return "MÉDIO"
        else:
            return "BAIXO"

    def check_ai_applications(self) -> List[Dict]:
        """
        Verifica especificamente por aplicativos de IA
        """
        ai_apps = []
        
        # Verificar processos em execução
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                pinfo = proc.info
                name = pinfo['name'].lower()
                exe = (pinfo['exe'] or '').lower()
                
                ai_keywords = [
                    "chatgpt", "claude", "copilot", "tabnine", "codeium",
                    "openai", "anthropic", "bard", "gemini"
                ]
                
                for keyword in ai_keywords:
                    if keyword in name or keyword in exe:
                        ai_apps.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'exe': pinfo['exe'],
                            'type': 'Aplicativo de IA',
                            'risk_level': 'ALTO'
                        })
                        break
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return ai_apps

    def generate_report(self) -> Dict:
        """
        Gera relatório completo de verificação
        """
        print("🔍 Iniciando verificação de segurança para exame...")
        
        # Detectar telas secundárias
        print("📺 Verificando telas secundárias...")
        screen_info = self.detect_secondary_screens()
        
        # Obter processos e serviços
        print("⚙️  Analisando processos em execução...")
        processes = self.get_running_processes()
        services = self.get_running_services()
        
        # Verificar itens suspeitos
        print("🚨 Verificando aplicativos suspeitos...")
        suspicious_processes = self.check_suspicious_processes(processes)
        suspicious_services = self.check_suspicious_services(services)
        ai_apps = self.check_ai_applications()
        
        # Calcular scores de risco
        total_processes = len(processes)
        total_suspicious = len(suspicious_processes) + len(suspicious_services) + len(ai_apps)
        risk_score = min(100, (total_suspicious / max(1, total_processes)) * 100)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "total_processes": total_processes,
                "total_services": len(services)
            },
            "screen_verification": screen_info,
            "security_analysis": {
                "suspicious_processes": suspicious_processes,
                "suspicious_services": suspicious_services,
                "ai_applications": ai_apps,
                "total_suspicious_items": total_suspicious,
                "risk_score": round(risk_score, 2)
            },
            "recommendations": self._generate_recommendations(screen_info, total_suspicious)
        }
        
        return report

    def _generate_recommendations(self, screen_info: Dict, suspicious_count: int) -> List[str]:
        """
        Gera recomendações baseadas na análise
        """
        recommendations = []
        
        if screen_info.get("has_secondary_screens", False):
            recommendations.append("❌ CRÍTICO: Desconecte todas as telas secundárias antes do exame")
        
        if suspicious_count > 0:
            recommendations.append(f"⚠️  Feche {suspicious_count} aplicativos/serviços suspeitos identificados")
        
        if suspicious_count > 5:
            recommendations.append("🔴 ALTO RISCO: Muitos aplicativos suspeitos detectados - reinicie o sistema")
        
        recommendations.extend([
            "✅ Feche todos os navegadores web",
            "✅ Desabilite conexões de rede desnecessárias", 
            "✅ Feche aplicativos de comunicação (Teams, Discord, etc.)",
            "✅ Desabilite assistentes de IA (Copilot, Cortana, etc.)"
        ])
        
        return recommendations

    def save_report(self, report: Dict, filename: str = None):
        """
        Salva o relatório em arquivo JSON
        """
        if not filename:
            logs_path = os.path.join(os.path.dirname(__file__), "logs")
            if not os.path.exists(logs_path):
                os.makedirs(logs_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(logs_path, f"exam_security_report_{timestamp}.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Relatório salvo em: {filename}")
        return filename


def main():
    """
    Função principal
    """
    print("=" * 60)
    print("🎓 VERIFICADOR DE SEGURANÇA PARA EXAMES SUPERVISIONADOS")
    print("=" * 60)
    
    verifier = ExamSecurityVerifier()
    
    try:
        # Gerar relatório completo
        report = verifier.generate_report()
        
        # Exibir resumo
        print("\n" + "=" * 40)
        print("📊 RESUMO DA VERIFICAÇÃO")
        print("=" * 40)
        
        screen_info = report["screen_verification"]
        security_info = report["security_analysis"]
        
        print(f"🖥️  Telas detectadas: {screen_info['total_monitors']}")
        print(f"⚠️  Tela secundária: {'SIM - CRÍTICO!' if screen_info['has_secondary_screens'] else 'Não'}")
        print(f"🔍 Processos suspeitos: {len(security_info['suspicious_processes'])}")
        print(f"⚙️  Serviços suspeitos: {len(security_info['suspicious_services'])}")
        print(f"🤖 Apps de IA: {len(security_info['ai_applications'])}")
        print(f"📈 Score de risco: {security_info['risk_score']}%")
        
        # Mostrar itens críticos
        if security_info['suspicious_processes']:
            print("\n🚨 PROCESSOS SUSPEITOS DETECTADOS:")
            for proc in security_info['suspicious_processes'][:5]:  # Mostrar apenas os 5 primeiros
                print(f"  • {proc['name']} (PID: {proc['pid']}) - {proc['risk_level']}")
        
        if security_info['ai_applications']:
            print("\n🤖 APLICATIVOS DE IA DETECTADOS:")
            for app in security_info['ai_applications']:
                print(f"  • {app['name']} (PID: {app['pid']})")
        
        print("\n" + "=" * 40)
        print("💡 RECOMENDAÇÕES")
        print("=" * 40)
        for rec in report["recommendations"]:
            print(f"  {rec}")
        
        # Salvar relatório
        filename = verifier.save_report(report)
        
        # Status final
        print("\n" + "=" * 40)
        if screen_info['has_secondary_screens']:
            print("🔴 STATUS: NÃO APROVADO PARA EXAME - Telas múltiplas detectadas")
        elif security_info['risk_score'] > 30:
            print("🟡 STATUS: RISCO ALTO - Revise aplicativos suspeitos")
        elif security_info['total_suspicious_items'] > 0:
            print("🟠 STATUS: RISCO MÉDIO - Alguns itens suspeitos detectados")
        else:
            print("🟢 STATUS: APROVADO - Sistema seguro para exame")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erro durante a verificação: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
