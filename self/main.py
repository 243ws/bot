import discord
import os
import json
import random
from discord.ext import commands
import re

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True
intents.reactions = True  # This is now valid, no need for message_reactions

bot = commands.Bot(command_prefix="!", intents=intents)
OWNER_ID = 1250150003301945464  # Replace with your Discord ID
whitelisted_users = [OWNER_ID]  # Initial whitelisted user (owner)
responses_file = "responses.json"
react_users = {}  # Tracks users to react to
stop_react_users = set()
afk_status = {}  # Stores AFK statuses for users
deleted_messages = {}  # Stores the last deleted message for each channel

# Load responses from a JSON file
if os.path.exists(responses_file):
    with open(responses_file, "r") as file:
        responses = json.load(file)
else:
    responses = [
        "shut up {user}",
        "bro idk u {user}",
        "uh can u stop talking to me {user}",
        "only almighty owns me. who is {user}",
        "yo slit ur wrist {user}",
        "u stink {user}",
        "fatso speaking in chat btw {user}",
        "random {user}",
        "hahaha u wish u were known like me {user}",
        "im not a bot ur dumb {user}",
        "yo {user}"
    ]

def save_responses():
    with open(responses_file, "w") as file:
        json.dump(responses, file, indent=4)

# Helper Functions
def is_owner(ctx):
    return ctx.author.id == OWNER_ID

def is_whitelisted(user_id):
    return user_id in whitelisted_users

# Events
@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Managing Emojis & Reactions"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # React to messages for users in react_users
    if message.author.id in react_users:
        if message.author.id not in stop_react_users:
            emojis = react_users[message.author.id]
            for emoji in emojis[:3]:  # Add up to 3 emojis
                try:
                    await message.add_reaction(emoji)
                except discord.errors.HTTPException as e:
                    print(f"Error adding reaction: {e}")

    # Respond to mentions with a random response
    if bot.user in message.mentions:
        response = random.choice(responses).format(user=message.author.mention)
        await message.channel.send(response)

    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    """Store the last deleted message in the channel."""
    if message.channel not in deleted_messages:
        deleted_messages[message.channel] = []
    deleted_messages[message.channel].append(message.content)

# Commands
@bot.command()
async def stealemoji(ctx, emoji: str):
    """Steal a custom emoji and show it as PNG or GIF depending on the emoji type."""
    if not emoji:
        await ctx.send("Please provide an emoji.")
        return

    # Extract emoji ID from the string
    emoji_id = re.search(r'\d+', emoji)
    if not emoji_id:
        await ctx.send("Invalid emoji format.")
        return

    emoji_id = emoji_id.group(0)

    # Check if the emoji is animated or static
    if emoji.startswith("<a:"):  # Animated emoji
        emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.gif"
        emoji_type = "GIF"
    else:  # Static emoji
        emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
        emoji_type = "Image (PNG)"

    # Send the emoji information along with the image
    embed = discord.Embed(title="Custom Emoji Information", color=0x1a1a1a)
    embed.add_field(name="Name", value=emoji)
    embed.add_field(name="ID", value=emoji_id)
    embed.add_field(name="Direct Link", value=emoji_url)
    embed.add_field(name="Emoji Type", value=emoji_type)

    embed.set_image(url=emoji_url)

    await ctx.send(embed=embed)

@bot.command()
async def emojisteal(ctx, emoji: str):
    """Display information about the emoji and show it as either PNG or GIF."""
    if not emoji:
        await ctx.send("Please provide an emoji.")
        return

    # Extract emoji ID from the string
    emoji_id = re.search(r'\d+', emoji)
    if not emoji_id:
        await ctx.send("Invalid emoji format.")
        return

    emoji_id = emoji_id.group(0)

    # Check if the emoji is animated or static
    if emoji.startswith("<a:"):  # Animated emoji
        emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.gif"
        emoji_type = "GIF"
    else:  # Static emoji
        emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
        emoji_type = "Image (PNG)"

    # Send the emoji information along with the image
    embed = discord.Embed(title="Custom Emoji Information", color=0x1a1a1a)
    embed.add_field(name="Name", value=emoji)
    embed.add_field(name="ID", value=emoji_id)
    embed.add_field(name="Direct Link", value=emoji_url)
    embed.add_field(name="Type", value=emoji_type)

    embed.set_image(url=emoji_url)

    await ctx.send(embed=embed)

@bot.command()
async def pfp(ctx, member: discord.Member = None):
    """Fetch a user's profile picture."""
    member = member or ctx.author
    pfp_url = member.avatar.url
    embed = discord.Embed(title=f"{member.name}'s Profile Picture", color=0x1a1a1a)
    embed.set_image(url=pfp_url)
    await ctx.send(embed=embed)

