import logging

from fastapi import FastAPI, HTTPException, Query

from datos import cargar_libros, guardar_libros
from schemas import LibroEntrada, LibroParcial, LibroSalida

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
libros = cargar_libros()
proximo_id = max((libro["id"] for libro in libros), default=0) + 1


def buscar_libro(id: int) -> dict:
    for libro in libros:
        if libro["id"] == id:
            return libro
    raise HTTPException(status_code=404, detail=f"No existe el libro {id}")


@app.get("/")
def inicio():
    """Devuelve el mensaje de bienvenida."""
    return {"mensaje": "API de la biblioteca"}


@app.get("/libros", response_model=list[LibroSalida])
def listar_libros(
    autor: str | None = None,
    disponible: bool | None = None,
    desde: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=0),
):
    """Lista los libros por id, con filtros y paginación."""
    resultado = sorted(libros, key=lambda libro: libro["id"])
    if autor is not None:
        autor_buscado = autor.lower()
        resultado = [
            libro for libro in resultado if libro["autor"].lower() == autor_buscado
        ]
    if disponible is not None:
        resultado = [libro for libro in resultado if libro["disponible"] == disponible]
    return resultado[desde:desde + limite]


@app.get("/libros/buscar", response_model=list[LibroSalida])
def buscar_libros(texto: str):
    """Busca texto dentro del título o del autor."""
    texto = texto.lower()
    return [
        libro
        for libro in sorted(libros, key=lambda libro: libro["id"])
        if texto in libro["titulo"].lower() or texto in libro["autor"].lower()
    ]


@app.get("/libros/estadisticas")
def estadisticas():
    """Cuenta libros totales, disponibles y prestados."""
    total = len(libros)
    disponibles = sum(1 for libro in libros if libro["disponible"])
    return {
        "total": total,
        "disponibles": disponibles,
        "prestados": total - disponibles,
    }


@app.post("/libros", status_code=201, response_model=LibroSalida)
def crear_libro(datos: LibroEntrada):
    """Crea un libro con un id nuevo, salvo que ya exista."""
    global proximo_id

    titulo = datos.titulo.lower()
    autor = datos.autor.lower()
    for existente in libros:
        if (
            existente["titulo"].lower() == titulo
            and existente["autor"].lower() == autor
        ):
            raise HTTPException(status_code=409, detail="El libro ya existe")

    libro = {"id": proximo_id, **datos.model_dump()}
    libros.append(libro)
    proximo_id += 1
    guardar_libros(libros)
    logger.info("Libro %s creado", libro["id"])
    return libro


@app.get("/libros/{id}", response_model=LibroSalida)
def obtener_libro(id: int):
    """Devuelve el libro solicitado o un 404 si no existe."""
    return buscar_libro(id)


@app.put("/libros/{id}", response_model=LibroSalida)
def reemplazar_libro(id: int, datos: LibroEntrada):
    """Reemplaza todos los campos editables, conservando el id."""
    libro = buscar_libro(id)
    libro.update(datos.model_dump())
    guardar_libros(libros)
    return libro


@app.patch("/libros/{id}", response_model=LibroSalida)
def actualizar_libro(id: int, datos: LibroParcial):
    """Actualiza únicamente los campos enviados."""
    libro = buscar_libro(id)
    cambios = datos.model_dump(exclude_unset=True)
    if cambios:
        libro.update(cambios)
        guardar_libros(libros)
    return libro


@app.delete("/libros/{id}", status_code=204)
def eliminar_libro(id: int):
    """Elimina un libro y devuelve una respuesta sin cuerpo."""
    libros.remove(buscar_libro(id))
    guardar_libros(libros)
    logger.info("Libro %s eliminado", id)


def cambiar_disponibilidad(id: int, disponible: bool) -> dict:
    libro = buscar_libro(id)
    if libro["disponible"] == disponible:
        estado = "disponible" if disponible else "prestado"
        raise HTTPException(status_code=409, detail=f"El libro ya está {estado}")
    libro["disponible"] = disponible
    guardar_libros(libros)
    logger.info("Disponibilidad del libro %s: %s", id, disponible)
    return libro


@app.post("/libros/{id}/prestar", response_model=LibroSalida)
def prestar_libro(id: int):
    """Marca un libro disponible como prestado."""
    return cambiar_disponibilidad(id, False)


@app.post("/libros/{id}/devolver", response_model=LibroSalida)
def devolver_libro(id: int):
    """Marca un libro prestado como disponible."""
    return cambiar_disponibilidad(id, True)
