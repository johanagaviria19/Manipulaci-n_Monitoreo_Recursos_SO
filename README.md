# Manipulación y Monitoreo de Recursos del SO

Cuatro scripts Python que simulan conceptos fundamentales de Sistemas Operativos:
jerarquía de memoria, monitoreo de recursos, paginación y planificación de procesos.

## Requisitos

- Python 3.8 o superior
- psutil (ya instalado en el entorno actual: v7.1.3)

```bash
pip install psutil
```

---

## Script 1 — Monitor de Recursos en Tiempo Real

**Archivo:** `1_monitor_recursos.py`  
**Concepto:** Panel de control del Sistema Operativo

Muestra en tiempo real el uso de CPU, RAM y disco con barras de progreso y
niveles de alerta (Normal / Moderado / Alerta / Crítico).
Cada vez que la RAM supera el **80%**, escribe una línea en `alertas_ram.txt`.

```bash
python 1_monitor_recursos.py
```

Detener con `Ctrl+C`. El log queda en `alertas_ram.txt`.

**Umbrales configurables** (líneas 20-21 del script):
| Variable | Valor por defecto | Descripción |
|---|---|---|
| `UMBRAL_RAM_ALERTA` | 80 % | Dispara alerta y escribe log |
| `UMBRAL_CPU_ALERTA` | 90 % | Solo alerta visual |
| `INTERVALO_SEGUNDOS` | 1 | Frecuencia de actualización |

---

## Script 2 — Simulador de Caché (L1/L2 vs RAM vs Disco)

**Archivo:** `2_simulador_cache.py`  
**Concepto:** Jerarquía de memoria y optimización de acceso

Implementa tres niveles de caché usando diccionarios en RAM y el sistema de archivos real:

| Nivel | Implementación | Velocidad típica |
|---|---|---|
| L1/L2 | Diccionario (3 entradas) | microsegundos (µs) |
| RAM | Diccionario (10 entradas) | microsegundos (µs) |
| Disco | Archivos `.dat` reales | milisegundos (ms) |

```bash
python 2_simulador_cache.py
```

El script:
1. Crea 5 archivos de prueba de 2 MB en `./archivos_prueba/`
2. Lee cada archivo por primera vez desde **disco** (lento)
3. Lee cada archivo por segunda vez desde **caché** (rápido)
4. Compara 10 accesos al mismo archivo y muestra el factor de mejora

---

## Script 3 — Estrés de Memoria y Paginación (Memoria Virtual)

**Archivo:** `3_estres_memoria.py`  
**Concepto:** Memoria Virtual y Archivo de Paginación (swap/pagefile)

Llena la RAM de forma controlada para forzar al SO a usar el archivo de paginación.
Mientras corre, abre el **Administrador de Tareas** (`Ctrl+Shift+Esc`) →
pestaña **Rendimiento** → **Memoria** para observar cómo sube la memoria virtual.

```bash
python 3_estres_memoria.py
```

**Límites de seguridad activos** (el script se detiene automáticamente si se cumple cualquiera):
- RAM física supera el **88 %**
- Se asignan más de **4 GB** por este proceso

Detener manualmente con `Ctrl+C`.

> ⚠️ No modificar `LIMITE_RAM_PCT` por encima de 92 % ni `LIMITE_GB_TOTAL`
> por encima de 8 GB sin verificar la RAM disponible del equipo.

---

## Script 4 — Prioridad de Procesos (Scheduling del Kernel)

**Archivo:** `4_prioridad_procesos.py`  
**Concepto:** Planificación de procesos del Kernel (no todos los procesos son iguales)

Lanza dos instancias del mismo cálculo matemático pesado con distinta prioridad de CPU
y mide cuál termina primero.

### Modos de uso

```bash
# Comparar ambas prioridades al mismo tiempo (modo recomendado)
python 4_prioridad_procesos.py --modo comparar

# Solo proceso con prioridad baja
python 4_prioridad_procesos.py --modo bajo

# Solo proceso con prioridad alta
python 4_prioridad_procesos.py --modo alto

# Ajustar número de iteraciones (más iteraciones = diferencia más notoria)
python 4_prioridad_procesos.py --modo comparar --iteraciones 5000000
```

> **Windows:** Ejecutar la terminal como **Administrador** para que la prioridad
> `HIGH_PRIORITY_CLASS` tenga efecto completo sobre el scheduler.

### Prioridades usadas

| Modo | Windows | Linux/Mac |
|---|---|---|
| Baja | `IDLE_PRIORITY_CLASS` | `nice = 19` |
| Alta | `HIGH_PRIORITY_CLASS` | `nice = -20` |

---

## Resumen de conceptos del SO cubiertos

| Script | Concepto del SO |
|---|---|
| 1 | Monitoreo de recursos, métricas del kernel |
| 2 | Jerarquía de memoria: caché L1/L2 → RAM → disco |
| 3 | Memoria virtual, paginación, archivo de intercambio |
| 4 | Planificación de procesos (scheduling), quantum de CPU |

---

## Estructura de archivos generados en tiempo de ejecución

```
Manipulación_Monitoreo_Recursos_SO/
├── alertas_ram.txt          ← generado por script 1 (log de alertas)
└── archivos_prueba/
    ├── archivo_1.dat        ← generado por script 2 (2 MB c/u)
    ├── archivo_2.dat
    ├── archivo_3.dat
    ├── archivo_4.dat
    └── archivo_5.dat
```
