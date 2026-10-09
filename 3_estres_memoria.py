"""
=============================================================
  SCRIPT 3: Estrés de Memoria y Paginación
=============================================================
  Concepto : Memoria Virtual y Archivo de Paginación (swap)
  Interfaz : TUI con panel de barras animadas y colores ANSI
  Seguridad: Se detiene al 88% RAM o 4 GB asignados
=============================================================
  Dependencia: pip install psutil
=============================================================
"""

import psutil, time, os, gc, sys

# ── Habilitar colores ANSI en Windows ──────────────────────
if os.name == "nt":
    import ctypes
    ctypes.windll.kernel32.SetConsoleMode(
        ctypes.windll.kernel32.GetStdHandle(-11), 7)

# ── Paleta ─────────────────────────────────────────────────
R="\033[0m"; B="\033[1m"; DIM="\033[2m"
VERDE="\033[92m"; AMARILLO="\033[93m"; ROJO="\033[91m"
CIAN="\033[96m"; AZUL="\033[94m"; BLANCO="\033[97m"
MAGENTA="\033[95m"; GRIS="\033[90m"; NARANJA="\033[38;5;208m"
BG_ROJO="\033[41m"; BG_AZUL="\033[44m"; BG_NEG="\033[40m"

LIMITE_RAM_PCT  = 88
LIMITE_GB       = 4.0
# Cada bloque agrega ~STRINGS_POR_BLOQUE strings de ~50 chars ≈ BLOQUE_MB de RAM
STRINGS_POR_BLOQUE = 200_000   # ≈ 20 MB por bloque
BLOQUE_MB          = 20        # referencia para el panel (aprox)
INTERVALO       = 0.6

def gb(b): return b / 1024**3
def mb(b): return b / 1024**2
def cls(): os.system("cls" if os.name=="nt" else "clear")

def color_pct(p):
    if p >= 90: return ROJO
    if p >= 80: return NARANJA
    if p >= 60: return AMARILLO
    return VERDE

def barra(p, w=34):
    lleno = int(w * p / 100)
    c = color_pct(p)
    return c + "█"*lleno + GRIS + "░"*(w-lleno) + R

def estado(p):
    if p >= 90: return f"{ROJO}{B}CRÍTICO — SWAP ACTIVO{R}"
    if p >= 80: return f"{NARANJA}{B}ALERTA  — Paginando {R}"
    if p >= 60: return f"{AMARILLO}MODERADO            {R}"
    return f"{VERDE}Normal              {R}"

def linea(c="─", w=64, col=GRIS): return col+c*w+R

def panel(contenedor, ram_ini, ciclo, total_strings):
    ram  = psutil.virtual_memory()
    swap = psutil.swap_memory()
    proc = psutil.Process(os.getpid())
    rss  = proc.memory_info().rss
    gb_strings = total_strings * 50 / 1024**3  # estimación ~50 bytes/string

    pct_limite_ram = ram.percent / LIMITE_RAM_PCT * 100
    pct_limite_gb  = gb_strings  / LIMITE_GB      * 100

    cls()
    print(f"{BG_ROJO}{BLANCO}{B}  🔥  ESTRÉS DE MEMORIA — SIMULADOR DE PAGINACIÓN          {R}")
    print(f"{BG_NEG}{GRIS}  ciclo #{ciclo}   RAM inicio: {ram_ini.percent:.1f}%   "
          f"PID: {os.getpid()}{R}")
    print(linea("═", 64))

    # RAM física
    print(f"\n  {MAGENTA}{B}RAM FÍSICA{R}")
    print(f"  {barra(ram.percent)}  {color_pct(ram.percent)}{B}{ram.percent:5.1f}%{R}  "
          f"{estado(ram.percent)}")
    print(f"  {GRIS}Usada : {BLANCO}{gb(ram.used):.2f} GB{GRIS}  "
          f"Disp : {BLANCO}{gb(ram.available):.2f} GB{GRIS}  "
          f"Total: {BLANCO}{gb(ram.total):.2f} GB{R}")

    # Swap / Pagefile
    print(f"\n  {AZUL}{B}MEMORIA VIRTUAL (SWAP / PAGEFILE){R}")
    if swap.total > 0:
        print(f"  {barra(swap.percent)}  {color_pct(swap.percent)}{B}{swap.percent:5.1f}%{R}")
        print(f"  {GRIS}Usada : {BLANCO}{gb(swap.used):.2f} GB{GRIS}  "
              f"Total: {BLANCO}{gb(swap.total):.2f} GB{R}")
    else:
        print(f"  {GRIS}Sin swap explícito — Windows usa pagefile.sys automático{R}")
        print(f"  {GRIS}→ Mira «Archivo de paginación» en Administrador de Tareas{R}")

    # Este proceso — strings acumulados
    print(f"\n  {CIAN}{B}ESTE PROCESO — Lista de strings{R}")
    print(f"  {GRIS}Memoria RSS      : {BLANCO}{mb(rss):.1f} MB{R}")
    print(f"  {GRIS}Strings en lista : {BLANCO}{total_strings:,}{GRIS}  "
          f"(≈ {gb_strings:.3f} GB en RAM){R}")
    print(f"  {GRIS}Bloques de       : {BLANCO}{STRINGS_POR_BLOQUE:,}{GRIS} strings c/u{R}")

    # Barras de límite de seguridad
    print(f"\n  {AMARILLO}{B}LÍMITES DE SEGURIDAD{R}")
    print(f"  RAM   {barra(min(pct_limite_ram,100), 28)}  "
          f"{ram.percent:.1f}% / {LIMITE_RAM_PCT}%")
    print(f"  Mem   {barra(min(pct_limite_gb, 100), 28)}  "
          f"{gb_strings:.3f} GB / {LIMITE_GB} GB  (estimado)")

    print(f"\n{linea('═', 64)}")
    print(f"  {GRIS}Presiona {B}Ctrl+C{R}{GRIS} para detener el estrés en cualquier momento{R}")


