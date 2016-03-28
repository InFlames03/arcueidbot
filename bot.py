import telepot
import arconfig
from pprint import pprint
import time
import sys
import re

bot = telepot.Bot(arconfig.TOKEN)
arconfig.BOTINFO = bot.getMe()
print(bot.getMe())
arconfig.registerPlugins()
arconfig.initRedis()


def testRegex(regexes, msgText):
    for regex in regexes:
        if re.match(regex, msgText):
            return True
    return False


def handle_msg(msg):
    flavor = telepot.flavor(msg)
    print(flavor)
    pprint(msg)
    if flavor == "normal":
        content_type, chat_type, chat_id = telepot.glance(msg, flavor)
        if content_type != "text":
            return
        msgText = msg["text"].strip()
        for plugin in arconfig.plugins:
            if testRegex(plugin.regex, msgText):
                ans = plugin.handler(bot, msgText, msg, flavor)
                if ans is not None:
                    bot.sendMessage(chat_id, ans, reply_to_message_id=msg["message_id"], parse_mode="Markdown",
                                    disable_web_page_preview=True)
        print(content_type, chat_type, chat_id)

    elif flavor == "inline_query":
        query_id, from_id, query_string = telepot.glance(msg, flavor)
        for plugin in arconfig.plugins:
            if testRegex(plugin.regexInline, query_string):
                ans = plugin.handler(bot, query_string, msg, flavor)
                if ans is not None:
                    bot.answerInlineQuery(query_id, ans)


bot.notifyOnMessage(handle_msg)
while 1:
    time.sleep(10)
