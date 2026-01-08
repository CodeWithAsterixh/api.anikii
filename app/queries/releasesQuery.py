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
      season_year: $year,
      type: ANIME,
      sort: [POPULARITY_DESC,TRENDING_DESC]
    ) {
      id
      title {
          romaji
          english
      }
      status
      format
      coverImage {
          extraLarge
          color
      }
      popularity
      averageScore
      episodes
      trending
      status
      "banner_image":bannerImage,
      startDate {
        year
      } 
    }
  }
}
'''
