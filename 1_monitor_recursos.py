"""
=============================================================
  SCRIPT 1: Monitor de Recursos en Tiempo Real
=============================================================
  Concepto : Panel de control del Sistema Operativo
  Interfaz : TUI con colores ANSI, barras animadas y alertas
  Log      : alertas_ram.txt  (cuando RAM > 80%)
  Salida   : Ctrl+C
=============================================================
  Dependencia: pip install psutil
=============================================================
"""

import psutil, time, os, datetime, sys

# ── Habilitar colores ANSI en Windows ──────────────────────
if os.name == "nt":
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

# ── Paleta ANSI ────────────────────────────────────────────
R  = "\033[0m"          # reset
B  = "\033[1m"          # bold
DIM= "\033[2m"          # dim

# Fondos de color para el encabezado
BG_AZUL   = "\033[44m"
BG_NEGRO  = "\033[40m"

# Colores de texto
CIAN      = "\033[96m"
VERDE     = "\033[92m"
AMARILLO  = "\033[93m"
NARANJA   = "\033[38;5;208m"
ROJO      = "\033[91m"
BLANCO    = "\033[97m"
GRIS      = "\033[90m"
AZUL      = "\033[94m"
MAGENTA   = "\033[95m"

LOG_FILE           = "alertas_ram.txt"
UMBRAL_RAM_ALERTA  = 80
UMBRAL_CPU_ALERTA  = 90
INTERVALO          = 1

# ── Helpers visuales ───────────────────────────────────────

def color_pct(p):
    if p >= 90: return ROJO
    if p >= 80: return NARANJA
    if p >= 60: return AMARILLO
    return VERDE

def barra(p, w=32):
    lleno = int(w * p / 100)
    c = color_pct(p)
    return c + "█" * lleno + GRIS + "░" * (w - lleno) + R

def etiqueta_nivel(p):
    if p >= 90: return f"{ROJO}{B}● CRÍTICO {R}"
    if p >= 80: return f"{NARANJA}{B}● ALERTA  {R}"
    if p >= 60: return f"{AMARILLO}{B}● MODERADO{R}"
    return f"{VERDE}{B}● NORMAL  {R}"

def linea(char="─", w=62, color=GRIS):
    return color + char * w + R

def cls():
    os.system("cls" if os.name == "nt" else "clear")

def escribir_log(ram_pct, cpu_pct, ram_info, alertas):
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ru = ram_info.used  / 1024**3
    rt = ram_info.total / 1024**3
    linea_log = (f"[{ahora}] RAM {ram_pct:.1f}% "
                 f"({ru:.2f}/{rt:.2f} GB) | CPU {cpu_pct:.1f}% "
                 f"| Alerta #{alertas}\n")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linea_log)

# ── Panel ──────────────────────────────────────────────────

def panel():
    alertas = 0
    ciclo   = 0
    W       = 62   # ancho total

    print(f"\n{CIAN}  Iniciando monitor… (Ctrl+C para salir){R}\n")
    time.sleep(0.8)

    try:
        while True:
            ciclo += 1
            cpu   = psutil.cpu_percent(interval=INTERVALO)
            ram   = psutil.virtual_memory()
            disco = psutil.disk_usage("/")
            freq  = psutil.cpu_freq()
            swap  = psutil.swap_memory()
            nproc = len(list(psutil.process_iter()))
            ahora = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

            ram_pct  = ram.percent
            cpu_pct  = cpu
            disk_pct = disco.percent

            cls()

            # ── Encabezado ──────────────────────────────────
            print(f"{BG_AZUL}{BLANCO}{B}{'':2}🖥️  MONITOR DE RECURSOS DEL SISTEMA OPERATIVO{'':7}{R}")
            print(f"{BG_NEGRO}{GRIS}  {ahora}{'':4}{CIAN}ciclo #{ciclo}{'':4}{GRIS}procesos: {BLANCO}{nproc}{R}")
            print(linea("═", W))

            # ── CPU ─────────────────────────────────────────
            frec_str = f"{freq.current:.0f} MHz" if freq else "N/A"
            cores    = psutil.cpu_count(logical=True)
            print(f"\n  {AZUL}{B}CPU{R}  {barra(cpu_pct)}  "
                  f"{color_pct(cpu_pct)}{B}{cpu_pct:5.1f}%{R}  {etiqueta_nivel(cpu_pct)}")
            print(f"  {GRIS}Núcleos lógicos: {BLANCO}{cores}{GRIS}   "
                  f"Frecuencia: {BLANCO}{frec_str}{R}")

            # ── RAM ─────────────────────────────────────────
            ru = ram.used      / 1024**3
            ra = ram.available / 1024**3
            rt = ram.total     / 1024**3
            print(f"\n  {MAGENTA}{B}RAM{R}  {barra(ram_pct)}  "
                  f"{color_pct(ram_pct)}{B}{ram_pct:5.1f}%{R}  {etiqueta_nivel(ram_pct)}")
            print(f"  {GRIS}Usada: {BLANCO}{ru:.2f} GB{GRIS}  "
                  f"Disp: {BLANCO}{ra:.2f} GB{GRIS}  "
                  f"Total: {BLANCO}{rt:.2f} GB{R}")

            # ── SWAP ────────────────────────────────────────
            if swap.total > 0:
                su = swap.used  / 1024**3
                st = swap.total / 1024**3
                print(f"\n  {CIAN}{B}SWP{R}  {barra(swap.percent)}  "
                      f"{color_pct(swap.percent)}{B}{swap.percent:5.1f}%{R}  {etiqueta_nivel(swap.percent)}")
                print(f"  {GRIS}Usada: {BLANCO}{su:.2f} GB{GRIS}  "
                      f"Total: {BLANCO}{st:.2f} GB{R}")

            # ── DISCO ────────────────────────────────────────
            df = disco.free  / 1024**3
            dt = disco.total / 1024**3
            print(f"\n  {AMARILLO}{B}DSK{R}  {barra(disk_pct)}  "
                  f"{color_pct(disk_pct)}{B}{disk_pct:5.1f}%{R}  {etiqueta_nivel(disk_pct)}")
            print(f"  {GRIS}Libre: {BLANCO}{df:.1f} GB{GRIS}  "
                  f"Total: {BLANCO}{dt:.1f} GB{R}")

            # ── Separador y pie ─────────────────────────────
            print(f"\n{linea('─', W)}")
            print(f"  {GRIS}Log alertas RAM: {BLANCO}{LOG_FILE}{GRIS}  "
                  f"│  Alertas sesión: {ROJO if alertas else VERDE}{B}{alertas}{R}")

            # ── Alerta RAM ────────────────────────────────────
            if ram_pct > UMBRAL_RAM_ALERTA:
                alertas += 1
                escribir_log(ram_pct, cpu_pct, ram, alertas)
                print(f"\n  {ROJO}{B}⚠  RAM al {ram_pct:.1f}% — registro #{alertas} guardado en {LOG_FILE}{R}")

            # ── Alerta CPU ────────────────────────────────────
            if cpu_pct > UMBRAL_CPU_ALERTA:
                print(f"  {ROJO}{B}⚠  CPU al {cpu_pct:.1f}% — consumo crítico{R}")

            print(f"\n{linea('═', W)}")
            print(f"  {GRIS}Actualización cada {INTERVALO}s  ·  {B}Ctrl+C{R}{GRIS} para detener{R}")

    except KeyboardInterrupt:
        print(f"\n\n  {VERDE}Monitor detenido.  "
              f"Alertas RAM registradas: {B}{alertas}{R}{VERDE}  →  {LOG_FILE}{R}\n")

if __name__ == "__main__":
    panel()
