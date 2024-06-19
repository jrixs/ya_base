from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from movies.mixin.base import UUIDMixin, TimeStampedMixin


class Genre(UUIDMixin, TimeStampedMixin):
    """ Модель с жанрами для кинокартин."""
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True, default='')

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    """ Модель с описанием персону, участника кинопроизведения """
    class Gender(models.TextChoices):
        MALE = 'male', _('male')
        FEMALE = 'female', _('female')

    full_name = models.CharField(_('full name'), max_length=255)
    gender = models.TextField(_('gender'), choices=Gender.choices,
                              default='')

    class Meta:
        db_table = "content\".\"person"
        verbose_name = 'Персонажи'
        verbose_name_plural = 'Персонажи'

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedMixin):
    """ Модель кинокартин."""
    class TypeChoices(models.TextChoices):
        MOVIE = 'movie', _('movie')
        TV_SHOW = 'tv show', _('tv show')

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), default='')
    premiere_date = models.DateField(_('premiere date'), blank=True,
                                     null=True)
    type = models.CharField(
        _('type'),
        null=False,
        max_length=10,
        choices=TypeChoices.choices,
        default=TypeChoices.MOVIE
        )
    rating = models.FloatField(_('rating'), blank=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)], null=True)
    file_path = models.CharField(_('file path'), max_length=255, blank=True,
                                 default='')
    genre_id = models.ManyToManyField(Genre, through='GenreFilmwork')
    person_id = models.ManyToManyField(Person, through='PersonFilmwork')

    class Meta:
        db_table = "content\".\"filmwork"
        verbose_name = 'Кинопроизведения'
        verbose_name_plural = 'Кинопроизведения'

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    """ Модель связывает жанр с кинопроизведением"""
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = 'Жанры'
        verbose_name_plural = 'Жанры'
        unique_together = ('film_work', 'genre',)


class PersonFilmwork(UUIDMixin):
    class Rale(models.TextChoices):
        ACTOR = 'actor', _('actor')
        DIRECTOR = 'director', _('director')
        WRITER = 'writer', _('writer')

    """ Модель связывает персону с кинопроизведением"""
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.TextField(_('role'), choices=Rale.choices, blank=False,
                            default='')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name = 'Учасники'
        verbose_name_plural = 'Учасники'
        unique_together = ('film_work', 'person', 'role',)
