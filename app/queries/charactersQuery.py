# queries/search.py

CHARACTERS = '''
query ($id: Int, $page: Int = 1) {
  Media(id: $id) {
    characters(sort:RELEVANCE, perPage: 10, page: $page) {
        pageInfo {
            lastPage
            currentPage
        }
        edges{
            node{
                id,
                name{
                    full
                    first
                    last
                    native
                    alternative
                    userPreferred
                }
                image{
                    medium
                }
                gender
            }
            name
            id
            role
            voiceActors {
                name{
                    full
                }
                languageV2
                image{
                    medium
                }
            }
        }
    }
  }
}
'''

