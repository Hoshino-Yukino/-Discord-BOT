import sqlite3


async def initTable(discordId:int,isGPT4:int=0):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS GPT_{discordId}")
    conn.commit()
    cursor.execute(f"CREATE TABLE GPT_{discordId}(_id INTEGER PRIMARY KEY autoincrement,Role VARCHAR(15), Message VARCHAR(2000), IsGPT4 INTEGER);")
    conn.commit()
    cursor.execute(f"""INSERT INTO GPT_{discordId} (Role,Message,IsGPT4) VALUES (?,?,?);""",("system","You are ChatGPT, a large language model trained by OpenAI.\\n Carefully heed the user's instructions.Respond using Markdown.",isGPT4))
    conn.commit()
    cursor.close()
    conn.close()

async def addMessage(discordId:int,role:str,message:str):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"""INSERT INTO GPT_{discordId} (Role,Message) VALUES (?,?);""",(role,message))
    conn.commit()
    cursor.close()
    conn.close()

async def checkMsgQuantity(discordId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT role FROM GPT_{discordId} WHERE role='user'")
    result = cursor.fetchall()
    return len(result)

async def getUserAllMsg(discordId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM GPT_{discordId}")
    result = cursor.fetchall()
    return result

async def dropTable(discordId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS GPT_{discordId}")
    conn.commit()
    cursor.close()
    conn.close()

async def checkTableExist(discordId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT count(*) FROM sqlite_master WHERE type="table" AND name = "GPT_{discordId}"')
    result = cursor.fetchall()
    if result[0][0]>0:
        cursor.close()
        conn.close()
        return True
    else:
        cursor.close()
        conn.close()
        return False
    

async def updateUserState(discordId:int,generatingNow:int=-1,newTimes:int=0,generatingTimes:int=0,language:str=None,transModel:str=None,gpt4Permission:int=None):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT count(*) FROM GPT_USERS WHERE Discordid={discordId}')
    result = cursor.fetchall()
    if result[0][0]==0:
        cursor.execute(f"INSERT INTO GPT_USERS VALUES ({discordId},0,0,0,'Chinese','gpt-3.5-turbo-16k-0613',0);")
        conn.commit()

    if generatingNow != -1:
        cursor.execute(f"UPDATE GPT_USERS SET GENERATING_NOW={generatingNow} WHERE Discordid= {discordId}")
        conn.commit()

    if newTimes != 0:
        cursor.execute(f"UPDATE GPT_USERS SET New_times= New_times + {newTimes} WHERE Discordid= {discordId}")
        conn.commit()

    if generatingTimes != 0:
        cursor.execute(f"UPDATE GPT_USERS SET Generate_Times= Generate_Times + {generatingTimes} WHERE Discordid= {discordId}")
        conn.commit()
    
    if language != None:
        cursor.execute(f"UPDATE GPT_USERS SET Translation_Language='{language}' WHERE Discordid= {discordId}")
        conn.commit()
    
    if transModel != None:
        cursor.execute(f"UPDATE GPT_USERS SET Translation_Model='{transModel}' WHERE Discordid= {discordId}")
        conn.commit()
    
    if gpt4Permission != None:
        cursor.execute(f"UPDATE GPT_USERS SET GPT4_Permission={gpt4Permission} WHERE Discordid= {discordId}")
        conn.commit()

    conn.close()

async def getUserFlag(discordId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT GENERATING_NOW FROM GPT_USERS WHERE DiscordID={discordId}")
    result = cursor.fetchall()
    return int(result[0][0])

async def adminBugFix(discordId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"UPDATE GPT_USERS SET GENERATING_NOW= 0 WHERE Discordid= {discordId}")
    conn.commit()
    cursor.close()
    conn.close()

async def getTransInfo(discordId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT count(*) FROM GPT_USERS WHERE Discordid={discordId}')
    result = cursor.fetchall()
    if result[0][0]==0:
        cursor.execute(f"INSERT INTO GPT_USERS VALUES ({discordId},0,0,0,'Chinese','gpt-3.5-turbo-0613',0);")
        conn.commit()
        return ["chinese","gpt-3.5-turbo-0613"]
    cursor.execute(f"SELECT Translation_Language,Translation_Model FROM GPT_USERS WHERE DiscordID={discordId}")
    result = cursor.fetchall()
    return result[0]

async def haveGPT4(discordId:int):
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT GPT4_Permission FROM GPT_USERS WHERE DiscordID={discordId}")
    result = cursor.fetchall()
    return int(result[0][0])

async def checkGPT4Enable():
    conn = sqlite3.connect('DiscordBot.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT GPT4_Permission FROM GPT_USERS WHERE DiscordID=0")
    result = cursor.fetchall()
    return int(result[0][0])



