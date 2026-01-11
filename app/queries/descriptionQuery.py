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
    season_year
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
    "banner_image":bannerImage,
    popularity
    trending
    episodes
    updatedAt
    format
    duration
    startDate{
      year
    }
    next_airing_episode{
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
