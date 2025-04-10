# Figma2Code - Conversor de Figma a Angular

## Descripción
Herramienta para convertir diseños de Figma a código Angular. Este proyecto permite transformar automáticamente diseños de Figma en componentes Angular funcionales, manteniendo la estructura y el estilo del diseño original.

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/fjcv2020/Figma2Code.git
cd figma2code
```

2. Crea y activa un entorno virtual:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Configura tu token de Figma en el archivo `.env`:
```
FIGMA_TOKEN=tu_token_aqui
```

2. Ejecuta la aplicación:
```bash
streamlit run app.py
```

3. En el navegador, ingresa:
   - URL del archivo Figma
   - ID del nodo específico (opcional)
   - Presiona "Convertir"

## Características

- Conversión automática de diseños Figma a componentes Angular
- Soporte para estilos, colores y tipografía
- Generación de código TypeScript y HTML
- Interfaz de usuario intuitiva con Streamlit
- Estimación de costos de desarrollo

## Documentación
La documentación completa se encuentra en la carpeta `docs/`:
- [Metodología](docs/METODOLOGIA.md)
- [Arquitectura](docs/ARQUITECTURA.md)
- [Módulos](docs/MODULOS.md)
- [Guía de Usuario](docs/GUIA_USUARIO.md)
- [Documentación Técnica](docs/DOCUMENTACION_TECNICA.md)

## Requisitos

- Python 3.8+
- Node.js 14+
- Angular CLI
- Token de API de Figma

## Licencia
MIT License - Ver [LICENSE](LICENSE) para más detalles. 