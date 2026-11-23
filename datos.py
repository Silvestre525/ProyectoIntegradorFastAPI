import json
from pathlib import Path

from pydantic import ValidationError

from schemas import LibroSalida

ARCHIVO_LIBROS = Path(__file__).resolve().parent / "datos" / "libros.json"


def cargar_libros() -> list[dict]:
    try:
        with ARCHIVO_LIBROS.open(encoding="utf-8") as archivo:
            libros = json.load(archivo)
        if not isinstance(libros, list):
            return []
        resultado = []
        for libro in libros:
            if not isinstance(libro, dict):
                return []
            modelo = LibroSalida(**libro)
            resultado.append(modelo.model_dump())
        return resultado
    except (FileNotFoundError, json.JSONDecodeError, UnicodeError, ValidationError):
        return []


def guardar_libros(libros: list[dict]) -> None:
    ARCHIVO_LIBROS.parent.mkdir(exist_ok=True)
    with ARCHIVO_LIBROS.open("w", encoding="utf-8") as archivo:
        json.dump(libros, archivo, ensure_ascii=False, indent=2)
