# queries/query_manager.py
from .charactersQuery import CHARACTERS
from .descriptionQuery import DESCRIPTIONS
from .genresQuery import GENRES
from .popularQuery import POPULAR
from .recommendedQuery import RECOMMENDED
from .releasesQuery import RELEASES
from .searchQueries import SEARCH
from .streamQuery import STREAM
from .genreItemQuery import GENRE_ITEM
from .fypQuery import FYP
from .trailerQuery import TRAILERS
from .upcomingQuery import UPCOMING
from .mediaRelationQuery import RELATIONS



class QueryManager:
    def __init__(self):
        self.queries = {
            "characters": {
                "get_characters": CHARACTERS,
            },
            "description": {
                "get_descriptions": DESCRIPTIONS,
            },
            "relations": {
                "get_relations": RELATIONS,
            },
            "genres": {
                "get_genres": GENRES,
            },
            "popular": {
                "get_popular_media": POPULAR,
            },
            "recommended": {
                "get_recommended": RECOMMENDED,
            },
            "releases": {
                "get_releases": RELEASES,
            },
            "upcoming": {
                "get_upcoming": UPCOMING,
            },
            "search": {
                "search_media": SEARCH,
            },
            "stream": {
                "get_stream_data": STREAM,
            },
            "genre_item": {
                "get_genre_item": GENRE_ITEM,
            },
            "fyp": {
                "get_fyp": FYP,
            },
            "trailers": {
                "get_trailers": TRAILERS,
            }
        }

    def get_query(self, category: str, query_name: str) -> str:
        """Retrieve a query string by category and query name."""
        return self.queries.get(category, {}).get(query_name, None)

# Example usage:
query_manager = QueryManager()
