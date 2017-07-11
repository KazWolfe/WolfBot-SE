import WolfUtils
import os

import ChatExchange.chatexchange as chatexchange
from git import Repo

from WolfPlugin import registerCommand, registerTask, registerListener
from WolfPrefs import PREFS
from WolfPrefs import SESSION_STORAGE

gitRepo = Repo(os.path.abspath('.'))
print("loaded git repo os.path.abspath('.')" + str(os.path.abspath('.')))

def getLatestVersionInfo(branch):
    onRemote = gitRepo.iter_commits(branch + '..origin/' + branch)
    onLocal = gitRepo.iter_commits('origin/' + branch + '..' + branch)

    if gitRepo.is_dirty:
        return("Update check unavailable: manual mode.")

    if len(onLocal) > 0:
        print(onLocal[-1])
        return("Update check unavailable: inconsistent state.")

    if len(onRemote) > 0:
        latestRemote = onRemote[-1]
        return("Update available!")

    return("Running latest version.")

@registerCommand("version", "Get current WolfBot version info.", "", {})
def getVersionInfo(message, args):
    commit = str(gitRepo.head.commit)
    branch = str(gitRepo.active_branch)

    versionString = "WolfBot version %A" + branch + "-" + commit[-7:] + "%B"

    if not gitRepo.is_dirty:
        git_url = "https://github.com/KazWolfe/WolfBot-SE/commit/" + commit
        versionString = versionString.replace("%A", "[`")
        versionString = versionString.replace("%B", "`](" + git_url + ")")
    else:
        versionString = versionString.replace("%A", "`")
        versionString = versionString.replace("%B", "")
        versionString += "+`"

    updateCheck = getLatestVersionInfo(branch)
    if (updateCheck != "Running latest version."):
        versionString += " - " + updateCheck

    message.message.reply(versionString)
