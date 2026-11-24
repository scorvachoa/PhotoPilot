# PhotoPilot

PhotoPilot es una aplicación de edición de fotos profesional para escritorio, construida con Python (Tkinter + Pillow + OpenCV). Ofrece un flujo de trabajo no destructivo estilo Lightroom para procesamiento por lotes — ajustes, recorte inteligente y exportación.

## Características

- **Edición no destructiva** — cada imagen conserva su propio preset de recorte, centro de recorte y 10 ajustes independientes
- **10 ajustes manuales**: brillo, contraste, saturación, exposición, temperatura, sombras, altas luces, nitidez, gamma, reducción de ruido
- **Mejora automática** — brillo, contraste, saturación, balance de blancos y nitidez
- **Recorte inteligente** — la detección de rostros propone el centro inicial y tú lo ajustas arrastrando sobre la previsualización con guías de tercios; el centro que elijas siempre manda
- **32 presets de recorte** en 7 plataformas (Facebook, Instagram, LinkedIn, Pinterest, Twitter/X, YouTube, Personalizado)
- **Procesamiento por lotes** — multihilo con barra de progreso, ETA y conteo de errores
- **Exportación** — foto individual o lote en JPG, PNG, WebP con calidad configurable

## Requisitos

- Python 3.11+
- Pillow
- OpenCV (carga diferida para evitar error OpenBLAS)
- numpy
- tkinterdnd2

## Instalación

```bash
git clone https://github.com/tuusuario/photopilot.git
cd photopilot
python -m venv env
env\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

1. Pulsa **Abrir imágenes** o arrastra imágenes/carpetas a la ventana
2. Selecciona una carpeta con **Carpeta origen**
3. Elige la carpeta de destino con **Carpeta destino**
4. Haz clic en una miniatura para editar
5. Usa los presets de recorte y arrastra la previsualización para encuadrar (guías de tercios y límites del recorte)
6. Ajusta los deslizadores para ajuste fino: flechas o botones ± en pasos de 0.01, con **Mayús** en pasos de 0.001
7. Activa **Mejorar automáticamente** para auto-mejora
8. Exporta con **Exportar esta foto** o **Exportar todas** (siempre a la resolución completa del preset)
9. Usa **Procesar carpeta** para procesamiento por lotes

## Interfaz

La ventana se organiza en seis zonas:

- **Barra superior** — marca, número de imágenes, carpeta destino y el botón **Abrir imágenes**
- **Panel izquierdo** — miniaturas con anillo de selección, contador y accesos a **Carpeta origen** / **Carpeta destino**
- **Vista previa** — imagen procesada sobre fondo neutro, guía de encuadre arrastrable y metadatos de la foto
- **Barra de recorte** — chips de plataforma y preset, tamaño resultante en píxeles y acciones de encuadre
- **Panel derecho** — herramientas, exportación, lote y los 10 ajustes agrupados en **LUZ**, **COLOR** y **DETALLE**
- **Barra de estado** — mensajes, progreso, ETA y errores del procesamiento por lotes

## Atajos de teclado

| Acción | Atajo |
| --- | --- |
| Abrir imágenes | `Ctrl+O` |
| Elegir carpeta origen | `Ctrl+Shift+O` |
| Exportar la foto actual | `Ctrl+E` |
| Procesar carpeta | `Ctrl+Enter` |
| Navegar miniaturas | Flechas (con la lista enfocada) |
| Ajuste grueso de un deslizador | `←` / `→` (0.01) |
| Ajuste fino de un deslizador | `Mayús` + `←` / `→` (0.001) |
| Encuadrar la foto | Arrastrar en la vista previa |
| Restablecer un ajuste | Doble clic en su valor |

## Estructura del proyecto

```
PhotoPilot/
├── main.py                 # Punto de entrada
├── config/                 # Tema, constantes, configuración
├── core/                   # Estado, pipeline, procesador por lotes, exportador
├── gui/                    # Interfaz Tkinter (app, widgets, sliders, presets)
├── opencv/                 # Recorte inteligente con detección de rostros
├── processing/             # Mejora automática, ajustes manuales
├── utils/                  # Validadores, helpers de relación de aspecto
└── assets/                 # Recursos estáticos
```

## Arquitectura

- **`AppState`** almacena todo el estado por imagen en diccionarios (`_crop_presets`, `_crop_centers`, `_processing_settings`)
- **`ProcessingPipeline`** encadena: recorte inteligente → mejora automática → ajustes manuales; cachea la base (recorte + mejora) y la versión escalada del preview para que mover un deslizador solo recalcule los ajustes manuales
- **`PreviewPanel`** muestra el resultado procesado a un máximo de 1800 px, cambia a original + superposición al arrastrar el encuadre y limita el centro al rango válido del recorte
- **`Exporter`** guarda imágenes procesadas a resolución completa (tamaño exacto del preset) con configuración de calidad según formato
- **`BatchProcessor`** ejecuta en multihilo con actualizaciones de progreso en tiempo real

## Licencia

MIT
