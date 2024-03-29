#!/usr/bin/env python3
# coding=utf-8
import os
import traceback
import logging
import discord
import asyncio
import requests
import json
import re
import socket
from datetime import timedelta, datetime, timezone
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
import aiomysql
import aiohttp
import random


running=False

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DATABASE = os.getenv('DB_DATABASE')

intents = discord.Intents().all()

class rio_conf:
    RAIDERIO_LINK = r"https:\/\/raider\.io\/characters\/eu\/(.+)\/([^?.]+)"
    base: str = "https://raider.io"
    role_threshhold: int = 2100
    highkey_threshhold: int = 2300
    hightier_threshhold: int = 2500

class Mybot(commands.Bot):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
    self.pool = None
    self._resolver = aiohttp.AsyncResolver()

    # Use AF_INET as its socket family to prevent HTTPS related problems both locally
    # and in production.
    self._connector = aiohttp.TCPConnector(
        resolver=self._resolver,
        family=socket.AF_INET,
    )

    self.http.connector = self._connector
    self.http_session = aiohttp.ClientSession(connector=self._connector)
    
    

  async def logout(self):
      """|coro|
      Logs out of Discord and closes all connections.
      """
      try:
        if self.pool:
          self.pool.close()
          await self.pool.wait_closed()
      finally:
          await super().logout()

bot = Mybot(command_prefix=commands.when_mentioned_or('apps!'), case_insensitive=True, intents=intents)

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='/NOVA/NOVA_Apps/NOVA_Apps.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
logger.addHandler(handler)

@bot.event
async def on_ready():
    global running
    try:
        if running==False:
            logger.info(f'{bot.user.name} {discord.__version__} has connected to Discord!')
            guild = bot.get_guild(815104630433775616)
            bot_log_channel = get(guild.text_channels, id=817552283209433098)
            embed_bot_log = discord.Embed(title="Info Log.",
                                description=f'{bot.user.name} {discord.__version__} has connected to Discord!',
                                color=0x5d4991)
            embed_bot_log.set_footer(text=
                                "Timestamp (UTC±00:00): "
                                f"{datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None)}")
            await bot_log_channel.send(embed=embed_bot_log)
            running=True
    except Exception:
        logger.error(traceback.format_exc())
        bot_log_channel = get(guild.text_channels, name='bot-logs')
        embed_bot_log = discord.Embed(
                                    title="Error Log.",
                                    description="on ready",
                                    color=0x5d4991)
        embed_bot_log.set_footer(text=
                                "Timestamp (UTC±00:00): "
                                f"{datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None)}")
        await bot_log_channel.send(embed=embed_bot_log)


