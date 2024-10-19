import sqlite3

async def ecoInit(DiscordId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO ECO VALUES({DiscordId},0)")
    conn.commit()
    cursor.close()
    conn.close()

async def ecoUpdate(DiscordId:int,changeMira:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()  
    cursor.execute(f"UPDATE ECO SET mira = mira +({changeMira}) WHERE DiscordId = {DiscordId}")
    conn.commit()
    cursor.close()
    conn.close()

async def ecoIsInit(DiscordId:int):
    try:
        conn = sqlite3.connect('DiscordBot.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT mira FROM ECO WHERE DiscordId={DiscordId}")
        result = cursor.fetchall()
        result[0][0]
        return True
    except IndexError:
        return False
    finally:
        cursor.close()
        conn.close()

async def ecoCal(DiscordId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT mira FROM ECO WHERE DiscordId={DiscordId}")
    result = cursor.fetchall()
    return result[0][0]

async def ecoSet(DiscordId:int,mira:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()  
    cursor.execute(f"UPDATE ECO SET mira = {mira} WHERE DiscordId = {DiscordId}")
    conn.commit()
    cursor.close()
    conn.close()
