import sqlite3

async def getLastNumber():
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(number)FROM countingGame")
    result = cursor.fetchall()
    value = result[0][0]
    cursor.close()
    conn.close()
    return int(value)

async def checkCountingLog(DiscordId:str,date:str):
    try:
        conn = sqlite3.connect('DiscordBot.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT number FROM countingGame WHERE DiscordId={DiscordId} and countDate='{date}'")
        result = cursor.fetchall()
        result[0][0]
        return False
    except IndexError:
        return True
    finally:
        cursor.close()
        conn.close()

async def insertCounting(DiscordId:str,number:int,date:str):
    print(date)
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO countingGame VALUES({DiscordId},{number},'{date}')")
    conn.commit()
    cursor.close()
    conn.close()