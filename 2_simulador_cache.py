"""
=============================================================
  SCRIPT 2: Simulador de Jerarquía de Memoria
=============================================================
  Concepto : Caché L1/L2 → RAM → Disco
  Interfaz : TUI con colores ANSI, animación y tabla final
=============================================================
  Sin dependencias externas (solo stdlib Python)
=============================================================
"""

import time, os, sys, hashlib, threading

# ── Habilitar colores ANSI en Windows ──────────────────────
if os.name == "nt":
    import ctypes
    ctypes.windll.kernel32.SetConsoleMode(
        ctypes.windll.kernel32.GetStdHandle(-11), 7)

# ── Paleta ─────────────────────────────────────────────────
R  = "\033[0m"; B = "\033[1m"; DIM = "\033[2m"
VERDE   = "\033[92m"; AMARILLO = "\033[93m"; ROJO   = "\033[91m"
CIAN    = "\033[96m"; AZUL     = "\033[94m"; BLANCO = "\033[97m"
MAGENTA = "\033[95m"; GRIS     = "\033[90m"; NARANJA= "\033[38;5;208m"
BG_AZUL = "\033[44m"; BG_NEG   = "\033[40m"

def linea(c="─", w=64, col=GRIS): return col + c*w + R
def cls(): os.system("cls" if os.name=="nt" else "clear")

# ── Spinner ────────────────────────────────────────────────
_spin_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
_spin_stop  = False
_spin_msg   = ""

def _spin_worker():
    i = 0
    while not _spin_stop:
        sys.stdout.write(f"\r  {CIAN}{_spin_chars[i % len(_spin_chars)]}{R}  {_spin_msg}  ")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()

def spinner_start(msg):
    global _spin_stop, _spin_msg
    _spin_stop = False
    _spin_msg  = msg
    t = threading.Thread(target=_spin_worker, daemon=True)
    t.start()
    return t

def spinner_stop():
    global _spin_stop
    _spin_stop = True
    time.sleep(0.15)

# ── Clase caché ────────────────────────────────────────────
class SimuladorCache:
    def __init__(self, cap_l1=3, cap_ram=10):
        self.l1   = {}; self.ram_cache = {}
        self.cl1  = cap_l1; self.cram = cap_ram
        self.hits = {"L1":0, "RAM":0, "DISCO":0}
        self.tiempos = {"L1":[], "RAM":[], "DISCO":[]}

    def _desalojar(self, d):
        del d[next(iter(d))]

    def leer(self, path):
        t0 = time.perf_counter()
        if path in self.l1:
            data    = self.l1[path]
            elapsed = time.perf_counter() - t0
            self.hits["L1"] += 1; self.tiempos["L1"].append(elapsed)
            return elapsed, "L1", data
        if path in self.ram_cache:
            data = self.ram_cache[path]
            if len(self.l1) >= self.cl1: self._desalojar(self.l1)
            self.l1[path] = data
            elapsed = time.perf_counter() - t0
            self.hits["RAM"] += 1; self.tiempos["RAM"].append(elapsed)
            return elapsed, "RAM", data
        with open(path, "rb") as f:
            data = f.read()
        elapsed = time.perf_counter() - t0
        if len(self.ram_cache) >= self.cram: self._desalojar(self.ram_cache)
        self.ram_cache[path] = data
        if len(self.l1) >= self.cl1: self._desalojar(self.l1)
        self.l1[path] = data
        self.hits["DISCO"] += 1; self.tiempos["DISCO"].append(elapsed)
        return elapsed, "DISCO", data

# ── Crear archivos de prueba ───────────────────────────────
def crear_archivos(d="archivos_prueba", n=5, mb=2.0):
    os.makedirs(d, exist_ok=True)
    rutas = []
    for i in range(n):
        p = os.path.join(d, f"archivo_{i+1}.dat")
        if not os.path.exists(p):
            with open(p, "wb") as f:
                f.write(os.urandom(int(mb * 1024**2)))
        rutas.append(p)
    return rutas

# ── Icono y color por nivel ────────────────────────────────
def icono_nivel(nivel):
    return {"L1": f"{VERDE}⚡ L1/L2 (caché){R}",
            "RAM": f"{AMARILLO}💾 RAM   (caché){R}",
            "DISCO": f"{ROJO}📀 DISCO (lectura){R}"}[nivel]

def tiempo_str(elapsed, nivel):
    if nivel == "DISCO":
        return f"{ROJO}{elapsed*1000:.3f} ms{R}"
    return f"{VERDE}{elapsed*1_000_000:.2f} µs{R}"

# ── Tabla de lectura ───────────────────────────────────────
def imprimir_fila(nombre, nivel, elapsed, md5=""):
    n_str  = icono_nivel(nivel)
    t_str  = tiempo_str(elapsed, nivel)
    md5_str = f"  {GRIS}md5:{md5}{R}" if md5 else ""
    print(f"  {BLANCO}{nombre:<18}{R} {n_str:<40}  {t_str}{md5_str}")

