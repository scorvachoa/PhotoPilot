# PhotoPilot

PhotoPilot is a professional desktop photo editing application built with Python (Tkinter + Pillow + OpenCV). It offers a non-destructive, Lightroom-style workflow for batch photo processing — adjustments, smart crop, and export.

## Features

- **Non-destructive editing** — each image preserves its own crop preset, crop center, and 10 adjustment sliders independently
- **10 manual adjustments**: brightness, contrast, saturation, exposure, temperature, shadows, highlights, sharpness, gamma, noise reduction
- **Auto enhance** — automatic brightness, contrast, saturation, white balance, and sharpening
- **Smart crop** — face detection blended with user-defined crop center, drag directly on the preview to reposition
- **32 crop presets** across 7 platforms (Facebook, Instagram, LinkedIn, Pinterest, Twitter/X, YouTube, Custom)
- **Batch processing** — multithreaded with progress bar, ETA, and error counting
- **Export** — single image or batch export in JPG, PNG, WebP with configurable quality

## Requirements

- Python 3.11+
- Pillow
- OpenCV (lazy-loaded to avoid OpenBLAS crash)
- numpy
- tkinterdnd2

## Installation

```bash
git clone https://github.com/yourusername/photopilot.git
cd photopilot
python -m venv env
env\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

1. Click **"Abrir imagenes"** or drag-and-drop images/folders onto the window
2. Select a folder with **"Carpeta origen"**
3. Set output directory with **"Carpeta destino"**
4. Click a thumbnail to edit
5. Use crop presets and drag the preview to reposition
6. Adjust sliders for fine-tuning
7. Click **"Mejorar automaticamente"** for auto-enhance
8. Export with **"Exportar esta foto"** or **"Exportar todas"**
9. Use **"Procesar carpeta"** for batch processing

## Project Structure

```
PhotoPilot/
├── main.py                 # Entry point
├── config/                 # Theme, constants, settings
├── core/                   # State, pipeline, batch processor, exporter
├── gui/                    # Tkinter UI (app, widgets, sliders, crop presets)
├── opencv/                 # Smart crop with face detection
├── processing/             # Auto enhance, manual adjustments
├── utils/                  # Validators, aspect ratio helpers
└── assets/                 # Static resources
```

## Architecture

- **`AppState`** stores all per-image state in dicts (`_crop_presets`, `_crop_centers`, `_processing_settings`)
- **`ProcessingPipeline`** chains: auto-enhance → smart crop → manual adjustments
- **`PreviewPanel`** shows the processed result by default, switches to original + overlay during crop drag
- **`Exporter`** saves processed images with format-aware quality settings
- **`BatchProcessor`** runs multithreaded with real-time progress updates

## License

MIT
