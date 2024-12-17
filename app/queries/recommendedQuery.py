RECOMMENDED = '''
query ($id: Int,$page: Int = 1) {
    Media(id: $id) {
        recommendations(page: $page, perPage: 20) {
            pageInfo {
                lastPage
                currentPage
            }
            nodes {
                mediaRecommendation(type:ANIME) {
                    id
                    title {
                        romaji
                        english
                    }
                    status
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
}
'''
