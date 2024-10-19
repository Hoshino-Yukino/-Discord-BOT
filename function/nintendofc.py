import sqlite3

async def nfcIsInit(DiscordId:str):
    try:
        conn = sqlite3.connect('DiscordBot.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT NintendoFriendCode FROM NFC WHERE DiscordId={DiscordId}")
        result = cursor.fetchall()
        result[0][0]
        return True
    except IndexError:
        return False
    finally:
        cursor.close()
        conn.close()

async def getNfc(DiscordId:str):
    try:
        conn = sqlite3.connect('DiscordBot.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT NintendoFriendCode FROM NFC WHERE DiscordId={DiscordId}")
        result = cursor.fetchall()
        return result[0][0]
    except IndexError:
        return -1
    finally:
        cursor.close()
        conn.close()

async def nfcUpdate(DiscordId:str,nfc:str):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"UPDATE NFC SET NintendoFriendCode = '{nfc}' WHERE DiscordId= {DiscordId}")
    conn.commit()
    cursor.close()
    conn.close()

async def nfcInit(DiscordId:str,nfc:str):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO NFC VALUES ('{DiscordId}','{nfc}')")
    conn.commit()
    cursor.close()
    conn.close()

async def delnfc(DiscordId:str):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM NFC WHERE DiscordId={DiscordId}")
    conn.commit()
    cursor.close()
    conn.close()

