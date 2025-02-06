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
                id
                name{
                    full
                }
                image{
                    large,
                    medium
                }
                gender
                description
                dateOfBirth{
                    month
                    day
                }
                age
            }
            role
            voiceActors {
                name{
                    full
                }
                languageV2
                image{
                    large,
                    medium
                }
            }
        }
    }
  }
}
'''

