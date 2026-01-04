FYP = '''
query ($id: Int, $page: Int = 1) {
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
                    format
                    coverImage {
                        extraLarge
                        medium
                        color
                    }
                    popularity
                    averageScore
                    episodes
                    trending
                    bannerImage
                    startDate {
                        year
                    }
                }
            }
        }
    }
}
'''
