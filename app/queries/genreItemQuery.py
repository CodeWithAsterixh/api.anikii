GENRE_ITEM = '''
query ($genre: String!,$page: Int = 1) {
  Page (page: $page, perPage: 20) {
    pageInfo {
      lastPage
      currentPage
    }
    media(genre: $genre, popularity_greater: 10000, type: ANIME,sort: [POPULARITY_DESC,TRENDING_DESC]) {
        id
        title {
            romaji
            english
        }
        status
        episodes
        coverImage {
            extraLarge
            medium
        }
        popularity
    }
  }
}
'''