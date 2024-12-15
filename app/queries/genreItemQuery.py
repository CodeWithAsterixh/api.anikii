GENRE_ITEM = '''
query ($genre: String!,$page: Int = 1) {
  Page (page: $page, perPage: 20) {
    pageInfo {
      lastPage
      currentPage
    }
    media(genre: $genre, type: ANIME, popularity_greater: 10000, sort:[TRENDING_DESC, POPULARITY_DESC]) {
        id
        title {
            romaji
            english
        }
        status
        coverImage {
            extraLarge
            medium
        }
        popularity
    }
  }
}
'''