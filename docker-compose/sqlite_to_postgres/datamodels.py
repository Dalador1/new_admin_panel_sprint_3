from dataclasses import dataclass
from typing import  Optional
from uuid import UUID

@dataclass
class Genre:
    id: UUID
    name: str
    description: Optional[str]
    created: Optional[str] = None
    modified: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)

@dataclass
class FilmWork:
    id: UUID
    title: str
    description: Optional[str]
    creation_date: Optional[str]
    rating: Optional[float]
    type: str
    file_path: Optional[str]
    created: Optional[str] = None
    modified: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)

@dataclass
class GenreFilmWork:
    id: UUID
    genre_id: UUID
    film_work_id: UUID
    created: Optional[str] = None
    modified: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)

@dataclass
class Person:
    id: UUID
    full_name: str
    created: Optional[str] = None
    modified: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)

@dataclass
class PersonFilmWork:
    id: UUID
    person_id: UUID
    film_work_id: UUID
    role: str
    created: Optional[str] = None
    modified: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)