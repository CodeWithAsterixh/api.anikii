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
        coverImage {
            extraLarge
            medium
        }
        popularity
    }
  }
}
'''