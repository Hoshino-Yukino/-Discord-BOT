import sqlite3

async def createParty(VoiceChannelId:int,TextChannelId:int,CategoryId:int,CreatorId:int,RoleId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO PartyChat VALUES({VoiceChannelId},{TextChannelId},-1,{CategoryId},{CreatorId},{RoleId},0)")
    conn.commit()
    cursor.close()
    conn.close()

async def addKickHis(VoiceChannelId:int,UserId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO PCKickHis VALUES({VoiceChannelId},{UserId})")
    conn.commit()
    cursor.close()
    conn.close()

async def delOneKick(VoiceChannelId:int,UserId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM PCKickHis WHERE VoiceChannelId={VoiceChannelId} and UserId={UserId}")
    conn.commit()
    cursor.close()
    conn.close()

async def isKicked(VoiceChannelId:int,UserId:int):
    try:
        conn = sqlite3.connect('DiscordBot.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT UserId FROM PCKickHis WHERE VoiceChannelId={VoiceChannelId} and UserId={UserId}")
        result = cursor.fetchall()
        result[0][0]
        return True
    except IndexError:
        return False
    finally:
        cursor.close()
        conn.close()


async def delKickHis(VoiceChannelId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM PCKickHis WHERE VoiceChannelId={VoiceChannelId}")
    conn.commit()
    cursor.close()
    conn.close()

async def isPublicPartyChannel(VoiceChannelId:int):
    try:
        conn = sqlite3.connect('DiscordBot.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT RoleId FROM PartyChat WHERE VoiceChannelId={VoiceChannelId} and Status=0")
        result = cursor.fetchall()
        result[0][0]
        return True
    except IndexError:
        return False
    finally:
        cursor.close()
        conn.close()

async def isPublicPartyChannel(VoiceChannelId:int):
    try:
        conn = sqlite3.connect('DiscordBot.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT RoleId FROM PartyChat WHERE VoiceChannelId={VoiceChannelId} and status=0")
        result = cursor.fetchall()
        result[0][0]
        return True
    except IndexError:
        return False
    finally:
        cursor.close()
        conn.close()

async def getRoleId(VoiceChannelId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT RoleId FROM PartyChat WHERE VoiceChannelId={VoiceChannelId}")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result[0][0]

async def getKickHis(VoiceChannelId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT UserId FROM PCKickHis WHERE VoiceChannelId={VoiceChannelId}")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

async def deleteParty(VoiceChannelId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM PartyChat WHERE VoiceChannelId={VoiceChannelId}")
    conn.commit()
    cursor.close()
    conn.close()

async def isPartyChat(ChannelId):
    try:
        conn = sqlite3.connect('DiscordBot.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT RoleId FROM PartyChat WHERE VoiceChannelId={ChannelId} or TextChannelId={ChannelId}")
        result = cursor.fetchall()
        result[0][0]
        return True
    except IndexError:
        return False
    finally:
        cursor.close()
        conn.close()

async def isPartyCreator(ChannelId,CreatorId):
    try:
        conn = sqlite3.connect('DiscordBot.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT RoleId FROM PartyChat WHERE (VoiceChannelId={ChannelId} or TextChannelId={ChannelId}) and CreatorId={CreatorId}")
        result = cursor.fetchall()
        result[0][0]
        return True
    except IndexError:
        return False
    finally:
        cursor.close()
        conn.close()

async def isApplyChannel(ApplyChannelId):
    try:
        conn = sqlite3.connect('DiscordBot.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT RoleId FROM PartyChat WHERE ApplyChannelId={ApplyChannelId}")
        result = cursor.fetchall()
        result[0][0]
        return True
    except IndexError:
        return False
    finally:
        cursor.close()
        conn.close()

async def toPrivateChannel(VoiceChannelId,ApplyChannelId):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"UPDATE PartyChat SET ApplyChannelId={ApplyChannelId},Status=1 WHERE VoiceChannelId={VoiceChannelId}")
    conn.commit()
    cursor.close()
    conn.close()

async def toPublicChannel(VoiceChannelId):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"UPDATE PartyChat SET ApplyChannelId=-1,status=0 WHERE VoiceChannelId={VoiceChannelId}")
    conn.commit()
    cursor.close()
    conn.close()

async def getCategory(VoiceChannelId):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT CategoryId FROM PartyChat WHERE VoiceChannelId={VoiceChannelId}")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result[0][0]

async def getTextChannel(VoiceChannelId):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT TextChannelId FROM PartyChat WHERE VoiceChannelId={VoiceChannelId}")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result[0][0]

async def getApplyChannel(VoiceChannelId):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT ApplyChannelId FROM PartyChat WHERE VoiceChannelId={VoiceChannelId}")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result[0][0]

async def getVoiceChannel(ChannelId):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT VoiceChannelId FROM PartyChat WHERE VoiceChannelId={ChannelId} or TextChannelId={ChannelId} or ApplyChannelId={ChannelId}")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result[0][0]

async def getCreator(VoiceChannelId):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT CreatorId FROM PartyChat WHERE VoiceChannelId={VoiceChannelId}")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result[0][0]

async def trasferOwner(VoiceChannelId,trasferId):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"UPDATE PartyChat SET CreatorId={trasferId} WHERE VoiceChannelId={VoiceChannelId}")
    conn.commit()
    cursor.close()
    conn.close()

async def checkPrivate(VoiceChannelId):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT Status FROM PartyChat WHERE VoiceChannelId={VoiceChannelId}")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    if result[0][0]==1:
        return True
    else:
        return False
