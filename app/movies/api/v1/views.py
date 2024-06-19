from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F, Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import Filmwork
from django.conf import settings


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        return Filmwork.objects.prefetch_related('genres', 'person').annotate(
            creation_date=F('created'),
            genres=ArrayAgg('genre_id__name', distinct=True),
            actors=ArrayAgg('person_id__full_name', distinct=True,
                            filter=Q(personfilmwork__role='actor')),
            directors=ArrayAgg('person_id__full_name', distinct=True,
                               filter=Q(personfilmwork__role='director')),
            writers=ArrayAgg('person_id__full_name', distinct=True,
                             filter=Q(personfilmwork__role='writer')),
        ).values(
            'id',
            'title',
            'description',
            'creation_date',
            'rating',
            'type',
            'genres',
            'actors',
            'directors',
            'writers'
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = settings.PAGINATE_BY

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()

        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.paginate_by
        )

        if is_paginated:
            context = {'results': list()}
            try:
                get_page_number = self.request.GET.get(
                    'page') if self.request.GET.get('page') else 1
                if get_page_number != 'last':
                    get_page_number = int(get_page_number)
                else:
                    get_page_number = paginator.num_pages
            except ValueError:
                get_page_number = 0

            if 0 < get_page_number <= paginator.num_pages:
                context = {
                    'count': paginator.count,
                    'total_pages': paginator.num_pages,
                    'prev': page.number,
                    'next': page.next_page_number(
                    ) if page.has_next() else None,
                    'results': list(paginator.page(
                        get_page_number).object_list),
                }
        else:
            context = {'results': list()}
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    pk_url_kwarg = 'get_pk'

    def get_context_data(self, **kwargs):
        movie_uuid = self.kwargs.get('get_pk')
        try:
            context = self.get_queryset().get(id=movie_uuid)
        except Filmwork.DoesNotExist:
            context = {}
        return context

    def get_object(self, queryset=None):
        try:
            return super().get_object(self, queryset=None)
        except TypeError:
            return JsonResponse({})
