#!/usr/bin/env python
# -*- coding: utf-8 -*-

CONTROLLER_GROUP_NAME = "房管控制台"


def sendMsgToController(bot, msg):
    group = bot.List('group', CONTROLLER_GROUP_NAME)[0]
    bot.SendTo(group, msg)


def onQQMessage(bot, contact, member, content):
    if not bot.isMe(contact, member) and contact.name == CONTROLLER_GROUP_NAME and "@ME" in content:
        if "show" in content:
            group = bot.List('group', CONTROLLER_GROUP_NAME)[0]
            memberList = bot.List(group)
            msg = ""
            for memberInfo in memberList:
                msg += memberInfo.name
            sendMsgToController(bot, msg)
        elif "update" in content:
            group = bot.List('group', CONTROLLER_GROUP_NAME)[0]
            bot.Update(group)
            sendMsgToController(bot, "更新列表成功")