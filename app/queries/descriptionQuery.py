# description

DESCRIPTIONS = '''
query ($id: Int) {
  Media(id: $id) {
    id
    title {
      romaji
      english
    }
    description
    season
    seasonYear
    status
    type
    trailer{
        id
        site
        thumbnail
    }
    coverImage{
        extraLarge
        color
    }
    bannerImage
    popularity
    trending
    episodes
    updatedAt
    format
    startDate{
      year
    }
    nextAiringEpisode{
      airingAt
      timeUntilAiring
      episode
    } 
    tags{
      rank
      id
      name
      description
      category
    }
    genres
  }
}
'''
