import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255, unique=True)  # Добавлено unique=True
    description = models.TextField(_('description'), blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class GenreFilmwork(UUIDMixin, TimeStampedMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.genre)

    class Meta:
        db_table = "content\".\"genre_film_work"
        constraints = [
            models.UniqueConstraint(fields=['film_work', 'genre'], name='unique_genre_film_work')
        ]


class Person(TimeStampedMixin, UUIDMixin):
    full_name = models.CharField(_('name'), max_length=255, unique=True)  # Добавлено unique=True

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = "content\".\"person"
        verbose_name = 'Актер'
        verbose_name_plural = 'Актеры'


class Filmwork(UUIDMixin, TimeStampedMixin):
    class FilmType(models.TextChoices):
        MOVIE = 'movie', 'Movie'
        TVSHOW = 'tvshow', 'TV Show'

    person = models.ManyToManyField(Person, through='PersonFilmwork')
    genre = models.ManyToManyField(Genre, through='GenreFilmwork')
    title = models.TextField(_('title'), blank=False)
    description = models.TextField(_('description'), blank=True)
    creation_date = models.DateField(_('creation_date'), auto_now=False)
    type = models.CharField(
        verbose_name=_('type'),
        max_length=10,
        choices=FilmType.choices,
        default=FilmType.MOVIE,
    )
    file_path = models.FileField(_('file'), blank=True, null=True, upload_to='movies/')
    rating = models.FloatField(_('rating'), blank=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)])

    def __str__(self):
        return self.title

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'


class PersonFilmwork(UUIDMixin, TimeStampedMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='filmworks')
    role = models.TextField(_('role'))

    def __str__(self):
        return f"{self.person.full_name} в фильме {self.film_work.title} в роли {self.role}"

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name_plural = 'person_film_work'
        constraints = [
            models.UniqueConstraint(fields=['film_work', 'person', 'role'], name='unique_person_film_work')
        ]
