# Trabajo 1 — Construcción de Software II

**Integrantes:**
- David Luza Ccorimanya
- Henry Javier Medina Malpartida

Aplicación Python que recibe la URL de una página web y devuelve el título, la cantidad de palabras, la cantidad de caracteres y la fecha/hora del análisis.

## Requisitos

- Python 3.10+
- pip

## Configuración

```bat
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Uso

```bat
python app.py
```

---

## LAB-1: Construcción segura de una aplicación Python con pip

Este documento registra la construcción de la aplicación *Security News Analyzer* y el análisis completo de su cadena de dependencias: cómo se instalan, cómo se relacionan entre sí (directas frente a transitivas), qué vulnerabilidades conocidas presentan y cómo se remedian.

---

### 1. Caso de estudio

*Security News Analyzer* recibe la URL de una noticia y devuelve el título de la página, la cantidad de palabras y caracteres, y la fecha/hora del análisis. Para ello se apoya en dos dependencias externas:

- `requests` — descarga el contenido de la URL.
- `beautifulsoup4` — parsea el HTML y extrae el texto.

La idea central del laboratorio aparece desde el inicio: el desarrollador instala `requests` y `beautifulsoup4`, pero esas librerías **necesitan otras librerías para funcionar**. Esas librerías adicionales son las *dependencias transitivas*, y son las que concentran la mayor parte del riesgo de seguridad.

### Código de la aplicación (`app.py`)

```python
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def analyze_url(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string if soup.title else "Sin título"

    text = soup.get_text(separator=" ", strip=True)
    words = text.split()

    return {
        "url": url,
        "title": title,
        "characters": len(text),
        "words": len(words),
        "analyzed_at": datetime.now(),
    }


def main():
    print("=== Security News Analyzer ===")
    url = input("Ingrese una URL: ")

    try:
        result = analyze_url(url)
        print("\nResultado")
        print("-" * 40)
        print(f"Título: {result['title']}")
        print(f"Caracteres: {result['characters']}")
        print(f"Palabras: {result['words']}")
        print(f"Fecha: {result['analyzed_at']}")
    except requests.exceptions.RequestException as error:
        print(f"Error al acceder a la URL: {error}")


if __name__ == "__main__":
    main()
```

---

### 2. Preparación del entorno virtual

Se crea el entorno virtual dentro del proyecto y se activa antes de instalar nada, de modo que las dependencias queden aisladas y no contaminen la instalación global de Python.

```bat
cd tarea1-cs2
python -m venv .venv
.venv\Scripts\activate.bat
```

![Creación y activación del entorno virtual en CMD de VS Code](<assets/creación del entorno venv.png>)

Con el prefijo `(.venv)` en el prompt se confirma que el entorno está activo y que las siguientes instalaciones se harán dentro de él.

---

### 3. Instalación de dependencias

Las dependencias se instalan a partir del archivo `requirements.txt`:

```bat
pip install -r requirements.txt
```

`pip` va resolviendo el árbol completo: además de las librerías que se pidieron explícitamente, descarga todo lo que estas necesitan para funcionar.

![pip install — recolección de paquetes, primera parte (beautifulsoup4 hasta msgpack)](<assets/installacion de requirements.png>)

![pip install — recolección de paquetes, segunda parte (nab-* hasta pipdeptree)](<assets/installacion de requirements 2.png>)

![pip install — recolección de paquetes, tercera parte (requests, rich, urllib3, colorama)](<assets/installacion de requirements 3.png>)

![pip install — descarga de wheels desde caché local](<assets/installacion de requirements 4.png>)

![pip install — instalación completada con lista completa de paquetes](<assets/installacion de requirements 5.png>)

En la última evidencia se observa el `Successfully installed ...` con todos los paquetes instalados, notablemente más que las dependencias pedidas de forma directa.

---

### 4. Dependencias directas y transitivas

Con el entorno ya poblado se lista todo lo instalado:

```bat
pip list
```

![Salida de pip list con todos los paquetes del entorno virtual](<assets/pip list.png>)

Aquí se hace visible la distinción clave del laboratorio:

- **Dependencia directa:** la que el proyecto solicita explícitamente (`requests`, `beautifulsoup4`).
- **Dependencia transitiva:** la que es requerida por otra dependencia y que el proyecto nunca pidió de forma directa (por ejemplo `urllib3`, `certifi`, `idna`, `charset-normalizer`, `soupsieve`).

Por eso `pip list` —y también `pip freeze`— muestran más paquetes de los que aparecen en los `import` del código.

---

### 5. Árbol de dependencias con pipdeptree

Para visualizar la relación jerárquica entre paquetes se usa `pipdeptree`:

```bat
pipdeptree
```

![Árbol de dependencias — primera parte: beautifulsoup4, pip_audit y requests con sus transitivas](<assets/pipdeptree.png>)

![Árbol de dependencias — segunda parte: nab-project, nab-index y continuación del árbol completo](<assets/pipdeptree 2.png>)

El árbol muestra con claridad que `requests` cuelga de sus transitivas `certifi`, `charset-normalizer`, `idna` y `urllib3`, y que cada una llega con un rango de versión requerido (`required`) y una versión efectivamente instalada (`installed`). Esa diferencia entre "lo requerido" y "lo instalado" es exactamente lo que permite que una transitiva se quede en una versión vulnerable aunque siga siendo *compatible*.

**Dependencias directas** (instaladas explícitamente):

| Paquete         | Versión  |
|-----------------|----------|
| `requests`      | 2.34.2   |
| `beautifulsoup4`| 4.15.0   |

**Dependencias transitivas** (instaladas automáticamente):

| Dependencia          | Requerida por      |
|----------------------|--------------------|
| `urllib3`            | requests           |
| `certifi`            | requests           |
| `charset-normalizer` | requests           |
| `idna`               | requests           |
| `soupsieve`          | beautifulsoup4     |

---

### 6. Detección de vulnerabilidades con pip-audit

Se aplica *Software Composition Analysis* (SCA) sobre las dependencias instaladas. Para demostrar el funcionamiento de `pip-audit`, se instalaron versiones antiguas con CVEs conocidos compatibles con Python 3.13:

```bat
pip install --force-reinstall requests==2.31.0 urllib3==2.0.6 certifi==2023.5.7
pip-audit
```

![pip-audit — 15 vulnerabilidades conocidas en 3 paquetes: certifi, requests y urllib3](<assets/pip-audit part1.png>)

El análisis reporta **15 vulnerabilidades conocidas en 3 paquetes**:

| Paquete   | Versión   | Advisory           | Versión corregida |
|-----------|-----------|--------------------|-------------------|
| certifi   | 2023.5.7  | PYSEC-2023-135     | 2023.7.22         |
| certifi   | 2023.5.7  | PYSEC-2024-230     | 2024.7.4          |
| requests  | 2.31.0    | PYSEC-2026-1873    | 2.32.0            |
| requests  | 2.31.0    | PYSEC-2026-1872    | 2.32.4            |
| requests  | 2.31.0    | PYSEC-2026-2275    | 2.33.0            |
| urllib3   | 2.0.6     | PYSEC-2023-212     | 1.26.18 / 2.0.7   |
| urllib3   | 2.0.6     | PYSEC-2026-141     | 2.7.0             |
| urllib3   | 2.0.6     | PYSEC-2026-1999    | 2.5.0             |
| urllib3   | 2.0.6     | PYSEC-2026-1998    | 2.6.0             |
| urllib3   | 2.0.6     | PYSEC-2026-1995    | 1.26.19 / 2.2.2   |
| urllib3   | 2.0.6     | PYSEC-2026-1994    | 2.6.0             |
| urllib3   | 2.0.6     | PYSEC-2026-1996    | 2.6.3             |

> De los tres paquetes afectados, `requests` es **directo**, mientras que `certifi` y `urllib3` son **transitivos**. El grueso del riesgo se concentra en `urllib3`, un paquete que la aplicación jamás importó de forma directa.

---

### 7. ¿Dónde está la vulnerabilidad?

La aplicación no usa `urllib3` directamente, pero **sí está afectada** por sus vulnerabilidades, porque `requests` depende de él:

```
Security News Analyzer
        │
        ▼
     requests        (dependencia directa)
        │
        ▼
     urllib3         (dependencia transitiva)
        │
        ▼
  vulnerabilidad
```

**¿Quién es responsable de solucionarla?** El equipo que mantiene la aplicación. Aunque la vulnerabilidad viva en una dependencia transitiva, es responsabilidad del proyecto identificarla, evaluar su impacto y actualizar la versión afectada.

---

### 8. Actualización de dependencias

Primero se consulta qué paquetes tienen versiones más nuevas disponibles:

```bat
pip list --outdated
```

![pip list --outdated — muestra requests 2.31.0→2.34.2 y urllib3 2.0.6→2.7.0 como desactualizados](<assets/pip list --outdated.png>)

Se actualiza la dependencia directa afectada:

```bat
pip install --upgrade requests
```

![pip install --upgrade requests — desinstala 2.31.0 e instala 2.34.2 exitosamente](<assets/pip install --upgrade requests.png>)

`requests` pasa de `2.31.0` a `2.34.2`. Se vuelve a auditar:

```bat
pip-audit
```

![pip-audit tras actualizar requests — baja a 12 vulnerabilidades: certifi y urllib3 siguen afectados](<assets/pip-audit part2 segunda vez despues de actualizar.png>)

#### El punto clave del laboratorio

Tras actualizar `requests`, `pip-audit` baja de 15 a **12 vulnerabilidades**, pero **`certifi` y `urllib3` siguen apareciendo**. Cuando `pip` actualizó `requests`, revisó que `urllib3 2.0.6` satisface el rango `>=1.26,<3` que `requests` exige, por lo que no lo tocó.

> **Actualizar una dependencia directa no garantiza que sus dependencias transitivas queden en versiones seguras.** Hay que actualizar explícitamente cada paquete vulnerable que reporte `pip-audit`.

```bat
pip install --upgrade certifi urllib3
```

![pip install --upgrade certifi urllib3 — desinstala certifi 2023.5.7 y urllib3 2.0.6, instala 2026.7.22 y 2.7.0](<assets/pipeline part5.png>)

Con las transitivas ya corregidas, la auditoría final queda limpia:

```bat
pip-audit
```

![pip-audit final — No known vulnerabilities found](<assets/pip-audit final sin vulnerabilidades.png>)

#### Antes / Después

| Estado      | Paquetes vulnerables          | Vulnerabilidades |
|-------------|-------------------------------|------------------|
| Antes       | certifi, requests, urllib3    | 15               |
| Intermedio  | certifi, urllib3              | 12               |
| Después     | ninguno                       | 0                |

---

### 9. Extensión: pipeline de seguridad con Security Gate

Se implementó `security_pipeline.py` que automatiza el análisis y aplica una **puerta de seguridad**: ejecuta `pip list`, `pipdeptree` y `pip-audit`, guarda el reporte en `dependency-report.txt` y decide si el build puede continuar.

```bat
python security_pipeline.py
```

![Pipeline — sección pip list con todos los paquetes instalados y sus versiones](<assets/pipeline part1.png>)

![Pipeline — árbol pipdeptree primera parte: beautifulsoup4, pip_audit, requests y sus transitivas](<assets/pipeline part2.png>)

![Pipeline — árbol pipdeptree segunda parte y cabecera de sección pip-audit](<assets/pipeline part3.png>)

![Pipeline — resultado pip-audit con 12 vulnerabilidades en certifi y urllib3, y mensaje FAIL](<assets/pipeline part4.png>)

La regla es simple: **si `pip-audit` encuentra vulnerabilidades, el pipeline se detiene con `[FAIL]`**; solo si la auditoría está limpia el proceso continúa. En la evidencia, el gate detecta las vulnerabilidades de `certifi` y `urllib3` y detiene la ejecución, dejando el reporte guardado en `dependency-report.txt`. Este esquema conecta el laboratorio directamente con prácticas de DevSecOps y CI/CD.

---

### 10. Análisis de Supply Chain

El ejercicio ilustra un problema central de la cadena de suministro de software: una aplicación con pocas dependencias directas termina arrastrando decenas de componentes de terceros. En este proyecto, dos librerías directas (`requests` y `beautifulsoup4`) trajeron consigo todo un subárbol de transitivas, y fueron precisamente esas transitivas (`certifi`, `urllib3`) las que concentraron la mayor parte de las vulnerabilidades.

```
              app.py
                 │
                 ▼
             requests          ← dependencia directa
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
    urllib3              idna      ← dependencias transitivas
       │
       ▼
  vulnerabilidad potencial
```

La superficie de riesgo de una aplicación **no** se mide por lo que uno instaló a mano, sino por el conjunto completo de código de terceros que efectivamente se ejecuta.

---

### 11. Conclusiones

1. **Directas vs. transitivas.** Una dependencia directa es la que el proyecto pide de forma explícita; una transitiva es la que arrastra otra dependencia. `pip freeze` muestra más paquetes que los `import` del código porque incluye todo el subárbol transitivo.
2. **Una app puede ser vulnerable sin importar el paquete vulnerable.** Fue el caso de `urllib3`: la aplicación nunca lo importó, pero estaba expuesta a través de `requests`.
3. **Actualizar la dependencia directa no basta.** Hay que remediar explícitamente cada paquete vulnerable, incluidas las transitivas.
4. **Actualizar todo automáticamente no es una buena estrategia.** Puede romper compatibilidad; conviene hacerlo de forma dirigida y verificar el resultado.
5. **Las dependencias son un riesgo de Supply Chain.** Introducen código de terceros que puede contener vulnerabilidades, comportamientos inesperados o restricciones de licencia, y su número real supera con creces al de las dependencias elegidas de forma directa.

---

### Preguntas de reflexión

**¿Cuál es la diferencia entre dependencia directa y transitiva?**

Una **dependencia directa** es aquella que el desarrollador declara explícitamente en `requirements.txt` porque su código la importa (`requests`, `beautifulsoup4`). Una **dependencia transitiva** es aquella que la dependencia directa necesita para funcionar, pero que el desarrollador nunca instala ni importa manualmente (`urllib3`, `certifi`, `soupsieve`, etc.).

**¿Por qué `pip freeze` puede mostrar más paquetes de los que aparecen en nuestro código?**

Porque `pip freeze` lista **todos** los paquetes instalados en el entorno virtual, incluyendo las dependencias transitivas. Cuando se instala `requests`, pip instala automáticamente `urllib3`, `certifi`, `idna` y `charset-normalizer` porque `requests` los necesita.

**¿Una aplicación puede tener una vulnerabilidad aunque nuestro código no tenga ningún `import` de la librería vulnerable?**

Sí. Si `urllib3` tiene una vulnerabilidad y nuestra aplicación usa `requests`, cualquier llamada a `requests.get()` utiliza internamente `urllib3`. El exploit puede alcanzar el código vulnerable a través de la cadena de llamadas, sin que nuestro código lo invoque directamente.

**¿Actualizar todas las dependencias automáticamente es una buena estrategia?**

No necesariamente. Una actualización automática puede romper la aplicación si hay cambios de API entre versiones, introducir nuevos bugs, generar conflictos entre dependencias, o cambiar comportamientos en los que el código confía implícitamente.

**¿Por qué las dependencias representan un riesgo para la Software Supply Chain?**

Porque introducen código de terceros que el equipo no controla ni revisa directamente. Cada dependencia puede contener vulnerabilidades conocidas o desconocidas, ser abandonada por su mantenedor, ser comprometida mediante un ataque al repositorio del paquete, cambiar de licencia, o ser suplantada por un paquete malicioso con nombre similar (typosquatting).
