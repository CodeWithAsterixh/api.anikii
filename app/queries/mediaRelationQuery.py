# relations

RELATIONS = '''
query ($id: Int) {
  Media(id: $id) {
    relations{
        edges{
            node{
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
                bannerImage
                startDate {
                    year
                }
            }
            relationType
        }
    }
  }
}
'''
