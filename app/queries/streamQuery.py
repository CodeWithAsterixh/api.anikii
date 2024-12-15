STREAM = '''
query ($id: Int) {
  Media(id: $id) {
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
  }
}
'''
