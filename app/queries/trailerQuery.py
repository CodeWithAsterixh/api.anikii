TRAILERS = '''
query ($id: Int) {
  Media(id: $id) {
    trailer{
      id
      site
      thumbnail
    }
  }
}
'''
