SEARCH = '''
query ($search: String!) {
  Page {
    media(search: $search, type: ANIME) {
        id
        format
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
'''