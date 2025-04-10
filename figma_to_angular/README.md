# FigmaToAngular

Una aplicación que convierte diseños de Figma a código Angular (TypeScript, HTML, SCSS) utilizando inteligencia artificial y técnicas de análisis de diseño avanzadas.

![FigmaToAngular](images/figma_to_angular_logo.png)

## Características Principales

- **Importación de Diseños Figma**: Conecta directamente con la API de Figma para importar diseños.
- **Carga de Imágenes**: Alternativa para cargar diseños como imágenes PNG/JPG.
- **Sistema de Nodos Intermedios**: Arquitectura similar a AltNodes de FigmaToCode para un procesamiento optimizado.
- **Análisis de Layout Avanzado**: Detección automática de sistemas de layout como Flexbox y Grid.
- **Detección de Componentes Angular Material**: Generación inteligente de componentes Material UI.
- **Estimación de Costos**: Cálculo de costos API basado en el número de nodos.
- **Vista Previa de Código**: Visualización inmediata del HTML/CSS generado.
- **Soporte para OpenAI y Azure OpenAI**: Compatible con ambas APIs.

## Arquitectura

El proyecto está organizado en módulos especializados que trabajan juntos:

1. **Interface de Usuario (Streamlit)**: Facilita la interacción del usuario y muestra resultados.
2. **Procesamiento de Diseño**: 
   - Extracción de datos de Figma
   - Conversión a nodos intermedios
   - Análisis de layout y estructura
3. **Generación de Código**: 
   - Generador basado en IA (OpenAI/Azure)
   - Generador estructural basado en nodos intermedios
4. **Visualización y Exportación**: Previsualización del resultado y opciones de descarga.

## Diagrama de la Arquitectura

```
+------------------+     +---------------------+     +----------------------+
|                  |     |                     |     |                      |
|  Interface (UI)  +---->+  Procesamiento de   +---->+  Generación de       |
|  (Streamlit)     |     |  Diseño             |     |  Código              |
|                  |     |                     |     |                      |
+------------------+     +---------------------+     +----------------------+
                               ^                             |
                               |                             |
                               |                             v
                         +-----+-----+             +---------+---------+
                         |           |             |                   |
                         |  API de   |             |  Visualización    |
                         |  Figma    |             |  y Exportación    |
                         |           |             |                   |
                         +-----------+             +-------------------+
```

## Enfoque Técnico

### Sistema de Procesamiento Dual

El proyecto utiliza dos enfoques complementarios:

1. **Enfoque basado en IA**: Utiliza OpenAI (GPT-4o) para generar código a partir de diseños complejos. Ideal para diseños menos estructurados o necesidades especiales.

2. **Enfoque estructural**: Usa una representación intermedia para analizar sistemáticamente el diseño:
   - Convierte los nodos de Figma a una estructura intermedia (`AngularNode`)
   - Analiza las relaciones espaciales para detectar layouts
   - Genera código optimizado basándose en patrones detectados

### Optimización de Recursos

- Limitación inteligente del número de nodos procesados para evitar problemas de memoria
- Muestreo de nodos para la detección de features
- Manejo robusto de errores y casos límite

## Requisitos

- Python 3.7+ 
- Streamlit
- Cuenta en OpenAI o Azure OpenAI
- Token de acceso personal de Figma (para importación directa)

## Configuración Local

1. Clona este repositorio
2. Instala las dependencias: `pip install -r requirements.txt`
3. Ejecuta la aplicación: `streamlit run app.py`
4. Configura las API keys necesarias en la interfaz

## Estructura de Archivos

```
/figma_to_angular
│
├── app.py                  # Punto de entrada de la aplicación (Streamlit UI)
├── figma_api.py            # Cliente para interactuar con la API de Figma
├── utils.py                # Funciones auxiliares generales
│
├── alt_nodes.py            # Sistema de nodos intermedios
├── angular_generator.py    # Generador de código Angular y Angular Material
├── enhanced_generator.py   # Integración de generadores
│
├── code_generator.py       # Generador basado en OpenAI/Azure
├── image_to_code.py        # Procesamiento de imágenes a código
├── cost_estimator.py       # Estimación de costos de API
│
└── api_tools.py            # Herramientas auxiliares para APIs
```

## Documentación Adicional

- [Guía de Usuario](GUIA_USUARIO.md)
- [Documentación Técnica](DOCUMENTACION_TECNICA.md)
- [Referencia de Módulos](MODULOS.md)

## Licencia

MIT