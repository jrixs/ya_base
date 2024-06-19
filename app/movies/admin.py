from django.contrib import admin

from .models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'created',)
    search_fields = ('name',)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'gender', 'created',)
    list_filter = ('gender',)
    search_fields = ('full_name',)


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class GenrePersonInline(admin.TabularInline):
    model = PersonFilmwork
    autocomplete_fields = ('person',)


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, GenrePersonInline)
    list_display = ('title', 'type', 'created', 'rating',)
    list_filter = ('type',)
    search_fields = ('title', 'description', 'id')
