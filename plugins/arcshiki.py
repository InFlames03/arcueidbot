import redis
from telepot.namedtuple import InlineQueryResultArticle

import arconfig
import tools.shikimoriapi

DB = redis.StrictRedis()

name = "arcshiki"
description = "Shikimori.org api plugin"
helpStr = ""
usage = "/character <name>"
regex = ["/character", "/similar"]
regexInline = ["/character"]
api = tools.shikimoriapi.Api(arconfig.SHIKI[0], arconfig.SHIKI[1])
MALANIME = "http://myanimelist.net/anime/%s"
MALMANGA = "http://myanimelist.net/manga/%s"


def setupAnimeIDs(animeID):
    if not DB.exists("arcueid:shiki:anime:%s:MAL" % animeID):
        anime = api.animes(animeID).get()
        DB.set("arcueid:shiki:anime:%s:MAL" % animeID, anime["myanimelist_id"])
        DB.set("arcueid:shiki:anime:%s:rating" % animeID, anime["rating"].upper())
        DB.set("arcueid:shiki:anime:%s:anidb" % animeID, anime["ani_db_id"])


def getMALId(animeId):
    setupAnimeIDs(animeId)
    return DB.get("arcueid:shiki:anime:%s:MAL" % animeId).decode("utf-8")


def getMangaIDs(mangaID):
    manga = api.mangas(mangaID).get()
    DB.set("arcueid:shiki:manga:%s:MAL" % mangaID, manga["myanimelist_id"])


def makeAns(chardata):
    ans = "*%s\n*" % chardata["name"]
    if "japanese" in chardata and chardata["japanese"] is not None:
        ans += "*Japanese name*: %s\n" % chardata["japanese"]
    if "russian" in chardata and chardata["russian"] is not None:
        ans += "*Russian name*: %s\n" % chardata["russian"]
    if "seyu" in chardata and len(chardata["seyu"]) > 0:
        ans += "*Seyu*: "
        for i in range(len(chardata["seyu"])):
            ans += chardata["seyu"][i]["name"]
            if i != len(chardata["seyu"]) - 1:
                ans += ","

    if "animes" in chardata and len(chardata["animes"]) > 0:
        ans += "\n*ANIME (%s)*:\n" % len(chardata["animes"])
        for i in range(min(len(chardata["animes"]), 10)):
            anime = chardata["animes"][i]
            if not DB.exists("arcueid:shiki:anime:%s:MAL" % anime["id"]):
                setupAnimeIDs(anime["id"])
            mal_id = DB.get("arcueid:shiki:anime:%s:MAL" % anime["id"]).decode("utf-8")
            ans += "[%s](%s) (%s episodes, %s)\n" % (
                anime["name"], MALANIME % mal_id, anime["episodes"], anime["kind"].upper())

    if "mangas" in chardata and len(chardata["mangas"]) > 0:
        ans += "*MANGA (%s):*\n" % len(chardata["mangas"])
        for i in range(min(len(chardata["mangas"]), 5)):
            manga = chardata["mangas"][i]
            if not DB.exists("arcueid:shiki:manga:%s:MAL" % manga["id"]):
                getMangaIDs(manga["id"])
            mal_id = DB.get("arcueid:shiki:manga:%s:MAL" % manga["id"]).decode("utf-8")
            ans += "[%s](%s) (%s chapters, %s volumes)\n" % (
                manga["name"], MALMANGA % mal_id, manga["chapters"], manga["volumes"])

    return ans


def handler(bot, msg, fullMsg, flavor):
    msg = msg.split(maxsplit=1)
    if len(msg) < 2:
        return usage
    if msg[0] == "/character":
        char = msg[1].strip()
        req = api.characters("search", q=char).get()
        if flavor == "normal":
            if len(req) == 0:
                return "Nothing found"
            chardata = api.characters(req[0]["id"]).get()
            return makeAns(chardata)
        elif flavor == "inline_query":
            if len(req) == 0:
                return None
            articles = []
            for i in range(min(len(req), 5)):
                chardata = api.characters(req[i]["id"]).get()
                if "animes" in chardata and len(chardata["animes"]) > 0:
                    firstAnime = chardata["animes"][0]["name"]
                else:
                    firstAnime = "No anime"

                articles.append(InlineQueryResultArticle(disable_web_page_preview=True, parse_mode="Markdown",
                                                         id=str(i), title="%s (%s)" % (req[i]["name"], firstAnime),
                                                         message_text=makeAns(chardata)))
            return articles
    elif msg[0] == "/similar":
        if flavor == "normal":
            name = msg[1].strip()
            animes = api.animes("search", q=name).get()
            if len(animes) == 0:
                return "Anime not found"
            chosen = 0
            maxEpsCount = 0
            for i in range(len(animes)):
                if animes[i]["episodes"] > maxEpsCount:
                    chosen, maxEpsCount = i, animes[i]["episodes"]

            animeId = animes[chosen]["id"]
            setupAnimeIDs(animeId)
            similar = api.animes("%s/similar" % animeId).get()
            if len(similar) == 0:
                return "No  anime similar    with *%s* found" % animes[chosen]["name"]
            ans = "Anime similar with *%s* (%s) \n" % (animes[chosen]["name"], len(similar))
            for i in range(min(len(similar), 10)):
                anime = similar[i]
                setupAnimeIDs(anime["id"])
                ans += "[%s](%s) (%s episodes, %s)\n" % (
                    anime["name"], MALANIME % getMALId(anime["id"]), anime["episodes"], anime["kind"].upper())

            return ans
