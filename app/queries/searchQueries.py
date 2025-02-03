SEARCH = '''
query ($search: String!) {
  Page {
    media(search: $search, type: ANIME) {
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
  }
}
'''