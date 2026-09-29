"""Genera y ejecuta localmente el notebook de adquisición a partir de los CSV."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import os

import nbformat as nbf


ROOT = Path(__file__).resolve().parent
NOTEBOOK = ROOT / "notebooks" / "01_adquisicion_dengue.ipynb"
NOTEBOOK.parent.mkdir(parents=True, exist_ok=True)

cells = []


def md(source):
    cells.append(nbf.v4.new_markdown_cell(source))


def code(source):
    cells.append(nbf.v4.new_code_cell(source))


md("""# Actividad 2 · Adquisición y cruce de datos de dengue

**Proyecto:** dengue por municipio en Colombia · **Integrante:** Jhonatan Gamboa  
**Corte 1:** notebook de adquisición (20 %) y sustentación oral (10 %).  
**Pregunta de decisión:** ¿Qué municipios y semanas epidemiológicas concentran más notificaciones de dengue entre 2021 y 2025 para orientar la vigilancia, prevención y control?

Este cuaderno entrega las cinco evidencias de la rúbrica: lectura con pandas, `.head()`/`.shape`, cruce con `pd.merge`, control de filas y diccionario. Los conteos de casos reportados **no son tasas de riesgo**; para hablar de incidencia comparable entre municipios se requiere población denominadora. Tampoco se infiere causalidad ni se diagnostican personas.""")

md("""## 1. Fuentes y preparación

