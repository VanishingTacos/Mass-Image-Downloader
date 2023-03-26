# Import the required modules
import discord

# from discord.ext import commands
from discord import app_commands

# import asyncio
import requests
import traceback
import os
import shutil
import json
from urllib.parse import urlparse


class aclint(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=guild_id))
            self.synced = True
        print(f"We have logged in as {self.user}")


client = aclint()
tree = app_commands.CommandTree(client)


@tree.command(
    name="mmd",
    description="Mass media downloader",
    guild=discord.Object(id=guild_id),
)
async def self(interaction: discord.Interaction, message_id: str):
    with open("usage.json", "r") as useage_json:
        read = json.load(useage_json)
    useage_json.close()
    if read["usage"] < 10:
        # get message using message_id
        get_channel = interaction.channel
        get_message = await get_channel.fetch_message(message_id)
        index = 1
        try:
            await interaction.response.defer(thinking=True)
            if get_message.attachments != []:
                for url in get_message.attachments:
                    r = requests.get(url)
                    path = urlparse(str(url)).path
                    extension = os.path.splitext(path)[1]
                    with open(
                        os.path.join("./images", "image" + str(index) + extension), "wb"
                    ) as f:
                        f.write(r.content)
                    index = index + 1
                shutil.make_archive("images", "zip", "./images")
                try:
                    packet_size = 7340032
                    file_size = os.path.getsize("images.zip")

                    if file_size > packet_size:
                        with open("images.zip", "rb") as split:
                            filecount = 0
                            while True:
                                data = split.read(packet_size)
                                if not data:
                                    break
                                with open(
                                    "{}{:03}".format("images.zip.", filecount), "wb"
                                ) as packet:
                                    packet.write(data)
                                    filecount = filecount + 1
                        await interaction.followup.send(
                            content="Total downloaded amount had exceeded 8MB. I have split "
                            + str(index - 1)
                            + " files into "
                            + str(filecount)
                            + " chunks."
                        )
                        for i in range(filecount):
                            await interaction.followup.send(
                                file=discord.File(
                                    "images.zip.00" + str(i),
                                )
                            )
                            os.remove("images.zip.00" + str(i))
                    elif file_size < packet_size:
                        await interaction.followup.send(
                            content="Zipped "
                            + str(index - 1)
                            + " images for easy downloading!",
                            file=discord.File(r"images.zip"),
                        )
                    os.remove("images.zip")
                    for i in os.listdir("images"):
                        os.remove(os.path.join("images", i))

                    read["usage"] = read["usage"] + 1

                    with open("usage.json", "w") as usage_json:
                        json.dump(read, usage_json)
                    usage_json.close()

                except:
                    traceback.print_exc()
            else:
                await interaction.followup.send(
                    content="Message does not contain any attachments!"
                )
        except:
            traceback.print_exc()
    elif read["usage"] >= 10:
        await interaction.followup.send(
            content="Sorry the max amount of download has been reached today! Please try again tomorrow."
        )


client.run(TOKEN)
