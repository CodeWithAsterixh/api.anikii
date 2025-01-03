# queries/search.py

CHARACTERS = '''
query ($id: Int, $page: Int = 1) {
  Media(id: $id) {
    characters(sort:RELEVANCE, perPage: 10, page: $page) {
        pageInfo {
            lastPage
            currentPage
        }
        nodes{
             
                name{
                    full
                    native
                    alternative
                    userPreferred
                }
                
        }
        edges{
            node{
                id,
                name{
                    full
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

