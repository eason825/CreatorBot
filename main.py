import requests
import discord
import asyncio
import keep_alive
from discord.ext import tasks
from utils.paginator import Paginator
import json
from discord.app_commands import Group, command
from discord.ext import commands
from discord.ext.commands import GroupCog

import time
import os

creator_id = "" #put creator id here
account_id = "" # your account id
device_id = "" # device auths id
secret = "" # device auths secret
discord_channel_id_updates = ""
discord_channel_id_ccu = ""
color = 0xFFFFFF

intents = discord.Intents.all()
intents.message_content = True

client = commands.Bot(command_prefix="burgr ", intents=intents)



@client.event
async def on_ready():
  rename_channel_task.start()
  map_updates.start()
  print(f'Client logged in as {client.user}')
  await client.change_presence(activity=discord.Streaming(name="Flipping Burgers At Durrr Burger", url="https://www.youtube.com/"))



@tasks.loop(minutes=5)
async def rename_channel_task():
  plays = get_creators_island_codes_ccu(creator_id=creator_id)

  channel = client.get_channel(int(discord_channel_id_ccu))

  if channel:
    await channel.edit(name=f"Current Players: {plays}")

@tasks.loop(minutes=5)
async def map_updates():
  
  await check_for_updates()


async def check_for_updates():
  new_islands = get_creators_islands_bulk(creator_id)
  with open("islandData.json") as f:
    islandData = json.load(f)
    
  for island in islandData:
    for islandnew in new_islands:
      if islandnew['mnemonic'] == island['mnemonic']:
        if island['version'] != islandnew['version']:
          channel = client.get_channel(int(discord_channel_id_updates))
          await channel.send(f"{islandnew['metadata']['title']} ({islandnew['mnemonic']}) has been updated from {island['version']} -> {islandnew['version']}")
  with open("islandData.json", "w") as fw:
    json.dump(new_islands, fw, indent=2)
    

def get_token(account_id: str, device_id: str, secret: str):
  headers = {
    "Content-Type":
    "application/x-www-form-urlencoded",
    "Authorization":
    "basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE="
  }
  data = f"grant_type=device_auth&account_id={account_id}&device_id={device_id}&secret={secret}"

  r = requests.post(
    "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token",
    headers=headers,
    data=data)
  data = r.json()
  return data["access_token"]




def get_creators_islands_bulk(creator_id):
  islands = []
  bearer_token = get_token(account_id, device_id, secret)
  headers = {"Authorization": f"Bearer {bearer_token}"}
  response = requests.get(
    "https://fn-service-discovery-live-public.ogs.live.on.epicgames.com/api/v1/creator/page/10b1afef509b4f1e80ff79f6b4f5097f?playerId=efe82613b7d44105b86c02c8c421a98a&limit=100",
    headers=headers)

  response_data = response.json()

  islnds = []
  for island in response_data['links']:
    islnds.append({
                "mnemonic": island['linkCode'],
                "filter": False,
                "v": ""
            })

  bulk_req = requests.post(
    f"https://links-public-service-live.ol.epicgames.com/links/api/fn/mnemonic?ignoreFailures=true",
    headers=headers,
    json=islnds)
  bulk_data = bulk_req.json()

  with open("testing.json", "w") as fw:
    json.dump(bulk_data, fw, indent=2)
  return bulk_data


def get_creators_island_codes_ccu(creator_id):
  bearer_token = get_token(account_id, device_id, secret)
  headers = {"Authorization": f"Bearer {bearer_token}"}
  response = requests.get(
    "https://fn-service-discovery-live-public.ogs.live.on.epicgames.com/api/v1/creator/page/10b1afef509b4f1e80ff79f6b4f5097f?playerId=efe82613b7d44105b86c02c8c421a98a&limit=100",
    headers=headers)

  response_data = response.json()

  #with open("islandData.json", "w") as f:
    #json.dump(response_data, f, indent=2)

  ccu = 0
  for island in response_data['links']:
    if island['globalCCU'] == -1:
      pass
    else:
      ccu += island['globalCCU']


  return ccu


import typing


@client.command()
async def sync(
    ctx: commands.Context,
    guilds: commands.Greedy[discord.Object],
    spec: typing.Optional[typing.Literal["~", "*", "^"]] = None) -> None:

  if not guilds:
    if spec == "~":
      synced = await ctx.bot.tree.sync(guild=ctx.guild)
    elif spec == "*":
      ctx.bot.tree.copy_global_to(guild=ctx.guild)
      synced = await ctx.bot.tree.sync(guild=ctx.guild)
    elif spec == "^":
      ctx.bot.tree.clear_commands(guild=ctx.guild)
      await ctx.bot.tree.sync(guild=ctx.guild)
      synced = []
    else:
      synced = await ctx.bot.tree.sync()

    await ctx.send(
      f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
    )
    return

  ret = 0
  for guild in guilds:
    try:
      await ctx.bot.tree.sync(guild=guild)
    except discord.HTTPException:
      pass
    else:
      ret += 1

  await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


@pixel_commands.command(description="Search For Creator Maps")
async def islands(ctx):
  await ctx.response.defer()
  discovered_maps = []

  #token_ref = get_token(account_id, device_id, secret)

  islands = get_creators_islands_bulk(creator_id)
  
  pages = []

  for island in islands:
    embed = discord.Embed(title=island['metadata']['title'],
                          description=island['metadata']['tagline'],
                          color=color)
    embed.add_field(name="Creator", value=island['creatorName'])
    embed.add_field(name="Island Code", value=island['mnemonic'])
    #embed.add_field(name="XP Status", value=island['xpStatus'])
    embed.set_image(url=island['metadata']['image_url'])

    pages.append(embed)

  pager = Paginator(pages)
  await pager.start(ctx)


client.run("")