def estres():
    print(f"\n{BG_AZUL}{BLANCO}{B}  🔥  ESTRÉS DE MEMORIA  {R}\n")
    ram_ini = psutil.virtual_memory()
    print(f"  RAM al inicio : {VERDE}{ram_ini.percent:.1f}%{R}  "
          f"({gb(ram_ini.used):.2f} / {gb(ram_ini.total):.2f} GB)")
    print(f"\n  {AMARILLO}Límites de seguridad activos:{R}")
    print(f"   → Detener si RAM > {ROJO}{B}{LIMITE_RAM_PCT}%{R}")
    print(f"   → Detener si asignado > {ROJO}{B}{LIMITE_GB} GB{R}")
    print(f"\n  {CIAN}Abre Administrador de Tareas (Ctrl+Shift+Esc){R}")
    print(f"  {CIAN}Pestaña «Rendimiento» → «Memoria» para ver la paginación{R}")
    print(f"\n  {GRIS}Iniciando en 3 segundos…{R}")
    time.sleep(3)

    contenedor = []   # Lista de listas de strings (millones de strings)
    detenido_por = "desconocido"
    ciclo = 0
    total_strings = 0

    try:
        while True:
            ciclo += 1
            ram  = psutil.virtual_memory()
            gb_a = total_strings * 50 / 1024**3  # estimación: ~50 bytes por string

            if ram.percent >= LIMITE_RAM_PCT:
                detenido_por = f"RAM al {ram.percent:.1f}% ≥ límite {LIMITE_RAM_PCT}%"
                break
            if gb_a >= LIMITE_GB:
                detenido_por = f"{gb_a:.2f} GB en strings ≥ límite {LIMITE_GB} GB"
                break

            # ── Crear bloque de strings (el requisito pide strings) ──────────
            # Cada iteración añade STRINGS_POR_BLOQUE strings a la lista
            bloque_strings = [
                f"pagina_{ciclo}_{i}_{'X' * 32}" for i in range(STRINGS_POR_BLOQUE)
            ]
            contenedor.append(bloque_strings)
            total_strings += STRINGS_POR_BLOQUE

            panel(contenedor, ram_ini, ciclo, total_strings)
            time.sleep(INTERVALO)

    except KeyboardInterrupt:
        detenido_por = "usuario (Ctrl+C)"

    # Resumen final
    cls()
    ram_fin = psutil.virtual_memory()
    print(f"\n{linea('═', 64, CIAN)}")
    print(f"  {B}{CIAN}RESUMEN DE ESTRÉS{R}")
    print(linea("═", 64, CIAN))
    print(f"  Detenido por      : {AMARILLO}{detenido_por}{R}")
    print(f"  Strings creados   : {BLANCO}{total_strings:,}{R}")
    print(f"  Memoria estimada  : {ROJO}{B}{total_strings*50/1024**3:.3f} GB{R} en strings")
    print(f"  RAM inicio / fin  : {VERDE}{ram_ini.percent:.1f}%{R} → "
          f"{color_pct(ram_fin.percent)}{B}{ram_fin.percent:.1f}%{R}")
    print(f"\n  {AMARILLO}Liberando memoria…{R}")
    contenedor.clear()
    gc.collect()
    ram_post = psutil.virtual_memory()
    print(f"  RAM tras liberar  : {VERDE}{ram_post.percent:.1f}%{R}")
    print(linea("─", 64))
    print(f"\n  {GRIS}💡 Cuando la RAM se agota, el SO mueve páginas inactivas{R}")
    print(f"  {GRIS}   al archivo pagefile.sys (Windows) — mucho más lento que RAM.{R}")
    print(linea("═", 64))
    print()

if __name__ == "__main__":
    estres()
