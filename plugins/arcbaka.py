from telepot.namedtuple import InlineQueryResultArticle

name = "baka"
description = "Simple baka plugin"
helpStr = "Says you are a baka"
usage = "/baka"
regex = ["/baka"]
regexInline = ["/baka"]


def handler(bot, msg, fullMsg, type):
    if type == "normal":
        return "You baka!"
    if type == "inline_query":
        articles = [InlineQueryResultArticle(id='xyz', title='BAKA!', message_text='YOU ARE STILL A BAKA')]
        return articles
