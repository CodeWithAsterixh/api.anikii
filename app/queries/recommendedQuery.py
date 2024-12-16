RECOMMENDED = '''
query ($id: Int,$page: Int = 1) {
    Media(id: $id) {
        recommendations(page: $page, perPage: 20) {
            pageInfo {
                lastPage
                currentPage
            }
            nodes {
                mediaRecommendation {
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
            }
          }
          }
      }
}
'''
