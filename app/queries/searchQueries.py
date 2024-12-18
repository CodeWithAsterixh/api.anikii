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
'''