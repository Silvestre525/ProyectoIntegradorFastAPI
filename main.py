from fastapi import FastAPI, HTTPException

from schemas import LibroEntrada, LibroSalida

app = FastAPI()
libros = []
proximo_id = 1


def buscar_libro(id: int) -> dict:
    for libro in libros:
        if libro["id"] == id:
            return libro
    raise HTTPException(status_code=404, detail=f"No existe el libro {id}")


@app.get("/")
def inicio():
    return {"mensaje": "API de la biblioteca"}


@app.get("/libros", response_model=list[LibroSalida])
def listar_libros():
    return sorted(libros, key=lambda libro: libro["id"])


@app.post("/libros", status_code=201, response_model=LibroSalida)
def crear_libro(datos: LibroEntrada):
    global proximo_id

    libro = {"id": proximo_id, **datos.model_dump()}
    libros.append(libro)
    proximo_id += 1
    return libro


@app.get("/libros/{id}", response_model=LibroSalida)
def obtener_libro(id: int):
    return buscar_libro(id)


@app.delete("/libros/{id}", status_code=204)
def eliminar_libro(id: int):
    libros.remove(buscar_libro(id))
