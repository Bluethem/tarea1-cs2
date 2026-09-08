# Trabajo 1 - Construccion de Software 2

Integrantes:
- David Luza Ccorimanya
- Henry Javier Medina Malpartida


Aplicación Python para analizar páginas web: extrae el título, cuenta palabras y caracteres, y registra la fecha/hora del análisis.

## Requisitos

- Python 3.10+
- pip


### 1. Crear el entorno virtual

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Uso

```bash
python app.py
```

---

## LAB-1: Construcción segura de una aplicación Python con pip

---

### Parte V — Árbol de dependencias

Se instala `pipdeptree` para visualizar las dependencias directas y transitivas:

```bash
pip install pipdeptree
pipdeptree
```

Salida obtenida:

```
beautifulsoup4==4.15.0
  - soupsieve [required: >1.2, installed: 2.9.2]

requests==2.34.2
  - certifi [required: >=2017.4.17, installed: 2026.7.22]
  - charset-normalizer [required: >=2,<4, installed: 3.5.1]
  - idna [required: >=2.5,<4, installed: 3.19]
  - urllib3 [required: >=1.21.1,<3, installed: 2.7.0]
```

Árbol visual del proyecto:

```
              PROYECTO (app.py)
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
    requests                beautifulsoup4
    (2.34.2)                  (4.15.0)
        │                         │
  ┌─────┼──────────┐              ▼
  ▼     ▼          ▼           soupsieve
urllib3 idna    certifi          (2.9.2)
(2.7.0)(3.19) (2026.7.22)
  │
  ▼
charset-normalizer
   (3.5.1)
```

**Dependencias directas** (instaladas explícitamente):
1. `requests==2.34.2`
2. `beautifulsoup4==4.15.0`

**Dependencias transitivas** (instaladas automáticamente):

| Dependencia         | Requerida por     |
|---------------------|-------------------|
| `urllib3`           | requests          |
| `certifi`           | requests          |
| `charset-normalizer`| requests          |
| `idna`              | requests          |
| `soupsieve`         | beautifulsoup4    |

---

### Parte VI — Detección de vulnerabilidades

Se instala `pip-audit` para realizar el análisis de composición de software (SCA):

```bash
pip install pip-audit
pip-audit
```

**Escenario simulado con dependencias vulnerables**

Para demostrar el funcionamiento de `pip-audit`, se instalaron versiones antiguas con CVEs conocidas (ver bloque comentado al final de `requirements.txt`):

```
# Para reproducir el escenario vulnerable:
# 1. Comentar: requests==2.34.2, urllib3==2.7.0, certifi==2026.7.22
# 2. Descomentar: requests==2.6.0, urllib3==1.24.1, certifi==2017.7.27.1
# 3. Ejecutar: pip install -r requirements.txt
# 4. Ejecutar: pip-audit
```

Salida de `pip-audit` con dependencias vulnerables instaladas:

```
Found 4 known vulnerabilities in 3 packages
Name      Version      ID                  Fix Versions
--------  -----------  ------------------  ------------
requests  2.6.0        PYSEC-2023-74       2.31.0
urllib3   1.24.1       PYSEC-2019-78       1.24.2
urllib3   1.24.1       PYSEC-2019-79       1.24.2
certifi   2017.7.27.1  PYSEC-2023-135      2023.7.22
```

| Paquete   | Versión     | CVE / ID          | Descripción                                      | Versión corregida |
|-----------|-------------|-------------------|--------------------------------------------------|-------------------|
| requests  | 2.6.0       | PYSEC-2023-74     | Filtrado de cabecera `Proxy-Authorization` en redirects | 2.31.0      |
| urllib3   | 1.24.1      | PYSEC-2019-78     | Inyección CRLF en cabeceras HTTP                 | 1.24.2            |
| urllib3   | 1.24.1      | PYSEC-2019-79     | Verificación incorrecta de certificados          | 1.24.2            |
| certifi   | 2017.7.27.1 | PYSEC-2023-135    | Inclusión de CA raíz revocada (e-Tugra)          | 2023.7.22         |

**Con versiones actuales** (estado real del proyecto):

```
No known vulnerabilities found
```

---

### Parte VII — ¿Dónde está la vulnerabilidad?

