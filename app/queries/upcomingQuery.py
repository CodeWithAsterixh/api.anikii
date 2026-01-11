UPCOMING = """
query($page: Int = 1) { 
    Page(page: $page, perPage: 20) {
        pageInfo {
            lastPage
            currentPage
        }
        airingSchedules(notYetAired: true) {
            media {
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
                "banner_image":bannerImage,
                startDate {
                    year
                }
            }
        }
    }
}
"""