@bot.command()
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
                163324686086832129,234065317037342721,200277087238619137,186433880872583169,263100178129485824,263100178129485824]
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
            realm_pre = re.sub('[^A-Za-z0-9\']+', '', realm_pre)
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
            elif realm_pre == "Aggramar":
                realm_final = "Aggramar"
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
            if float(dps_score) >= rio_conf.role_threshhold:
                dps_role = "Damage"
                await applicant.add_roles(get(guild.roles, name=dps_role))
            else:
                dps_role = None
            if float(heal_score) >= rio_conf.role_threshhold:
                healer_role = "Heal"
                await applicant.add_roles(get(guild.roles, name=healer_role))
            else:
                healer_role = None
            if float(tank_score) >= rio_conf.role_threshhold:
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
                "inside the community.__\n \n**<#815104635584774165>** That you must follow at all costs or your risk yourself getting Struck / Banned; \n"
                "**<#815104636251275312>** Important info regarding how payment works and to check your weekly earnings; \n"
                "**<#815104636251275311>** To see when the next payment wave will be done;\n"
                "**<#815104636037627919>** To get the Highkey Booster role (+14,+15 keys) if you have the required score;\n"
                "**<#815104636037627917>** To request further roles (you don't need to do this if it's your first time in);\n"
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
            elif realm_pre == "Aggramar":
                realm_final = "Aggramar"
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
            if float(dps_score) >= rio_conf.role_threshhold:
                dps_role = "Damage"
                await applicant.add_roles(get(guild.roles, name=dps_role))
            else:
                dps_role = None
            if float(heal_score) >= rio_conf.role_threshhold:
                healer_role = "Heal"
                await applicant.add_roles(get(guild.roles, name=healer_role))
            else:
                healer_role = None
            if float(tank_score) >= rio_conf.role_threshhold:
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
                "inside the community.__\n \n**<#815104635584774165>** That you must follow at all costs or you risk yourself getting Struck / Banned; \n"
                "**<#815104636251275312>** Important info regarding how payment works and to check your weekly earnings; \n"
                "**<#815104636251275311>** To see when the next payment wave will be done;\n"
                "**<#815104636037627919>** To get the Highkey Booster role (+14,+15 keys) if you have the required score;\n"
                "**<#815104636037627917>** To request further roles (you don't need to do this if it's your first time in);\n"
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
        logger.error("--Raw Reaction Add---")
        logger.error(traceback.format_exc())
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
            MBoosterA = get(message.guild.roles, name='M+ Booster [A]')
            MBoosterH = get(message.guild.roles, name='M+ Booster [H]')
            applicant = message.author
            if len(auto_rank_msg)==2 and not message.author.bot:
                if MBoosterA not in applicant.roles and MBoosterH not in applicant.roles:
                    if auto_rank_msg[1].lower().startswith('character realm') and not message.author.bot and \
                        message.author.id not in rio_allowed_ids and "https" not in message.content:
                        auto_rank_char_name = auto_rank_msg[0].partition(":")[2].strip()
                        auto_rank_realm_name = auto_rank_msg[1].partition(":")[2].strip()
                        response = requests.get(
                                    "https://raider.io/api/v1/characters/profile?region=eu&realm=" + auto_rank_realm_name + 
                                    "&name=" + auto_rank_char_name + "&fields=mythic_plus_scores_by_season%3Acurrent")
                        if response.status_code == 200:
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
                            if season_curr_tank >= rio_conf.role_threshhold or season_curr_heal >= rio_conf.role_threshhold or season_curr_dps >= rio_conf.role_threshhold:
                                auto_rank_embed = discord.Embed(title="Application of:", description=f"{applicant.mention} / [{auto_rank_char_name}-{auto_rank_realm_name}]({resp['profile_url']})")
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
                                auto_rank_embed = discord.Embed(title="Application of:", description=f"[{auto_rank_char_name}-{auto_rank_realm_name}]({resp['profile_url']})", color = discord.Color.red())
                                auto_rank_embed.set_thumbnail(url=resp['thumbnail_url'])
                                auto_rank_embed.set_footer(text="Timestamp (UTC±00:00): " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"), icon_url="https://cdn.discordapp.com/avatars/634917649335320586/ea303e8b580d56ff6837e256b1df6ef6.png")
                                auto_rank_embed.add_field(name="Tank", value=season_curr['scores']['tank'], inline=True)
                                auto_rank_embed.add_field(name="Heal", value=season_curr['scores']['healer'], inline=True)
                                auto_rank_embed.add_field(name="DPS", value=season_curr['scores']['dps'], inline=True)
                                auto_rank_embed.add_field(name="Overall", value=season_curr_all, inline=False)
                                auto_rank_embed.add_field(name="Application declined", value="you have less than the required rio in a specific role", inline=False)
                                await applicant.send(
                                f"Hello **{applicant.name}**\n\nThank you for submitting an application to become a booster for ***NOVA***, "
                                "however on this occasion we regret to inform you that your application has been declined.\n"
                                "\nThank you,"
                                "\n***NOVA Team***")
                                auto_rank_embed_sent=await message.channel.send(embed = auto_rank_embed, delete_after=10)
                                await auto_rank_embed_sent.add_reaction(u"\u274C")
                        else:
                            await message.channel.send("No such character ("+ auto_rank_char_name + "-" + auto_rank_realm_name +") found on Raider.io, double check spelling", delete_after=10)
                    elif not auto_rank_msg[1].lower().startswith('character realm') or not auto_rank_msg[0].lower().startswith('character name') or \
                        "https" in message.content:
                        await message.delete()
                        await message.channel.send(f"You used wrong template, check the pinned messages {message.author.mention}", delete_after=10)
                else:
                    await message.delete()
                    await applicant.create_dm()
                    await applicant.dm_channel.send(
                        f"Hello **{applicant.name}**\n\nYou already have m+ booster rank. If you are trying to apply for high key booster, go to this channel: <#815104636037627919>.\n"
                                "If you think this is an error, please, contact Staff.\n"
                                "\nThank you,"
                                "\n***NOVA Team***")
                    
            elif (len(auto_rank_msg)<2 or len(auto_rank_msg)>2) and not message.author.bot and \
                    message.author.id not in rio_allowed_ids:
                    await message.delete()
                    await message.channel.send(f"You used wrong template, check the pinned messages {message.author.mention}", delete_after=10)
        except discord.errors.Forbidden:
            await message.channel.send(f"Cannot send a DM to {applicant.mention}", delete_after=5)
        except Exception:
            logger.error("--Auto Ranks START---")
            logger.error(traceback.format_exc())
            logger.error("--Auto Ranks END---")
            bot_log_channel = get(message.guild.text_channels, name='bot-logs')
            embed_bot_log = discord.Embed(title="NOVA Apps Error Log.", description="on reaction add EU MPlus Applications", color=0x5d4991)
            embed_bot_log.add_field(name="Author", value=message.author.name, inline=True)
            embed_bot_log.add_field(name="Channel", value=message.channel.name, inline=False)
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
                    auto_rank_realm_name = auto_rank_msg[1].partition(":")[2].strip()
                    response = requests.get(
                                "https://raider.io/api/v1/characters/profile?region=us&realm=" + auto_rank_realm_name + 
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
                        if season_curr_tank >= rio_conf.role_threshhold or season_curr_heal >= rio_conf.role_threshhold or season_curr_dps >= rio_conf.role_threshhold:
                            auto_rank_embed = discord.Embed(title="Application of:", description=f"{applicant.mention} / [{auto_rank_char_name}-{auto_rank_realm_name}]({resp['profile_url']})")
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
                            await applicant.send(
                                f"Hello **{applicant.name}**\n\nThank you for submitting an application to become a booster for ***NOVA***, "
                                "all the applications will be verified by our team every day, you don't have to DM us to speed up the process, your DMs will be ignored..\n"
                                "\nThank you,"
                                "\n***NOVA Team***")
                            await auto_rank_embed_sent.add_reaction('<:nova_c:817558639241592859>')
                            await auto_rank_embed_sent.add_reaction('<:nova_x:817559679760465980>')
                        else:
                            auto_rank_embed = discord.Embed(title="Application of:", description=f"[{auto_rank_char_name}-{auto_rank_realm_name}]({resp['profile_url']})", color = discord.Color.red())
                            auto_rank_embed.set_thumbnail(url=resp['thumbnail_url'])
                            auto_rank_embed.set_footer(text="Timestamp (UTC±00:00): " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"), icon_url="https://cdn.discordapp.com/avatars/634917649335320586/ea303e8b580d56ff6837e256b1df6ef6.png")
                            auto_rank_embed.add_field(name="Tank", value=season_curr['scores']['tank'], inline=True)
                            auto_rank_embed.add_field(name="Heal", value=season_curr['scores']['healer'], inline=True)
                            auto_rank_embed.add_field(name="DPS", value=season_curr['scores']['dps'], inline=True)
                            auto_rank_embed.add_field(name="Overall", value=season_curr_all, inline=False)
                            auto_rank_embed.add_field(name="Application declined", value="you have less than the required rio in a specific role", inline=False)
                            await applicant.send(
                            f"Hello **{applicant.name}**\n\nThank you for submitting an application to become a booster for ***NOVA***, "
                            "however on this occasion we regret to inform you that your application has been declined.\n"
                            "\nThank you,"
                            "\n***NOVA Team***")
                            auto_rank_embed_sent=await message.channel.send(embed = auto_rank_embed, delete_after=10)
                            await auto_rank_embed_sent.add_reaction(u"\u274C")
                    else:
                        await message.channel.send("No such character ("+ auto_rank_char_name + "-" + auto_rank_realm_name +") found on Raider.io, double check spelling", delete_after=10)
                elif not auto_rank_msg[1].lower().startswith('character realm') or not auto_rank_msg[0].lower().startswith('character name') or \
                    "https" in message.content:
                    await message.delete()
                    await message.channel.send(f"You used wrong template, check the pinned messages {message.author.mention}", delete_after=10)
            elif (len(auto_rank_msg)<2 or len(auto_rank_msg)>2) and not message.author.bot and \
                    message.author.id not in rio_allowed_ids:
                    await message.delete()
                    await message.channel.send(f"You used wrong template, check the pinned messages {message.author.mention}", delete_after=10)
        except discord.errors.Forbidden:
            await message.channel.send(f"Cannot send you a DM to {applicant.mention}", delete_after=5)
        except Exception:
            logger.error("--Auto Ranks START---")
            logger.error(traceback.format_exc())
            logger.error("--Auto Ranks END---")
            bot_log_channel = get(message.guild.text_channels, name='bot-logs')
            embed_bot_log = discord.Embed(title="NOVA Apps Error Log.", description="on reaction add NA MPlus Applications", color=0x5d4991)
            embed_bot_log.add_field(name="Author", value=message.author.name, inline=True)
            embed_bot_log.add_field(name="Channel", value=message.channel.name, inline=False)
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
                        elif realm_pre == "Aggramar":
                            realm_final = "Aggramar"
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
                        if season_4_dps >= rio_conf.role_threshhold:
                            dps_role = "Damage"
                            await user.add_roles(get(message.guild.roles, name=dps_role))
                        else:
                            dps_role = None
                        if season_4_healer >= rio_conf.role_threshhold:
                            healer_role = "Heal"
                            await user.add_roles(get(message.guild.roles, name=healer_role))
                        else:
                            healer_role = None
                        if season_4_tank >= rio_conf.role_threshhold:
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
            logger.error("--S1 Ranks START---")
            logger.error(traceback.format_exc())
            logger.error("--S1 Ranks END---")
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
                    request_rank_realm_name = request_rank_msg[1].partition(":")[2].strip()
                    if message.author.nick.partition("-")[0].strip().lower() == request_rank_char_name.strip().lower():
                        response = requests.get(
                                    "https://raider.io/api/v1/characters/profile?region=eu&realm=" + request_rank_realm_name + 
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
                            if season_curr_all >= rio_conf.highkey_threshhold:
                                await message.channel.send("Character ("+ request_rank_char_name + "-" + request_rank_realm_name +")\nSeason 1: " + str(season_curr_all))
                                if get(message.guild.roles, name="High Key Booster [A]") not in message.author.roles:
                                    await message.author.add_roles(get(message.guild.roles, name="High Key Booster [A]"))
                                    await message.add_reaction(u"\u2705")
                            else:
                                await message.channel.send(message.author.mention + "you have less than the required rio, application declined!")
                                await message.add_reaction(u"\u274C")
                        else:
                            await message.channel.send("No such character ("+ request_rank_char_name + "-" + request_rank_realm_name +") found on Raider.io, double check spelling")
                    else:
                        await message.channel.send(message.author.mention + "the character you are applying with doesn't match the character you signed to NOVA!")
                        await message.add_reaction(u"\u274C")
                elif request_rank_msg[1].lower().startswith('character realm') and not message.author.bot and message.author.nick.endswith("[H]"):
                    request_rank_char_name = request_rank_msg[0].partition(":")[2].strip()
                    request_rank_realm_name = request_rank_msg[1].partition(":")[2].strip()
                    if message.author.nick.partition("-")[0].strip().lower() == request_rank_char_name.strip().lower():
                        response = requests.get(
                                    "https://raider.io/api/v1/characters/profile?region=eu&realm=" + request_rank_realm_name + 
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
                            if season_curr_all >= rio_conf.highkey_threshhold:
                                await message.channel.send("Character ("+ request_rank_char_name + "-" + request_rank_realm_name +")\nSeason 1: " + str(season_curr_all))
                                if get(message.guild.roles, name="High Key Booster [H]") not in message.author.roles:
                                    await message.author.add_roles(get(message.guild.roles, name="High Key Booster [H]"))
                                    await message.add_reaction(u"\u2705")
                            else:
                                await message.channel.send(message.author.mention + "you have less than the required rio, application declined!")
                                await message.add_reaction(u"\u274C")
                        else:
                            await message.channel.send("No such character ("+ request_rank_char_name + "-" + request_rank_realm_name +") found on Raider.io, double check spelling")
                    else:
                        await message.channel.send(message.author.mention + "the character you are applying with doesn't match the character you signed to NOVA!")
                        await message.add_reaction(u"\u274C")
                else:
                    await message.delete()
        except Exception:
            logger.error("--S1 HighKey START---")
            logger.error(traceback.format_exc())
            logger.error("--S1 HighKey END---")
    elif message.channel.id == 894280340586258462: #HIGH TIER BOOSTER:
        try:
            await asyncio.sleep(3)
            request_rank_msg = message.content.split("\n")
            if len(request_rank_msg)>1 and not message.author.bot:
                if request_rank_msg[1].lower().startswith('character realm') and not message.author.bot and message.author.nick.endswith("[A]"):
                    request_rank_char_name = request_rank_msg[0].partition(":")[2].strip()
                    request_rank_realm_name = request_rank_msg[1].partition(":")[2].strip()
                    if message.author.nick.partition("-")[0].strip().lower() == request_rank_char_name.strip().lower():
                        response = requests.get(
                                    "https://raider.io/api/v1/characters/profile?region=eu&realm=" + request_rank_realm_name + 
                                    "&name=" + request_rank_char_name + "&fields=mythic_plus_scores_by_season%3Acurrent")
                        if response.status_code == 200:
                            json_str = json.dumps(response.json())
                            resp = json.loads(json_str)
                            char_class = resp['class']
                            char_faction = resp['faction']
                            season = resp['mythic_plus_scores_by_season']
                            season_curr = season[0]
                            season_curr_all = season_curr["scores"]["all"]
                            if season_curr_all >= rio_conf.hightier_threshhold:
                                await message.channel.send("Character ("+ request_rank_char_name + "-" + request_rank_realm_name +")\nSeason 2: " + str(season_curr_all))
                                if get(message.guild.roles, name="High Tier Booster [A]") not in message.author.roles:
                                    await message.author.add_roles(get(message.guild.roles, name="High Tier Booster [A]"))
                                    await message.add_reaction(u"\u2705")
                            else:
                                await message.channel.send(message.author.mention + "you have less than the required rio, application declined!")
                                await message.add_reaction(u"\u274C")
                        else:
                            await message.channel.send("No such character ("+ request_rank_char_name + "-" + request_rank_realm_name +") found on Raider.io, double check spelling")
                    else:
                        await message.channel.send(message.author.mention + "the character you are applying with doesn't match the character you signed to NOVA!")
                        await message.add_reaction(u"\u274C")
                elif request_rank_msg[1].lower().startswith('character realm') and not message.author.bot and message.author.nick.endswith("[H]"):
                    request_rank_char_name = request_rank_msg[0].partition(":")[2].strip()
                    request_rank_realm_name = request_rank_msg[1].partition(":")[2].strip()
                    if message.author.nick.partition("-")[0].strip().lower() == request_rank_char_name.strip().lower():
                        response = requests.get(
                                    "https://raider.io/api/v1/characters/profile?region=eu&realm=" + request_rank_realm_name + 
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
                            if season_curr_all >= rio_conf.hightier_threshhold:
                                await message.channel.send("Character ("+ request_rank_char_name + "-" + request_rank_realm_name +")\nSeason 2: " + str(season_curr_all))
                                if get(message.guild.roles, name="High Tier Booster [H]") not in message.author.roles:
                                    await message.author.add_roles(get(message.guild.roles, name="High Tier Booster [H]"))
                                    await message.add_reaction(u"\u2705")
                            else:
                                await message.channel.send(message.author.mention + "you have less than the required rio, application declined!")
                                await message.add_reaction(u"\u274C")
                        else:
                            await message.channel.send("No such character ("+ request_rank_char_name + "-" + request_rank_realm_name +") found on Raider.io, double check spelling")
                    else:
                        await message.channel.send(message.author.mention + "the character you are applying with doesn't match the character you signed to NOVA!")
                        await message.add_reaction(u"\u274C")
                else:
                    await message.delete()
        except Exception:
            logger.error("--S1 HighTier START---")
            logger.error(traceback.format_exc())
            logger.error("--S1 HighTier END---")

    elif message.channel.id == 856561520611688478: #s2 get high rank again:
        try:
            await asyncio.sleep(3)
            request_rank_msg = message.content.split("\n")
            if len(request_rank_msg)>1 and not message.author.bot:
                if request_rank_msg[1].lower().startswith('character realm') and not message.author.bot and message.author.nick.endswith("[A]"):
                    request_rank_char_name = request_rank_msg[0].partition(":")[2].strip()
                    request_rank_realm_name = request_rank_msg[1].partition(":")[2].strip()
                    if message.author.nick.partition("-")[0].strip().lower() == request_rank_char_name.strip().lower():
                        response = requests.get(
                                    "https://raider.io/api/v1/characters/profile?region=eu&realm=" + request_rank_realm_name + 
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
                            if season_curr_all >= rio_conf.hightier_threshhold:
                                await message.channel.send("Character ("+ request_rank_char_name + "-" + request_rank_realm_name +")\nSeason 1: " + str(season_curr_all))
                                if get(message.guild.roles, name="S2 High Booster [A]") not in message.author.roles:
                                    await message.author.add_roles(get(message.guild.roles, name="S2 High Booster [A]"))
                                    await message.add_reaction(u"\u2705")
                            else:
                                await message.channel.send(message.author.mention + "you have less than the required rio, application declined!")
                                await message.add_reaction(u"\u274C")
                        else:
                            await message.channel.send("No such character ("+ request_rank_char_name + "-" + request_rank_realm_name +") found on Raider.io, double check spelling")
                    else:
                        await message.channel.send(message.author.mention + "the character you are applying with doesn't match the character you signed to NOVA!")
                        await message.add_reaction(u"\u274C")
                elif request_rank_msg[1].lower().startswith('character realm') and not message.author.bot and message.author.nick.endswith("[H]"):
                    request_rank_char_name = request_rank_msg[0].partition(":")[2].strip()
                    request_rank_realm_name = request_rank_msg[1].partition(":")[2].strip()
                    if message.author.nick.partition("-")[0].strip().lower() == request_rank_char_name.strip().lower():
                        response = requests.get(
                                    "https://raider.io/api/v1/characters/profile?region=eu&realm=" + request_rank_realm_name + 
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
                            if season_curr_all >= rio_conf.hightier_threshhold:
                                await message.channel.send("Character ("+ request_rank_char_name + "-" + request_rank_realm_name +")\nSeason 1: " + str(season_curr_all))
                                if get(message.guild.roles, name="S2 High Booster [H]") not in message.author.roles:
                                    await message.author.add_roles(get(message.guild.roles, name="S2 High Booster [H]"))
                                    await message.add_reaction(u"\u2705")
                            else:
                                await message.channel.send(message.author.mention + "you have less than the required rio, application declined!")
                                await message.add_reaction(u"\u274C")
                        else:
                            await message.channel.send("No such character ("+ request_rank_char_name + "-" + request_rank_realm_name +") found on Raider.io, double check spelling")
                    else:
                        await message.channel.send(message.author.mention + "the character you are applying with doesn't match the character you signed to NOVA!")
                        await message.add_reaction(u"\u274C")
                else:
                    await message.delete()
        except Exception:
            logger.error("--S2 HighKey START---")
            logger.error(traceback.format_exc())
            logger.error("--S2 HighKey END---")
            bot_log_channel = get(message.guild.text_channels, name='bot-logs')
            embed_bot_log = discord.Embed(title="Error Log.", description="Reclaim Booster Channel", color=0x5d4991)
            embed_bot_log.add_field(name="Author", value=message.author.nick, inline=True)
            embed_bot_log.add_field(name="Content", value=message.content, inline=False)
            embed_bot_log.set_footer(text="Timestamp: " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
            await bot_log_channel.send(embed=embed_bot_log)       

    await bot.process_commands(message)
        

@bot.command()
async def NameChange(ctx, *, rio_url):
    """To change member name
        command structure is `apps!NameChange RaiderIO link`
        example: `apps!NameChange https://raider.io/characters/eu/tarren-mill/Sanfura`
    """
    raiderio_regex = re.compile(rio_conf.RAIDERIO_LINK)
    match = raiderio_regex.findall(rio_url)
    command_issuer = ctx.author
    Moderator_role = get(ctx.guild.roles, name="Moderator")
    Management_role = get(ctx.guild.roles, name="Management")
    Staff_role = get(ctx.guild.roles, name="staff active")
    CS_role = get(ctx.guild.roles, name="Community Support")
    balance_check_channel = get(ctx.guild.text_channels, id=815104636251275312)
    if (ctx.message.channel.id != 815104636251275312 and 
        (Moderator_role not in ctx.author.roles and Management_role not in ctx.author.roles and Staff_role not in ctx.author.roles and CS_role not in ctx.author.roles)):
        return await ctx.message.channel.send(
            f"Head to {balance_check_channel.mention} to issue the command", 
            delete_after=5)
    if not match:
        await ctx.author.send("""
                            Wrong Raider.IO link, please double check it, 
                            example: https://raider.io/characters/eu/tarren-mill/Sanfura
                            """, delete_after=10)
        return

    realm = match[0][0]
    char = match[0][1]
    if not (realm and char):
        await ctx.author.send(f"No such character ({char}-{realm} "
                            "found on Raider.io, double check your rio url", delete_after=10)
        return

    try:
        async with ctx.bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query  = """
                    SELECT date_of_change FROM name_changes where discord_id = %s 
                """
                val = (command_issuer.id,)
                await cursor.execute(query, val)
                query_result = await cursor.execute(query, val)
                if query_result:
                    (date_of_change,) = await cursor.fetchone()
                    end_date = date_of_change + timedelta(days=60)
                else:
                    date_of_change = None
                    end_date = None

            if ((date_of_change is None and end_date is None) or 
                (end_date is not None and datetime.now(timezone.utc).date() > end_date)):
                confirmation_msg = await ctx.send(
                    "**Attention!**\n"
                    f"{command_issuer.mention} When changing your name, beware that any pending balance you have will be sent "
                    "to your previous character name. If you no longer have that character, "
                    "make a level 1 with the same name so that it can receive the gold.\n"
                    "**NOVA** __is not responsible__ if you make an error in changing your name, " 
                    "we will send the gold to the associated character names given, "
                    "if you fail to receive it, that is on you.\n"
                    "`By typing 'Yes', you accept these terms. You have 30 seconds to reply here.`"
                )

                def check(m):
                    return m.content.lower() == "yes" and m.channel == ctx.channel and m.author == ctx.author

                try:
                    msg = await bot.wait_for("message", timeout=30.0, check=check)
                except asyncio.TimeoutError:
                    await ctx.send("User didn't confirm within 30 seconds, cancelling name change", 
                                    delete_after=5)
                    await confirmation_msg.delete()
                else:
                    await confirmation_msg.delete()
                    await msg.delete()
                    rio_api = (
                        f"{rio_conf.base}/api/v1/characters/profile?region=eu"
                        f"&realm={realm}"
                        f"&name={char}&fields=mythic_plus_scores_by_season:current"
                    )
                    response = requests.get(rio_api)
                    if response.status_code == 200:
                        guild = bot.get_guild(815104630433775616)
                        applicant = ctx.author
                        json_str = json.dumps(response.json())
                        resp = json.loads(json_str)
                        faction = resp["faction"]
                        rio_name = resp["name"]
                        dps_score = resp["mythic_plus_scores_by_season"][0]["scores"]["dps"]
                        tank_score = resp["mythic_plus_scores_by_season"][0]["scores"]["tank"]
                        heal_score = resp["mythic_plus_scores_by_season"][0]["scores"]["healer"]
                        char_class = resp['class']
                        char_faction = resp['faction']
                        if tank_score >= rio_conf.role_threshhold or heal_score >= rio_conf.role_threshhold or dps_score >= rio_conf.role_threshhold:
                            faction_short = "H" if faction == "horde" else "A"
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
                            elif realm_pre == "Aggramar":
                                realm_final = "Aggramar"
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
                            elif realm_pre == "Zuljin":
                                realm_final = "Zul'jin"
                            else:
                                realm_final = realm_pre
                            if get(applicant.guild.roles, name="M+ Booster [A]") in applicant.roles:
                                await applicant.remove_roles(get(applicant.guild.roles, name="M+ Booster [A]"))
                            if get(applicant.guild.roles, name="M+ Booster [H]") in applicant.roles:
                                await applicant.remove_roles(get(applicant.guild.roles, name="M+ Booster [H]"))
                            if get(applicant.guild.roles, name="High Key Booster [A]") in applicant.roles:
                                await applicant.remove_roles(get(applicant.guild.roles, name="High Key Booster [A]"))
                            if get(applicant.guild.roles, name="High Key Booster [H]") in applicant.roles:
                                await applicant.remove_roles(get(applicant.guild.roles, name="High Key Booster [H]"))
                            if get(applicant.guild.roles, name="High Tier Booster [A]") in applicant.roles:
                                await applicant.remove_roles(get(applicant.guild.roles, name="High Tier Booster [A]"))
                            if get(applicant.guild.roles, name="High Tier Booster [H]") in applicant.roles:
                                await applicant.remove_roles(get(applicant.guild.roles, name="High Tier Booster [H]"))
                            if get(applicant.guild.roles, name="Alliance") in applicant.roles:
                                await applicant.remove_roles(get(applicant.guild.roles, name="Alliance"))
                            if get(applicant.guild.roles, name="Horde") in applicant.roles:
                                await applicant.remove_roles(get(applicant.guild.roles, name="Horde"))

                            if float(dps_score) >= rio_conf.role_threshhold:
                                dps_role = "Damage"
                                await applicant.add_roles(get(guild.roles, name=dps_role))
                            else:
                                dps_role = None
                            if float(heal_score) >= rio_conf.role_threshhold:
                                healer_role = "Heal"
                                await applicant.add_roles(get(guild.roles, name=healer_role))
                            else:
                                healer_role = None
                            if float(tank_score) >= rio_conf.role_threshhold:
                                tank_role = "Tank"
                                await applicant.add_roles(get(guild.roles, name=tank_role))
                            else:
                                tank_role = None
                            if tank_role is not None or healer_role is not None or dps_role is not None:
                                if char_class == "Demon Hunter" or char_class == "Druid" or char_class == "Monk" or \
                                    char_class == "Rogue":
                                    char_armor = "Leather"
                                    roles_toadd = [get(guild.roles, name=char_armor), get(guild.roles, name=char_class),
                                                get(guild.roles, name=char_faction.capitalize()),
                                                get(guild.roles, name=f"M+ Booster [{char_faction[0].upper()}]"),
                                                get(guild.roles, name=f"{char_class} Main"),
                                                get(guild.roles, name="EU")]
                                    await applicant.add_roles(*roles_toadd)
                                elif char_class == "Mage" or char_class == "Priest" or char_class == "Warlock":
                                    char_armor = "Cloth"
                                    roles_toadd = [get(guild.roles, name=char_armor), get(guild.roles, name=char_class),
                                                get(guild.roles, name=char_faction.capitalize()),
                                                get(guild.roles, name=f"M+ Booster [{char_faction[0].upper()}]"),
                                                get(guild.roles, name=f"{char_class} Main"),
                                                get(guild.roles, name="EU")]
                                    await applicant.add_roles(*roles_toadd)
                                elif char_class == "Hunter" or char_class == "Shaman":
                                    char_armor = "Mail"
                                    roles_toadd = [get(guild.roles, name=char_armor), get(guild.roles, name=char_class),
                                                get(guild.roles, name=char_faction.capitalize()),
                                                get(guild.roles, name=f"M+ Booster [{char_faction[0].upper()}]"),
                                                get(guild.roles, name=f"{char_class} Main"),
                                                get(guild.roles, name="EU")]
                                    await applicant.add_roles(*roles_toadd)
                                elif char_class == "Paladin" or char_class == "Warrior" or char_class == "Death Knight":
                                    char_armor = "Plate"
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
                            async with conn.cursor() as cursor:
                                query = """
                                        INSERT INTO name_changes 
                                            (discord_id, old_name, new_name, date_of_change) 
                                            VALUES (%s, %s, %s, %s)
                                        ON DUPLICATE KEY UPDATE 
                                            `old_name`=%s, `new_name`=%s, `date_of_change`=%s
                                    """
                                val = (
                                    ctx.author.id, ctx.author.display_name, f"{rio_name}-{realm_final} [{faction_short}]", 
                                    {datetime.now(timezone.utc).date()},ctx.author.display_name, f"{rio_name}-{realm_final} [{faction_short}]", 
                                    {datetime.now(timezone.utc).date()})
                                await cursor.execute(query, val)
                            await ctx.author.edit(nick=f"{rio_name}-{realm_final} [{faction_short}]")
                            await ctx.message.delete()
                        else:
                            await ctx.send("The character your are renaming to has less than the required score",
                                            delete_after = 10)
                            return
            elif end_date is not None and datetime.now(timezone.utc).date() < end_date:
                await ctx.send(
                    f"You have changed your name in the last 60 days, you cannot change "
                    f"again until {end_date}", 
                    delete_after=10
                )
    except discord.errors.Forbidden:
        await ctx.send(f"Cannot send a DM to {ctx.author.mention}", delete_after=10)
    except Exception:
        logger.error("--On NameChange Command---")
        logger.error(traceback.format_exc())
        logger.error("--On NameChange Command---")
        bot_log_channel = get(ctx.guild.text_channels, name='bot-logs')
        embed_bot_log = discord.Embed(title="NOVA Apps Error Log.", description="on CheckCurve", color=0x5d4991)
        embed_bot_log.set_footer(text=
                                "Timestamp (UTC±00:00): "
                                f"{datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None)}")
        await bot_log_channel.send(embed=embed_bot_log)

@bot.command()
@commands.has_any_role('Moderator', 'NOVA')
async def filterOldBoosterRole(ctx):
    try:
        client_role = get(ctx.guild.roles, name="Client")
        clientNA_role = get(ctx.guild.roles, name="Client NA")
        pickyourregion_role = get(ctx.guild.roles, name="PickYourRegion")
        nova_role = get(ctx.guild.roles, name="NOVA")
        moderator_role = get(ctx.guild.roles, name="Moderator")
        management_role = get(ctx.guild.roles, name="Management")
        staff_role = get(ctx.guild.roles, name="Staff")
        managementNA_role = get(ctx.guild.roles, name="Management NA")
        staffNA_role = get(ctx.guild.roles, name="Staff NA")
        bot_role = get(ctx.guild.roles, name="Bots")
        partners_role = get(ctx.guild.roles, name="Partners")

        HighKeyBoosterA = get(ctx.guild.roles, name='High Key Booster [A]')
        MBoosterA = get(ctx.guild.roles, name='M+ Booster [A]')
        HighKeyBoosterH = get(ctx.guild.roles, name='High Key Booster [H]')
        MBoosterH = get(ctx.guild.roles, name='M+ Booster [H]')

        buggy_member_ids =[579155972115660803, 131533528616665089, 753029074531909694]
        booster_roles = [HighKeyBoosterA,MBoosterA,HighKeyBoosterH,MBoosterH]
        old_boosterA = get(ctx.guild.roles, id=815104630517268532)
        old_boosterH = get(ctx.guild.roles, id=815104630517268531)
        async for member in ctx.guild.fetch_members():
            booster_roles_check =  any(item in member.roles for item in booster_roles)
            if (not member.bot and member.nick is not None and pickyourregion_role not in member.roles and 
                client_role not in member.roles and clientNA_role not in member.roles and 
                management_role not in member.roles and staff_role not in member.roles and 
                managementNA_role not in member.roles and staffNA_role not in member.roles and 
                nova_role not in member.roles and moderator_role not in member.roles and 
                bot_role not in member.roles and partners_role not in member.roles and 
                member.id not in buggy_member_ids):
                if booster_roles_check and (old_boosterA in member.roles):
                    await member.remove_roles(old_boosterA)
                    await ctx.send(f"{member.display_name} has normal booster ranks, removed old booster")
                elif booster_roles_check and (old_boosterH in member.roles):
                    await member.remove_roles(old_boosterH)
                    await ctx.send(f"{member.display_name} has normal booster ranks, removed old booster")
        await ctx.message.delete()
        await ctx.send("Roles filtered")
    except Exception:
        logger.error("--On filterOldBoosterRole Command---")
        logger.error(traceback.format_exc())
        logger.error("--On filterOldBoosterRole Command---")
        bot_log_channel = get(ctx.guild.text_channels, name='bot-logs')
        embed_bot_log = discord.Embed(title="NOVA Apps Error Log.", description="on filterOldBoosterRole", color=0x5d4991)
        embed_bot_log.set_footer(text=
                                "Timestamp (UTC±00:00): "
                                f"{datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None)}")
        await bot_log_channel.send(embed=embed_bot_log)

@bot.command()
@commands.has_any_role('Moderator', 'NOVA', 'developer')
async def ListWrongRoles(ctx):
    try:
        client_role = get(ctx.guild.roles, name="Client")
        clientNA_role = get(ctx.guild.roles, name="Client NA")
        pickyourregion_role = get(ctx.guild.roles, name="PickYourRegion")
        nova_role = get(ctx.guild.roles, name="NOVA")
        moderator_role = get(ctx.guild.roles, name="Moderator")
        management_role = get(ctx.guild.roles, name="Management")
        staff_role = get(ctx.guild.roles, name="Staff")
        managementNA_role = get(ctx.guild.roles, name="Management NA")
        staffNA_role = get(ctx.guild.roles, name="Staff NA")
        bot_role = get(ctx.guild.roles, name="Bots")
        partners_role = get(ctx.guild.roles, name="Partners")

        HighKeyBoosterA = get(ctx.guild.roles, name='High Key Booster [A]')
        MBoosterA = get(ctx.guild.roles, name='M+ Booster [A]')
        HighKeyBoosterH = get(ctx.guild.roles, name='High Key Booster [H]')
        MBoosterH = get(ctx.guild.roles, name='M+ Booster [H]')
        PVP = get(ctx.guild.roles, name = "PVP")
        RBG = get(ctx.guild.roles, name = "RBG")
        RBGLeader = get(ctx.guild.roles, name = "RBG Leader")
        Mounts = get(ctx.guild.roles, name = "Mounts")
        LegacyA = get(ctx.guild.roles, name = "Legacy Alliance [A]")
        LegacyH = get(ctx.guild.roles, name="Legacy Horde [H]")
        TorghastA = get(ctx.guild.roles, name="Torghast Booster [A]")
        TorghastH = get(ctx.guild.roles, name="Torghast Booster [H]")
        OldBoosterA = get(ctx.guild.roles, name="Old Booster [A]")
        OldBoosterH = get(ctx.guild.roles, name="Old Booster [H]")
        TrialAdvA = get(ctx.guild.roles, name="Trial Advertiser {A}")
        TrialAdvH = get(ctx.guild.roles, name="Trial Advertiser {H}")
        AdvA = get(ctx.guild.roles, name="Advertiser {A}")
        AdvH = get(ctx.guild.roles, name="Advertiser {H}")
        HotshotA = get(ctx.guild.roles, name="Hotshot Advertiser [A]")
        HotshotH = get(ctx.guild.roles, name="Hotshot Advertiser [A]")
        RaiderA = get(ctx.guild.roles, name="Raider {A}")
        RaiderH = get(ctx.guild.roles, name="Raider {H}")
        Curve = get(ctx.guild.roles, name="Curve Booster")
        CurveTrial = get(ctx.guild.roles, name="Curve Trial")
        AdvertiserHNA = get(ctx.guild.roles, name="Advertiser [H] NA")
        TrialAdvHNA = get(ctx.guild.roles, name="Trial Advertiser [H] NA")
        MBoosterANA = get(ctx.guild.roles, name="M+ Booster [A] NA")
        MBoosterHNA = get(ctx.guild.roles, name="M+ Booster [H] NA")
        RaiderHNA = get(ctx.guild.roles, name="Raider [H] NA")
        GuildRepA = get(ctx.guild.roles, name="Guild Representative {A}")
        GuildRepH = get(ctx.guild.roles, name="Guild Representative {H}")
        GuildRepHNA = get(ctx.guild.roles, name="Guild Representative [H] NA")
        SuspendH = get(ctx.guild.roles, name="Suspended {H}")
        SuspendA = get(ctx.guild.roles, name="Suspended")
        buggy_member_ids =[579155972115660803, 131533528616665089, 753029074531909694]
        booster_roles = [HighKeyBoosterA,MBoosterA,HighKeyBoosterH,MBoosterH,PVP,RBG,RBGLeader,Mounts,LegacyA,LegacyH,TorghastA,TorghastH]
        async for member in ctx.guild.fetch_members():
            # booster_roles_check =  any(item in member.roles for item in booster_roles)
            if (not member.bot and member.nick is not None and pickyourregion_role not in member.roles and 
                client_role not in member.roles and clientNA_role not in member.roles and 
                management_role not in member.roles and staff_role not in member.roles and 
                managementNA_role not in member.roles and staffNA_role not in member.roles and 
                nova_role not in member.roles and moderator_role not in member.roles and 
                bot_role not in member.roles and partners_role not in member.roles and
                HighKeyBoosterA not in member.roles and HighKeyBoosterH not in member.roles and
                MBoosterA not in member.roles and MBoosterH not in member.roles and
                PVP not in member.roles and RBG not in member.roles and RBGLeader not in member.roles and
                Mounts not in member.roles and LegacyA not in member.roles and LegacyH not in member.roles and
                TorghastA not in member.roles and TorghastH not in member.roles and
                OldBoosterA not in member.roles and OldBoosterH not in member.roles and
                TrialAdvA not in member.roles and TrialAdvH not in member.roles and
                AdvA not in member.roles and AdvH not in member.roles and
                HotshotA not in member.roles and HotshotH not in member.roles and
                RaiderA not in member.roles and RaiderH not in member.roles and
                Curve not in member.roles and CurveTrial not in member.roles and
                AdvertiserHNA not in member.roles and TrialAdvHNA not in member.roles and
                MBoosterANA not in member.roles and MBoosterHNA not in member.roles and RaiderHNA not in member.roles and
                GuildRepA not in member.roles and GuildRepH not in member.roles and GuildRepHNA not in member.roles and
                SuspendH not in member.roles and SuspendA not in member.roles and
                member.id not in buggy_member_ids and member.roles is not None):
                await ctx.send(f"<@!{member.id}> has wrong roles.")
        await ctx.message.delete()
        await ctx.send("Checked all users")
    except Exception:
        logger.error("--On ListWrongRoles Command---")
        logger.error(traceback.format_exc())
        logger.error("--On ListWrongRoles Command---")
        bot_log_channel = get(ctx.guild.text_channels, name='bot-logs')
        embed_bot_log = discord.Embed(title="NOVA Apps Error Log.", description="on ListWrongRoles", color=0x5d4991)
        embed_bot_log.set_footer(text=
                                "Timestamp (UTC±00:00): "
                                f"{datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None)}")
        await bot_log_channel.send(embed=embed_bot_log)

@bot.command()
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
            elif realm_pre == "Aggramar":
                realm_final = "Aggramar"
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
                await user.add_roles(get(ctx.guild.roles, name="A-Vaults"))                
            elif (realm_final.lower().startswith("pozzo") or realm_final.lower()=="drak'thul" or realm_final.lower()=="burningblade" or
                    realm_final.lower()=="frostmane" or realm_final.lower()=="grimbatol" or realm_final.lower()=="aggra" or 
                    realm_final.lower()=="dalaran" or realm_final.lower().startswith("marécage")) and char_faction.lower() == "horde":
                await user.add_roles(get(ctx.guild.roles, name="H-Vaults"))
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
        logger.error("--On CheckCurve Command---")
        logger.error(traceback.format_exc())
        logger.error("--On CheckCurve Command---")
        bot_log_channel = get(ctx.guild.text_channels, name='bot-logs')
        embed_bot_log = discord.Embed(title="NOVA Apps Error Log.", description="on CheckCurve", color=0x5d4991)
        embed_bot_log.set_footer(text="Timestamp (UTC±00:00): " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
        await bot_log_channel.send(embed=embed_bot_log)

time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}
def convert(argument):

    args = argument.lower()
    matches = re.findall(time_regex, args)
    time = 0
    for key, value in matches:
        try:
            time += time_dict[value] * float(key)
        except KeyError:
            raise commands.BadArgument(
                f"{value} is an invalid time key! h|m|s|d are valid arguments"
            )
        except ValueError:
            raise commands.BadArgument(f"{key} is not a number!")
    return round(time)

@bot.command()
@commands.has_any_role('Staff', 'Moderator', 'NOVA')
async def StartGiveaway(ctx, timing, winners: int, *, prize):
    """Make a giveaway with this command
       The command structure is `apps!StartGiveaway <time> <amount_winners> <prize>
    """
    await ctx.send('Preparing a cool giveaway for you all. Stand by!', delete_after=3)
    gwembed = discord.Embed(
    title="🎉 __**Giveaway**__ 🎉",
    description=f'Prize: {prize}',
    color=0xb4e0fc
    )
    time = convert(timing)
    gwembed.set_footer(text=f"This giveaway will end in {time} seconds from this message.")
    gwembed = await ctx.send(embed=gwembed)
    await gwembed.add_reaction("🎉")
    await asyncio.sleep(time)
    message = await ctx.fetch_message(gwembed.id)
    users = await message.reactions[0].users().flatten()
    users.pop(users.index(ctx.guild.me))
    if len(users) == 0:
        await ctx.send("No winner was decided.")
        return
    for i in range(winners):
        winner = random.choice(users)
        await ctx.send(f"**Congrats to: {winner}!**")

@bot.command()
@commands.has_any_role('staff active', 'Moderator', 'NOVA')
async def MountsPanels(ctx):
    """Does this even work??
    """
    embed=discord.Embed(title="**Voidtalon of the Dark Star**", url="https://www.wowhead.com/item=121815/voidtalon-of-the-dark-star", description="Corrupted by the presence of the Dark Star in Draenor, the Voidtalons resisted being broken by the Shadowmoon Clan and were ultimately destroyed by Ner'zhul. Only a single egg remains, lost in the void.", color=0x711e6e)
    embed.set_thumbnail(url="https://perfectway.one/images/prev/7c3dbd88853217c857ffce7eba1ce6c6_s300x350.png")
    embed.add_field(name="Price:", value="700k", inline=True)
    embed.add_field(name="Delivery time:", value="1-4 Days", inline=True)
    embed.set_footer(text="Note: Having a character level 17-50 on any faction helps a lot.")
    await ctx.send(embed=embed)
    embed=discord.Embed(title="Warlords of Draenor rare mount", description="Bloodhoof Bulll - Great Greytusk - Mottled Meadowstomper - Sapphire Riverbeast - Sunhide Gronning - Swift Breezestrider", color=0x913801)
    embed.set_thumbnail(url="https://pngimg.com/uploads/warcraft/warcraft_PNG36.png")
    embed.add_field(name="Price:", value="50k each", inline=True)
    embed.add_field(name="Delivery time:", value="1-2 Days", inline=True)
    await ctx.send(embed=embed)


    # Elusive Quickhoof:

    embed=discord.Embed(title="Elusive Quickhoof", color=0x4b4f52)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/688836139922227237/854841243015839755/Untitled-3.png")
    embed.add_field(name="Price:", value="300k", inline=True)
    embed.add_field(name="Delivery time:", value="1-3 days", inline=True)
    await ctx.send(embed=embed)
    # Fabious:

    embed=discord.Embed(title="Fabious", color=0x7c88ba)
    embed.set_thumbnail(url="https://wow.zamimg.com/modelviewer/live/webthumbs/npc/192/88768.png")
    embed.add_field(name="Price:", value="600k", inline=True)
    embed.add_field(name="Delivery time:", value="1-7 Days", inline=True)
    embed.add_field(name="Note:", value="You NEED to have a selfie camera and have the Nazjatar zone unlocked", inline=True)
    await ctx.send(embed=embed)

    # Frightened Kodo:

    embed=discord.Embed(title="Frightened Kodo", color=0x6c5728)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/688836139922227237/854844474794311700/Untitled-4.png")
    embed.add_field(name="Price:", value="200k", inline=True)
    embed.add_field(name="Delivery time:", value="1-4 days", inline=True)
    await ctx.send(embed=embed)

    # Grey Riding Camel:

    embed=discord.Embed(title="Grey Riding Camel", color=0x595751)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/565143528393539594/854783223628300329/grey-riding-camel-fos1.png")
    embed.add_field(name="Price:", value="300k", inline=True)
    embed.add_field(name="Delivery time:", value="1-7 Days", inline=True)
    await ctx.send(embed=embed)


    # Long-Forgotten Hippogryph: 

    embed=discord.Embed(title="Long-Forgotten Hippogryh", color=0xa673a1)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/688836139922227237/854856641685225512/Untitled-5.png")
    embed.add_field(name="Price:", value="75k", inline=True)
    embed.add_field(name="Delivery time:", value="1-7 days", inline=True)
    await ctx.send(embed=embed)


    # Phosphorescent Stone Drake: (Check picture)

    embed=discord.Embed(title="Phosphorescent Stone Drake", color=0x874fda)
    embed.set_thumbnail(url="https://cdn.itemforge.com/catalog/product/cache/image/1000x1320/e9c3970ab036de70892d86c6d221abfe/p/h/phosphorescent-stone-drake.png")
    embed.add_field(name="Price:", value="350k", inline=True)
    embed.add_field(name="Delivery time:", value="1-7 Days", inline=True)
    await ctx.send(embed=embed)


    # Time-Lost Proto-Drake:

    embed=discord.Embed(title="Time-Lost Proto-Drake", color=0x735212)
    embed.set_thumbnail(url="https://wow.zamimg.com/modelviewer/live/webthumbs/npc/141/28045.webp")
    embed.add_field(name="Price:", value="450k", inline=True)
    embed.add_field(name="Delivery time:", value="1-7 Days", inline=True)
    await ctx.send(embed=embed)




    # Voidtalon:

    embed=discord.Embed(title="Voidtalon of the Dark Star", color=0x6826cb)
    embed.set_thumbnail(url="https://wow.zamimg.com/modelviewer/live/webthumbs/npc/129/38785.png")
    embed.add_field(name="Price:", value="700k", inline=True)
    embed.add_field(name="Delivery time:", value="1-4 Days", inline=True)
    embed.add_field(name="Note:", value="Having a character level 17-50 on any faction is a big help", inline=True)
    await ctx.send(embed=embed)


    # PvP Mounts:

    # Ashhide Mushan Beast – (EDIT THIS WITH A NOTE TEXT)
    # Ashide Mushan + “Fire-Watcher” Title

    embed=discord.Embed(title="Ashhide Mushan Beast and \"Fire-Watcher\" Title", color=0x3f2e29)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/688836139922227237/855097601119748116/Untitled-7.png")
    embed.add_field(name="Price for mount:", value="80k", inline=True)
    embed.add_field(name="Price for mount + Title", value="175k", inline=False)
    embed.add_field(name="Delivery time:", value="1-3 days", inline=False)
    await ctx.send(embed=embed)



    # Secret Mounts:

    # Fathom Dweller:

    embed=discord.Embed(title="Fathom Dweller", color=0x7060ae)
    embed.set_thumbnail(url="https://cdn.itemforge.com/catalog/product/cache/image/1000x1320/e9c3970ab036de70892d86c6d221abfe/f/a/fathom-dweller.png")
    embed.add_field(name="Price:", value="300k", inline=True)
    embed.add_field(name="Delivery time:", value="1-7 days", inline=True)
    await ctx.send(embed=embed)

    # Hivemind:

    embed=discord.Embed(title="The Hivemind", color=0x715d89)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/688836139922227237/855097602177630208/Untitled-8.png")
    embed.add_field(name="Price:", value="300k", inline=True)
    embed.add_field(name="Delivery time:", value="1-3 days", inline=True)
    await ctx.send(embed=embed)

    # Riddler’s Mind Worm: 

    embed=discord.Embed(title="Riddler's Mind Worm", color=0x2b4d69)
    embed.set_thumbnail(url="https://cdn.itemforge.com/catalog/product/cache/image/1000x1320/e9c3970ab036de70892d86c6d221abfe/r/i/riddlers-mind-worm.png")
    embed.add_field(name="Price:", value="300k", inline=True)
    embed.add_field(name="Delivery time:", value="1-4 days", inline=True)
    await ctx.send(embed=embed)

    # Smoldering Ember Wyrm:

    embed=discord.Embed(title="Smoldering Ember Wyrm", color=0xbb3d10)
    embed.set_thumbnail(url="https://static.boostbay.com/site/images/landing/common/first-block/wow/101_buy-smoldering-ember-wyrm_max.png")
    embed.add_field(name="Price:", value="150k", inline=True)
    embed.add_field(name="Delivery time:", value="1-2 days", inline=True)
    await ctx.send(embed=embed)


    # Zandalari Warbringers:
    # Amber Primordial Direhorn
    # Jade Primordial Direhorn
    # Slate Primordial Direhorn

    embed=discord.Embed(title="Zandalari Warbringers", description="Amber Primordial Direhorn - Jade Primordial Direhorn - Slate Primordial Direhorn", color=0x6a7a8f)
    embed.set_thumbnail(url="https://cdn.itemforge.com/catalog/product/cache/image/1000x1320/e9c3970ab036de70892d86c6d221abfe/s/l/slate-primordial-direhorn.png")
    embed.add_field(name="Price:", value="250k each or 650k for all 3", inline=True)
    embed.add_field(name="Delivery time:", value="1-7 days", inline=False)
    embed.add_field(name="Note:", value="Each mount have a 5% drop chance", inline=True)
    await ctx.send(embed=embed)


    # Netherwing Reputation:

    embed=discord.Embed(title="Netherwing Reputation", description="Azure Netherwing Drake - Cobalt Netherwing Drake - Onyx Netherwing Drake - Purple Netherwing Drake - Veridian Netherwing Drake - Violet Netherwing Drake", color=0x2c5f92)
    embed.set_thumbnail(url="https://cdn.itemforge.com/catalog/product/cache/image/1000x1320/e9c3970ab036de70892d86c6d221abfe/a/z/azure-netherwing-drake.png")
    embed.add_field(name="Price:", value="7.5k per Netherwing Egg or 800k from friendly to Exalted", inline=True)
    embed.add_field(name="Delivery time:", value="1-7 days", inline=False)
    embed.add_field(name="Note:", value="You need to have completed a short questline. The quest line is starting with the quest \"Kindness\"", inline=True)
    await ctx.send(embed=embed)

    # Miscellaneous Boosts:

    # Burgy Blackheart’s Handsome Hat Toy:

    embed=discord.Embed(title="Burgy Blackheart's Handsome Hat Toy", color=0x363c8c)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/688836139922227237/855101012539604992/Untitled-9.png")
    embed.add_field(name="Price", value="50k", inline=True)
    embed.add_field(name="Delivery time:", value="1-2 days", inline=True)
    await ctx.send(embed=embed)

    # Hunter Pets:

    embed=discord.Embed(title="Hunter pets", color=0xa7cd71)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/688836139922227237/855101004448792586/Untitled-10.png")
    embed.add_field(name="Price:", value="75k", inline=True)
    embed.add_field(name="Delivery time:", value="1-3 days", inline=False)
    await ctx.send(embed=embed)

    # Springfur Alpaca:

    embed=discord.Embed(title="Springfur Alpaca", color=0x9b7c58)
    embed.set_thumbnail(url="https://cdn.itemforge.com/catalog/product/cache/image/1000x1320/e9c3970ab036de70892d86c6d221abfe/s/p/springfur-alpaca.png")
    embed.add_field(name="Price:", value="400k", inline=True)
    embed.add_field(name="Delivery time:", value="7 days", inline=True)
    embed.add_field(name="Note:", value="This takes 7 days to obtain. ~20 min per day", inline=True)
    await ctx.send(embed=embed)


async def start_bot():
    pool = await aiomysql.create_pool(host=DB_HOST, port=3306,
                            user=DB_USER, password=DB_PASSWORD,
                            db=DB_DATABASE, autocommit=True)

    bot.pool = pool
    await bot.start(token)

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
except Exception as e:
    logger.warning("Exception raised from main thread.")
    logger.exception(e)
