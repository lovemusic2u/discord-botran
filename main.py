import discord
from discord.ext import commands
import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define your intents
intents = discord.Intents.default()
intents.messages = True # This allows your bot to receive message events

load_dotenv()
# Discord bot token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Define your DSN (Data Source Name)
DSN = os.getenv('DSN_NAME')

# Create a bot instance with intents
bot = commands.Bot(command_prefix='^', intents=intents)

@bot.command()
async def point(ctx, user_id: str): # Assuming user_id is an integer

    current_time = datetime.now()
    formatted_time = current_time.strftime("%d/%m/%Y %H:%M:%S")

    logging.info("เวลา %s ชื่อผู้ใช้ %s", formatted_time, user_id)
    
    try:
        # Connect to the database using DSN
        with pyodbc.connect('DSN=' + DSN) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT UserName, UserPoint, UserPoint2,PlayTime FROM UserInfo WHERE UserID = ?', (user_id,))
            rows = cursor.fetchall()

        if not rows:
            await ctx.send("ไม่มี ID นี้นะเมี๊ยว ถ้ามั่นใจว่ามีให้ลองติดต่อ GM นะเมี๊ยว")
            return

        # Format and send the results to Discord channel
        for row in rows:
            # Example: sending only the user's name (assuming the first column is the user's name)
            await ctx.send(f"ID ของคุณท่าน คือ : {row[0]} \nเวลา Online คงเหลือ : {row[3]}\nPont กิจกรรม : {row[1]} \nPoint เติมเงิน: {row[2]}")

            logging.info("ID ของคุณท่าน คือ : %s , เวลา Online คงเหลือ : %s , Pont กิจกรรม : %s , Point เติมเงิน: %s", row[0], row[3], row[1], row[2])
            print("=====================================================================")

        user = ctx.message.author
        logging.info("User ID: %s, Username: %s", user.id, user.name)

    except ValueError:
        await ctx.send(f"Invalid user ID format. Please ensure the user ID is an integer.")
    except pyodbc.Error as e:
        await ctx.send(f"An error occurred while processing your request: {str(e)}")


@point.error
async def point_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("โปรดใส่ User ID ด้วย นะเมี๊ยว")

@bot.command()
async def playpoint(ctx, user_id: str, user_cha: str, playtime_to_exchange: int): # Assuming user_id is an integer

    current_time = datetime.now()
    formatted_time = current_time.strftime("%d/%m/%Y %H:%M:%S")

    logging.info("เวลา %s ชื่อผู้ใช้ %s", formatted_time, user_id)
    
    try:
        # Connect to the database using DSN
        with pyodbc.connect('DSN=' + DSN) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT UserName, UserPoint, UserPoint2,PlayTime,UserSA FROM UserInfo WHERE UserID = ? and UserSA = ? and UserLoginState = 0', (user_id,user_cha,))
            rows = cursor.fetchall()

        if not rows:
            await ctx.send(":x: User หรือ รหัสเข้าถึงตัวละคร ไม่ถูกต้อง หรือ User กำลัง Online อยู่ โปรดตรวจสอบให้แน่ใจ ก่อนนะเมี๊ยว")
            return
        
        # Check if the selected playtime matches the specified options
        if playtime_to_exchange not in [300, 600, 900, 1200]:
            await ctx.send(":warning: เกิดข้อผิดพลาดแล้วเมี๊ยว! \nเราให้เลือก ได้ตามนี้นะ `300`, `600`, `900`, หรือ `1200` นาที เท่านั้น นะเมี๊ยว \nไม่งั้นเราจะโกรธ :anger: แล้วไม่คุยด้วยแล้วนะเมี๊ยว !")
            return

        # Format and send the results to Discord channel
        for row in rows:
            # Example: sending only the user's name (assuming the first column is the user's name)
            await ctx.send(f"ID ของคุณท่าน คือ : {row[0]} \nเวลา Online ก่อนแลก : {row[3]}\nPont กิจกรรม ก่อนแลก : {row[1]} \nPoint เติมเงิน: {row[2]}")

            logging.info("ID ของคุณท่าน คือ : %s , เวลา Online คงเหลือ : %s , Pont กิจกรรม : %s , Point เติมเงิน: %s", row[0], row[3], row[1], row[2])
            print("=====================================================================")

            if row[3] >= playtime_to_exchange: # Check if PlayTime is at least the amount the user wants to exchange
                points_to_add = 5
                if playtime_to_exchange >= 600:
                    points_to_add = 10
                if playtime_to_exchange >= 900:
                    points_to_add = 15
                if playtime_to_exchange >= 1200:
                    points_to_add = 20
                # Update the database to redeem PlayTime for UserPoints
                cursor.execute('UPDATE UserInfo SET UserPoint = UserPoint + ?, PlayTime = PlayTime - ? WHERE UserID = ? and UserSA = ?', (points_to_add, playtime_to_exchange, user_id, user_cha,))
                conn.commit()
                await ctx.send(f":white_check_mark: คุณท่านได้รับ {points_to_add} Point จากการแลกเวลา Online \nคงเหลือ {row[3] - playtime_to_exchange} ชั่วโมง \nเช็ค Point ของคุณท่านโดยใช้คำสั่ง `^point เว้นวรรค ID` นะเมี๊ยว")
            else:
                await ctx.send(":no_entry: คุณท่านไม่มีเวลา Online ไม่พอสำหรับการแลก Point กิจกรรม ไปเล่นเกมให้เวลาเพียงพอก่อนนะเมี๊ยว")

        user = ctx.message.author
        logging.info("User ID: %s, Username: %s", user.id, user.name)

    except ValueError:
        await ctx.send(f"Invalid user ID format. Please ensure the user ID is an integer.")
    except pyodbc.Error as e:
        await ctx.send(f"An error occurred while processing your request: {str(e)}")

@playpoint.error
async def playpoint_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(":warning: เกิดข้อผิดพลาดแล้วเมี๊ยว! \n ข้อมูลที่ให้มา น้องหาไม่พบ หรือ มีบางอย่างผิด เช่น UserID ผิด หรือ รหัสเข้าถึงตัวละคร ผิด หรือ ไม่ได้ใส่เวลาที่จะแลก นะเมี๊ยว")

# Run the bot
bot.run(TOKEN)
