# Arquitectura del Sistema FigmaToAngular

Este documento detalla la arquitectura técnica y los flujos de datos del sistema FigmaToAngular.

## Visión General

FigmaToAngular está diseñado como un sistema modular que procesa datos de diseño (Figma o imágenes) y los transforma en código Angular funcional. La arquitectura permite dos flujos principales de generación de código que se seleccionan automáticamente según las características del diseño.

## Diagrama de Arquitectura
```
┌────────────────┐      ┌─────────────────┐
│                │      │                 │
│  Interfaz de   │◄────►│ Administrador   │
│  Usuario       │      │ de Estado       │
│  (Streamlit)   │      │                 │
│                │      └────────┬────────┘
└───────┬────────┘               │
        │                        │
        ▼                        ▼
┌───────────────┐      ┌─────────────────┐
│               │      │                 │
│ Adquisición   │◄────►│ Preprocesador   │
│ de Datos      │      │ de Diseño       │
│               │      │                 │
└───────┬───────┘      └────────┬────────┘
        │                       │
        ▼                       ▼
┌───────────────┐      ┌─────────────────┐
│               │      │                 │
│ Analizador    │◄────►│ Selector de     │
│ de Estructura │      │ Estrategia      │
│               │      │                 │
└───────┬───────┘      └────────┬────────┘
        │                       │
        ▼                       ▼
┌─────────────────────┐  ┌─────────────────────┐
│                     │  │                     │
│ Generador           │  │ Generador           │
│ Estructural         │  │ Basado en IA        │
│ (Sistema de Nodos)  │  │ (OpenAI/Azure)      │
│                     │  │                     │
└──────────┬──────────┘  └──────────┬──────────┘
           │                        │
           ▼                        ▼
      ┌─────────────────────────────────┐
      │                                 │
      │     Postprocesador de Código    │
      │                                 │
      └────────────────┬────────────────┘
                       │
                       ▼
      ┌─────────────────────────────────┐
      │                                 │
      │ Visualizador y Exportación      │
      │                                 │
      └─────────────────────────────────┘
```

## Componentes Principales

### 1. Interfaz de Usuario (app.py)
- **Responsabilidad**: Proporcionar una interfaz gráfica amigable usando Streamlit
- **Funciones clave**:
  - Configuración de opciones de entrada
  - Visualización de resultados y vista previa
  - Gestión de interacciones del usuario

### 2. Administrador de Estado
- **Responsabilidad**: Gestionar el estado de la aplicación y datos entre sesiones
- **Componentes**:
  - Sesión de Streamlit
  - Variables de estado para histórico de conversiones
  - Almacenamiento temporal de datos de diseño

### 3. Adquisición de Datos
- **Responsabilidad**: Obtener datos de diseño de diferentes fuentes
- **Componentes**:
  - Cliente API Figma (`figma_api.py`)
  - Procesador de imágenes (`image_to_code.py`)
  - Normalizador de datos de entrada

### 4. Preprocesador de Diseño
- **Responsabilidad**: Transformar y normalizar datos de diseño
- **Procesos**:
  - Extracción de nodos (`utils.py:extract_nodes()`)
  - Aplanamiento de estructura jerárquica (`utils.py:flatten_figma_tree()`)
  - Limitación de nodos para evitar problemas de memoria

### 5. Analizador de Estructura
- **Responsabilidad**: Analizar y entender la estructura del diseño
- **Componentes**:
  - Sistema de nodos intermedios (`alt_nodes.py`)
  - Analizador de layout (`alt_nodes.py:analyze_layout()`)
  - Detector de patrones de diseño

### 6. Selector de Estrategia
- **Responsabilidad**: Determinar qué enfoque de generación utilizar
- **Componente principal**: `enhanced_generator.py:process_figma_with_mixed_approach()`
- **Factores de decisión**:
  - Complejidad del diseño
  - Presencia de Auto Layout
  - Uso de constraints
  - Preferencias del usuario (uso de Material UI)

