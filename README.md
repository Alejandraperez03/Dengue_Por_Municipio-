# Análisis de Salud Pública: Casos de Dengue por Municipio en Colombia

Este proyecto está diseñado para analizar, segmentar y predecir el comportamiento epidemiológico del dengue en Colombia, permitiendo identificar zonas críticas y patrones estacionales para optimizar la toma de decisiones en salud pública.

## ❓ Pregunta Analítica
**¿Qué municipios o periodos concentran mayor riesgo de dengue, y qué patrones estacionales existen en el territorio nacional?**

---

## 📊 Fuentes de Datos
El proyecto se alimenta de dos fuentes oficiales de **Datos Abiertos Colombia**:
1. **Dengue — Notificaciones por municipio**: Datos de reportes y vigilancia epidemiológica. 
   * [Enlace al dataset](https://www.datos.gov.co/dataset/Dengue/ke8u-qixu)
2. **Dengue grave — Casos y mortalidad**: Datos específicos sobre la severidad y desenlaces fatales del evento.
   * [Enlace al dataset](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Dengue-grave/n4ab-jkpv)

---

## 🛠️ Alcance y Componentes del Proyecto

El desarrollo del proyecto se divide en cuatro fases principales, estructuradas en los cuadernos de trabajo y aplicaciones correspondientes:

* **1. Análisis Exploratorio de Datos (EDA):** Identificación de tendencias históricas por municipio y comportamiento de los casos a lo largo de las semanas y meses epidemiológicos para hallar ciclos repetitivos.
* **2. Segmentación de Riesgo:** Agrupación (*clustering*) de municipios según su volumen de carga epidemiológica, letalidad y estacionalidad del riesgo.
* **3. Modelo Predictivo:** Desarrollo de un modelo de Machine Learning enfocado en anticipar brotes epidemiológicos o clasificar de manera temprana el nivel de riesgo por municipio.
* **4. Dashboard Interactivo:** Creación de un mapa epidemiológico dinámico que visualiza alertas tempranas por zona y facilita el monitoreo geográfico.

---

## 📁 Estructura del Repositorio

* **`data/`**: Contiene los conjuntos de datos. *Nota: Los archivos de datos crudos deben descargarse de los enlaces oficiales.*
  * `raw/`: Archivos CSV originales sin modificaciones.
  * `processed/`: Datos limpios, indexados por municipio y semana epidemiológica, listos para los modelos.
* **`notebooks/`**: Cuadernos de Jupyter numerados secuencialmente según las fases del proyecto (EDA, Segmentación, Modelado).
* **`dashboard/`**: Código fuente y recursos de la aplicación web visual (mapa epidemiológico).

---

## 🚀 Cómo Empezar
1. Clona este repositorio: `git clone <url-de-tu-repositorio>`
2. Descarga los datasets de los enlaces en la sección de **Fuentes de Datos** y ubícalos en `data/raw/`.
3. Instala las dependencias necesarias (se recomienda usar un entorno virtual): `pip install -r requirements.txt`
