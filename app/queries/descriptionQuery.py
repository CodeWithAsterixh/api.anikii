# description

DESCRIPTIONS = '''
query ($id: Int) {
  Media(id: $id) {
    id
    title {
      romaji
      english
      native
    }
    description(asHtml:true)
    season
    seasonYear
    status
    type
    idMal
    trailer{
        id
        site
        thumbnail
    }
    coverImage{
        extraLarge
        medium
        color
    }
    bannerImage
    popularity
    trending
    episodes
    updatedAt
    startDate{
      year
      month
      day
    }
    endDate{
      year
      month
      day
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
