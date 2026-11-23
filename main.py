from fastapi import FastAPI, HTTPException, Query

from datos import cargar_libros, guardar_libros
from schemas import LibroEntrada, LibroParcial, LibroSalida

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
    return {"mensaje": "API de la biblioteca"}


@app.get("/libros", response_model=list[LibroSalida])
def listar_libros(
    autor: str | None = None,
    disponible: bool | None = None,
    desde: int = Query(default=0, ge=0),
    limite: int = Query(default=100, ge=0),
):
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
    texto = texto.lower()
    return [
        libro
        for libro in sorted(libros, key=lambda libro: libro["id"])
        if texto in libro["titulo"].lower() or texto in libro["autor"].lower()
    ]


@app.post("/libros", status_code=201, response_model=LibroSalida)
def crear_libro(datos: LibroEntrada):
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
    return libro


@app.get("/libros/{id}", response_model=LibroSalida)
def obtener_libro(id: int):
    return buscar_libro(id)


@app.put("/libros/{id}", response_model=LibroSalida)
def reemplazar_libro(id: int, datos: LibroEntrada):
    libro = buscar_libro(id)
    libro.update(datos.model_dump())
    guardar_libros(libros)
    return libro


@app.patch("/libros/{id}", response_model=LibroSalida)
def actualizar_libro(id: int, datos: LibroParcial):
    libro = buscar_libro(id)
    cambios = datos.model_dump(exclude_unset=True)
    if cambios:
        libro.update(cambios)
        guardar_libros(libros)
    return libro


@app.delete("/libros/{id}", status_code=204)
def eliminar_libro(id: int):
    libros.remove(buscar_libro(id))
    guardar_libros(libros)
