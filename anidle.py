import argparse
from dataclasses import dataclass
import random
from apitools import fetchDataForMedia, fetchDataForType
from enum import Enum


class Proximity(Enum):
    FAR = 1
    CLOSE = 2
    EXACT = 3


@dataclass
class GuessProximity:
    guessVal: int
    prox: Proximity


@dataclass
class Diff:
    commonTags: list
    commonGenres: list
    commonStudios: list
    year: Proximity
    episodes: Proximity
    meanScore: Proximity

    def __str__(self):
        string = f"""Correct tags: {[a['name'] for a in self.commonTags]}
Correct genres: {self.commonGenres}
Correct studios: {[a['name'] for a in self.commonStudios]}
The year {self.year.guessVal} is {self.year.prox.name}
"""
        if self.episodes:
            string += f"The episode count {self.episodes.guessVal} is {self.episodes.prox.name}\n"
        string += (
            f"The mean score {self.meanScore.guessVal}% is {self.meanScore.prox.name}\n"
        )
        return string


def getListIntersection(guessList: list, secretList: list) -> list:
    return [item for item in guessList if item in secretList]


def getProximity(guessVal: int, secretVal: int, delta: int = 10) -> Proximity | None:
    if not guessVal or not secretVal:
        return None
    if guessVal == secretVal:
        return GuessProximity(guessVal, Proximity.EXACT)
    if abs(guessVal - secretVal) <= delta:
        return GuessProximity(guessVal, Proximity.CLOSE)
    return GuessProximity(guessVal, Proximity.FAR)


def generateDiff(guessMedia, secretMedia) -> Diff:
    return Diff(
        getListIntersection(guessMedia["tags"], secretMedia["tags"]),
        getListIntersection(guessMedia["genres"], secretMedia["genres"]),
        getListIntersection(
            guessMedia["studios"]["nodes"], secretMedia["studios"]["nodes"]
        ),
        getProximity(guessMedia["startDate"]["year"], secretMedia["startDate"]["year"]),
        getProximity(guessMedia["episodes"], secretMedia["episodes"]),
        getProximity(guessMedia["meanScore"], secretMedia["meanScore"]),
    )

parser = argparse.ArgumentParser()
parser.add_argument(
    "userName",
    help="your Anilist username",
)
args = parser.parse_args()

userListIds = fetchDataForType("ANIME", args.userName)

secretMedia = fetchDataForMedia(random.choice(userListIds))

while True:
    print("Guess the series by entering an AniList ID!")
    guessId = int(input())

    if guessId == secretMedia["id"]:
        print("You got it right!")
        break

    guessMedia = fetchDataForMedia(guessId)

    diff = generateDiff(guessMedia, secretMedia)
    print(diff)
