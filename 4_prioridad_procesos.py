"""
=============================================================
  SCRIPT 4: Prioridad de Procesos (Scheduling del Kernel)
=============================================================
  Concepto : No todos los procesos son iguales para el SO
  Interfaz : TUI con barra de progreso animada y comparativa
  Modos    : bajo | alto | comparar (default)
=============================================================
  Dependencia: pip install psutil
  Windows    : correr como Administrador para efecto total
=============================================================
"""

import psutil, time, os, sys, subprocess, argparse, math, threading

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
BG_AZUL="\033[44m"; BG_NEG="\033[40m"; BG_MAG="\033[45m"

def linea(c="─", w=66, col=GRIS): return col+c*w+R
def cls(): os.system("cls" if os.name=="nt" else "clear")

# ── Prioridades ────────────────────────────────────────────
if os.name == "nt":
    PRIO_BAJA  = psutil.IDLE_PRIORITY_CLASS
    PRIO_ALTA  = psutil.REALTIME_PRIORITY_CLASS   # "Tiempo Real" como pide el enunciado
    NOM_BAJA   = "IDLE        (Baja)"
    NOM_ALTA   = "REALTIME    (Tiempo Real)"
    FLAGS_MAP  = {
        psutil.IDLE_PRIORITY_CLASS:         0x00000040,
        psutil.BELOW_NORMAL_PRIORITY_CLASS: 0x00004000,
        psutil.NORMAL_PRIORITY_CLASS:       0x00000020,
        psutil.ABOVE_NORMAL_PRIORITY_CLASS: 0x00008000,
        psutil.HIGH_PRIORITY_CLASS:         0x00000080,
        psutil.REALTIME_PRIORITY_CLASS:     0x00000100,
    }
else:
    PRIO_BAJA  = 19
    PRIO_ALTA  = -20
    NOM_BAJA   = "nice=19 (Baja)"
    NOM_ALTA   = "nice=-20 (Tiempo Real)"
    FLAGS_MAP  = {}

# ── Cálculo pesado ─────────────────────────────────────────
def calculo_pesado(n=3_000_000):
    acc = 0.0
    for i in range(1, n+1):
        acc += math.sqrt(i) * math.log(i)
    return acc

# ── Modo trabajador (proceso hijo) ────────────────────────
def modo_trabajador(etiqueta, n):
    t0  = time.perf_counter()
    res = calculo_pesado(n)
    dt  = time.perf_counter() - t0
    print(f"RESULTADO|{etiqueta}|{os.getpid()}|{dt:.6f}|{res:.2f}", flush=True)

# ── Barra animada para proceso individual ─────────────────
def barra_animada(titulo, color, n):
    """Muestra una barra que crece mientras corre el cálculo."""
    resultado = [None]
    done      = [False]

    def worker():
        t0 = time.perf_counter()
        r  = calculo_pesado(n)
        resultado[0] = (time.perf_counter() - t0, r)
        done[0] = True

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t_ini = time.time()

    frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    fi = 0
    while not done[0]:
        elapsed = time.time() - t_ini
        w   = 36
        osc = int((elapsed % 2) / 2 * w)
        bar = color + "█"*osc + GRIS + "░"*(w-osc) + R
        sys.stdout.write(f"\r  {color}{frames[fi%len(frames)]}{R}  "
                         f"{titulo}  {bar}  {GRIS}{elapsed:.1f}s{R}  ")
        sys.stdout.flush()
        fi += 1
        time.sleep(0.1)

    t.join()
    sys.stdout.write("\r" + " "*80 + "\r")
    sys.stdout.flush()
    return resultado[0]

# ── Lanzar subproceso con prioridad ───────────────────────
def lanzar(etiqueta, prio, n):
    cmd = [sys.executable, __file__,
           "--modo", "trabajador",
           "--etiqueta", etiqueta,
           "--iteraciones", str(n)]
    flags = FLAGS_MAP.get(prio, 0x00000020) if os.name == "nt" else 0
    p = subprocess.Popen(cmd,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         creationflags=flags)
    if os.name != "nt":
        try: psutil.Process(p.pid).nice(prio)
        except: pass
    return p

