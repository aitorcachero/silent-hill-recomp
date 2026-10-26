<div align="center">

# 🌫️ Silent Hill Recompiled
### *Port Nativo para PC (Windows x64) mediante Recompilación Estática MIPS R3000A*

[![Platform](https://img.shields.io/badge/Plataforma-Windows%20x64%20Nativo-blue.svg?style=for-the-badge&logo=windows)](https://github.com)
[![Resolution](https://img.shields.io/badge/Resoluci%C3%B3n-4K%20UHD%20(3840x2160)-brightgreen.svg?style=for-the-badge)](https://github.com)
[![Framerate](https://img.shields.io/badge/Refresco-60%20%2F%20120%20%2F%20144%20FPS-orange.svg?style=for-the-badge)](https://github.com)
[![Aspect Ratio](https://img.shields.io/badge/Modos-16%3A9%20Full--Screen%20%26%204%3A3%20UHD-purple.svg?style=for-the-badge)](https://github.com)
[![Stability](https://img.shields.io/badge/Estabilidad-Sin%20Cuelgues%20(Iglesia%2FPuente)-success.svg?style=for-the-badge)](https://github.com)
[![License](https://img.shields.io/badge/Licencia-MIT-lightgrey.svg?style=for-the-badge)](LICENSE)

---

</div>

## 📖 Descripción del Proyecto

**Silent Hill Recompiled** es una adaptación nativa para PC de 64 bits de la obra maestra del survival horror creada por **Team Silent (Konami)** en 1999 para la PlayStation 1.

A diferencia de los emuladores convencionales (que interpretan el código máquina MIPS en un bucle virtual con sobrecoste de CPU y latencia de entrada), este proyecto realiza una **traducción estática completa** del código binario de PS1 a código C nativo optimizado para procesadores x86-64 modernos.

El ejecutable resultante interactúa directamente con la GPU a través de OpenGL/Vulkan de bajo nivel, ofreciendo una experiencia fluida, nítida y con latencia ultrabaja imposible de alcanzar en el hardware original de 32 bits.

---

## ✨ Características y Mejoras Implementadas

### 🛡️ 1. Corrección de Cuelgues Críticos de Emulación (Balkan Church / Puente)
- **Eliminación de Softlocks:** En la emulación tradicional con PGXP activado, *Silent Hill* sufre cuelgues irreversibles con audio en bucle en transiciones clave (dentro de la **Iglesia Balkan** tras las cinemáticas de Dahlia, al cruzar el **puente levadizo** o en el **tiovivo del parque de atracciones**). En este port el pipeline de geometría se ha estabilizado por completo, permitiendo completar el juego de principio a fin sin bloqueos ni costuras blancas en texturas.

### 🌫️ 2. Niebla Volumétrica y Linterna OLED Atmosférica
- **Preservación del Difuminado Original:** Se elimina el ruido artificial y las rejillas de dithering que producían los filtros de realce 2D sobre la niebla en 4K.
- **Shader OLED de Terror Psicológico:** Canal de postprocesamiento diseñado para pantallas modernas y paneles OLED: negros puros y profundos en la oscuridad, haz de linterna contrastado y paleta cromática oxidada y tétrica fiel al Otherworld original.

### 🗺️ 3. Inventario, Notas y Mapa 100% Alineados
- **Interfaz Cohesionada:** Se ha desactivado el anclaje heurístico por tercios (`auto_ui_squash`), evitando que el mapa que dibuja Harry, las descripciones de objetos, el menú de inventario y los cuadros de diálogo se separen o queden estirados en los bordes.

### 🖥️ 4. Modos de Visualización Adaptativos

| Modo | Lanzador | Descripción |
|---|---|---|
| **16:9 Panorámico Pantalla Completa** | `SilentHill.exe`<br>`JUGAR_SILENT_HILL.bat` | Llena el **100% de la pantalla** sin bandas negras laterales. Las cinemáticas FMV en vídeo (intro, Cheryl en el callejón) conservan automáticamente la proporción original 4:3 para no deformarse. |
| **4:3 UHD Puro Pixel-Perfect** | `JUGAR_SILENT_HILL_4K_43.bat` | Proporción clásica 4:3 en resolución nativa **4K UHD (2160p)**. Cero pop-in lateral en las esquinas de la cámara fija y niebla perfectamente delimitada. |

### 🔇 5. Lanzador Nativo Silencioso (`.exe`)
- `SilentHill.exe` compilado con Clang en modo `-mwindows`, arrancando de manera inmediata sin consolas de texto CMD de fondo.
- Se incluye también un script silencioso adicional `JUGAR_SILENT_HILL_SIN_VENTANAS.vbs`.

---

## 🎮 Compatibilidad Universal de Discos

El preparador universal integrado (`tools/setup_disc.py`) detecta y configura automáticamente las siguientes versiones:

| Región | Código de Disco | Título | Frecuencia | Idioma |
|---|---|---|---|---|
| **PAL España** | `SLES-01514` | Silent Hill | 50.0 Hz | Castellano |
| **PAL Europa** | `SCES-01514` | Silent Hill | 50.0 Hz | Inglés |
| **NTSC-U** | `SLUS-00707` | Silent Hill (v1.0 / v1.1) | 59.94 Hz | Inglés |
| **NTSC-J** | `SLPM-86192` | Silent Hill (v1.0) | 59.94 Hz | Japonés |
| **NTSC-J The Best** | `SLPM-86641` | Silent Hill (Konami The Best) | 59.94 Hz | Japonés |
| **NTSC-J PSone Books** | `SLPM-87328` | Silent Hill (PSone Books) | 59.94 Hz | Japonés |

Formatos aceptados: **`.BIN/.CUE`**, **`.PBP`** (PSP/PS3 eBoot), **`.ISO`**, **`.IMG`**, **`.CHD`**.

---

## 🚀 Guía de Instalación y Uso Rápido

1. **Descarga el release:**
   Descarga y descomprime `Silent_Hill_Recompiled_v1.0_Windows_x64.zip`.

2. **Añade tu juego legal:**
   Copia tu imagen de disco de Silent Hill en la subcarpeta `disc/` (o en la carpeta raíz del juego).

3. **Ejecuta el preparador:**
   Haz doble clic en **`PREPARAR_DISCO.bat`**. Detectará tu copia, extraerá los archivos necesarios si es un `.PBP` y configurará el motor automáticamente.

4. **¡A jugar!:**
   - Para jugar en **16:9 Panorámico Completo**: ejecuta `SilentHill.exe` o `JUGAR_SILENT_HILL.bat`.
   - Para jugar en **4:3 UHD Puro Clásico**: ejecuta `JUGAR_SILENT_HILL_4K_43.bat`.

---

## 🕹️ Controles por Defecto

Compatible de forma nativa con **Mandos de Xbox Series/One/360, PlayStation DualSense/DualShock 4, Mandos Genéricos DirectInput/XInput y Teclado**.

| Acción | Mando (Xbox / PS) | Teclado (Alternativo) |
|---|---|---|
| **Mover a Harry (Avanzar / Girar / Retroceder)** | Stick Izquierdo / Cruceta | `Flechas de Dirección` |
| **Correr** | `Cuadrado` / `X` | `Shift Izquierdo` |
| **Apuntar Arma (Postura de Tiro)** | `R2` / `RT` | `Espacio` |
| **Disparar / Atacar / Examinar / Abrir** | `Cruz` / `A` | `Enter` |
| **Encender / Apagar Linterna** | `Círculo` / `B` | `F` |
| **Abrir Mapa** | `Triángulo` / `Y` | `M` |
| **Desplazamiento Lateral (Paso Izq / Der)** | `L1` / `R1` (`LB` / `RB`) | `Q` / `E` |
| **Cambiar Modo de Vista (Mirar)** | `L2` / `LT` | `V` |
| **Menú de Inventario** | `Select` / `Back` | `Tab` |
| **Pausa** | `Start` | `Escape` |

---

## 📂 Estructura del Paquete

```text
Silent_Hill_Recompiled/
├── SilentHill.exe                     # Lanzador nativo Windows silencioso
├── Silent_Hill_Recompiled.exe         # Ejecutable principal del motor recompilado
├── game.toml                           # Configuración de renderizado 4K, PGXP y aspecto
├── settings.toml                       # Preferencias de usuario portables
├── disc.cfg                            # Ruta al descriptor del disco
├── JUGAR_SILENT_HILL.bat              # Acceso rápido en 16:9 Full-Screen
├── JUGAR_SILENT_HILL_4K_43.bat        # Acceso rápido en 4:3 UHD Puro
├── JUGAR_SILENT_HILL_SIN_VENTANAS.vbs # Acceso 100% silencioso
├── PREPARAR_DISCO.bat                  # Asistente de detección de disco
├── LEEME_INSTRUCCIONES.txt             # Guía rápida en texto plano
├── README.md                           # Documentación completa
├── LICENSE                             # Licencia MIT del proyecto
├── disc/                               # Carpeta donde depositar el juego legal
│   └── PON_TU_JUEGO_AQUI.txt
├── saves/                              # Tarjetas de memoria virtuales (.mcd)
├── shaders/                            # Shaders Atmosféricos OLED
│   ├── hd2d.glsl
│   └── hd2d.pfx
└── tools/                              # Utilidad multiplataforma de ingestión
    └── setup_disc.py
```

---

## 💻 Requisitos del Sistema

- **Sistema Operativo:** Windows 10 / Windows 11 (64-bit).
- **Procesador:** Cualquier CPU moderna con soporte x86-64 (Intel Core i3 / AMD Ryzen 3 o superior).
- **Memoria RAM:** 2 GB mínimo.
- **Tarjeta Gráfica:** Compatible con OpenGL 3.3 o superior (Intel HD Graphics 4000+, NVIDIA GeForce GT 710+, AMD Radeon HD 7000+ o cualquier GPU dedicada moderna).
- **Almacenamiento:** ~650 MB para la imagen de disco del juego.

---

## ⚖️ Aviso Legal y Cumplimiento

* **Silent Hill** es una marca registrada de **Konami Digital Entertainment Co., Ltd.**
* Este proyecto es una reimplementación independiente de código limpio desarrollada con fines de preservación técnica e investigación histórica.
* **Este paquete NO contiene ninguna BIOS de Sony PlayStation, ni imágenes de disco, música, vídeos ni ningún archivo con derechos de autor.**
* Cada usuario debe poseer una copia original del juego para generar los activos necesarios para jugar.