# ── Main ───────────────────────────────────────────────────
def main():
    cls()
    print(f"{BG_AZUL}{BLANCO}{B}  💾  SIMULADOR DE JERARQUÍA DE MEMORIA — Caché vs Disco  {R}")
    print(f"{BG_NEG}{GRIS}  L1/L2 (µs)  →  RAM (µs)  →  Disco (ms){R}")
    print(linea("═", 64))
    print(f"""
  {CIAN}Niveles simulados:{R}
    {VERDE}⚡ L1/L2{R}  →  Diccionario Python  {GRIS}(3 entradas, ~µs){R}
    {AMARILLO}💾 RAM  {R}  →  Diccionario amplio  {GRIS}(10 entradas, ~µs){R}
    {ROJO}📀 DISCO{R}  →  Sistema de archivos {GRIS}(lectura real, ~ms){R}
""")

    # Crear archivos
    t = spinner_start("Creando archivos de prueba (5 × 2 MB)…")
    rutas = crear_archivos(n=5, mb=2.0)
    spinner_stop()
    print(f"  {VERDE}✓{R}  5 archivos listos en {BLANCO}./archivos_prueba/{R}\n")
    time.sleep(0.3)

    cache = SimuladorCache(cap_l1=3, cap_ram=10)

    # ── RONDA 1: disco frío ─────────────────────────────────
    print(linea("─", 64))
    print(f"  {B}{AZUL}RONDA 1{R} — Primera lectura  {GRIS}(cache vacía → va al disco){R}")
    print(linea("─", 64))
    for ruta in rutas:
        t_spin = spinner_start(f"Leyendo {os.path.basename(ruta)}…")
        elapsed, nivel, data = cache.leer(ruta)
        spinner_stop()
        md5 = hashlib.md5(data).hexdigest()[:8]
        imprimir_fila(os.path.basename(ruta), nivel, elapsed, md5)
        time.sleep(0.1)

    # ── RONDA 2: caché caliente ─────────────────────────────
    print(f"\n{linea('─', 64)}")
    print(f"  {B}{VERDE}RONDA 2{R} — Segunda lectura  {GRIS}(datos en caché → RAM/L1){R}")
    print(linea("─", 64))
    for ruta in rutas:
        elapsed, nivel, data = cache.leer(ruta)
        imprimir_fila(os.path.basename(ruta), nivel, elapsed)
        time.sleep(0.05)

    # ── RONDA 3: 10 accesos al mismo archivo ────────────────
    print(f"\n{linea('─', 64)}")
    print(f"  {B}{MAGENTA}RONDA 3{R} — 10 accesos repetidos al mismo archivo")
    print(linea("─", 64))
    cache.l1.clear(); cache.ram_cache.clear()
    archivo_test = rutas[0]
    tiempos_disco = []; tiempos_cache = []

    REF_DISCO_MS = 10.0   # referencia visual para escalar la barra
    REF_CACHE_US = 50.0

    for i in range(10):
        elapsed, nivel, _ = cache.leer(archivo_test)
        barra_w = 24
        if nivel == "DISCO":
            ratio = min(elapsed * 1000 / REF_DISCO_MS, 1.0)
            color = ROJO
            tiempos_disco.append(elapsed * 1000)
        else:
            ratio = min(elapsed * 1_000_000 / REF_CACHE_US, 1.0)
            color = VERDE
            tiempos_cache.append(elapsed * 1_000_000)
        lleno = max(1, int(barra_w * ratio))
        bar   = color + "█"*lleno + GRIS + "░"*(barra_w - lleno) + R
        t_s   = tiempo_str(elapsed, nivel)
        print(f"  {GRIS}#{i+1:>2}{R}  {bar}  {icono_nivel(nivel):<40} {t_s}")
        time.sleep(0.08)

    # ── Tabla resumen ────────────────────────────────────────
    print(f"\n{linea('═', 64, CIAN)}")
    print(f"  {B}{CIAN}RESUMEN DE RENDIMIENTO{R}")
    print(linea("═", 64, CIAN))
    total = sum(cache.hits.values())
    for nivel, hits in cache.hits.items():
        ts  = cache.tiempos[nivel]
        avg = (sum(ts)/len(ts)) if ts else 0
        pct = hits/max(total,1)*100
        bar_h = int(20 * pct / 100)
        icon  = icono_nivel(nivel)
        unidad = "ms" if nivel=="DISCO" else "µs"
        avg_v  = avg*1000 if nivel=="DISCO" else avg*1_000_000
        bar_col = ROJO if nivel=="DISCO" else (AMARILLO if nivel=="RAM" else VERDE)
        barra_hits = bar_col + "█"*bar_h + GRIS + "░"*(20-bar_h) + R
        print(f"  {icon:<40} hits: {BLANCO}{hits:>3}{R}  "
              f"{barra_hits}  {GRIS}avg: {BLANCO}{avg_v:.2f} {unidad}{R}")

    if cache.tiempos["DISCO"] and cache.tiempos["L1"]:
        avg_d = sum(cache.tiempos["DISCO"]) / len(cache.tiempos["DISCO"])
        avg_l = sum(cache.tiempos["L1"])    / len(cache.tiempos["L1"])
        factor = avg_d / avg_l
        print(f"\n  {VERDE}{B}🚀  La caché L1 es {factor:,.0f}× más rápida que el disco{R}")

    print(f"\n{linea('─', 64)}")
    print(f"  {GRIS}Analogía real:{R}")
    print(f"    {VERDE}L1/L2{R}  →  SRAM dentro del procesador   {GRIS}(nanosegundos){R}")
    print(f"    {AMARILLO}RAM  {R}  →  DRAM del sistema              {GRIS}(microsegundos){R}")
    print(f"    {ROJO}Disco{R}  →  SSD / HDD                     {GRIS}(milisegundos){R}")
    print(linea("═", 64))
    print()

if __name__ == "__main__":
    main()
