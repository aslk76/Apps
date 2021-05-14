#!/usr/bin/env python3
# coding=utf-8
import os, random, time, traceback, logging, \
    discord, asyncio, collections, \
    requests, json
from datetime import datetime
from datetime import timedelta
from discord.ext import commands, tasks
from discord.utils import get
from itertools import cycle 
from dotenv import load_dotenv

running=False

status= cycle(['Welcome to','NOVA Community'])


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('apps!'), case_insensitive=True, intents=intents)

logging.basicConfig(filename='/NOVA/NOVA_Apps/NOVA_Apps.log', level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logging.basicConfig(filename='NOVAApps.log', level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@bot.event
async def on_ready():
    global running
    try:
        if running==False:
            await asyncio.sleep (3)
            guild = bot.get_guild(815104630433775616)
            bot_log_channel = get(guild.text_channels, id=817552283209433098)
            embed_bot_log = discord.Embed(title="Info Log.", description=f'{bot.user.name} {discord.__version__} has connected to Discord!',
                                          color=0x5d4991)
            embed_bot_log.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            await bot_log_channel.send(embed=embed_bot_log)
            running=True
    except Exception:
        logging.error(traceback.format_exc())
        bot_log_channel = get(guild.text_channels, name='bot-logs')
        embed_bot_log = discord.Embed(title="Error Log.", description=traceback.format_exc(), color=0x5d4991)
        embed_bot_log.add_field(name="Source", value="on ready", inline=True)
        embed_bot_log.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        await bot_log_channel.send(embed=embed_bot_log)


@bot.command(pass_context=True)
@commands.has_any_role('NOVA', 'Moderator')
async def Logout(ctx):
    await ctx.message.delete()
    await ctx.bot.logout()


@bot.event
async def on_raw_reaction_add(payload):
    reactionPL = payload.emoji
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)
    hundred_emoji = [reaction for reaction in message.reactions if reaction.emoji == u"\U0001F4AF"]
    rio_channel = get(guild.text_channels, name='raiderio-channel')
    rio_allowed_ids=[241687840151437313,227102790349094923,278172998496944128,768024256822902815,226069789754392576,
                163324686086832129,234065317037342721,200277087238619137]
    try:
        if not user.bot and payload.user_id not in rio_allowed_ids and \
            (payload.channel_id == 815104634698858581 or payload.channel_id == 815104632208490570):
            await message.remove_reaction(reactionPL, user)
        elif len(hundred_emoji) == 0 and reactionPL.name == 'nova_c' and \
            payload.user_id in rio_allowed_ids and payload.channel_id == 815104634698858581:
            embed_pre = message.embeds[0].to_dict()
            embed_fields = embed_pre['fields']
            applicant = guild.get_member_named(embed_fields[2]["value"])
            embed_desc = embed_pre['description']
            char_name=embed_desc.partition("/ [")[2].partition("-")[0].strip()
            char_realm=embed_desc.partition("/ [")[2].partition("-")[2].partition("]")[0].strip()
            char_faction = embed_fields[0]["value"]
            char_class = embed_fields[1]["value"]
            tank_score = embed_fields[3]["value"]
            heal_score = embed_fields[4]["value"]
            dps_score = embed_fields[5]["value"]
            overall_score = embed_fields[6]["value"]
            
            realm_pre = char_realm.replace(' ', '').replace('-','').replace('```','').capitalize()
            if realm_pre.startswith("Pozzo"):
                realm_final = "Pozzo"
            elif realm_pre == "Dunmodr":
                realm_final = "DunModr"
            elif realm_pre.startswith("Twisting"):
                realm_final = "TwistingNether"
            elif realm_pre.startswith("Tarren"):
                realm_final = "TarrenMill"
            elif realm_pre == "Colinaspardas":
                realm_final = "ColinasPardas"
            elif realm_pre == "Burninglegion":
                realm_final = "BurningLegion"
            elif realm_pre == "Themaelstrom":
                realm_final = "TheMaelstrom"
            elif realm_pre == "Defiasbrotherhood":
                realm_final = "Defias"
            elif realm_pre == "Shatteredhand":
                realm_final = "Shattered"
            elif realm_pre.startswith("Argent"):
                realm_final = "ArgentDawn"
            elif realm_pre == "Burningblade":
                realm_final = "BurningBlade"
            elif realm_pre.startswith("Aggra"):
                realm_final = "Aggra"
            elif realm_pre.startswith("Chamberof"):
                realm_final = "ChamberofAspects"
            elif realm_pre.startswith("Emerald"):
                realm_final = "EmeraldDream"
            elif realm_pre.startswith("Grim"):
                realm_final = "GrimBatol"
            elif realm_pre.startswith("Quel"):
                realm_final = "Quel'Thalas"
            elif realm_pre.startswith("Mal'ganis"):
                realm_final = "Mal'Ganis"
            elif realm_pre.startswith("Azjol"):
                realm_final = "AzjolNerub"
            elif realm_pre.startswith("Los"):
                realm_final = "LosErrantes"
            elif realm_pre.startswith("Twilight"):
                realm_final = "Twilight'sHammer"
            else:
                realm_final = realm_pre
            if float(dps_score) >= 1300:
                dps_role = "Damage"
                await applicant.add_roles(get(guild.roles, name=dps_role))
            else:
                dps_role = None
            if float(heal_score) >= 1300:
                healer_role = "Heal"
                await applicant.add_roles(get(guild.roles, name=healer_role))
            else:
                healer_role = None
            if float(tank_score) >= 1300:
                tank_role = "Tank"
                await applicant.add_roles(get(guild.roles, name=tank_role))
            else:
                tank_role = None
            if tank_role is not None or healer_role is not None or dps_role is not None:
                if char_class == "Demon Hunter" or char_class == "Druid" or char_class == "Monk" or \
                    char_class == "Rogue":
                    char_armor = "Leather"
                    await applicant.edit(nick=f"{char_name.capitalize()}-{realm_final} [{char_faction[0].upper()}]")
                    roles_toadd = [get(guild.roles, name=char_armor), get(guild.roles, name=char_class),
                                   get(guild.roles, name=char_faction.capitalize()),
                                   get(guild.roles, name=f"M+ Booster [{char_faction[0].upper()}]"),
                                   get(guild.roles, name=f"{char_class} Main"),
                                   get(guild.roles, name="EU")]
                    await applicant.add_roles(*roles_toadd)
                elif char_class == "Mage" or char_class == "Priest" or char_class == "Warlock":
                    char_armor = "Cloth"
                    await applicant.edit(nick=f"{char_name.capitalize()}-{realm_final} [{char_faction[0].upper()}]")
                    roles_toadd = [get(guild.roles, name=char_armor), get(guild.roles, name=char_class),
                                   get(guild.roles, name=char_faction.capitalize()),
                                   get(guild.roles, name=f"M+ Booster [{char_faction[0].upper()}]"),
                                   get(guild.roles, name=f"{char_class} Main"),
                                   get(guild.roles, name="EU")]
                    await applicant.add_roles(*roles_toadd)
                elif char_class == "Hunter" or char_class == "Shaman":
                    char_armor = "Mail"
                    await applicant.edit(nick=f"{char_name.capitalize()}-{realm_final} [{char_faction[0].upper()}]")
                    roles_toadd = [get(guild.roles, name=char_armor), get(guild.roles, name=char_class),
                                   get(guild.roles, name=char_faction.capitalize()),
                                   get(guild.roles, name=f"M+ Booster [{char_faction[0].upper()}]"),
                                   get(guild.roles, name=f"{char_class} Main"),
                                   get(guild.roles, name="EU")]
                    await applicant.add_roles(*roles_toadd)
                elif char_class == "Paladin" or char_class == "Warrior" or char_class == "Death Knight":
                    char_armor = "Plate"
                    await applicant.edit(nick=f"{char_name.capitalize()}-{realm_final} [{char_faction[0].upper()}]")
                    roles_toadd = [get(guild.roles, name=char_armor), get(guild.roles, name=char_class),
                                   get(guild.roles, name=char_faction.capitalize()),
                                   get(guild.roles, name=f"M+ Booster [{char_faction[0].upper()}]"),
                                   get(guild.roles, name=f"{char_class} Main"),
                                   get(guild.roles, name="EU")]
                    await applicant.add_roles(*roles_toadd)

                if (realm_final.lower().startswith("pozzo") or realm_final.lower()=="hyjal" or 
                    realm_final.lower()=="dalaran" or realm_final.lower().startswith("marécage") or 
                    realm_final.lower()=="exodar" or realm_final.lower()=="themaelstrom") and char_faction.lower() == "alliance":
                    await applicant.add_roles(get(guild.roles, name="A-Vaults"))
                elif (realm_final.lower().startswith("pozzo") or realm_final.lower()=="drak'thul" or realm_final.lower()=="burningblade" or
                        realm_final.lower()=="frostmane" or realm_final.lower()=="grimbatol" or realm_final.lower()=="aggra" or 
                        realm_final.lower()=="dalaran" or realm_final.lower().startswith("marécage")) and char_faction.lower() == "horde":
                    await applicant.add_roles(get(guild.roles, name="H-Vaults"))

            embed_pre['color'] = 0x00ff00
            auto_rank_embed = discord.Embed.from_dict(embed_pre)
            auto_rank_embed.add_field(name="Application accepted", value="check your DM for more info", inline=False)
            await message.edit(embed=auto_rank_embed)
            await message.add_reaction(u"\U0001F4AF")
            if get(guild.roles, name="Client") in applicant.roles:
                await applicant.remove_roles(get(guild.roles, name="Client"))
            if get(guild.roles, name="PickYourRegion") in applicant.roles:
                await applicant.remove_roles(get(guild.roles, name="PickYourRegion"))
            await applicant.create_dm()
            await applicant.dm_channel.send(
                f"Hello **{applicant.name}** :slight_smile:\nYour application for ***NOVA*** as a booster has been "
                "accepted, **CHECK YOUR ROLES** and__ please read all our channels before taking further steps "
                "inside the community.__\n \n**#rules** That you must follow at all costs or your risk yourself getting Striked / Banned; \n"
                "**#balance-check** Important info regarding how payment works and to check your weekly earnings; \n"
                "**#payday-info** To see when the next payment wave will be done;\n"
                "**#high-key-roles** To get the Highkey Booster role (+14,+15 keys) if you have the required score;\n"
                "**#pick-your-roles** To request further roles (you don't need to do this if its your first time in);\n"
                "\nThank you,\n"
                "***NOVA Team***")
            await rio_channel.send(f"`{char_name.capitalize()}-{realm_final} "
                                   f"[{char_faction[0].upper()}] Accepted and given the ranks`")
            await rio_channel.send(f"Current Season\n{overall_score}")
            await rio_channel.send(f"Faction:{char_faction.capitalize()}")
            await rio_channel.send(f"Class: {char_class}\nRoles: {dps_role} | {healer_role} | {tank_role}\n=============================")
        elif len(hundred_emoji) == 0 and reactionPL.name == 'nova_x' and \
            payload.user_id in rio_allowed_ids and payload.channel_id == 815104634698858581:
            embed_pre = message.embeds[0].to_dict()
            embed_fields = embed_pre['fields']
            applicant = guild.get_member_named(embed_fields[2]["value"])
            embed_pre['color'] = 0xff0000
            auto_rank_embed = discord.Embed.from_dict(embed_pre)
            auto_rank_embed.add_field(name="Application declined", value="check your DM for more info", inline=False)
            await applicant.create_dm()
            await applicant.dm_channel.send(
                f"Hello **{applicant.name}**\n\nThank you for submitting an application to become a booster for ***NOVA***, "
                "however on this occasion we regret to inform you that your application has been declined.\n"
                "\nThank you,"
                "\n***NOVA Team***")
            await message.edit(embed=auto_rank_embed)
            await message.clear_reactions()
            await message.add_reaction(u"\u274C")
        #######################____________THIS IS NA______####################################
        elif len(hundred_emoji) == 0 and reactionPL.name == 'nova_c' and \
            payload.user_id in rio_allowed_ids and payload.channel_id == 815104632208490570:
            embed_pre = message.embeds[0].to_dict()
            embed_fields = embed_pre['fields']
            applicant = guild.get_member_named(embed_fields[2]["value"])
            embed_desc = embed_pre['description']
            char_name=embed_desc.partition("/ [")[2].partition("-")[0].strip()
            char_realm=embed_desc.partition("/ [")[2].partition("-")[2].partition("]")[0].strip()
            char_faction = embed_fields[0]["value"]
            char_class = embed_fields[1]["value"]
            tank_score = embed_fields[3]["value"]
            heal_score = embed_fields[4]["value"]
            dps_score = embed_fields[5]["value"]
            overall_score = embed_fields[6]["value"]
            
            realm_pre = char_realm.replace(' ', '').replace('-','').replace('```','').capitalize()
            if realm_pre.startswith("Pozzo"):
                realm_final = "Pozzo"
            elif realm_pre == "Dunmodr":
                realm_final = "DunModr"
            elif realm_pre.startswith("Twisting"):
                realm_final = "TwistingNether"
            elif realm_pre.startswith("Tarren"):
                realm_final = "TarrenMill"
            elif realm_pre == "Colinaspardas":
                realm_final = "ColinasPardas"
            elif realm_pre == "Burninglegion":
                realm_final = "BurningLegion"
            elif realm_pre == "Themaelstrom":
                realm_final = "TheMaelstrom"
            elif realm_pre == "Defiasbrotherhood":
                realm_final = "Defias"
            elif realm_pre == "Shatteredhand":
                realm_final = "Shattered"
            elif realm_pre.startswith("Argent"):
                realm_final = "ArgentDawn"
            elif realm_pre == "Burningblade":
                realm_final = "BurningBlade"
            elif realm_pre.startswith("Aggra"):
                realm_final = "Aggra"
            elif realm_pre.startswith("Chamberof"):
                realm_final = "ChamberofAspects"
            elif realm_pre.startswith("Emerald"):
                realm_final = "EmeraldDream"
            elif realm_pre.startswith("Grim"):
                realm_final = "GrimBatol"
            elif realm_pre.startswith("Quel"):
                realm_final = "Quel'Thalas"
            elif realm_pre.startswith("Mal'ganis"):
                realm_final = "Mal'Ganis"
            elif realm_pre.startswith("Twilight"):
                realm_final = "Twilight'sHammer"
            else:
                realm_final = realm_pre
            if float(dps_score) >= 1300:
                dps_role = "Damage"
                await applicant.add_roles(get(guild.roles, name=dps_role))
            else:
                dps_role = None
            if float(heal_score) >= 1300:
                healer_role = "Heal"
                await applicant.add_roles(get(guild.roles, name=healer_role))
            else:
                healer_role = None
            if float(tank_score) >= 1300:
                tank_role = "Tank"
                await applicant.add_roles(get(guild.roles, name=tank_role))
            else:
                tank_role = None
            if tank_role is not None or healer_role is not None or dps_role is not None:
                if char_class == "Demon Hunter" or char_class == "Druid" or char_class == "Monk" or \
                    char_class == "Rogue":
                    char_armor = "Leather"
                    await applicant.edit(nick=f"{char_name.capitalize()}-{realm_final} [{char_faction[0].upper()}]")
                    roles_toadd = [get(guild.roles, name=char_armor), get(guild.roles, name=char_class),
                                   get(guild.roles, name=f"{char_faction.capitalize()} NA"),
                                   get(guild.roles, name=f"M+ Booster [{char_faction[0].upper()}] NA"),
                                   get(guild.roles, name=f"{char_class} Main"),
                                   get(guild.roles, name="NA")]
                    await applicant.add_roles(*roles_toadd)
                elif char_class == "Mage" or char_class == "Priest" or char_class == "Warlock":
                    char_armor = "Cloth"
                    await applicant.edit(nick=f"{char_name.capitalize()}-{realm_final} [{char_faction[0].upper()}]")
                    roles_toadd = [get(guild.roles, name=char_armor), get(guild.roles, name=char_class),
                                   get(guild.roles, name=f"{char_faction.capitalize()} NA"),
                                   get(guild.roles, name=f"M+ Booster [{char_faction[0].upper()}] NA"),
                                   get(guild.roles, name=f"{char_class} Main"),
                                   get(guild.roles, name="NA")]
                    await applicant.add_roles(*roles_toadd)
                elif char_class == "Hunter" or char_class == "Shaman":
                    char_armor = "Mail"
                    await applicant.edit(nick=f"{char_name.capitalize()}-{realm_final} [{char_faction[0].upper()}]")
                    roles_toadd = [get(guild.roles, name=char_armor), get(guild.roles, name=char_class),
                                   get(guild.roles, name=f"{char_faction.capitalize()} NA"),
                                   get(guild.roles, name=f"M+ Booster [{char_faction[0].upper()}] NA"),
                                   get(guild.roles, name=f"{char_class} Main"),
                                   get(guild.roles, name="NA")]
                    await applicant.add_roles(*roles_toadd)
                elif char_class == "Paladin" or char_class == "Warrior" or char_class == "Death Knight":
                    char_armor = "Plate"
                    await applicant.edit(nick=f"{char_name.capitalize()}-{realm_final} [{char_faction[0].upper()}]")
                    roles_toadd = [get(guild.roles, name=char_armor), get(guild.roles, name=char_class),
                                   get(guild.roles, name=f"{char_faction.capitalize()} NA"),
                                   get(guild.roles, name=f"M+ Booster [{char_faction[0].upper()}] NA"),
                                   get(guild.roles, name=f"{char_class} Main"),
                                   get(guild.roles, name="NA")]
                    await applicant.add_roles(*roles_toadd)

                if (realm_final.lower().startswith("pozzo") or realm_final.lower()=="hyjal" or 
                    realm_final.lower()=="dalaran" or realm_final.lower().startswith("marécage") or 
                    realm_final.lower()=="exodar" or realm_final.lower()=="themaelstrom") and char_faction.lower() == "alliance":
                    await applicant.add_roles(get(guild.roles, name="A-Vaults")) 
                elif (realm_final.lower().startswith("pozzo") or realm_final.lower()=="drak'thul" or realm_final.lower()=="burningblade" or
                        realm_final.lower()=="frostmane" or realm_final.lower()=="grimbatol" or realm_final.lower()=="aggra" or 
                        realm_final.lower()=="dalaran" or realm_final.lower().startswith("marécage")) and char_faction.lower() == "horde":
                    await applicant.add_roles(get(guild.roles, name="H-Vaults"))

            embed_pre['color'] = 0x00ff00
            auto_rank_embed = discord.Embed.from_dict(embed_pre)
            auto_rank_embed.add_field(name="Application accepted", value="check your DM for more info", inline=False)
            await message.edit(embed=auto_rank_embed)
            await message.add_reaction(u"\U0001F4AF")
            if get(guild.roles, name="Client NA") in applicant.roles:
                await applicant.remove_roles(get(guild.roles, name="Client NA"))
            if get(guild.roles, name="PickYourRegion") in applicant.roles:
                await applicant.remove_roles(get(guild.roles, name="PickYourRegion"))
            await applicant.create_dm()
            await applicant.dm_channel.send(
                f"Hello **{applicant.name}** :slight_smile:\nYour application for ***NOVA*** as a booster has been "
                "accepted, **CHECK YOUR ROLES** and__ please read all our channels before taking further steps "
                "inside the community.__\n \n**#rules** That you must follow at all costs or your risk yourself getting Striked / Banned; \n"
                "**#balance-check** Important info regarding how payment works and to check your weekly earnings; \n"
                "**#payday-info** To see when the next payment wave will be done;\n"
                "**#high-key-roles** To get the Highkey Booster role (+14,+15 keys) if you have the required score;\n"
                "**#pick-your-roles** To request further roles (you don't need to do this if its your first time in);\n"
                "\nThank you,\n"
                "***NOVA Team***")
            await rio_channel.send(f"`{char_name.capitalize()}-{realm_final} "
                                   f"[{char_faction[0].upper()}] Accepted and given the ranks`")
            await rio_channel.send(f"Current Season\n{overall_score}")
            await rio_channel.send(f"Faction:{char_faction.capitalize()}\nRegion: NA")
            await rio_channel.send(f"Class: {char_class}\nRoles: {dps_role} | {healer_role} | {tank_role}\n=============================")
        elif len(hundred_emoji) == 0 and reactionPL.name == 'nova_x' and \
            payload.user_id in rio_allowed_ids and payload.channel_id == 815104632208490570:
            embed_pre = message.embeds[0].to_dict()
            embed_fields = embed_pre['fields']
            applicant = guild.get_member_named(embed_fields[2]["value"])
            embed_pre['color'] = 0xff0000
            auto_rank_embed = discord.Embed.from_dict(embed_pre)
            auto_rank_embed.add_field(name="Application declined", value="check your DM for more info", inline=False)
            await applicant.create_dm()
            await applicant.dm_channel.send(
                f"Hello **{applicant.name}**\n\nThank you for submitting an application to become a booster for ***NOVA***, "
                "however on this occasion we regret to inform you that your application has been declined.\n"
                "\nThank you,"
                "\n***NOVA Team***")
            await message.edit(embed=auto_rank_embed)
            await message.clear_reactions()
            await message.add_reaction(u"\u274C")
    
    except discord.errors.Forbidden:
        await channel.send(f"Cannot send a DM to {applicant.mention}", delete_after=10)
    except Exception:
        logging.error("--Raw Reaction Add---")
        logging.error(traceback.format_exc())
        bot_log_channel = get(guild.text_channels, name='bot-logs')
        embed_bot_log = discord.Embed(title="NOVA Apps Error Log.", description=traceback.format_exc(), color=0x5d4991)
        embed_bot_log.add_field(name="Source", value="on reaction add outer", inline=True)
        embed_bot_log.add_field(name="Author", value=message.author.name, inline=True)
        embed_bot_log.add_field(name="Channel", value=channel.name, inline=False)
        # embed_bot_log.add_field(name="Content", value=message.content, inline=False)
        embed_bot_log.set_footer(text="Timestamp (UTC±00:00): " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
        await bot_log_channel.send(embed=embed_bot_log)


@bot.event
async def on_message(message):
    if message.channel.id == 815104634698858580: #EU MPlus Applications Channel:
        try:
            #await asyncio.sleep(2)
            rio_allowed_ids=[241687840151437313,227102790349094923,278172998496944128,768024256822902815,226069789754392576,
                                163324686086832129,234065317037342721,200277087238619137]
            auto_rank_msg = message.content.split("\n")
            if len(auto_rank_msg)==2 and not message.author.bot:
                if auto_rank_msg[1].lower().startswith('character realm') and not message.author.bot and \
                    message.author.id not in rio_allowed_ids and "https" not in message.content:
                    auto_rank_char_name = auto_rank_msg[0].partition(":")[2].strip()
                    auto_rank_relam_name = auto_rank_msg[1].partition(":")[2].strip()
                    response = requests.get(
                                "https://raider.io/api/v1/characters/profile?region=eu&realm=" + auto_rank_relam_name + 
                                "&name=" + auto_rank_char_name + "&fields=mythic_plus_scores_by_season%3Acurrent")
                    if response.status_code == 200:
                        applicant = message.author
                        await message.delete()
                        json_str = json.dumps(response.json())
                        resp = json.loads(json_str)
                        char_class = resp['class']
                        char_faction = resp['faction']
                        season = resp['mythic_plus_scores_by_season']
                        season_curr = season[0]
                        season_curr_all = season_curr['scores']['all']
                        season_curr_tank = season_curr['scores']['tank']
                        season_curr_heal = season_curr['scores']['healer']
                        season_curr_dps = season_curr['scores']['dps']
                        if season_curr_tank >= 1300 or season_curr_heal >= 1300 or season_curr_dps >= 1300:
                            auto_rank_embed = discord.Embed(title="Application of:", description=f"{applicant.mention} / [{auto_rank_char_name}-{auto_rank_relam_name}]({resp['profile_url']})")
                            auto_rank_embed.set_thumbnail(url=resp['thumbnail_url'])
                            auto_rank_embed.set_footer(text="Timestamp (UTC±00:00): " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"), icon_url="https://cdn.discordapp.com/avatars/634917649335320586/ea303e8b580d56ff6837e256b1df6ef6.png")
                            auto_rank_embed.add_field(name="Faction", value=char_faction.capitalize(), inline=True)
                            auto_rank_embed.add_field(name="Class", value=char_class.title(), inline=True)
                            auto_rank_embed.add_field(name="DiscordID", value=applicant, inline=False)
                            auto_rank_embed.add_field(name="Tank", value=season_curr['scores']['tank'], inline=True)
                            auto_rank_embed.add_field(name="Heal", value=season_curr['scores']['healer'], inline=True)
                            auto_rank_embed.add_field(name="DPS", value=season_curr['scores']['dps'], inline=True)
                            auto_rank_embed.add_field(name="Overall", value=season_curr_all, inline=False)
                            mplus_applications_review_channel = get(message.guild.text_channels, id=815104634698858581)
                            auto_rank_embed_sent = await mplus_applications_review_channel.send(embed = auto_rank_embed)
                            await applicant.create_dm()
                            await applicant.dm_channel.send(
                                f"Hello **{applicant.name}**\n\nThank you for submitting an application to become a booster for ***NOVA***, "
                                "all the applications will be verified by our team every day, you don't have to DM us to speed up the process, your DMs will be ignored..\n"
                                "\nThank you,"
                                "\n***NOVA Team***")
                            await auto_rank_embed_sent.add_reaction('<:nova_c:817558639241592859>')
                            await auto_rank_embed_sent.add_reaction('<:nova_x:817559679760465980>')
                        else:
                            auto_rank_embed = discord.Embed(title="Application of:", description=f"[{auto_rank_char_name}-{auto_rank_relam_name}]({resp['profile_url']})", color = discord.Color.red())
                            auto_rank_embed.set_thumbnail(url=resp['thumbnail_url'])
                            auto_rank_embed.set_footer(text="Timestamp (UTC±00:00): " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"), icon_url="https://cdn.discordapp.com/avatars/634917649335320586/ea303e8b580d56ff6837e256b1df6ef6.png")
                            auto_rank_embed.add_field(name="Tank", value=season_curr['scores']['tank'], inline=True)
                            auto_rank_embed.add_field(name="Heal", value=season_curr['scores']['healer'], inline=True)
                            auto_rank_embed.add_field(name="DPS", value=season_curr['scores']['dps'], inline=True)
                            auto_rank_embed.add_field(name="Overall", value=season_curr_all, inline=False)
                            auto_rank_embed.add_field(name="Application declined", value="you have less than the required rio in a specific role", inline=False)
                            await applicant.create_dm()
                            await applicant.dm_channel.send(
                            f"Hello **{applicant.name}**\n\nThank you for submitting an application to become a booster for ***NOVA***, "
                            "however on this occasion we regret to inform you that your application has been declined.\n"
                            "\nThank you,"
                            "\n***NOVA Team***")
                            auto_rank_embed_sent=await message.channel.send(embed = auto_rank_embed)
                            await auto_rank_embed_sent.add_reaction(u"\u274C")
                    else:
                        await message.channel.send("No such character ("+ auto_rank_char_name + "-" + auto_rank_relam_name +") found on Raider.io, double check spelling", delete_after=10)
                elif not auto_rank_msg[1].lower().startswith('character realm') or not auto_rank_msg[0].lower().startswith('character name') or \
                    "https" in message.content:
                    await message.delete()
                    await message.channel.send(f"You used wrong template, check the pinned messages {message.author.mention}", delete_after=10)
            elif (len(auto_rank_msg)<2 or len(auto_rank_msg)>2) and not message.author.bot and \
                    message.author.id not in rio_allowed_ids:
                    await message.delete()
                    await message.channel.send(f"You used wrong template, check the pinned messages {message.author.mention}", delete_after=10)
        except discord.errors.Forbidden:
            await message.channel.send(f"Cannot send you a DM to {user.mention}", delete_after=5)
        except Exception:
            logging.error("--Auto Ranks START---")
            logging.error(traceback.format_exc())
            logging.error("--Auto Ranks END---")
            bot_log_channel = get(message.guild.text_channels, name='bot-logs')
            embed_bot_log = discord.Embed(title="NOVA Apps Error Log.", description="on reaction add EU MPlus Applications", color=0x5d4991)
            embed_bot_log.add_field(name="Author", value=message.author.name, inline=True)
            embed_bot_log.add_field(name="Channel", value=channel.name, inline=False)
            embed_bot_log.set_footer(text="Timestamp (UTC±00:00): " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
            await bot_log_channel.send(embed=embed_bot_log)
    elif message.channel.id == 815104632208490569: #NA MPlus Applications Channel:
        try:
            #await asyncio.sleep(3)
            rio_allowed_ids=[241687840151437313,227102790349094923,278172998496944128,768024256822902815,226069789754392576,
                                163324686086832129,234065317037342721,200277087238619137,200277087238619137]
            auto_rank_msg = message.content.split("\n")
            if len(auto_rank_msg)==2 and not message.author.bot:
                if auto_rank_msg[1].lower().startswith('character realm') and not message.author.bot:
                    auto_rank_char_name = auto_rank_msg[0].partition(":")[2].strip()
                    auto_rank_relam_name = auto_rank_msg[1].partition(":")[2].strip()
                    response = requests.get(
                                "https://raider.io/api/v1/characters/profile?region=us&realm=" + auto_rank_relam_name + 
                                "&name=" + auto_rank_char_name + "&fields=mythic_plus_scores_by_season%3Acurrent")
                    if response.status_code == 200:
                        applicant = message.author
                        await message.delete()
                        json_str = json.dumps(response.json())
                        resp = json.loads(json_str)
                        char_class = resp['class']
                        char_faction = resp['faction']
                        season = resp['mythic_plus_scores_by_season']
                        season_curr = season[0]
                        season_curr_all = season_curr['scores']['all']
                        season_curr_tank = season_curr['scores']['tank']
                        season_curr_heal = season_curr['scores']['healer']
                        season_curr_dps = season_curr['scores']['dps']
                        if season_curr_tank >= 1300 or season_curr_heal >= 1300 or season_curr_dps >= 1300:
                            auto_rank_embed = discord.Embed(title="Application of:", description=f"{applicant.mention} / [{auto_rank_char_name}-{auto_rank_relam_name}]({resp['profile_url']})")
                            auto_rank_embed.set_thumbnail(url=resp['thumbnail_url'])
                            auto_rank_embed.set_footer(text="Timestamp (UTC±00:00): " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"), icon_url="https://cdn.discordapp.com/avatars/634917649335320586/ea303e8b580d56ff6837e256b1df6ef6.png")
                            auto_rank_embed.add_field(name="Faction", value=char_faction.capitalize(), inline=True)
                            auto_rank_embed.add_field(name="Class", value=char_class.title(), inline=True)
                            auto_rank_embed.add_field(name="DiscordID", value=applicant, inline=False)
                            auto_rank_embed.add_field(name="Tank", value=season_curr['scores']['tank'], inline=True)
                            auto_rank_embed.add_field(name="Heal", value=season_curr['scores']['healer'], inline=True)
                            auto_rank_embed.add_field(name="DPS", value=season_curr['scores']['dps'], inline=True)
                            auto_rank_embed.add_field(name="Overall", value=season_curr_all, inline=False)
                            mplus_applications_review_channel = get(message.guild.text_channels, id=815104632208490570)
                            auto_rank_embed_sent = await mplus_applications_review_channel.send(embed = auto_rank_embed)
                            await applicant.create_dm()
                            await applicant.dm_channel.send(
                                f"Hello **{applicant.name}**\n\nThank you for submitting an application to become a booster for ***NOVA***, "
                                "all the applications will be verified by our team every day, you don't have to DM us to speed up the process, your DMs will be ignored..\n"
                                "\nThank you,"
                                "\n***NOVA Team***")
                            await auto_rank_embed_sent.add_reaction('<:nova_c:817558639241592859>')
                            await auto_rank_embed_sent.add_reaction('<:nova_x:817559679760465980>')
                        else:
                            auto_rank_embed = discord.Embed(title="Application of:", description=f"[{auto_rank_char_name}-{auto_rank_relam_name}]({resp['profile_url']})", color = discord.Color.red())
                            auto_rank_embed.set_thumbnail(url=resp['thumbnail_url'])
                            auto_rank_embed.set_footer(text="Timestamp (UTC±00:00): " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"), icon_url="https://cdn.discordapp.com/avatars/634917649335320586/ea303e8b580d56ff6837e256b1df6ef6.png")
                            auto_rank_embed.add_field(name="Tank", value=season_curr['scores']['tank'], inline=True)
                            auto_rank_embed.add_field(name="Heal", value=season_curr['scores']['healer'], inline=True)
                            auto_rank_embed.add_field(name="DPS", value=season_curr['scores']['dps'], inline=True)
                            auto_rank_embed.add_field(name="Overall", value=season_curr_all, inline=False)
                            auto_rank_embed.add_field(name="Application declined", value="you have less than the required rio in a specific role", inline=False)
                            await applicant.create_dm()
                            await applicant.dm_channel.send(
                            f"Hello **{applicant.name}**\n\nThank you for submitting an application to become a booster for ***NOVA***, "
                            "however on this occasion we regret to inform you that your application has been declined.\n"
                            "\nThank you,"
                            "\n***NOVA Team***")
                            auto_rank_embed_sent=await message.channel.send(embed = auto_rank_embed)
                            await auto_rank_embed_sent.add_reaction(u"\u274C")
                    else:
                        await message.channel.send("No such character ("+ auto_rank_char_name + "-" + auto_rank_relam_name +") found on Raider.io, double check spelling", delete_after=10)
                elif not auto_rank_msg[1].lower().startswith('character realm') or not auto_rank_msg[0].lower().startswith('character name') or \
                    "https" in message.content:
                    await message.delete()
                    await message.channel.send(f"You used wrong template, check the pinned messages {message.author.mention}", delete_after=10)
            elif (len(auto_rank_msg)<2 or len(auto_rank_msg)>2) and not message.author.bot and \
                    message.author.id not in rio_allowed_ids:
                    await message.delete()
                    await message.channel.send(f"You used wrong template, check the pinned messages {message.author.mention}", delete_after=10)
        except discord.errors.Forbidden:
            await message.channel.send(f"Cannot send you a DM to {user.mention}", delete_after=5)
        except Exception:
            logging.error("--Auto Ranks START---")
            logging.error(traceback.format_exc())
            logging.error("--Auto Ranks END---")
            bot_log_channel = get(message.guild.text_channels, name='bot-logs')
            embed_bot_log = discord.Embed(title="NOVA Apps Error Log.", description="on reaction add NA MPlus Applications", color=0x5d4991)
            embed_bot_log.add_field(name="Author", value=message.author.name, inline=True)
            embed_bot_log.add_field(name="Channel", value=channel.name, inline=False)
            embed_bot_log.set_footer(text="Timestamp (UTC±00:00): " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
            await bot_log_channel.send(embed=embed_bot_log)
    elif message.channel.id == 817865057051869204: #reclaim-booster-role Request Rank Channel:
        try:
            ##################################################################################################################
            rio_allowed_ids=[241687840151437313,227102790349094923,278172998496944128,768024256822902815,226069789754392576,
                                163324686086832129,234065317037342721,200277087238619137]
            auto_rank_msg = message.content.split("\n")
            if len(auto_rank_msg)==2 and not message.author.bot:
                if auto_rank_msg[1].lower().startswith('character realm') and not message.author.bot and \
                    message.author.id not in rio_allowed_ids:
                    await message.delete()
                    rio_channel = get(message.guild.text_channels, name='raiderio-channel')
                    name = auto_rank_msg[0].partition(":")[2].strip()
                    realm = auto_rank_msg[1].partition(":")[2].strip()
                    response = requests.get(
                                "https://raider.io/api/v1/characters/profile?region=eu&realm=" + realm + 
                                "&name=" + name + "&fields=mythic_plus_scores_by_season%3Acurrent")
                    user= message.author
                    if response.status_code == 200:
                        json_str = json.dumps(response.json())
                        resp = json.loads(json_str)
                        char_class = resp['class']
                        char_faction = resp['faction']
                        season = resp['mythic_plus_scores_by_season']
                        season_4 = season[0]
                        season_4_all = season_4["scores"]["all"]
                        season_4_dps = season_4["scores"]["dps"]
                        season_4_healer = season_4["scores"]["healer"]
                        season_4_tank = season_4["scores"]["tank"]
                        #season_3 = season[1]["scores"]["all"]
                        realm_pre = realm.replace(' ', '').replace('-','').capitalize()
                        if realm_pre.startswith("Pozzo"):
                            realm_final = "Pozzo"
                        elif realm_pre == "Dunmodr":
                            realm_final = "DunModr"
                        elif realm_pre.startswith("Twisting"):
                            realm_final = "TwistingNether"
                        elif realm_pre.startswith("Tarren"):
                            realm_final = "TarrenMill"
                        elif realm_pre == "Colinaspardas":
                            realm_final = "ColinasPardas"
                        elif realm_pre == "Burninglegion":
                            realm_final = "BurningLegion"
                        elif realm_pre == "Themaelstrom":
                            realm_final = "TheMaelstrom"
                        elif realm_pre == "Defiasbrotherhood":
                            realm_final = "Defias"
                        elif realm_pre == "Shatteredhand":
                            realm_final = "Shattered"
                        elif realm_pre.startswith("Argent"):
                            realm_final = "ArgentDawn"
                        elif realm_pre == "Burningblade":
                            realm_final = "BurningBlade"
                        elif realm_pre.startswith("Aggra"):
                            realm_final = "Aggra"
                        elif realm_pre.startswith("Chamberof"):
                            realm_final = "ChamberofAspects"
                        elif realm_pre.startswith("Emerald"):
                            realm_final = "EmeraldDream"
                        elif realm_pre.startswith("Grim"):
                            realm_final = "GrimBatol"
                        elif realm_pre.startswith("Quel"):
                            realm_final = "Quel'Thalas"
                        elif realm_pre.startswith("Mal'ganis"):
                            realm_final = "Mal'Ganis"
                        elif realm_pre.startswith("Azjol"):
                            realm_final = "AzjolNerub"
                        elif realm_pre.startswith("Twilight"):
                            realm_final = "Twilight'sHammer"
                        else:
                            realm_final = realm_pre
                        if season_4_dps >= 1300:
                            dps_role = "Damage"
                            await user.add_roles(get(message.guild.roles, name=dps_role))
                        else:
                            dps_role = None
                        if season_4_healer >= 1300:
                            healer_role = "Heal"
                            await user.add_roles(get(message.guild.roles, name=healer_role))
                        else:
                            healer_role = None
                        if season_4_tank >= 1300:
                            tank_role = "Tank"
                            await user.add_roles(get(message.guild.roles, name=tank_role))
                        else:
                            tank_role = None
                        if tank_role is not None or healer_role is not None or dps_role is not None:
                            if char_class == "Demon Hunter" or char_class == "Druid" or char_class == "Monk" or \
                                char_class == "Rogue":
                                char_armor = "Leather"
                                await user.edit(nick=f"{name.capitalize()}-{realm_final} [{char_faction[0].upper()}]")
                                roles_toadd = [get(message.guild.roles, name=char_armor), get(message.guild.roles, name=char_class),
                                               get(message.guild.roles, name=char_faction.capitalize()),
                                               get(message.guild.roles, name=f"M+ Booster [{char_faction[0].upper()}]"),
                                               get(message.guild.roles, name=f"{char_class} Main"),
                                               get(message.guild.roles, name="EU")]
                                await user.add_roles(*roles_toadd)
                            elif char_class == "Mage" or char_class == "Priest" or char_class == "Warlock":
                                char_armor = "Cloth"
                                await user.edit(nick=f"{name.capitalize()}-{realm_final} [{char_faction[0].upper()}]")
                                roles_toadd = [get(message.guild.roles, name=char_armor), get(message.guild.roles, name=char_class),
                                               get(message.guild.roles, name=char_faction.capitalize()),
                                               get(message.guild.roles, name=f"M+ Booster [{char_faction[0].upper()}]"),
                                               get(message.guild.roles, name=f"{char_class} Main"),
                                               get(message.guild.roles, name="EU")]
                                await user.add_roles(*roles_toadd)
                            elif char_class == "Hunter" or char_class == "Shaman":
                                char_armor = "Mail"
                                await user.edit(nick=f"{name.capitalize()}-{realm_final} [{char_faction[0].upper()}]")
                                roles_toadd = [get(message.guild.roles, name=char_armor), get(message.guild.roles, name=char_class),
                                               get(message.guild.roles, name=char_faction.capitalize()),
                                               get(message.guild.roles, name=f"M+ Booster [{char_faction[0].upper()}]"),
                                               get(message.guild.roles, name=f"{char_class} Main"),
                                               get(message.guild.roles, name="EU")]
                                await user.add_roles(*roles_toadd)
                            elif char_class == "Paladin" or char_class == "Warrior" or char_class == "Death Knight":
                                char_armor = "Plate"
                                await user.edit(nick=f"{name.capitalize()}-{realm_final} [{char_faction[0].upper()}]")
                                roles_toadd = [get(message.guild.roles, name=char_armor), get(message.guild.roles, name=char_class),
                                               get(message.guild.roles, name=char_faction.capitalize()),
                                               get(message.guild.roles, name=f"M+ Booster [{char_faction[0].upper()}]"),
                                               get(message.guild.roles, name=f"{char_class} Main"),
                                               get(message.guild.roles, name="EU")]
                                await user.add_roles(*roles_toadd)
                                
                            #if (realm.lower()=="sanguino" or realm.lower()=="uldum" or realm.lower()=="shen'dralar" or realm.lower()=="zul'jin") and char_faction.lower() == "horde":
                            #    await user.add_roles(get(message.guild.roles, name="SPA"))
                            if realm_final.lower().startswith("pozzo") and char_faction.lower() == "alliance":
                                await user.add_roles(get(message.guild.roles, name="ITA"))
                            elif realm_final.lower().startswith("pozzo") and char_faction.lower() == "horde":
                                await user.add_roles(get(message.guild.roles, name="ITA [H]"))
                            elif realm_final.lower()=="hyjal":
                                await user.add_roles(get(message.guild.roles, name="Hyjal"))
                            elif realm_final.lower()=="dalaran" or realm_final.lower().startswith("marécage"):
                                await user.add_roles(get(message.guild.roles, name="Dalaran"))
                            #elif realm_final.lower()=="drak'thul" and char_faction.lower() == "alliance":
                                #await user.add_roles(get(message.guild.roles, name="Drak'thul"))
                            elif realm_final.lower()=="exodar":
                                await user.add_roles(get(message.guild.roles, name="Exodar"))
                            elif realm_final.lower()=="themaelstrom":
                                await user.add_roles(get(message.guild.roles, name="The-Maelstrom"))
                            elif (realm_final.lower()=="drak'thul" or realm_final.lower()=="burningblade") and char_faction.lower() == "horde":
                                await user.add_roles(get(message.guild.roles, name="DB"))
                            elif (realm_final.lower()=="frostmane" or realm_final.lower()=="grimbatol" or realm_final.lower()=="aggra") and char_faction.lower() == "horde":
                                await user.add_roles(get(message.guild.roles, name="GFA"))

                            if get(message.guild.roles, name="Client") in user.roles:
                                await user.remove_roles(get(message.guild.roles, name="Client"))
                            if get(message.guild.roles, name="PickYourRegion") in user.roles:
                                await user.remove_roles(get(message.guild.roles, name="PickYourRegion"))
                            await rio_channel.send(f"`{name.capitalize()}-{realm_final} "
                                                   f"[{char_faction[0].upper()}] Accepted and given the ranks`")
                            await message.channel.send(f"{user.mention} `{name.capitalize()}-{realm_final} "
                                                   f"[{char_faction[0].upper()}] Accepted and given the ranks`", delete_after=10)
                            await rio_channel.send(f"Current Season: \n{season_4_all}")
                            #await rio_channel.send(f"Season 3\n{season_3}")
                            await rio_channel.send(f"Faction:{char_faction.capitalize()}")
                            await rio_channel.send(f"Class: {char_class}\nArmor: {char_armor}\nRoles: {dps_role} | {healer_role} | {tank_role}\n=============================")
                        else:
                            await rio_channel.send(f"`{name.capitalize()}-{realm_final} "
                                                   f"[{char_faction[0].upper()}] Have less than 1300 rio in any spec`")
                            await message.channel.send(f"{message.author.mention}`{name.capitalize()}-{realm_final} "
                                                   f"[{char_faction[0].upper()}] Have less than 1300 rio in any spec`",delete_after=10)
                        await asyncio.sleep(1)
                    else:
                        await rio_channel.send(f"No records found for {name.capitalize()}-{realm.capitalize().replace(' ', '')} "
                                               f"on raider.io")
                elif not auto_rank_msg[1].lower().startswith('character realm') or not auto_rank_msg[0].lower().startswith('character name'):
                    await message.delete()
                    await message.channel.send(f"You used wrong template, check the pinned messages {message.author.mention}", delete_after=10)
            elif (len(auto_rank_msg)<2 or len(auto_rank_msg)>2) and not message.author.bot and \
                    message.author.id not in rio_allowed_ids:
                    await message.delete()
                    await message.channel.send(f"You used wrong template, check the pinned messages {message.author.mention}", delete_after=10)
        except discord.errors.Forbidden:
            await message.channel.send(f"Cannot send you a DM to {user.mention}", delete_after=5)
        except Exception:
            logging.error("--S1 Ranks START---")
            logging.error(traceback.format_exc())
            logging.error("--S1 Ranks END---")
            bot_log_channel = get(message.guild.text_channels, name='bot-logs')
            embed_bot_log = discord.Embed(title="Error Log.", description="Reclaim Booster Channel", color=0x5d4991)
            embed_bot_log.add_field(name="Author", value=message.author.nick, inline=True)
            embed_bot_log.add_field(name="Content", value=message.content, inline=False)
            embed_bot_log.set_footer(text="Timestamp: " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
            await bot_log_channel.send(embed=embed_bot_log)
            ##################################################################################################################
    elif message.channel.id == 815104636037627919: #highkey-booster-role Request Rank Channel:
        try:
            await asyncio.sleep(3)
            request_rank_msg = message.content.split("\n")
            if len(request_rank_msg)>1 and not message.author.bot:
                if request_rank_msg[1].lower().startswith('character realm') and not message.author.bot and message.author.nick.endswith("[A]"):
                    request_rank_char_name = request_rank_msg[0].partition(":")[2].strip()
                    request_rank_relam_name = request_rank_msg[1].partition(":")[2].strip()
                    if message.author.nick.partition("-")[0].strip().lower() == request_rank_char_name.strip().lower():
                        response = requests.get(
                                    "https://raider.io/api/v1/characters/profile?region=eu&realm=" + request_rank_relam_name + 
                                    "&name=" + request_rank_char_name + "&fields=mythic_plus_scores_by_season%3Acurrent")
                        if response.status_code == 200:
                            json_str = json.dumps(response.json())
                            resp = json.loads(json_str)
                            char_class = resp['class']
                            char_faction = resp['faction']
                            season = resp['mythic_plus_scores_by_season']
                            #season_4_pre = season[0]
                            #season_4_pre_all = season_4_pre["scores"]["all"]
                            season_curr = season[0]
                            season_curr_all = season_curr["scores"]["all"]
                            if season_curr_all >= 1600:
                                await message.channel.send("Character ("+ request_rank_char_name + "-" + request_rank_relam_name +")\nSeason 1: " + str(season_curr_all))
                                if get(message.guild.roles, name="High Key Booster [A]") not in message.author.roles:
                                    await message.author.add_roles(get(message.guild.roles, name="High Key Booster [A]"))
                                    await message.add_reaction(u"\u2705")
                            else:
                                await message.channel.send(message.author.mention + "you have less than the required rio, application declined!")
                                await message.add_reaction(u"\u274C")
                        else:
                            await message.channel.send("No such character ("+ request_rank_char_name + "-" + request_rank_relam_name +") found on Raider.io, double check spelling")
                    else:
                        await message.channel.send(message.author.mention + "the character you are applying with doesnt match the character you signed to NOVA!")
                        await message.add_reaction(u"\u274C")
                elif request_rank_msg[1].lower().startswith('character realm') and not message.author.bot and message.author.nick.endswith("[H]"):
                    request_rank_char_name = request_rank_msg[0].partition(":")[2].strip()
                    request_rank_relam_name = request_rank_msg[1].partition(":")[2].strip()
                    if message.author.nick.partition("-")[0].strip().lower() == request_rank_char_name.strip().lower():
                        response = requests.get(
                                    "https://raider.io/api/v1/characters/profile?region=eu&realm=" + request_rank_relam_name + 
                                    "&name=" + request_rank_char_name + "&fields=mythic_plus_scores_by_season%3Acurrent")
                        if response.status_code == 200:
                            json_str = json.dumps(response.json())
                            resp = json.loads(json_str)
                            char_class = resp['class']
                            char_faction = resp['faction']
                            season = resp['mythic_plus_scores_by_season']
                            #season_4_pre = season[0]
                            #season_4_pre_all = season_4_pre["scores"]["all"]
                            season_curr = season[0]
                            season_curr_all = season_curr["scores"]["all"]
                            if season_curr_all >= 1600:
                                await message.channel.send("Character ("+ request_rank_char_name + "-" + request_rank_relam_name +")\nSeason 1: " + str(season_curr_all))
                                if get(message.guild.roles, name="High Key Booster [H]") not in message.author.roles:
                                    await message.author.add_roles(get(message.guild.roles, name="High Key Booster [H]"))
                                    await message.add_reaction(u"\u2705")
                            else:
                                await message.channel.send(message.author.mention + "you have less than the required rio, application declined!")
                                await message.add_reaction(u"\u274C")
                        else:
                            await message.channel.send("No such character ("+ request_rank_char_name + "-" + request_rank_relam_name +") found on Raider.io, double check spelling")
                    else:
                        await message.channel.send(message.author.mention + "the character you are applying with doesnt match the character you signed to NOVA!")
                        await message.add_reaction(u"\u274C")
                else:
                    await message.delete()
        except Exception:
            logging.error("--S1 HighKey START---")
            logging.error(traceback.format_exc())
            logging.error("--S1 HighKey END---")

    await bot.process_commands(message)
        


@bot.command(pass_context=True)
@commands.has_any_role('Moderator', 'NOVA', 'Curve Section Leader')
async def CheckCurve(ctx, user: discord.Member, name: str, realm: str):
    await ctx.message.delete()
    raiders_channel = get(ctx.guild.text_channels, name='raiders-channel')
    try:
        response = requests.get(
            "https://raider.io/api/v1/characters/profile?region=eu&realm=" + realm + "&name=" + name +
            "&fields=mythic_plus_scores_by_season%3Acurrent")
        if response.status_code == 200:
            json_str = json.dumps(response.json())
            resp = json.loads(json_str)
            char_class = resp['class']
            char_faction = resp['faction']
            realm_pre = realm.replace(' ', '').replace('-','').capitalize()
            if realm_pre.startswith("Pozzo"):
                realm_final = "Pozzo"
            elif realm_pre == "Dunmodr":
                realm_final = "DunModr"
            elif realm_pre.startswith("Twisting"):
                realm_final = "TwistingNether"
            elif realm_pre.startswith("Tarren"):
                realm_final = "TarrenMill"
            elif realm_pre == "Colinaspardas":
                realm_final = "ColinasPardas"
            elif realm_pre == "Burninglegion":
                realm_final = "BurningLegion"
            elif realm_pre == "Themaelstrom":
                realm_final = "TheMaelstrom"
            elif realm_pre == "Defiasbrotherhood":
                realm_final = "Defias"
            elif realm_pre == "Shatteredhand":
                realm_final = "Shattered"
            elif realm_pre.startswith("Argent"):
                realm_final = "ArgentDawn"
            elif realm_pre == "Burningblade":
                realm_final = "BurningBlade"
            elif realm_pre.startswith("Aggra"):
                realm_final = "Aggra"
            elif realm_pre.startswith("Chamberof"):
                realm_final = "ChamberofAspects"
            elif realm_pre.startswith("Emerald"):
                realm_final = "EmeraldDream"
            elif realm_pre.startswith("Grim"):
                realm_final = "GrimBatol"
            elif realm_pre.startswith("Quel"):
                realm_final = "Quel'Thalas"
            elif realm_pre.startswith("Mal'ganis"):
                realm_final = "Mal'Ganis"
            elif realm_pre.startswith("Azjol"):
                realm_final = "AzjolNerub"
            elif realm_pre.startswith("Los"):
                realm_final = "LosErrantes"
            elif realm_pre.startswith("Twilight"):
                realm_final = "Twilight'sHammer"
            else:
                realm_final = realm_pre
            await user.edit(nick=f"{name.capitalize()}-{realm_final} [{char_faction[0].upper()}]")
            roles_toadd = [get(ctx.guild.roles, name=char_class),
                            get(ctx.guild.roles, name=char_faction.capitalize()),
                            get(ctx.guild.roles, name="Curve Booster"),
                            get(ctx.guild.roles, name="EU")]
            await user.add_roles(*roles_toadd)
            if (realm_final.lower().startswith("pozzo") or realm_final.lower()=="hyjal" or 
                    realm_final.lower()=="dalaran" or realm_final.lower().startswith("marécage") or 
                    realm_final.lower()=="exodar" or realm_final.lower()=="themaelstrom") and char_faction.lower() == "alliance":
                await applicant.add_roles(get(guild.roles, name="A-Vaults"))                
            elif (realm_final.lower().startswith("pozzo") or realm_final.lower()=="drak'thul" or realm_final.lower()=="burningblade" or
                    realm_final.lower()=="frostmane" or realm_final.lower()=="grimbatol" or realm_final.lower()=="aggra" or 
                    realm_final.lower()=="dalaran" or realm_final.lower().startswith("marécage")) and char_faction.lower() == "horde":
                await applicant.add_roles(get(guild.roles, name="H-Vaults"))
            if get(ctx.guild.roles, name="Client") in user.roles:
                    await user.remove_roles(get(ctx.guild.roles, name="Client"))
            if get(ctx.guild.roles, name="PickYourRegion") in user.roles:
                await user.remove_roles(get(ctx.guild.roles, name="PickYourRegion"))
            await raiders_channel.send(f"`{name.capitalize()}-{realm_final} "
                                    f"[{char_faction[0].upper()}] Accepted and given the ranks`")
        else:
            await raiders_channel.send(f"No records found for {name.capitalize()}-{realm.capitalize().replace(' ', '')} "
                                   f"on raider.io")
    except commands.BadArgument:
        await ctx.send("Please double check command structure", delete_after=5)
    except Exception:
        logging.error("--On CheckCurve Command---")
        logging.error(traceback.format_exc())
        logging.error("--On CheckCurve Command---")
        bot_log_channel = get(guild.text_channels, name='bot-logs')
        embed_bot_log = discord.Embed(title="NOVA Apps Error Log.", description="on CheckCurve", color=0x5d4991)
        embed_bot_log.set_footer(text="Timestamp (UTC±00:00): " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
        await bot_log_channel.send(embed=embed_bot_log)
        
bot.run(token)
