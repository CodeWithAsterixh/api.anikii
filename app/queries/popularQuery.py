POPULAR =  '''
query ($page: Int = 1) {
  Page (page: $page, perPage: 20) {
    pageInfo {
      lastPage
      currentPage
    }
    media(popularity_greater: 10000, sort:[TRENDING_DESC, POPULARITY_DESC]) {
            id
            title {
                romaji
                english
            }
            status
            coverImage {
                extraLarge
                medium
                color
            }
            popularity
            averageScore
            trending
            isAdult
            status
            nextAiringEpisode{
                airingAt,
                episode
            }        
    }
  }
}
'''
