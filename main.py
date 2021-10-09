from sys import set_coroutine_origin_tracking_depth
from discord import *
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks
import json

description = 'ByteSlash Community Discord bot'
bot = commands.Bot(command_prefix='b,', description=description)

token = "TOKEN"

#                                                                                                                       #
#-----------------------------------------------------------------------------------------------------------------------#
#                                                                                                                       #

@bot.command()
async def engage(ctx):
    sender = ctx.message.author.id
    author = ctx.message.author.name
    embed = Embed(title="Engagement", description=f"{author}'s engagement score is {engagement_users[list(map(lambda x: x[0], engagement_users)).index(sender)][1]}. This score is reset every hour.", color=0x6093ac)
    await ctx.send(embed=embed)

@bot.command()
async def stats(ctx):
    print(engagement_users)
    embed = Embed(title="Statistics", description=f"Total users this round: {len(engagement_users)}", color=0x6093ac)

    try:
        top_3 = sorted(engagement_users, key=lambda x: x[1], reverse=True)[0]
        p1 = (await bot.fetch_user(top_3[0])).name
        s1 = top_3[1]
    except:
        p1 = 'None'
        s1 = 0
    try:
        top_3 = sorted(engagement_users, key=lambda x: x[1], reverse=True)[1]
        p2 = (await bot.fetch_user(top_3[0])).name
        s2 = top_3[1]
    except: 
        p2 = 'None'
        s2 = 0
    try:
        top_3 = sorted(engagement_users, key=lambda x: x[1], reverse=True)[2]
        p3 = (await bot.fetch_user(top_3[0])).name
        s3 = top_3[1]
    except:
        p3 = 'None'
        s3 = 0

    with open("data.json", "r") as f:
        data = json.load(f)
    top_3_list = data['top_3_all_time']
    try:n1 = (await bot.fetch_user(top_3_list[0][0])).name 
    except:n1 = top_3_list[0][0]
    try:n2 = (await bot.fetch_user(top_3_list[1][0])).name
    except:n2 = top_3_list[1][0]
    try:n3 = (await bot.fetch_user(top_3_list[2][0])).name
    except:n3 = top_3_list[2][0]

    embed.add_field(name="Top 3", value=f"{p1} - {s1}\n{p2} - {s2}\n{p3} - {s3}", inline=True)    
    embed.add_field(name="Top 3 all time", value=f"{n1} - {top_3_list[0][1]}\n{n2} - {top_3_list[1][1]}\n{n3} - {top_3_list[2][1]}", inline=True)
    embed.add_field(name="Score", value=f"Score this round : {sum(list(map(lambda x: x[1], engagement_users)))} \n Max score all time {data['max_all_time']}", inline=False)
    
    await ctx.send(embed=embed)

@tasks.loop(hours=1)
async def engagement_reset():
    print('resetting the score :)')

    with open('data.json', 'r') as f:
        json_file = json.load(f)

    max_score = json_file['max_all_time']
    if sum(list(map(lambda x: x[1], engagement_users))) > max_score:
        max_score = sum(list(map(lambda x: x[1], engagement_users)))
        json_file['max_all_time'] = max_score
    engagement_users.append(['None1', 0])
    engagement_users.append(['None2', 0])
    engagement_users.append(['None3', 0])
    top_3 = sorted(engagement_users, key=lambda x: x[1], reverse=True)[:3]
    all_time_top_3 = json_file['top_3_all_time']

    all_time_top_3.append(top_3[0])
    all_time_top_3.append(top_3[1])
    all_time_top_3.append(top_3[2])
    all_time_top_3 = sorted(all_time_top_3, key=lambda x: x[1], reverse=True)

    for i in range(len(all_time_top_3)-1, -1, -1):
        checker = list(map(lambda x: x[0], all_time_top_3))
        if checker.count(all_time_top_3[i][0]) > 1:
            all_time_top_3.remove(all_time_top_3[i])

    json_file['top_3_all_time'] = all_time_top_3[:3]
    with open('data.json', 'w') as f:
        json.dump(json_file, f)

    engagement_users.clear()

@tasks.loop(seconds=300)
async def engagement_loop():
    emojis = {0: '🙁',  50: '😐', 100: '🙂', 200: '😃', 300: '😄', 400: '😁'}
    print('looping over the score :)')
    chan_id = 896297227436314654
    #rename this channel with the number of engagement points
    channel = bot.get_channel(chan_id)
    eng = sum(list(map(lambda x: x[1], engagement_users)))
    emoji = emojis[min(list(emojis.keys()), key=lambda x: abs(x - eng))]
    await channel.edit(name=f"Engagement: {eng} {emoji}")


@bot.event
async def on_message(message):
    if not (message.author.bot):
        sender = message.author.id
        channel = message.channel
        content = message.content
        print(f'{sender} in {channel}: {content}')
        if sender not in list(map(lambda x: x[0], engagement_users)):
            engagement_users.append([sender, 1])
        else:
            engagement_users[list(map(lambda x: x[0], engagement_users)).index(sender)][1] += 1
        score = map(lambda x: x[1], engagement_users)
        print(sum(score))
    else:
        pass

    await bot.process_commands(message)

#                                                                                                                       #
#-----------------------------------------------------------------------------------------------------------------------#
#                                                                                                                       #

@bot.event
async def on_ready():
    print("Bot is ready")
    print("Logged in as:")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

    print('Starting the engagement loop')
    engagement_loop.start()
    engagement_reset.start()
    print('Engagement loop : ok')
    print("------")

    # define global vars
    global engagement_users
    global score
    global eng_msg_id
    engagement_users = []
    score = 0
    eng_msg_id = 0


bot.run(token)
