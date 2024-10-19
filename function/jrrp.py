import sqlite3

async def jrrpIsInit(DiscordId:str):
    try:
        conn = sqlite3.connect('DiscordBot.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT DiscordId FROM JRRP WHERE DiscordId={DiscordId}")
        result = cursor.fetchall()
        result[0][0]
        return True
    except IndexError:
        return False
    finally:
        cursor.close()
        conn.close()

async def jrrpInit(DiscordId:str):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO JRRP VALUES ({DiscordId},-1,'2000-01-01')")
    conn.commit()
    cursor.close()
    conn.close()

async def getTodayJrrp(DiscordId:str,date:str):
    try:
        conn = sqlite3.connect('DiscordBot.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT rp FROM JRRP WHERE DiscordId={DiscordId} AND jrrpDate='{date}'")
        result = cursor.fetchall()
        return int(result[0][0])
    except IndexError:
        return -1
    finally:
        cursor.close()
        conn.close()

async def jrrpUpdate(DiscordId:str,jrrp:int,date:str):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"UPDATE JRRP SET rp = {jrrp},jrrpDate='{date}' WHERE Discordid= {DiscordId}")
    conn.commit()
    cursor.close()
    conn.close()

