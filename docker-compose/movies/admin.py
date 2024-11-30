from django.contrib import admin
from .models import Genre, Filmwork, GenreFilmwork,Person, PersonFilmwork

class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork

class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name','description') 
    list_filter = ('name',) 


@admin.register(Person)
class Person(admin.ModelAdmin):
    list_display = ('full_name',) 
    list_filter = ('full_name',) 
    search_fields = ('full_name',) 

 
@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline,PersonFilmworkInline)
    list_display = ('title', 'type', 'creation_date', 'rating',) 
    list_filter = ('type',) 
    search_fields = ('title', 'description', 'id',) 

