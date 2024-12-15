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
            }
            popularity
        }
      }
      }
    }
  }
}
'''