# ── Modo comparar ─────────────────────────────────────────
def modo_comparar(n):
    cls()
    print(f"{BG_MAG}{BLANCO}{B}  ⚙️   COMPARADOR DE PRIORIDAD DE PROCESOS  {R}")
    print(f"{BG_NEG}{GRIS}  Planificador del Kernel — Scheduling{R}")
    print(linea("═", 66))
    print(f"""
  {CIAN}Cálculo:{R} Σ √i × ln(i)   i ∈ [1 … {n:,}]

  Se lanzarán {B}DOS procesos simultáneos{R} con distinta prioridad:

    {ROJO}🔻 Proceso A{R}  →  Prioridad {ROJO}{B}{NOM_BAJA}{R}
    {VERDE}🔺 Proceso B{R}  →  Prioridad {VERDE}{B}{NOM_ALTA}{R}

  {AMARILLO}El scheduler del Kernel asigna más tiempo de CPU{R}
  {AMARILLO}al proceso con mayor prioridad.{R}

  {GRIS}⚠  Ejecuta como Administrador para el efecto máximo en Windows.{R}
""")
    print(linea("─", 66))
    print(f"  {GRIS}Lanzando procesos…{R}")

    t_ini = time.perf_counter()
    proc_bajo = lanzar("BAJA", PRIO_BAJA, n)
    proc_alto = lanzar("ALTA", PRIO_ALTA, n)
    print(f"  {ROJO}Proceso BAJA  PID {proc_bajo.pid}{R}")
    print(f"  {VERDE}Proceso ALTA  PID {proc_alto.pid}{R}\n")

    resultados = {}

    def esperar(proc):
        out, _ = proc.communicate()
        for l in out.decode("utf-8", errors="replace").splitlines():
            if l.startswith("RESULTADO|"):
                p = l.split("|")
                if len(p) >= 5:
                    resultados[p[1]] = {"pid": int(p[2]), "dur": float(p[3])}

    # Animar mientras esperamos
    frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    fi = 0
    t1 = threading.Thread(target=esperar, args=(proc_bajo,), daemon=True)
    t2 = threading.Thread(target=esperar, args=(proc_alto,), daemon=True)
    t1.start(); t2.start()

    while t1.is_alive() or t2.is_alive():
        elapsed = time.perf_counter() - t_ini
        w  = 30
        p_b = (not t1.is_alive())
        p_a = (not t2.is_alive())
        bar_b = (VERDE  + "█"*w + R) if p_b else (ROJO  + "█"*int(w*0.5) + GRIS + "░"*int(w*0.5) + R)
        bar_a = (VERDE  + "█"*w + R) if p_a else (VERDE + "█"*int(w*0.6) + GRIS + "░"*int(w*0.4) + R)
        done_b = f"{VERDE}✓ listo{R}" if p_b else f"{GRIS}corriendo…{R}"
        done_a = f"{VERDE}✓ listo{R}" if p_a else f"{GRIS}corriendo…{R}"
        sys.stdout.write(
            f"\r  {frames[fi%len(frames)]}  "
            f"{ROJO}BAJA{R} {bar_b} {done_b}  "
            f"{VERDE}ALTA{R} {bar_a} {done_a}  "
            f"{GRIS}{elapsed:.1f}s{R}  ")
        sys.stdout.flush()
        fi += 1
        time.sleep(0.1)

    t1.join(); t2.join()
    sys.stdout.write("\r" + " "*100 + "\r")
    t_total = time.perf_counter() - t_ini

    # ── Resultados ─────────────────────────────────────────
    print(f"\n{linea('═', 66, CIAN)}")
    print(f"  {B}{CIAN}RESULTADOS{R}")
    print(linea("═", 66, CIAN))

    if "BAJA" in resultados and "ALTA" in resultados:
        dur_b = resultados["BAJA"]["dur"]
        dur_a = resultados["ALTA"]["dur"]
        max_d = max(dur_b, dur_a)

        # Barras proporcionales
        w = 36
        bar_b = ROJO  + "█"*int(w * dur_b/max_d) + R
        bar_a = VERDE + "█"*int(w * dur_a/max_d) + R

        print(f"\n  {ROJO}🔻 BAJA  (PID {resultados['BAJA']['pid']:>6}){R}  "
              f"{bar_b}  {ROJO}{B}{dur_b:.4f} s{R}")
        print(f"  {VERDE}🔺 ALTA  (PID {resultados['ALTA']['pid']:>6}){R}  "
              f"{bar_a}  {VERDE}{B}{dur_a:.4f} s{R}")
        print(f"\n  {GRIS}Tiempo total (muro): {BLANCO}{t_total:.4f} s{R}")

        if dur_b > dur_a:
            diff = dur_b - dur_a
            factor = dur_b / dur_a
            print(f"\n  {VERDE}{B}✅  Proceso ALTA terminó {diff:.4f} s antes "
                  f"({factor:.2f}× más rápido){R}")
            print(f"  {GRIS}→ El scheduler privilegió el proceso de mayor prioridad{R}")
        elif dur_a > dur_b:
            diff = dur_a - dur_b
            print(f"\n  {AMARILLO}⚠️  Proceso BAJA fue más rápido por {diff:.4f} s{R}")
            print(f"  {GRIS}→ Sistema con poca carga; efecto de prioridad mínimo.{R}")
            print(f"  {GRIS}   Prueba con --iteraciones 8000000 para mayor diferencia.{R}")
        else:
            print(f"\n  {AMARILLO}≈  Ambos terminaron al mismo tiempo{R}")
            print(f"  {GRIS}→ Suficientes núcleos disponibles para ambos procesos.{R}")

        print(f"\n{linea('─', 66)}")
        print(f"  {GRIS}💡 Windows asigna «quantums» de tiempo de CPU por prioridad.{R}")
        print(f"  {GRIS}   REALTIME_PRIORITY_CLASS es la clase más alta del sistema.{R}")
        print(f"  {GRIS}   IDLE_PRIORITY_CLASS solo corre cuando la CPU está libre.{R}")
        print(f"  {GRIS}   ⚠  REALTIME requiere Administrador — sin él se usa HIGH.{R}")
    else:
        print(f"\n  {ROJO}⚠  No se obtuvieron resultados de ambos procesos.{R}")

    print(linea("═", 66))
    print()

