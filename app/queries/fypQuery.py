FYP = '''
query ($id: Int) {
  Media(id: $id) {
    id
    title {
      romaji
      english
      native
    }
    recommendations {
      edges {
        node {
            mediaRecommendation(type:ANIME) {
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
    }
  }
}
'''
