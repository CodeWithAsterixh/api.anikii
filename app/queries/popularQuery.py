POPULAR = '''
query ($page: Int = 1) {
    Page(page: $page, perPage: 20) {
        pageInfo {
            lastPage
            currentPage
        }
        media(type: ANIME, popularity_greater: 10000, sort: [TRENDING_DESC, POPULARITY_DESC]) {
            id
            title {
                romaji
                english
            }
            status
            format
            coverImage {
                extraLarge
                color
            }
            popularity
            averageScore
            episodes
            trending
            bannerImage
            startDate {
                year
            }
        }
    }
}
'''
