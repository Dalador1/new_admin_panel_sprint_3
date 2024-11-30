from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from movies.models import Filmwork, Genre, Person


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        return Filmwork.objects.prefetch_related(
            'genre',  
            'person',  
            'personfilmwork_set'  
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context,json_dumps_params={"indent":4}, safe=False)


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, **kwargs):
        obj = self.get_object()
        context = {
            'id': obj.id,
            'title': obj.title,
            'description': obj.description,
            'creation_date': obj.creation_date,
            'rating': obj.rating,
            'type': obj.type,
            'genres': [genre.name for genre in obj.genre.all()],
            'actors': [
                person.full_name
                for person in obj.person.filter(filmworks__role='actor')
            ],
            'directors': [
                person.full_name
                for person in obj.person.filter(filmworks__role='director')
            ],
            'writers': [
                person.full_name
                for person in obj.person.filter(filmworks__role='writer')
            ],
        }
        return context


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50
    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list or self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page', 1)
        if page_number == 'last':
            page_number = paginator.page_range.stop-1
        try:
            page_number = int(page_number)
            if page_number < 1:
                raise ValueError   
        except ValueError:
            page_number = 1
        page = paginator.get_page(page_number)
        
        
        results = []
        for film in page.object_list:
            results.append(
                {
                'id': film.id,
                'title': film.title,
                'description': film.description,
                'creation_date': film.creation_date,
                'rating': film.rating,
                'type': film.type,
                'genres': [genre.name for genre in film.genre.all()],
                'actors': [
                    person.full_name
                    for person in film.person.filter(filmworks__role='actor')
                ],
                'directors': [
                    person.full_name
                    for person in film.person.filter(filmworks__role='director')
                ],
                'writers': [
                    person.full_name
                    for person in film.person.filter(filmworks__role='writer')
                ],
            }
            )
                    

        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': results
        }
        return context
