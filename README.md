# Dengue por municipio en Colombia · Actividad 2

**Integrante:** Jhonatan Gamboa  
**Entrega:** notebook de adquisición (20 % del corte 1) y sustentación oral (10 %).

## Pregunta y alcance

¿Qué municipios y periodos epidemiológicos concentran más notificaciones de dengue entre 2021 y 2025, y qué patrones temporales pueden orientar la vigilancia, prevención y control de las autoridades de salud?

En esta entrega se documenta la **adquisición y el cruce**. El análisis descriptivo usa registros de dengue (evento 210) de 2021–2025. El cruce con la segunda tabla puede verificarse solo en 2021–2022, porque esa es la cobertura disponible de la publicación nacional agregada consultada. No se estiman tasas, riesgo individual ni causalidad.

El notebook debe quedar específicamente en **`/notebooks`**. Los cinco Excel originales pesan alrededor de 400 MB en conjunto, por lo que se conservan fuera de GitHub y se publica la tabla depurada y agregada. No se publican identificadores de notificaciones ni variables individuales.

## Fuentes verificadas

| Fuente | Origen | Cobertura utilizada | Archivo preparado |
|---|---|---|---|
| Microdatos dengue, evento 210 | [INS/SIVIGILA](https://portalsivigila.ins.gov.co/buscador), cinco Excel originales facilitados para el proyecto | 2021–2025 | `ins_dengue_municipio_semana_2021_2025.csv` |
| Tabla nacional agregada de vigilancia | [Datos Abiertos Colombia, recurso 4hyg-wa9d](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Datos-de-Vigilancia-en-Salud-P-blica-de-Colombia/4hyg-wa9d) | 2021–2022 para evento 210 | `portal_dengue_municipio_semana_2021_2022.csv` |

La ficha inicial y el README anterior citaban [`ke8u-qixu`](https://www.datos.gov.co/dataset/Dengue/ke8u-qixu) como fuente de notificaciones nacionales. Su metadata lo identifica como un catálogo federado publicado por la Alcaldía de Medellín, con un CSV de esa ciudad; no ofrece la tabla nacional municipio + semana prevista para este cruce. Se sustituyó por el recurso nacional `4hyg-wa9d` sin cambiar la pregunta de decisión. La segunda fuente agregada y los microdatos provienen del mismo sistema de vigilancia, así que sus conteos **no se suman** ni constituyen confirmación independiente. Tras excluir 177 filas del portal marcadas `EXTERIOR`, las claves y conteos 2021–2022 coinciden en ambas publicaciones.

## Cómo abrir en Google Colab

1. Abra [Google Colab](https://colab.research.google.com/) y seleccione **Archivo → Subir notebook**. Seleccione `notebooks/01_adquisicion_dengue.ipynb`.
2. Ejecute las celdas en orden. La primera celda de código pedirá cargar los dos **CSV** de `data/processed/`. Selecciónelos juntos.
3. Para sustentar, muestre las celdas de lectura (`.shape`, `.head()`), el `pd.merge`, la verificación de filas y el diccionario. Las salidas locales ya están guardadas en el notebook para revisarlo en GitHub.

En un clon de GitHub, el notebook detecta los CSV tanto si se ejecuta desde la raíz como desde `/notebooks`.

## Reproducir la preparación de datos

Con los cinco `Datos_YYYY_210.xlsx` en `data/raw/`, en la raíz del proyecto o en la carpeta superior:

```bash
python -m pip install -r requirements.txt
python preparar_datos.py
python crear_notebook.py
```

`preparar_datos.py` lee los Excel en modo de solo lectura, conserva `COD_EVE=210`, `COD_PAIS_O=170`, año, semana y códigos/nombres del **municipio de ocurrencia**. Forma el código municipal de cinco dígitos con `COD_DPTO_O` + `COD_MUN_O`, agrupa las notificaciones y exporta CSV y Excel compactos. También consulta la API pública `4hyg-wa9d` y guarda un reporte de calidad. Los originales permanecen intactos.

La clave de cruce del notebook es `(anio, semana, codigo_municipio)`. `pd.merge(..., how="left", validate="one_to_one", indicator=True)` conserva todas las filas de la fuente INS, verifica la unicidad y muestra las parejas ausentes. Un valor vacío del portal no significa cero casos.

### Resultado comprobado con los archivos entregados

Se procesaron 671.618 filas originales de los cinco Excel. Se excluyeron 1.401 con país de ocurrencia distinto de Colombia (`COD_PAIS_O != 170`); quedaron **670.217 notificaciones**, agrupadas en **84.895 filas**. El portal aportó **22.187 filas nacionales** para 2021–2022 tras excluir 177 marcadas `EXTERIOR`. El cruce dejó **84.895 filas antes y después**. Todas las 22.187 claves emparejadas tienen el mismo conteo en ambas publicaciones.

| Año | Notificaciones INS | Filas municipio-semana | Filas con pareja en portal |
|---:|---:|---:|---:|
| 2021 | 49.174 | 9.781 | 9.781 |
| 2022 | 65.428 | 12.406 | 12.406 |
| 2023 | 126.166 | 17.586 | 0 |
| 2024 | 309.166 | 26.061 | 0 |
| 2025 | 120.283 | 19.061 | 0 |

## Estado de la rúbrica

| Requisito | Evidencia |
|---|---|
| Lectura de dos fuentes con pandas | Sección 2 del notebook: `.shape`, `.head()`, `.dtypes` |
| Cruce y número de filas antes/después | Secciones 3–4: clave validada, `pd.merge`, aserción y cobertura |
| Diccionario de datos | Sección 5: columna, tipo, significado y fuente de todas las columnas cruzadas |
| Organización y repositorio | Notebook comentado en `/notebooks`, datos en `/data/processed`, este README |
| Coherencia con la ficha | Municipio de ocurrencia y semana epidemiológica, 2021–2025, para priorizar vigilancia |

## Límites y siguientes pasos

- Los datos son **notificaciones**, no todas las infecciones. Pueden existir cambios de clasificación y de corte entre publicaciones.
- La segunda tabla termina en 2022 para el evento 210; su ausencia en 2023–2025 no se rellena con ceros.
- Los totales absolutos no son tasas de incidencia ni miden por sí solos el riesgo municipal. Para comparar riesgo se necesitan denominadores de población y reglas de comparabilidad temporal.
- La hipótesis de estacionalidad y su posible relación con lluvias es preliminar. Estas fuentes no contienen lluvia; el mecanismo deberá probarse con datos adicionales y análisis posterior.
