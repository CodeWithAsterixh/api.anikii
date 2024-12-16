RELEASES = '''
query ($page: Int = 1, $season: MediaSeason, $year: Int = 2024) {
  Page(page: $page, perPage: 20) {
    pageInfo {
      lastPage
      currentPage
    }
    media(
      popularity_greater: 10000,
      season: $season,
      seasonYear: $year,
      type: ANIME,
      sort: [POPULARITY_DESC,TRENDING_DESC]
    ) {
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
      nextAiringEpisode {
        airingAt
        episode
      }
    }
  }
}
'''
