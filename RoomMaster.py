#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import json
import io

CONTROLLER_GROUP_NAME = "房管控制台"
# TARGET_GROUP_NAME = "涂鸦战士绝武互刷群"
TARGET_GROUP_NAME = "房管控制台"
MAX_MEMBER_NUM = 4

DATA_PATH = "/Users/Siuver/.qqbot-tmp/plugins/Plugins/data.json"

HELP_MSG = '''鉴于之前绝武队组人总是组着组着人全不见了，这个房管插件是为了方便傻逼群友们写的。

首先，所有指令都要@一下房管才能生效

目前总共有如下指令：
帮助：查看帮助（尽量少调用，避免刷屏）
all：查看目前所有绝武的组队情况
xxx：xxx代表绝武名，例如光灯，可查看对应绝武的组队情况
xxx+ 或 xxx1：xxx代表绝武名，表示请求该绝武的组队
xxx-：xxx表示绝武名，表示退出该绝武的组队

例如：
“@房管 光灯”：查询光灯求组信息
“@房管 光灯+”或“@房管 光灯1”：进组

目前基本也就这么多指令了，当某个绝武的队伍人数达到4人后会发出通知并清空当前列表
（目前通知这一块虽然有@出去但好像没有@人的效果，意思就是qq没有提示，所以麻烦见到通知的人手动@一下另外3个人吧）

注意：
绝武名是有规范的，比如风镖是定位不到风飞镖的，目前提供以下绝武名：
['火斧','火弩','火杖','风矛','风飞镖','风环','水爪','水枪','水书','光剑','光铳','光灯','暗刀','暗机枪','吉他','混刷','局地','废矿']
如果指令无法识别请先看看是不是绝武名输错了，如果有补充可以随时私聊房管。

目前这个插件还处于测试阶段，只进行过简单的测试，有没有bug遗漏不敢保证。发现问题或者有功能上的建议的也可以随时私聊房管。初步打算先测试1天，收集问题并改进，如果没什么问题并且有帮助再投入长期使用。

谢谢傻逼群友们。

没啦'''

WEAPON_NAME = ['火斧', '火弩', '扫把#火杖#火扫把', '风矛#风枪', '风镖#风飞镖', '风环', '水爪', '水枪', '水书', '光剑', '光铳',
               '光灯', '暗刀', '暗机枪', '吉他', '混刷#杂图#绝图混刷#杂图混刷', '局地', '废矿', '火废矿', '光废矿', '风废矿', '暗废矿', '水废矿', '火图#火图混刷', '水图#水图混刷', '风图#风图混刷', '光图#光图混刷', '暗图#暗图混刷']

GROUP_INFO = {}


def sendMsgToTargetGroup(bot, msg):
    group = bot.List('group', TARGET_GROUP_NAME)[0]
    bot.SendTo(group, msg)


def joinGroup(weaponName, memberName):
    if weaponName not in GROUP_INFO.keys():
        GROUP_INFO[weaponName] = []

    if memberName in GROUP_INFO[weaponName]:
        return '【%s】已加入过【%s】队，居然还想再加一次？' % (memberName, weaponName)
    else:
        GROUP_INFO[weaponName].append(memberName)
        return '【%s】成功加入【%s】队' % (memberName, weaponName)


def quitGroup(weaponName, memberName):
    if weaponName not in GROUP_INFO.keys():
        GROUP_INFO[weaponName] = []

    if memberName not in GROUP_INFO[weaponName]:
        return '你都没加过这队退啥呢'
    else:
        GROUP_INFO[weaponName].remove(memberName)
        return '【%s】已退出【%s】队' % (memberName, weaponName)


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
                    retStr += '\t%s\n' % memberName
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
    if os.path.exists(DATA_PATH):
        with io.open(DATA_PATH, 'r') as f:
            GROUP_INFO = json.load(f)


def onQQMessage(bot, contact, member, content):
    if not bot.isMe(contact, member) and contact.name == TARGET_GROUP_NAME and "@ME" in content:
        if '帮助' in content:
            sendMsgToTargetGroup(bot, HELP_MSG)
        else:
            flag = False
            debugStr = ''
            if 'All' in content or 'all' in content:
                sendMsgToTargetGroup(bot, getGroupInfo())
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
                        sendMsgToTargetGroup(bot, joinGroup(targetName, member.name))
                        flag = True
                    if re.search(name + r'(?![+\-1])', content):
                        sendMsgToTargetGroup(bot, getGroupInfo(targetName))
                        flag = True

            if debugStr != "":
                sendMsgToTargetGroup(bot, debugStr)

            if not flag:
                sendMsgToTargetGroup(bot, "无法识别指令")
