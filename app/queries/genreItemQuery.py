GENRE_ITEM = '''
query ($genre: String!,$page: Int = 1) {
  Page (page: $page, perPage: 20) {
    pageInfo {
      lastPage
      currentPage
    }
    media(genre: $genre, type: ANIME, sort:[POPULARITY_DESC]) {
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