@bot.command()
async def banner(ctx, member: discord.Member = None):
    """Fetch a user's banner."""
    member = member or ctx.author
    if member.banner:
        banner_url = member.banner.url
        embed = discord.Embed(title=f"{member.name}'s Banner", color=0x1a1a1a)
        embed.set_image(url=banner_url)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"{member.name} does not have a banner.")

@bot.command()
async def reactuser(ctx, user: discord.User, *emojis: str):
    """React to a user's messages with up to 3 emojis at once."""
    if len(emojis) > 3:
        await ctx.send("You can only add up to 3 emojis.")
        return

    # Ensure the emojis are valid
    valid_emojis = []
    for emoji in emojis:
        if re.match(r'^[^\u0000-\u007F]*$', emoji):  # Check for valid emoji character
            valid_emojis.append(emoji)
        else:
            await ctx.send(f"Sorry {ctx.author.mention}, looks like I'm not in the server where the emoji is located.")
            return

    # Store the emojis for reacting
    react_users[user.id] = valid_emojis
    await ctx.send(f"Will react to {user.name}'s messages with {', '.join(valid_emojis)}!")

@bot.command()
async def stopreact(ctx):
    """Stop reacting to a user's messages. Only the bot owner can use this."""
    if not is_owner(ctx):
        await ctx.send(f"Sorry {ctx.author.mention}, you do not have permission to use this command.")
        return

    # Stop reacting to users' messages
    react_users.clear()
    await ctx.send("Stopped reacting to all users' messages.")

@bot.command()
async def whitelist(ctx):
    """Show the list of whitelisted users."""
    if not is_owner(ctx):
        await ctx.send(f"Sorry {ctx.author.mention}, you do not have permission to use this command.")
        return

    # Display the list of whitelisted users in a rich presence format
    embed = discord.Embed(title="Whitelisted Users", description="Here are the whitelisted users:", color=0x1a1a1a)
    embed.add_field(name="Whitelisted Users", value="\n".join([f"<@{user_id}>" for user_id in whitelisted_users]), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def whitelist_add(ctx, user: discord.User):
    """Add a user to the whitelist."""
    if not is_owner(ctx):
        await ctx.send(f"Sorry {ctx.author.mention}, you do not have permission to use this command.")
        return

    if user.id not in whitelisted_users:
        whitelisted_users.append(user.id)
        await ctx.send(f"{user.mention} has been added to the whitelist.")
    else:
        await ctx.send(f"{user.mention} is already on the whitelist.")

@bot.command()
async def whitelist_remove(ctx, user: discord.User):
    """Remove a user from the whitelist."""
    if not is_owner(ctx):
        await ctx.send(f"Sorry {ctx.author.mention}, you do not have permission to use this command.")
        return

    if user.id in whitelisted_users:
        whitelisted_users.remove(user.id)
        await ctx.send(f"{user.mention} has been removed from the whitelist.")
    else:
        await ctx.send(f"{user.mention} is not on the whitelist.")

@bot.command()
async def afk(ctx, *, status: str = "AFK"):
    """Set your AFK status."""
    afk_status[ctx.author.id] = status
    await ctx.send(f"{ctx.author.mention} is now AFK: {status}")

@bot.command()
async def snipe(ctx):
    """Get the last deleted message in the current channel."""
    if ctx.channel in deleted_messages and deleted_messages[ctx.channel]:
        last_deleted = deleted_messages[ctx.channel].pop()
        await ctx.send(f"Last deleted message: {last_deleted}")
    else:
        await ctx.send("No deleted messages in this channel.")

@bot.command()
async def acmds(ctx):
    """Show command list with rich presence."""
    embed = discord.Embed(title="Available Commands", description="Here are the commands you can use with this bot:", color=0x1a1a1a)

    embed.add_field(name=" <a:EG_aRealDiamond:1166733408605585408> **General Commands**", value="!pfp [@user | user_id] - Fetch a user's profile picture\n!banner [@user | user_id] - Fetch a user's banner\n!acmds - Show command list\n!stealemoji [emoji] - Get custom emoji info\n!afk [status] - Set your AFK status\n!snipe - Get last deleted message", inline=False)
    embed.add_field(name="<a:Black_Verification:1080255403788615801> **For Admins and Whitelisted Users Only**", value="!reactuser @user emoji1 [emoji2] - React to a user's messages with up to 2 emojis\n!stopreact - Stop reacting to a user's messages", inline=False)
    embed.add_field(name="<a:CROWN10:1166731837071171634> **Owner Commands**", value="!newchat text - Add a new response to bot mentions", inline=False)

    # Set a larger image below the text
    embed.set_image(url="https://i.pinimg.com/originals/eb/ab/65/ebab65c5cecc362803578a077b66703b.gif")

    # Add small text at the bottom about the bot creator
    embed.set_footer(text="Bot made by Almighty")

    await ctx.send(embed=embed)

# Run the bot
token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise ValueError("No bot token provided!")

bot.run(token)