El desarrollador afirma que `requests` es la única dependencia directa afectada, pero el análisis revela que la cadena completa está comprometida:

```
app.py
  │
  ▼
requests (2.6.0)  ← vulnerable (PYSEC-2023-74)
  │
  ▼
urllib3 (1.24.1)  ← vulnerable (PYSEC-2019-78, PYSEC-2019-79)
```

La aplicación **no importa `urllib3` directamente**, pero está afectada porque `requests` lo utiliza internamente para realizar las conexiones HTTP. Una vulnerabilidad en `urllib3` puede explotarse a través de cualquier llamada a `requests.get()`.

**¿Quién es responsable de solucionarlo?**

El equipo que mantiene la aplicación. Aunque la vulnerabilidad esté en una dependencia transitiva, la responsabilidad de identificarla, evaluar su impacto y actualizar la cadena es del propietario de la aplicación.

---

### Parte VIII — Actualizar dependencias

```bash
pip list --outdated
```

```bash
pip install --upgrade requests urllib3 certifi
pip freeze > requirements.txt
pip-audit
```

**Comparativa ANTES / DESPUÉS:**

| Métrica              | ANTES (versiones vulnerables) | DESPUÉS (versiones actuales) |
|----------------------|-------------------------------|------------------------------|
| requests             | 2.6.0                         | 2.34.2                       |
| urllib3              | 1.24.1                        | 2.7.0                        |
| certifi              | 2017.7.27.1                   | 2026.7.22                    |
| Vulnerabilidades     | 4                             | 0                            |
| Estado del pipeline  | FAIL                          | PASS                         |

**¿Actualizar siempre soluciona el problema?**

No necesariamente. Actualizar puede introducir:
- Incompatibilidades de API (cambios breaking entre versiones mayores)
- Nuevos bugs no detectados aún
- Conflictos con otras dependencias que requieren versiones antiguas
- Cambios de comportamiento que rompen tests existentes

---

### Parte IX — Conflicto de dependencias

Escenario conceptual donde dos librerías requieren versiones incompatibles de una misma dependencia:

```
app.py
  │
  ├── Librería A
  │      └── urllib3 >= 2.0
  │
  └── Librería B
         └── urllib3 < 2.0
```

```
urllib3 >= 2.0
urllib3 <  2.0
─────────────
   CONFLICTO — ninguna versión satisface ambas restricciones
```

El gestor de paquetes intentará resolver las restricciones, pero cuando son mutuamente excluyentes el resultado es un error de instalación o una instalación silenciosamente incorrecta. La solución pasa por fijar versiones compatibles o buscar alternativas a alguna de las librerías.

---

### Parte X — Supply Chain (Cadena de suministro)

```
              app.py
                 │
                 ▼
             requests          ← 1 dependencia directa
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
    urllib3              idna      ← dependencias transitivas
       │
       ▼
  vulnerabilidad potencial
```

**Caso planteado:**

Una aplicación tiene 2 dependencias directas (`requests`, `beautifulsoup4`), pero esas dependencias requieren otras 5 librerías adicionales. En proyectos reales con 15 dependencias directas, el árbol total puede superar los 80 paquetes de terceros.

Cada uno de esos paquetes:
- Tiene su propio historial de vulnerabilidades
- Puede ser abandonado por su mantenedor
- Puede ser comprometido (typosquatting, supply chain attack)
- Puede cambiar de licencia

Esto es precisamente el problema de la **cadena de suministro de software**: aceptamos código de cientos de terceros sin revisarlo directamente.

---

### Parte XII — Actividad final: "Detective de dependencias"

**Escenario:** Un desarrollador afirma que ninguna de las librerías que él instaló directamente tiene vulnerabilidades. Se debe investigar si esa afirmación es suficiente para considerar segura la aplicación.

**Comandos ejecutados:**

```bash
pip list
pipdeptree
pip-audit
pip list --outdated
```

**Análisis:**

1. **Dependencias directas:**
   - `requests==2.6.0`
   - `beautifulsoup4==4.15.0`

2. **Dependencias transitivas:**
   - De `requests`: `urllib3==1.24.1`, `certifi==2017.7.27.1`, `charset-normalizer`, `idna`
   - De `beautifulsoup4`: `soupsieve`

