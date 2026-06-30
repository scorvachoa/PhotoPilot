# PhotoPilot

PhotoPilot es una aplicación de edición de fotos profesional para escritorio, construida con Python (Tkinter + Pillow + OpenCV). Ofrece un flujo de trabajo no destructivo estilo Lightroom para procesamiento por lotes — ajustes, recorte inteligente y exportación.

## Características

- **Edición no destructiva** — cada imagen conserva su propio preset de recorte, centro de recorte y 10 ajustes independientes
- **10 ajustes manuales**: brillo, contraste, saturación, exposición, temperatura, sombras, altas luces, nitidez, gamma, reducción de ruido
- **Mejora automática** — brillo, contraste, saturación, balance de blancos y nitidez
- **Recorte inteligente** — detección de rostros combinada con centro definido por el usuario, arrastra directamente en la previsualización para reposicionar
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

1. Haz clic en **"Abrir imagenes"** o arrastra imágenes/carpetas a la ventana
2. Selecciona una carpeta con **"Carpeta origen"**
3. Elige la carpeta de destino con **"Carpeta destino"**
4. Haz clic en una miniatura para editar
5. Usa los presets de recorte y arrastra la previsualización para reposicionar
6. Ajusta los deslizadores para ajuste fino
7. Activa **"Mejorar automaticamente"** para auto-mejora
8. Exporta con **"Exportar esta foto"** o **"Exportar todas"**
9. Usa **"Procesar carpeta"** para procesamiento por lotes

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
- **`ProcessingPipeline`** encadena: mejora automática → recorte inteligente → ajustes manuales
- **`PreviewPanel`** muestra el resultado procesado por defecto, cambia a original + superposición durante el arrastre de recorte
- **`Exporter`** guarda imágenes procesadas con configuración de calidad según formato
- **`BatchProcessor`** ejecuta en multihilo con actualizaciones de progreso en tiempo real

## Licencia

MIT
