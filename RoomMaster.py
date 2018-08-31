#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import json
import io

CONTROLLER_GROUP_NAME = "房管控制台"
TARGET_GROUP_NAME = "涂鸦战士绝武互刷群"
# TARGET_GROUP_NAME = "房管控制台"
MAX_MEMBER_NUM = 4

DATA_PATH = "/Users/Siuver/.qqbot-tmp/plugins/Plugins/data.json"

NEW_MSG = '''新房管的功能可以说强大了不少，基本上连松鼠都能用，不会再有太多的指令无法识别的问题了，除非你是真的在乱搞（bug是没有的，这辈子都不会有的）

首先新特性：
1. 多词义匹配，火杖可以自动匹配到扫把了
2. 查询功能扩展，可以看自己已加入过的队伍
3. 指令组合。指令的组合方式可以更灵活
4. 数据存储问题，解决了之前重启房管就会清空组队信息的问题

问题：
1. 整个系统依然是跑在我的主机上，所有会影响到我电脑的因素都会直接影响到房管系统，各位做好房管随时会挂的准备。
2. 因为上一条的原因，房管不可能有24/7的工作制，随时下线休息。
3. 数据也是存储在本机上，这个影响并没有太大。
4. 队伍人齐的通知并没有真正的提示效果，这个已确定无法解决。

注意：
该系统以群名片作为标识进行识别，也就是说改名、重名等情况都会影响正常使用所以，尽量不要频繁改名。如果需要改名的，在改名之前要退出所有自己已加入的队伍。
'''

HELP_MSG = '''所有指令都要@一下房管才能生效

目前总共有如下指令：
帮助：查看帮助（尽量少调用，避免刷屏）
all：查看目前所有绝武的组队情况
me: 查看目前自己已加入过的队伍
xxx：xxx代表绝武名，例如光灯，可查看对应绝武的组队情况
xxx+ 或 xxx1：xxx代表绝武名，表示请求该绝武的组队
xxx-：xxx表示绝武名，表示退出该绝武的组队

各种指令可以组合使用。
'''

WEAPON_NAME = ['火斧', '火弩', '扫把#火杖', '风矛#风枪', '风镖#风飞镖', '风环', '水爪', '水枪', '水书', '光剑', '光铳#光枪',
               '光灯', '暗刀', '暗机枪', '吉他', '混刷#杂图', '局地', '废矿', '火矿', '水矿', '风矿', '光矿', '暗矿', '火武#火图', '水武#水图', '风武#风图', '光武#光图', '暗武#暗图']

GROUP_INFO = {}

