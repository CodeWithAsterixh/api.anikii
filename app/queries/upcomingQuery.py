UPCOMING = """
query($page: Int = 1) { 
  Page(page: $page, perPage: 20) {
    pageInfo {
      lastPage
      currentPage
    }
    airingSchedules(notYetAired: true) {
      media {
        id
        title {
          romaji
          english
        }
        status
        episodes
        format
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
        genres
        nextAiringEpisode {
          airingAt
          episode
        }
      }
    }
  }
}
"""