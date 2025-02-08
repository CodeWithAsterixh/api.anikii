# description

DESCRIPTIONS = '''
query ($id: Int) {
  Media(id: $id) {
    id
    title {
      romaji
      english
    }
    synonyms
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
    duration
    startDate{
      year
    }
    nextAiringEpisode{
      airingAt
      timeUntilAiring
      episode
    }
    stats{
      scoreDistribution{
        score
        amount
      }
    }
    tags{
      rank
      id
      name
      description
      category
    }
    genres
    studios(isMain: true){
      edges{
        node{
          name
        }
      }
    }
  }
}
'''
