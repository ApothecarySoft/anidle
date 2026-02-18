import json
import time
from gql import gql, Client
from gql.transport.httpx import HTTPXTransport
from gql.transport.exceptions import TransportQueryError
import queries
from cachefiles import saveUserDataFile


_transport = HTTPXTransport(url="https://graphql.anilist.co", timeout=120)
_client = Client(transport=_transport, fetch_schema_from_transport=False)


def _fetchDataForChunk(mediaType: str, chunk: int, userName: str):
    print(f"fetching for chunk #{chunk}")
    query = gql(queries.userListQuery)
    result = None
    MAX_RETRIES = 3
    retries = 0
    while result == None and retries <= MAX_RETRIES:
        try:
            result = _client.execute(
                query,
                variable_values={"name": userName, "type": mediaType, "chunk": chunk},
            )
        except TransportQueryError as e:
            errorCode = e.errors[0]["status"]
            retries += 1
            if errorCode == 429:
                print(
                    f"got http {errorCode}, server is rate limiting us. waiting to continue fetching data"
                )
                _countdownTimer_s(65)
            else:
                print(f"unhandled http error {errorCode}. trying again in 10 seconds")
                _countdownTimer_s(10)
    lists = result["MediaListCollection"]["lists"]
    entries = [
        listEntries
        for currentList in lists
        for listEntries in currentList["entries"]
        if not currentList["isCustomList"]
    ]
    return entries, result["MediaListCollection"]["hasNextChunk"]


def _countdownTimer_s(seconds: int):
    while seconds > 0:
        print(seconds)
        time.sleep(1)
        seconds -= 1


def fetchDataForType(mediaType: str, userName: str):
    print(f"fetching data for type {mediaType}")
    chunkNum = 0
    hasNextChunk = True
    entries = []
    while hasNextChunk:
        chunkNum += 1
        newEntries, hasNextChunk = _fetchDataForChunk(
            mediaType=mediaType, chunk=chunkNum, userName=userName
        )
        entries += newEntries

    entries = [x["media"]["id"] for x in entries]
    saveUserDataFile(userName=userName, mediaType=mediaType, entries=entries)

    return entries


def fetchDataForMedia(mediaId: int):

    result = _client.execute(
        gql(queries.animeQuery()),
        variable_values={"id": mediaId},
    )
    return result["Media"]
