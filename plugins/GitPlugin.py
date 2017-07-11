import WolfUtils
import os

import ChatExchange.chatexchange as chatexchange
from git import Repo
import git

from WolfPlugin import registerCommand, registerTask, registerListener
from WolfPrefs import PREFS
from WolfPrefs import SESSION_STORAGE

from BasePlugin import restart

gitRepo = Repo(os.path.abspath('.'))
git_base_url = "https://github.com/KazWolfe/WolfBot-SE/commit/"

def getLatestVersionInfo(branch):
    onRemote = list(gitRepo.iter_commits(branch + '..origin/' + branch))
    onLocal = list(gitRepo.iter_commits('origin/' + branch + '..' + branch))

    latestRemote = str(git.remote.Remote(gitRepo, 'origin').fetch()[0].commit)

    state = -1

    if gitRepo.is_dirty():
        state = 100
    elif len(onLocal) > 0:
        state = 101
    elif len(onRemote) > 0:
        state = 1
    elif str(gitRepo.head.commit) == latestRemote:
        state = 0

    return {'state': state, 'latest': latestRemote}

@registerCommand("version", "Get current WolfBot version info.", "", {})
def getVersionInfo(message, args):
    commit = str(gitRepo.head.commit)
    branch = str(gitRepo.active_branch)

    updateCheck = getLatestVersionInfo(branch)
    updateState = updateCheck['state']

    versionString = "WolfBot version %A" + branch + "-" + commit[-7:] + "%B"

    if updateState == 0:
        git_url = git_base_url + commit
        versionString = versionString.replace("%A", "[`")
        versionString = versionString.replace("%B", "`](" + git_url + ")")
    else:
        versionString = versionString.replace("%A", "`")
        versionString = versionString.replace("%B", "")
        if updateState == 100:
            versionString += "+"
        versionString += "`"

    if (updateState == -1):
        versionString += " - Error checking for updates."
    elif (updateState == 100):
        versionString += " - unversioned, origin's latest [`" \
            + updateCheck['latest'][-7:] + "`](" \
            + git_base_url + updateCheck['latest'] + ")"
    elif (updateState == 101):
        versionString += " - prerelease, origin's latest [`" \
            + updateCheck['latest'][-7:] + "`](" \
            + git_base_url + updateCheck['latest'] + ")"


    message.message.reply(versionString)

@registerCommand("update", "Update WolfBot to the latest code version", "", {"superuserNeeded": True})
def updateWolfbot(message, args):
    commit = str(gitRepo.head.commit)
    branch = str(gitRepo.active_branch)
    origin = git.remote.Remote(gitRepo, 'origin')

    updateCheck = getLatestVersionInfo(branch)
    updateStatus = updateCheck['state']

    if updateStatus == -1:
        message.message.reply("Error with updater. Please try again later.")
        return None
    elif updateStatus == 0:
        message.message.reply("No need to update, at latest version.")
        return None
    elif updateStatus == 1:
        origin.pull()
        message.message.reply("Updated to commit `" \
            + updateCheck['latest'][-7] + "`. Bot restarting...")
        restart()
        return None
    elif updateStatus >= 100:
        message.message.reply("Manual update necessary to resolve issues.")
        return None
