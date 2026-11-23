from pydantic import BaseModel, Field


class LibroEntrada(BaseModel):
    model_config = {"extra": "forbid"}

    titulo: str = Field(min_length=3, max_length=100)
    autor: str = Field(min_length=3, max_length=60)
    anio: int = Field(ge=1000, le=2100)
    disponible: bool = True


class LibroSalida(LibroEntrada):
    id: int
    disponible: bool


class LibroParcial(BaseModel):
    model_config = {"extra": "forbid"}

    # El default permite omitir el campo; el tipo rechaza un null explícito.
    titulo: str = Field(default=None, min_length=3, max_length=100)
    autor: str = Field(default=None, min_length=3, max_length=60)
    anio: int = Field(default=None, ge=1000, le=2100)
    disponible: bool = Field(default=None)
