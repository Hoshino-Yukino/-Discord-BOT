import sqlite3
import datetime


async def addLog(DiscordId:int,Operation:str):

    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"""INSERT INTO AuditLog (DiscordID,Datetime,Operation) VALUES (?,?,?);"""
                    ,(DiscordId,datetime.datetime.now(),Operation))
    conn.commit()
    cursor.close()
    conn.close()

