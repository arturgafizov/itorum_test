from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from apps.events.models import Event


def search_events(query):
    search_vector = SearchVector('description', config='english')
    search_query = SearchQuery(query, config='english')

    results = Event.objects.annotate(
        search=search_vector,
        rank=SearchRank(search_vector, search_query)
    ).filter(search=search_query).order_by('-rank')
    return results