3. **Versiones instaladas:** Mezcla de versiones antiguas y actuales.

4. **Vulnerabilidades detectadas:** 4 CVEs en 3 paquetes (`requests`, `urllib3`, `certifi`).

5. **Dependencias desactualizadas:** `pip list --outdated` muestra que `requests`, `urllib3` y `certifi` tienen versiones más recientes disponibles.

6. **Posibles conflictos:** Si se actualiza `urllib3` a la versión 2.x y existe alguna librería que requiere `urllib3 < 2.0`, se producirá un conflicto.

7. **Riesgos para la aplicación:**
   - La vulnerabilidad `PYSEC-2023-74` en `requests` puede filtrar credenciales del proxy en redirects automáticos.
   - Las vulnerabilidades en `urllib3` permiten inyección de cabeceras y omisión de validación de certificados.
   - El certificado CA comprometido en `certifi` puede permitir ataques MITM.

**Conclusión:** La afirmación del desarrollador es **insuficiente**. Las vulnerabilidades en dependencias transitivas son igual de peligrosas que las de las directas, y la responsabilidad de remediarlas recae en el equipo que mantiene la aplicación.

---

### Pipeline de seguridad

Se implementa un script `security_pipeline.py` en la raíz del proyecto que automatiza el análisis y genera `dependency-report.txt`:

```bash
python security_pipeline.py
```

El pipeline sigue este flujo:

```
pip list
    │
    ▼
pipdeptree
    │
    ▼
pip-audit
    │
   / \
  /   \
 ▼     ▼
PASS  FAIL → exit code 1
  │
  ▼
dependency-report.txt generado
```

---

### Preguntas de reflexión

**Pregunta 1: ¿Cuál es la diferencia entre dependencia directa y transitiva?**

Una **dependencia directa** es aquella que el desarrollador declara explícitamente en `requirements.txt` porque su código la importa (`requests`, `beautifulsoup4`). Una **dependencia transitiva** es aquella que la dependencia directa necesita para funcionar, pero que el desarrollador nunca instala ni importa manualmente (`urllib3`, `certifi`, `soupsieve`, etc.). Ambas forman parte del árbol de dependencias del proyecto y ambas representan riesgo de seguridad.

**Pregunta 2: ¿Por qué `pip freeze` puede mostrar más paquetes de los que aparecen en nuestro código?**

Porque `pip freeze` lista **todos** los paquetes instalados en el entorno virtual, incluyendo las dependencias transitivas. Cuando se instala `requests`, pip instala automáticamente `urllib3`, `certifi`, `idna` y `charset-normalizer` porque `requests` los necesita. Ninguno de esos aparece en el código fuente con un `import`, pero sí están en el entorno.

**Pregunta 3: ¿Una aplicación puede tener una vulnerabilidad aunque nuestro código no tenga ningún `import` de la librería vulnerable?**

Sí. Si `urllib3` tiene una vulnerabilidad y nuestra aplicación usa `requests`, cualquier llamada a `requests.get()` utiliza internamente `urllib3` para gestionar la conexión. El exploit puede alcanzar el código vulnerable a través de la cadena de llamadas, sin que nuestro código lo invoque directamente.

**Pregunta 4: ¿Actualizar todas las dependencias automáticamente es una buena estrategia?**

No necesariamente. Una actualización automática puede romper la aplicación si hay cambios de API entre versiones (especialmente en saltos de versión mayor), introducir nuevos bugs aún no reportados, generar conflictos entre dependencias que requieren versiones específicas, o cambiar comportamientos en los que el código confía implícitamente. La estrategia correcta es evaluar cada actualización en un entorno de pruebas y ejecutar la suite de tests antes de llevarla a producción.

**Pregunta 5: ¿Por qué las dependencias representan un riesgo para la Software Supply Chain?**

Porque introducen código de terceros que el equipo no controla ni revisa directamente. Cada dependencia puede contener vulnerabilidades conocidas o desconocidas, ser abandonada por su mantenedor (sin parches futuros), ser comprometida mediante un ataque al repositorio del paquete (supply chain attack), cambiar de licencia en una nueva versión, o ser suplantada por un paquete malicioso con nombre similar (typosquatting). El riesgo se multiplica con cada nivel de dependencias transitivas.