### 7. Generador Estructural
- **Responsabilidad**: Generar código usando análisis estructural
- **Componentes**:
  - Generador Angular (`angular_generator.py`)
  - Generador de HTML/SCSS/TypeScript
  - Detector de componentes Material

### 8. Generador Basado en IA
- **Responsabilidad**: Generar código usando modelos de IA
- **Componentes**:
  - Generador de código por IA (`code_generator.py`)
  - Sistemas de prompts y contexto
  - Integración con APIs (OpenAI/Azure)

### 9. Postprocesador de Código
- **Responsabilidad**: Finalizar y optimizar el código generado
- **Procesos**:
  - Formateo de código
  - Incorporación de instrucciones adicionales
  - Integración de diferentes partes (HTML/SCSS/TS)

### 10. Visualizador y Exportación
- **Responsabilidad**: Mostrar y exportar los resultados
- **Funciones**:
  - Renderización de vista previa HTML
  - Exportación de archivos de componentes
  - Generación de documentación adicional

## Flujos de Datos Principales

### Flujo 1: Importación desde Figma
1. Usuario introduce token de acceso y clave de archivo Figma
2. `figma_api.py` recupera datos del diseño de la API de Figma
3. Se extraen y aplanan los nodos del diseño
4. El selector de estrategia evalúa la complejidad
5. Se genera código mediante el enfoque estructural o basado en IA
6. El resultado se muestra al usuario con opciones de exportación

### Flujo 2: Importación desde Imagen
1. Usuario carga una imagen de diseño
2. Se procesa la imagen y se prepara para la API de visión
3. Se usa la API de OpenAI para interpretar la imagen
4. Se genera el código Angular basado en la interpretación
5. El resultado se muestra al usuario

## Estrategia de Generación Dual

El sistema implementa un enfoque dual de generación, con dos estrategias complementarias:

### Enfoque Estructural
- **Cuándo se usa**: Diseños con estructura clara, uso de Auto Layout, componentes bien organizados
- **Ventajas**:
  - Mayor consistencia
  - Mejor rendimiento
  - Más eficiente en recursos
  - Control preciso del resultado
- **Componentes clave**:
  - Sistema de nodos intermedios (`AngularNode`)
  - Análisis de layout (flexbox, grid)
  - Generador Angular Material

### Enfoque basado en IA
- **Cuándo se usa**: Diseños complejos, layouts irregulares, necesidades especiales
- **Ventajas**:
  - Mayor flexibilidad
  - Mejor interpretación de diseños complejos
  - Capacidad para seguir instrucciones específicas
- **Componentes clave**:
  - Construcción de prompts optimizados
  - APIs de OpenAI/Azure
  - Sistema de división de nodos para superar límites de tokens

## Optimizaciones y Consideraciones Técnicas

### Gestión de Memoria
- Límites configurables de nodos a procesar
- División automática de diseños grandes
- Protección contra errores de memoria (OOM)

### Rendimiento
- Análisis muestral para diseños grandes
- Caché de resultados intermedios
- Procesamiento optimizado de árboles de nodos

### Robustez
- Manejo extensivo de errores
- Validación de entradas de usuario
- Comprobaciones de formato y estructura de datos

### Extensibilidad
- Arquitectura modular
- Interfaces bien definidas
- Capacidad para añadir nuevos generadores o analizadores

## Dependencias Externas

- **Streamlit**: Interfaz de usuario
- **OpenAI/Azure OpenAI**: Generación de código basada en IA
- **API de Figma**: Obtención de datos de diseño
- **Pillow**: Procesamiento de imágenes

## Conclusión

La arquitectura de FigmaToAngular está diseñada para ofrecer la máxima flexibilidad y robustez, combinando el análisis estructural detallado con la potencia de la generación de código por IA. Este enfoque dual permite manejar eficientemente una amplia variedad de diseños, desde simples a complejos, y proporcionar resultados de alta calidad en todos los casos.