1. **INS/SIVIGILA, microdatos de dengue (evento 210), 2021–2025.** Archivos originales `Datos_YYYY_210.xlsx` aportados para la actividad. `preparar_datos.py` selecciona evento, año, semana y **municipio de ocurrencia**; descarta filas con país/código/periodo inválidos y agrega notificaciones a una fila por municipio y semana. Resultado: `ins_dengue_municipio_semana_2021_2025.csv`. [Portal de microdatos INS](https://portalsivigila.ins.gov.co/buscador).
2. **Datos Abiertos Colombia/INS, tabla nacional agregada de vigilancia.** Se descargan los registros del evento 210, 2021–2025, del recurso [`4hyg-wa9d`](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Datos-de-Vigilancia-en-Salud-P-blica-de-Colombia/4hyg-wa9d). La consulta devolvió datos **solo para 2021–2022**. Se excluyen las filas marcadas `EXTERIOR` para mantener el mismo alcance nacional. Resultado: `portal_dengue_municipio_semana_2021_2022.csv`.

**Trazabilidad y cautela.** Ambas publican datos del sistema de vigilancia; no se suman entre sí ni se interpretan como mediciones independientes. El enlace `ke8u-qixu` de la ficha es un catálogo federado de **Medellín**, no una tabla nacional con clave municipio + semana. Este cuaderno usa el recurso nacional anterior y conserva la pregunta de la ficha. Los CSV y el Excel depurado están en `data/processed/`; los Excel originales no se modifican.""")

md("""### Ejecutar en Google Colab o desde GitHub

En Colab: importa este `.ipynb`, ejecuta la primera celda de código y, cuando aparezca el selector, sube los **dos CSV** de `data/processed/` (no hace falta subir los cinco Excel grandes). En un clon del repositorio, ejecuta desde la raíz o desde `notebooks/`; los CSV se detectan solos. Colab borra los archivos subidos al cerrar la sesión.""")

code("""from pathlib import Path
import sys
import pandas as pd

ARCHIVOS = {
    "ins": "ins_dengue_municipio_semana_2021_2025.csv",
    "portal": "portal_dengue_municipio_semana_2021_2022.csv",
}
CARPETAS = [Path("data/processed"), Path("../data/processed"),
            Path("actividad2/data/processed"), Path(".")]

def localizar(nombre):
    return next((ruta / nombre for ruta in CARPETAS if (ruta / nombre).is_file()), None)

faltantes = [nombre for nombre in ARCHIVOS.values() if localizar(nombre) is None]
if faltantes and "google.colab" in sys.modules:
    from google.colab import files
    print("Sube los dos CSV de data/processed/:", ", ".join(faltantes))
    files.upload()
faltantes = [nombre for nombre in ARCHIVOS.values() if localizar(nombre) is None]
if faltantes:
    raise FileNotFoundError(f"Faltan archivos: {faltantes}. Consulta el README.")

ruta_ins = localizar(ARCHIVOS["ins"])
ruta_portal = localizar(ARCHIVOS["portal"])
print("INS:", ruta_ins)
print("Portal:", ruta_portal)""")

md("""## 2. Leer y verificar las dos fuentes

`codigo_municipio` se lee como texto para preservar ceros iniciales. Se muestran cantidad de filas y columnas, primeras cinco filas y tipos, tal como exige la rúbrica. Cada fila ya es un **municipio en un año y una semana epidemiológica**.""")

code("""ins = pd.read_csv(ruta_ins, dtype={"codigo_municipio": "string"})
portal = pd.read_csv(ruta_portal, dtype={"codigo_municipio": "string"})

print("INS .shape:", ins.shape)
print(ins.head().to_string(index=False))
print("\\nINS .dtypes:\\n", ins.dtypes.to_string())
print("\\nPortal .shape:", portal.shape)
print(portal.head().to_string(index=False))
print("\\nPortal .dtypes:\\n", portal.dtypes.to_string())""")

md("""## 3. Clave de cruce y control de calidad

La clave es **(`anio`, `semana`, `codigo_municipio`)**: mismo periodo y mismo municipio de **ocurrencia** en ambas fuentes. `codigo_municipio` es DANE de cinco dígitos: en los Excel se forma con dos dígitos de departamento + tres de municipio; en la API se completa a cinco dígitos. El nombre del municipio no es clave porque puede repetirse o escribirse distinto. Antes del cruce, ambas fuentes deben tener una sola fila por clave.""")

code("""CLAVE = ["anio", "semana", "codigo_municipio"]
for nombre, df in [("INS", ins), ("Portal", portal)]:
    print(nombre, "filas:", len(df),
          "claves incompletas:", int(df[CLAVE].isna().any(axis=1).sum()),
          "claves duplicadas:", int(df.duplicated(CLAVE).sum()))
    assert df[CLAVE].notna().all().all(), f"Clave incompleta en {nombre}"
    assert not df.duplicated(CLAVE).any(), f"Clave duplicada en {nombre}"
    assert df.codigo_municipio.str.fullmatch(r"\\d{5}").all(), f"Código incorrecto en {nombre}"
""")

md("""## 4. Cruce con `pd.merge` y verificación de filas

El cruce es **left** con INS como base, para conservar 2021–2025. `validate="one_to_one"` detiene la ejecución si una fuente tiene claves duplicadas. `indicator=True` permite medir la cobertura: los 2023–2025 quedan sin pareja porque la tabla del portal termina en 2022. El valor faltante del portal **no equivale a cero casos**.""")

code("""filas_antes = len(ins)
cruce = pd.merge(
    ins,
    portal[CLAVE + ["casos_portal"]],
    on=CLAVE,
    how="left",
    validate="one_to_one",
    indicator=True,
)
cruce["casos_portal"] = cruce["casos_portal"].astype("Int64")
print("Filas INS antes:", filas_antes)
print("Filas después del cruce:", len(cruce))
print("Cambio de filas:", len(cruce) - filas_antes)
print("Estado del cruce:\\n", cruce["_merge"].value_counts().to_string())
assert len(cruce) == filas_antes, "El cruce perdió o duplicó filas"
print("\\nPrimeras cinco filas cruzadas:\\n", cruce.head().to_string(index=False))""")

md("""### Cobertura y diferencias entre fuentes

La comparación de conteos solo se hace donde hay pareja. En estos archivos, todas las parejas 2021–2022 tienen el mismo conteo, coherente con su origen común en SIVIGILA; esto no implica validación independiente. Los años posteriores a 2022 permanecen útiles para el análisis descriptivo del INS, pero no pueden contrastarse con este portal.""")

code("""resumen = cruce.groupby("anio", as_index=False).agg(
    filas_ins=("casos_ins", "size"),
    notificaciones_ins=("casos_ins", "sum"),
    filas_con_pareja=("casos_portal", "count"),
)
resumen["porcentaje_con_pareja"] = (
    100 * resumen["filas_con_pareja"] / resumen["filas_ins"]
).round(1)
print(resumen.to_string(index=False))

parejas = cruce.loc[cruce["casos_portal"].notna()].copy()
parejas["diferencia_ins_menos_portal"] = (
    parejas["casos_ins"] - parejas["casos_portal"]
)
print("\\nFilas emparejadas:", len(parejas))
print("Conteos iguales en las parejas:",
      int((parejas["diferencia_ins_menos_portal"] == 0).sum()))
diferencias = parejas.loc[parejas["diferencia_ins_menos_portal"] != 0,
                           CLAVE + ["casos_ins", "casos_portal", "diferencia_ins_menos_portal"]]
print("Parejas con conteos distintos:", len(diferencias))
if not diferencias.empty:
    print(diferencias.head(5).to_string(index=False))""")

md("""## 5. Diccionario de datos del conjunto cruzado

El tipo mostrado es el de pandas **después** del cruce. `casos_portal` es entero anulable (`Int64`) porque 2023–2025 no tienen dato en esa fuente. `casos_ins` y `casos_portal` son conteos de registros/notificaciones publicados; no se suman.""")

code("""DESCRIPCIONES = {
    "anio": ("INS y portal", "Año epidemiológico de la notificación agregada."),
    "semana": ("INS y portal", "Semana epidemiológica, de 1 a 53."),
    "codigo_municipio": ("INS y portal", "Código DANE de cinco dígitos del municipio de ocurrencia."),
    "departamento": ("INS", "Nombre del departamento de ocurrencia; nombre modal por código."),
    "municipio": ("INS", "Nombre del municipio de ocurrencia; nombre modal por código."),
    "casos_ins": ("Microdatos INS", "Número de filas válidas del evento 210 para esa clave."),
    "casos_portal": ("Portal Datos Abiertos/INS", "Conteo publicado para esa clave; vacío si no hay pareja."),
    "_merge": ("Derivada por pd.merge", "Estado del cruce: both o left_only."),
}
diccionario = pd.DataFrame([
    {"columna": columna, "tipo_pandas": str(cruce[columna].dtype),
     "fuente": DESCRIPCIONES[columna][0],
     "significado": DESCRIPCIONES[columna][1]}
    for columna in cruce.columns
])
print(diccionario.to_string(index=False))
assert set(diccionario.columna) == set(cruce.columns)""")

md("""## 6. Primer resultado descriptivo alineado con la pregunta

La tabla siguiente ordena municipios por **volumen total de notificaciones** en los cinco años del INS. Esta es una aproximación inicial para priorizar revisión; municipios grandes pueden tener más casos por tener más habitantes. En una siguiente fase se agregarán denominadores poblacionales y se evaluará estacionalidad sin usar información futura para predecir periodos anteriores.""")

code("""top_municipios = (
    ins.groupby(["codigo_municipio", "departamento", "municipio"], as_index=False)
       ["casos_ins"].sum()
       .sort_values("casos_ins", ascending=False)
       .head(10)
)
print(top_municipios.to_string(index=False))""")

md("""## 7. Para explicar en la sustentación

- **Decisión:** localizar municipios y semanas con más notificaciones para orientar vigilancia y prevención.
- **Dos fuentes:** microdatos INS 2021–2025 y agregado nacional del portal 2021–2022; ambas se leen con pandas.
- **Cruce:** año + semana + código de municipio de ocurrencia. Ejecutar la celda de `pd.merge` y mostrar filas antes/después y `resumen`.
- **Diccionario:** mostrar la tabla anterior y explicar `casos_portal` vacío fuera de cobertura.
- **Riesgo resuelto:** los códigos de municipio tenían formato distinto (3 dígitos municipales en Excel frente a 5 dígitos DANE en el portal); se normalizaron. La disponibilidad 2021–2022 y las diferencias de conteo siguen documentadas. Los casos notificados no equivalen a incidencia ni a infecciones totales.

**Hipótesis inicial, aún por contrastar:** pueden repetirse picos en ciertas semanas por municipio. La lluvia podría favorecer criaderos de *Aedes* y aumentar la transmisión, pero estas dos tablas no contienen lluvia ni prueban ese mecanismo.""")

notebook = nbf.v4.new_notebook(
    cells=cells,
    metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
        "colab": {"name": NOTEBOOK.name, "provenance": []},
    },
)

# Ejecutar las celdas de código para guardar evidencias visibles también en GitHub.
scope = {"__name__": "__main__"}
old_cwd = Path.cwd()
os.chdir(ROOT)
try:
    execution_count = 0
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        execution_count += 1
        output = StringIO()
        with redirect_stdout(output):
            exec(compile(cell.source, f"celda_{execution_count}", "exec"), scope)
        cell.execution_count = execution_count
        if output.getvalue():
            cell.outputs = [nbf.v4.new_output("stream", name="stdout", text=output.getvalue())]
finally:
    os.chdir(old_cwd)

nbf.validate(notebook)
nbf.write(notebook, NOTEBOOK)
print(f"Creado: {NOTEBOOK}")
