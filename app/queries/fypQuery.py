FYP = '''
query ($id: Int,$page: Int = 1) {
    Media(id: $id) {
        recommendations(page: $page, perPage: 20) {
            nodes {
                mediaRecommendation {
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
}
'''
