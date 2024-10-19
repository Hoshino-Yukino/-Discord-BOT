import sqlite3
import datetime

async def checkHaveRole(DiscordId:int,RoleId:int):
    try:
        conn = sqlite3.connect('DiscordBot.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT endTime FROM timeRole WHERE discordId={DiscordId} AND roleId={RoleId}")
        result = cursor.fetchall()
        result[0][0]
        return True
    except IndexError:
        return False
    finally:
        cursor.close()
        conn.close()

async def addRole(DiscordId:int,RoleId:int,days:int):
    endTime = str(datetime.datetime.now() + datetime.timedelta(days=days)).split(".")[0]
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO timeRole VALUES({DiscordId},{RoleId},'{endTime}')")
    conn.commit()
    cursor.close()
    conn.close()

async def getRoleTime(DiscordId:int,RoleId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT endTime FROM timeRole WHERE discordId={DiscordId} AND roleId={RoleId}")
    result = cursor.fetchall()
    return str(result[0][0])

async def updateRoleTime(DiscordId:int,RoleId:int,days:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"UPDATE timeRole SET endTime=datetime(endTime,'+{days} days') WHERE discordId={DiscordId} AND roleId={RoleId}")
    conn.commit()
    cursor.close()
    conn.close()

async def addLinkedRoleData(DiscordId:int,Role:str):
    conn = sqlite3.connect('../DiscordBot/DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT count(*) FROM LinkedRoles WHERE {DiscordId}')
    result = cursor.fetchall()
    if result[0][0]<=0:
        cursor.execute(f"""INSERT INTO LinkedRoles (DiscordID,UroborosOwner,UroborosAdmin,UroborosMod) VALUES (?,?,?,?);"""
                ,(DiscordId,0,0,0))
        conn.commit()    
    cursor.execute(f"UPDATE LinkedRoles SET {Role}=1 WHERE Discordid= {DiscordId}")
    conn.commit()        
    cursor.close()
    conn.close()

async def removeRoleData(DiscordId:int,Role:str):
    conn = sqlite3.connect('../DiscordBot/DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT count(*) FROM LinkedRoles WHERE {DiscordId}')
    result = cursor.fetchall()
    returnFlag=0
    if result[0][0]<=0:
        cursor.execute(f"""INSERT INTO LinkedRoles (DiscordID,UroborosOwner,UroborosAdmin,UroborosMod) VALUES (?,?,?,?);"""
                ,(DiscordId,0,0,0))
        conn.commit()  
    else:
        cursor.execute(f"UPDATE LinkedRoles SET {Role}=0 WHERE Discordid= {DiscordId}")
        conn.commit()
        cursor.execute(f'SELECT AccessToken FROM LinkedRoles WHERE {DiscordId}')
        result = cursor.fetchall()
        if result[0][0] != None:
            returnFlag=1
     
    cursor.close()
    conn.close()
    return returnFlag

async def getDiscordTokens(user_id):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM LinkedRoles WHERE DiscordID={user_id}")
    result = cursor.fetchall()
    return result[0]

async def storeDiscordTokens(discordId,tokens):
    print(tokens)
    conn = sqlite3.connect('../DiscordBot/DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT count(*) FROM LinkedRoles WHERE {discordId}')
    result = cursor.fetchall()
    expirationTime = datetime.datetime.now() + datetime.timedelta(seconds=int(tokens["expires_in"])-10)
    if result[0][0]>0:
        cursor.execute(f"UPDATE LinkedRoles SET AccessToken='{tokens['access_token']}', RefreshToken='{tokens['refresh_token']}', ExpirationTime='{expirationTime}' WHERE Discordid= {discordId}")
    else:
        cursor.execute(f"""INSERT INTO LinkedRoles (DiscordID,AccessToken,RefreshToken,ExpirationTime,UroborosOwner,UroborosAdmin,UroborosMod) VALUES (?,?,?,?,?,?,?);"""
                        ,(discordId,tokens["access_token"],tokens["refresh_token"],expirationTime,0,0,0))
    conn.commit()        
    cursor.close()
    conn.close()