# ── Modo individual ────────────────────────────────────────
def modo_individual(prio, nombre, n):
    cls()
    color = VERDE if "Alta" in nombre or "alto" in nombre.lower() else ROJO
    print(f"{BG_MAG}{BLANCO}{B}  ⚙️   PROCESO INDIVIDUAL — Prioridad: {nombre}  {R}")
    print(linea("═", 66))
    print(f"\n  PID        : {BLANCO}{os.getpid()}{R}")
    print(f"  Prioridad  : {color}{B}{nombre}{R}")
    print(f"  Iteraciones: {BLANCO}{n:,}{R}\n")

    try:
        psutil.Process(os.getpid()).nice(prio)
        print(f"  {VERDE}✓  Prioridad aplicada{R}\n")
    except psutil.AccessDenied:
        print(f"  {AMARILLO}⚠  Sin permisos de Administrador — prioridad normal{R}\n")

    print(f"  {GRIS}Iniciando cálculo…{R}\n")
    res = barra_animada(f"Calculando con prioridad {nombre}", color, n)
    if res:
        dur, val = res
        print(f"  {VERDE}{B}✓  Completado en {dur:.4f} s{R}")
        print(f"  {GRIS}Resultado: {BLANCO}{val:.2f}{R}")
    print(linea("═", 66))
    print()

# ── CLI ────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Prioridad de procesos del SO")
    ap.add_argument("--modo", choices=["bajo","alto","comparar","trabajador"],
                    default="comparar")
    ap.add_argument("--iteraciones", type=int, default=3_000_000)
    ap.add_argument("--etiqueta", type=str, default="")
    args = ap.parse_args()

    if   args.modo == "trabajador": modo_trabajador(args.etiqueta, args.iteraciones)
    elif args.modo == "bajo":       modo_individual(PRIO_BAJA, NOM_BAJA, args.iteraciones)
    elif args.modo == "alto":       modo_individual(PRIO_ALTA, NOM_ALTA, args.iteraciones)
    else:                           modo_comparar(args.iteraciones)

if __name__ == "__main__":
    main()
