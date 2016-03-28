import arconfig

description = "help plugin"
helpStr = "prints help"
name = "help"
regex = ["/help"]
regexInline = []

def handler(bot,msg, fullMsg, type):
    if type == "normal":
        msg = msg.split()
        if len(msg) == 1:
            ans = "Help for *Arcueid* bot\n"
            ans += "List of plugins:\n\n"
            for plug in arconfig.plugins:
                if plug.description is not None:
                    ans += "*%s* - %s\n" % (plug.name, plug.description)
            return ans
        elif len(msg) == 2:
            plugName = msg[1]
            for plug in arconfig.plugins:
                if plug.name == plugName and plug.helpStr is not None:
                    ans = "Help for *%s*\n" % plug.name
                    ans += plug.helpStr
                    return ans
            return "No help on this topic"