def eraseTheFxxkingU(input, encoding='utf-8'):
    if isinstance(input, dict):
        return {eraseTheFxxkingU(key): eraseTheFxxkingU(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [eraseTheFxxkingU(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode(encoding)
    else:
        return input


def sendMsgToTargetGroup(bot, msg):
    group = bot.List('group', TARGET_GROUP_NAME)[0]
    bot.SendTo(group, msg)


def sendMsgToController(bot, msg):
    group = bot.List('group', CONTROLLER_GROUP_NAME)[0]
    bot.SendTo(group, msg)


def getFormerRecord(bot):
    if os.path.exists(DATA_PATH): 
            with open(DATA_PATH, 'r') as f:
                try:
                    global GROUP_INFO
                    GROUP_INFO = eraseTheFxxkingU(json.loads(f.read(), encoding='utf-8'))
                except:
                    pass


def recordGroupInfo():
    with open(DATA_PATH, "w") as f:
        f.write(json.dumps(GROUP_INFO, ensure_ascii = False))


def debug(bot):
    info = json.dumps(GROUP_INFO)
    sendMsgToController(bot, info)


def joinGroup(weaponName, memberName):
    if weaponName not in GROUP_INFO.keys():
        GROUP_INFO[weaponName] = []
    ret = ''
    if memberName in GROUP_INFO[weaponName]:
        ret = '【%s】已加入过【%s】队，居然还想再加一次？' % (memberName, weaponName)
    else:
        GROUP_INFO[weaponName].append(memberName)
        ret = '【%s】已加入【%s】队' % (memberName, weaponName)
    recordGroupInfo()
    return ret


def quitGroup(weaponName, memberName):
    if weaponName not in GROUP_INFO.keys():
        GROUP_INFO[weaponName] = []
    ret = ''
    if memberName not in GROUP_INFO[weaponName]:
        ret = '你都没加过【%s】队还想退' % weaponName
    else:
        GROUP_INFO[weaponName].remove(memberName)
        ret = '【%s】已退出【%s】队' % (memberName, weaponName)
    recordGroupInfo()
    return ret


def getGroupInfo(weaponName="All"):
    retStr = ""
    devider = "------------------\n"
    if weaponName == "All":
        memberNum = 0
        retStr = "目前所有绝武求组信息如下：\n" + devider
        for key in GROUP_INFO.keys():
            memberList = GROUP_INFO[key]
            if len(memberList):
                retStr += key + "：\n"
                for memberName in memberList:
                    retStr += '    %s\n' % memberName
                    memberNum += 1
                retStr += devider
        if memberNum == 0:
            retStr = '暂无任何求组信息'
    else:
        if weaponName in GROUP_INFO.keys():
            memberList = GROUP_INFO[weaponName]
            if len(memberList):
                retStr = '【%s】求组信息如下：\n' % weaponName
                for memberName in memberList:
                    retStr += '%s\n' % memberName
            else:
                retStr = '目前还没人求组【%s】' % weaponName
        else:
            retStr = '目前还没人求组【%s】' % weaponName

    return retStr


def checkMyGroup(memberName):
    retMsg = '【%s】加入过的队伍有:\n    ' % memberName
    num = 0
    for weaponName in GROUP_INFO.keys():
        memberList = GROUP_INFO[weaponName]
        if memberName in memberList:
            num += 1
            retMsg += '【%s】  ' % weaponName
    if num == 0:
        retMsg = '【%s】目前未加入任何队伍' % memberName
    return retMsg


def checkGroupFull(weaponName):
    msg = ""
    if weaponName in GROUP_INFO.keys():
        memberList = GROUP_INFO[weaponName]
        if len(memberList) == MAX_MEMBER_NUM:
            msg = '【%s】队已经人齐了：\n' % weaponName
            while len(memberList):
                msg += '@%s ' % memberList.pop()
    return msg


def onPlug(bot):
    sendMsgToController(bot, "房管上线成功")
    getFormerRecord(bot)


def onUnplug(bot):
    sendMsgToController(bot, "房管已下线")


def onQQMessage(bot, contact, member, content):
    if not bot.isMe(contact, member) and contact.name == TARGET_GROUP_NAME and "@ME" in content:
        if '帮助' in content:
            sendMsgToTargetGroup(bot, HELP_MSG)
        elif 'new' in content:
            sendMsgToTargetGroup(bot, NEW_MSG)
        else:
            flag = False
            debugStr = ''
            if 'All' in content or 'all' in content:
                sendMsgToTargetGroup(bot, getGroupInfo())
                flag = True

            if 'me' in content or 'me' in content:
                sendMsgToTargetGroup(bot, checkMyGroup(member.name))
                flag = True
            
            for weaponName in WEAPON_NAME:
                nameList = weaponName.split("#")
                targetName = nameList[0]
                for name in nameList:
                    if re.search(name + r'(?=[+1])', content):
                        sendMsgToTargetGroup(bot, joinGroup(targetName, member.name))
                        fullMsg = checkGroupFull(weaponName)
                        if fullMsg:
                            sendMsgToTargetGroup(bot, fullMsg)
                        flag = True
                    if re.search(name + r'(?=-)', content):
                        sendMsgToTargetGroup(bot, quitGroup(targetName, member.name))
                        flag = True
                    if re.search(name + r'(?![+\-1])', content):
                        sendMsgToTargetGroup(bot, getGroupInfo(targetName))
                        flag = True

            if debugStr != "":
                sendMsgToTargetGroup(bot, debugStr)

            if not flag:
                sendMsgToTargetGroup(bot, "？？？")
