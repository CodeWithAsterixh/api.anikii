STREAM = '''
query ($id: Int) {
  Media(id: $id) {
    episodes
    streamingEpisodes {
      title
      thumbnail
      url
      site
    }
    externalLinks {
      url
      type
    }
    trailer{
      id
      site
      thumbnail
    }
  }
}
'''
