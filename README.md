# API de la Biblioteca

Trabajo integrador del Módulo 3 del Bootcamp de Desarrollo Backend con Python
(Silicon Misiones). Permite administrar, buscar y prestar libros. El catálogo se
guarda en `datos/libros.json`, que se crea al hacer el primer cambio.

## Instalación y ejecución

Requiere Python 3.10 o posterior, FastAPI, Pydantic y Uvicorn. Desde la raíz:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Cómo probar la API

Abrí [la documentación interactiva](http://127.0.0.1:8000/docs), elegí una
ruta y usá **Try it out** y **Execute**. Empezá con un catálogo vacío en una
copia de prueba si ya tenés datos que querés conservar.

1. `GET /` devuelve `200` y `{"mensaje": "API de la biblioteca"}`.
   `GET /libros` devuelve `200` y `[]`.
2. Creá dos libros con `POST /libros`. Usá, por ejemplo,
   `{"titulo": "El Aleph", "autor": "Jorge Luis Borges", "anio": 1949}` y
   `{"titulo": "Rayuela", "autor": "Julio Cortázar", "anio": 1963}`.
   Esperá `201`, ids `1` y `2`, y `disponible: true`. El listado los ordena por id.
3. Consultá `/libros/1` (`200`), `/libros/999` (`404`) y `/libros/abc` (`422`).
   Repetí el primer POST (`409`). Probá también un título de dos caracteres,
   `anio: 999` o `anio: "abc"` (`422`).
4. Reemplazá el libro `1` con `PUT /libros/1`, enviando `titulo`, `autor` y `anio`.
   Conserva su id y, si no enviás `disponible`, queda en `true`.
   En `PATCH /libros/2`, enviá `{"disponible": false}`: solo cambia ese campo.
   Con `{}` no cambia nada; con `{"disponible": null}` devuelve `422`.
5. Probá `GET /libros` con `autor`, con `disponible=false` y con
   `desde=1&limite=1`. En `GET /libros/buscar` usá `texto=RAY` para hallar
   *Rayuela*. Si omitís `texto`, devuelve `422`.
6. Borrá el libro `2`: `DELETE /libros/2` devuelve `204` sin cuerpo. Consultarlo
   o borrarlo otra vez devuelve `404`. Creá otro libro sin reiniciar: su id es `3`.
7. Probá `POST /libros/1/prestar` y `POST /libros/1/devolver`: cada cambio
   devuelve `200`; repetirlo devuelve `409`. Consultá `GET /libros/estadisticas`
   para ver `total`, `disponibles` y `prestados`.
8. Revisá `datos/libros.json`, detené Uvicorn y volvé a iniciarlo. El listado y
   la búsqueda conservan los datos; el próximo id es el mayor guardado más uno.
   En una copia de prueba, detené el servidor y probá arrancar sin el archivo,
   con el archivo vacío y con JSON inválido (por ejemplo `[{},]`): en los tres
   casos `GET /libros` devuelve `[]`.

La importación debe terminar sin salida: `python -c "import main"`.
Si tenés Ruff instalado, comprobá el estilo con `ruff check .`.
