userListQuery: str = """
    query MediaListCollection($name: String, $type: MediaType, $chunk: Int) {
        MediaListCollection (userName: $name, type: $type, status: COMPLETED, chunk: $chunk, perChunk: 60) {
            hasNextChunk
            lists {
                name
                isCustomList
                entries {
                    media {
                        id
                    }
                }
            }
        }
    }"""

mediaDetails: str = """
    id
    title {
        english
        userPreferred
    }
    meanScore
    episodes
    startDate {
        year
    }
    studios (isMain: true) {
        nodes {
            name
            id
        }
    }
    genres
    tags {
        id
        name
    }
"""


def animeQuery() -> str:
    return f"""query($id: Int) {{
        Media (id: $id) {{
            {mediaDetails}
        }}
    }}"""
