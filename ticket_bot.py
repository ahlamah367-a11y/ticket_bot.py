import discord
from discord.ext import commands
from discord import app_commands

import json
import os
from datetime import datetime, timedelta
import asyncio
import random


# ==================================
# ط¥ط¹ط¯ط§ط¯ ط§ظ„ط¨ظˆطھ
# ==================================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


GUILD_ID = 1532326696714240062


# ==================================
# ظ‚ط§ط¹ط¯ط© ط§ظ„ط¨ظٹط§ظ†ط§طھ ظˆط¥ط¹ط¯ط§ط¯ط§طھظ‡ط§
# ==================================

DATABASE_FILE = "tickets_database.json"
BACKUP_FILE = "tickets_backup.json"


def default_ticket():

    return {
        "name": "طھط°ظƒط±ط© ط¬ط¯ظٹط¯ط©",
        "description": "ط§ط¶ط؛ط· ظ„ظپطھط­ ط§ظ„طھط°ظƒط±ط©",
        "panel_description": "ط§ط¶ط؛ط· ظ„ظپطھط­ ط§ظ„طھط°ظƒط±ط©",
        "emoji": "ًںژ«",
        "color": "blue",
        "welcome_message": "ط£ظ‡ظ„ط§ظ‹ {user} ًں‘‹\nط³ظٹطھظ… ط§ظ„ط±ط¯ ط¹ظ„ظٹظƒ ظ‚ط±ظٹط¨ط§ظ‹.",
        "ticket_image": None,
        "image": None,
        "open_category": None,
        "close_category": None,
        "staff_roles": [],
        "blocked_roles": [],
        "blocked_role": None,
        "open_logs": None,
        "close_logs": None,
        "rating_room": None,
        "claim": True,
        "rating": True,
        "transcript": True,
        "ask_reason": False,
        "max_tickets": 1,
        "prevent_same_type": True,
        "counter": 0,
        "opened": 0,
        "closed": 0,
        "ratings": [],
        "priority": "normal",
        "auto_close": False,
        "auto_close_time": 24,
        "notes": [],
        "added_members": [],
        "last_activity": None
    }



def default_database():

    return {
        "tickets": {},
        "panel": {
            "title": "ًںژ« ظ†ط¸ط§ظ… ط§ظ„طھط°ط§ظƒط±",
            "description": "ط§ط®طھط± ظ†ظˆط¹ ط§ظ„طھط°ظƒط±ط© ظ…ظ† ط§ظ„ظ‚ط§ط¦ظ…ط© ط¨ط§ظ„ط£ط³ظپظ„",
            "image": None,
            "channel": None,
            "message_id": None
        },
        "open_tickets": {},
        "closed_today": 0,
        "stats": {
            "total_opened": 0,
            "total_closed": 0,
            "tickets_today": 0,
            "daily_opened": {},
            "daily_closed": {},
            "ratings": [],
            "staff": {},
            "logs": [],
            "permissions": {
                "managers": [],
                "setup_admins": []
            }
        },
        "auto_setup": {}
    }



def load_database():

    if not os.path.exists(DATABASE_FILE):
        return default_database()

    with open(DATABASE_FILE, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except:
            return default_database()



try:
    database = load_database()
except:
    database = default_database()
    save_database = lambda: open(DATABASE_FILE, "w", encoding="utf-8").write(json.dumps(database, indent=4, ensure_ascii=False))
    save_database()



def save_database():

    with open(DATABASE_FILE, "w", encoding="utf-8") as file:
        json.dump(
            database,
            file,
            indent=4,
            ensure_ascii=False
        )



# ==================================
# ط£ط¯ظˆط§طھ ظ…ط³ط§ط¹ط¯ط© ظˆطھطµظ…ظٹظ… ظ…ظˆط­ط¯
# ==================================

def make_embed(title, description, color=discord.Color.blue()):

    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now()
    )

    embed.set_footer(
        text="ًںژ« Professional Ticket System"
    )

    return embed



def is_manager(user):
    if user.guild_permissions.administrator:
        return True
    return user.id in database["stats"]["permissions"]["managers"]



def create_ticket_id():

    number = len(database["tickets"]) + 1
    return f"ticket_{number}"



def get_ticket(ticket_id):

    return database["tickets"].get(ticket_id)



def get_ticket_from_channel(channel_id):

    return database["open_tickets"].get(str(channel_id))



def check_staff(interaction):

    ticket = get_ticket_from_channel(interaction.channel.id)

    if not ticket:
        return False

    settings = database["tickets"].get(ticket["type"])

    if not settings:
        return False

    staff_roles = settings.get("staff_roles", [])
    
    if is_manager(interaction.user):
        return True

    user_roles = [role.id for role in interaction.user.roles]

    for role in staff_roles:
        if role in user_roles:
            return True

    return False


print("âœ… ط§ظ„ط£ط¬ط²ط§ط، ط§ظ„ط£ط³ط§ط³ظٹط© ظˆظ‚ظˆط§ط¹ط¯ ط§ظ„ط¨ظٹط§ظ†ط§طھ ط¬ط§ظ‡ط²ط©")


# ==================================
# ط¥ظ†ط´ط§ط، ط£ظ†ظˆط§ط¹ ط§ظ„طھط°ط§ظƒط± ظˆط§ظ„ط£ظˆط§ظ…ط± ط§ظ„ط¥ط¯ط§ط±ظٹط© (ظ…ط¹ ط­ظ…ط§ظٹط© ط§ظ„ظ…ط´ط±ظپظٹظ†)
# ==================================

@bot.tree.command(
    name="reload-data",
    description="ط¥ط¹ط§ط¯ط© طھط­ظ…ظٹظ„ ظ‚ط§ط¹ط¯ط© ط§ظ„ط¨ظٹط§ظ†ط§طھ"
)
async def reload_data(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "â‌Œ ظ„ظ„ظ…ط´ط±ظپظٹظ† ظپظ‚ط·",
            ephemeral=True
        )
        return

    global database
    database = load_database()

    await interaction.response.send_message(
        "âœ… طھظ… طھط­ط¯ظٹط« ط§ظ„ط¨ظٹط§ظ†ط§طھ",
        ephemeral=True
    )



@bot.tree.command(
    name="backup-tickets",
    description="ط¹ظ…ظ„ ظ†ط³ط®ط© ط§ط­طھظٹط§ط·ظٹط©"
)
async def backup_tickets(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "â‌Œ ظ„ظ„ظ…ط´ط±ظپظٹظ† ظپظ‚ط·",
            ephemeral=True
        )
        return

    filename = f"backup-{datetime.now().strftime('%Y-%m-%d')}.json"

    with open(filename,"w",encoding="utf-8") as f:
        json.dump(
            database,
            f,
            indent=4,
            ensure_ascii=False
        )

    await interaction.response.send_message(
        "âœ… طھظ… ط¥ظ†ط´ط§ط، ظ†ط³ط®ط© ط§ط­طھظٹط§ط·ظٹط©",
        file=discord.File(filename),
        ephemeral=True
    )



@bot.tree.command(
    name="restore-backup",
    description="ط§ط³طھط±ط¬ط§ط¹ ظ†ط³ط®ط© ط§ط­طھظٹط§ط·ظٹط©"
)
async def restore_backup(interaction:discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "â‌Œ ظ„ظ„ظ…ط´ط±ظپظٹظ† ظپظ‚ط·",
            ephemeral=True
        )
        return

    global database

    if not os.path.exists(BACKUP_FILE):
        await interaction.response.send_message(
            "â‌Œ ظ„ط§ ظٹظˆط¬ط¯ ظ†ط³ط®ط© ط§ط­طھظٹط§ط·ظٹط©",
            ephemeral=True
        )
        return

    with open(BACKUP_FILE, "r", encoding="utf-8") as file:
        database = json.load(file)

    await interaction.response.send_message(
        embed=make_embed(
            "âœ… طھظ… ط§ظ„ط§ط³طھط±ط¬ط§ط¹",
            "طھظ… ط§ط³طھط±ط¬ط§ط¹ ظ‚ط§ط¹ط¯ط© ط¨ظٹط§ظ†ط§طھ ط§ظ„طھط°ط§ظƒط± ط¨ظ†ط¬ط§ط­.",
            discord.Color.green()
        ),
        ephemeral=True
    )



@bot.tree.command(
    name="add-manager",
    description="ط¥ط¶ط§ظپط© ظ…ط¯ظٹط± ظ„ظ†ط¸ط§ظ… ط§ظ„طھط°ط§ظƒط±"
)
@app_commands.describe(
    member="ط§ظ„ط¹ط¶ظˆ"
)
async def add_manager(
    interaction: discord.Interaction,
    member: discord.Member
):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "â‌Œ ظ„ظ„ظ…ط´ط±ظپظٹظ† ظپظ‚ط·",
            ephemeral=True
        )
        return

    database["stats"]["permissions"]["managers"].append(
        member.id
    )

    save_database()

    database["stats"]["logs"].append({
        "user": str(interaction.user.id),
        "action": f"ط£ط¶ط§ظپ ط§ظ„ظ…ط¯ظٹط± {member.id}",
        "time": str(datetime.now())
    })

    await interaction.response.send_message(
        embed=make_embed(
            "ًں‘‘ طھظ… ط¥ط¶ط§ظپط© ظ…ط¯ظٹط±",
            f"{member.mention} ط£طµط¨ط­ ظ…ط¯ظٹط± ظ†ط¸ط§ظ… ط§ظ„طھط°ط§ظƒط±.",
            discord.Color.green()
        )
    )



@bot.tree.command(
    name="ticket-auto-setup",
    description="ط¥ط¹ط¯ط§ط¯ ظ†ط¸ط§ظ… ط§ظ„طھط°ط§ظƒط± طھظ„ظ‚ط§ط¦ظٹط§ظ‹"
)
async def ticket_auto_setup(
    interaction: discord.Interaction
):

    if not is_manager(interaction.user):
        await interaction.response.send_message(
            "â‌Œ ظ„ط§ طھظ…ظ„ظƒ طµظ„ط§ط­ظٹط©",
            ephemeral=True
        )
        return

    guild = interaction.guild

    open_category = await guild.create_category(
        "ًںژ« ط§ظ„طھط°ط§ظƒط± ط§ظ„ظ…ظپطھظˆط­ط©"
    )

    close_category = await guild.create_category(
        "ًں”’ ط§ظ„طھط°ط§ظƒط± ط§ظ„ظ…ط؛ظ„ظ‚ط©"
    )

    logs = await guild.create_text_channel(
        "ًں“œ-ticket-logs"
    )

    database["panel"]["channel"] = logs.id

    database["auto_setup"] = {
        "open_category": open_category.id,
        "close_category": close_category.id,
        "logs": logs.id
    }

    save_database()

    await interaction.response.send_message(
        embed=make_embed(
            "âœ… طھظ… ط§ظ„ط¥ط¹ط¯ط§ط¯",
            "طھظ… ط¥ظ†ط´ط§ط، ظ†ط¸ط§ظ… ط§ظ„طھط°ط§ظƒط± ط¨ط§ظ„ظƒط§ظ…ظ„.",
            discord.Color.green()
        ),
        ephemeral=True
    )



@bot.tree.command(
    name="ticket-system-info",
    description="ظ…ط¹ظ„ظˆظ…ط§طھ ط§ظ„ظ†ط¸ط§ظ…"
)
async def ticket_system_info(
    interaction: discord.Interaction
):

    embed = make_embed(
        "ًں¤– ط­ط§ظ„ط© ط§ظ„ظ†ط¸ط§ظ…",
        ""
    )

    embed.add_field(
        name="ًںژ« ط£ظ†ظˆط§ط¹ ط§ظ„طھط°ط§ظƒط±",
        value=str(len(database["tickets"]))
    )

    embed.add_field(
        name="ًں“‚ ط§ظ„طھط°ط§ظƒط± ط§ظ„ظ…ظپطھظˆط­ط©",
        value=str(len(database["open_tickets"]))
    )

    embed.add_field(
        name="ًں‘‘ ط§ظ„ظ…ط¯ط±ط§ط،",
        value=str(len(database["stats"]["permissions"]["managers"]))
    )

    await interaction.response.send_message(
        embed=embed
    )



@bot.tree.command(
    name="dashboard",
    description="ظ„ظˆط­ط© ط¥ط­طµط§ط¦ظٹط§طھ ط§ظ„طھط°ط§ظƒط±"
)
async def dashboard(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "â‌Œ ظ„ظ„ظ…ط´ط±ظپظٹظ† ظپظ‚ط·",
            ephemeral=True
        )
        return

    stats = database["stats"]

    embed = discord.Embed(
        title="ًں“ٹ ظ„ظˆط­ط© ط§ظ„طھط­ظƒظ…",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="ًںژ« ط¥ط¬ظ…ط§ظ„ظٹ ط§ظ„ظپطھط­",
        value=str(stats["total_opened"])
    )

    embed.add_field(
        name="ًں”’ ط¥ط¬ظ…ط§ظ„ظٹ ط§ظ„ط¥ط؛ظ„ط§ظ‚",
        value=str(stats["total_closed"])
    )

    embed.add_field(
        name="ًں‘‘ ط¹ط¯ط¯ ط§ظ„ط¥ط¯ط§ط±ظٹظٹظ†",
        value=str(len(stats["staff"]))
    )

    embed.set_footer(
        text="Ticket System Professional"
    )

    await interaction.response.send_message(
        embed=embed
    )



@bot.tree.command(
    name="ticket-create",
    description="ط¥ظ†ط´ط§ط، ظ†ظˆط¹ طھط°ظƒط±ط© ط¬ط¯ظٹط¯"
)
@app_commands.describe(
    name="ط§ط³ظ… ط§ظ„طھط°ظƒط±ط©",
    description="ظˆطµظپ ط§ظ„طھط°ظƒط±ط© ظپظٹ ط§ظ„ط¨ط§ظ†ظ„"
)
async def ticket_create(
    interaction: discord.Interaction,
    name: str,
    description: str
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("â‌Œ ظ‡ط°ط§ ط§ظ„ط£ظ…ط± ظ…ط®طµطµ ظ„ظ„ظ…ط´ط±ظپظٹظ† ظپظ‚ط·", ephemeral=True)
        return

    ticket_id = create_ticket_id()

    database["tickets"][ticket_id] = default_ticket()
    database["tickets"][ticket_id]["name"] = name
    database["tickets"][ticket_id]["description"] = description
    database["tickets"][ticket_id]["panel_description"] = description

    save_database()

    await interaction.response.send_message(
        f"âœ… طھظ… ط¥ظ†ط´ط§ط، ظ†ظˆط¹ طھط°ظƒط±ط© ط¬ط¯ظٹط¯\nًںژ« ط§ظ„ط§ط³ظ…: {name}\nًں†” ط§ظ„ظ…ط¹ط±ظپ: `{ticket_id}`",
        ephemeral=True
    )



@bot.tree.command(
    name="ticket-delete",
    description="ط­ط°ظپ ظ†ظˆط¹ طھط°ظƒط±ط©"
)
@app_commands.describe(
    ticket_id="ظ…ط¹ط±ظپ ط§ظ„طھط°ظƒط±ط©"
)
async def ticket_delete(
    interaction: discord.Interaction,
    ticket_id: str
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("â‌Œ ظ‡ط°ط§ ط§ظ„ط£ظ…ط± ظ…ط®طµطµ ظ„ظ„ظ…ط´ط±ظپظٹظ† ظپظ‚ط·", ephemeral=True)
        return

    if ticket_id not in database["tickets"]:
        await interaction.response.send_message("â‌Œ ظ‡ط°ط§ ط§ظ„ظ†ظˆط¹ ط؛ظٹط± ظ…ظˆط¬ظˆط¯", ephemeral=True)
        return

    del database["tickets"][ticket_id]
    save_database()

    await interaction.response.send_message("âœ… طھظ… ط­ط°ظپ ظ†ظˆط¹ ط§ظ„طھط°ظƒط±ط©", ephemeral=True)



@bot.tree.command(
    name="tickets-list",
    description="ط¹ط±ط¶ ط£ظ†ظˆط§ط¹ ط§ظ„طھط°ط§ظƒط±"
)
async def tickets_list(
    interaction: discord.Interaction
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("â‌Œ ظ‡ط°ط§ ط§ظ„ط£ظ…ط± ظ…ط®طµطµ ظ„ظ„ظ…ط´ط±ظپظٹظ† ظپظ‚ط·", ephemeral=True)
        return

    if not database["tickets"]:
        await interaction.response.send_message("â‌Œ ظ„ط§ ظٹظˆط¬ط¯ ط£ظ†ظˆط§ط¹ طھط°ط§ظƒط± ط­ط§ظ„ظٹط§ظ‹", ephemeral=True)
        return

    embed = discord.Embed(
        title="ًںژ« ط£ظ†ظˆط§ط¹ ط§ظ„طھط°ط§ظƒط±",
        color=discord.Color.blue()
    )

    for ticket_id, data in database["tickets"].items():
        embed.add_field(
            name=f"{data['emoji']} {data['name']}",
            value=f"ًں†” `{ticket_id}`\nًں“‌ {data.get('description', data.get('panel_description', ''))}",
            inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)



@bot.tree.command(
    name="ticket-copy",
    description="ظ†ط³ط® ط¥ط¹ط¯ط§ط¯ط§طھ طھط°ظƒط±ط© ظ…ظˆط¬ظˆط¯ط© ط¨ط§ظ„ظƒط§ظ…ظ„"
)
@app_commands.describe(
    ticket_id="ظ…ط¹ط±ظپ ط§ظ„طھط°ظƒط±ط© ط§ظ„ظ…ط±ط§ط¯ ظ†ط³ط®ظ‡ط§"
)
async def ticket_copy(
    interaction: discord.Interaction,
    ticket_id: str
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("â‌Œ ظ‡ط°ط§ ط§ظ„ط£ظ…ط± ظ…ط®طµطµ ظ„ظ„ظ…ط´ط±ظپظٹظ† ظپظ‚ط·", ephemeral=True)
        return

    original_ticket = get_ticket(ticket_id)
    if not original_ticket:
        await interaction.response.send_message("â‌Œ ط§ظ„طھط°ظƒط±ط© ط§ظ„ظ…ط±ط§ط¯ ظ†ط³ط®ظ‡ط§ ط؛ظٹط± ظ…ظˆط¬ظˆط¯ط©", ephemeral=True)
        return

    new_id = create_ticket_id()
    copied_data = json.loads(json.dumps(original_ticket))
    copied_data["name"] = f"{copied_data['name']} (ظ†ط³ط®ط©)"
    copied_data["counter"] = 0
    copied_data["opened"] = 0
    copied_data["closed"] = 0
    copied_data["ratings"] = []

    database["tickets"][new_id] = copied_data
    save_database()

    await interaction.response.send_message(f"âœ… طھظ… ظ†ط³ط® ط§ظ„طھط°ظƒط±ط© ط¨ظ†ط¬ط§ط­!\nًں†” ط§ظ„ظ…ط¹ط±ظپ ط§ظ„ط¬ط¯ظٹط¯: `{new_id}`", ephemeral=True)



@bot.tree.command(
    name="ticket-rename-type",
    description="طھط؛ظٹظٹط± ط§ط³ظ… ظ†ظˆط¹ ط§ظ„طھط°ظƒط±ط©"
)
@app_commands.describe(
    ticket_id="ظ…ط¹ط±ظپ ط§ظ„طھط°ظƒط±ط©",
    new_name="ط§ظ„ط§ط³ظ… ط§ظ„ط¬ط¯ظٹط¯"
)
async def ticket_rename_type(
    interaction: discord.Interaction,
    ticket_id: str,
    new_name: str
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("â‌Œ ظ‡ط°ط§ ط§ظ„ط£ظ…ط± ظ…ط®طµطµ ظ„ظ„ظ…ط´ط±ظپظٹظ† ظپظ‚ط·", ephemeral=True)
        return

    ticket = get_ticket(ticket_id)

    if not ticket:
        await interaction.response.send_message("â‌Œ ط§ظ„طھط°ظƒط±ط© ط؛ظٹط± ظ…ظˆط¬ظˆط¯ط©", ephemeral=True)
        return

    ticket["name"] = new_name
    save_database()

    await interaction.response.send_message("âœ… طھظ… طھط؛ظٹظٹط± ط§ظ„ط§ط³ظ…", ephemeral=True)


# ==================================
# ط¥ط¹ط¯ط§ط¯ط§طھ ط§ظ„ط¨ط§ظ†ظ„ ظˆط§ظ„ظ…ظˆط¯ط§ظ„
# ==================================

class PanelSettingsModal(discord.ui.Modal):

    def __init__(self, option):
        super().__init__(title="طھط¹ط¯ظٹظ„ ط§ظ„ط¨ط§ظ†ظ„")
        self.option = option

        self.value = discord.ui.TextInput(
            label="ط§ظ„ظ‚ظٹظ…ط© ط§ظ„ط¬ط¯ظٹط¯ط©",
            placeholder="ط§ظƒطھط¨ ط§ظ„طھط¹ط¯ظٹظ„ ظ‡ظ†ط§",
            required=True,
            max_length=500
        )
        self.add_item(self.value)

    async def on_submit(self, interaction: discord.Interaction):
        value = self.value.value

        if self.option == "title":
            database["panel"]["title"] = value
        elif self.option == "description":
            database["panel"]["description"] = value
        elif self.option == "image":
            database["panel"]["image"] = value

        save_database()
        await interaction.response.send_message("âœ… طھظ… طھط¹ط¯ظٹظ„ ط§ظ„ط¨ط§ظ†ظ„", ephemeral=True)



class PanelSettingsView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="ط¥ط¹ط¯ط§ط¯ط§طھ ط§ظ„ط¨ط§ظ†ظ„",
        options=[
            discord.SelectOption(label="طھط¹ط¯ظٹظ„ ط¹ظ†ظˆط§ظ† ط§ظ„ط¨ط§ظ†ظ„", value="title", emoji="âœڈï¸ڈ"),
            discord.SelectOption(label="طھط¹ط¯ظٹظ„ ظˆطµظپ ط§ظ„ط¨ط§ظ†ظ„", value="description", emoji="ًں“‌"),
            discord.SelectOption(label="ط¥ط¶ط§ظپط© طµظˆط±ط© ظ„ظ„ط¨ط§ظ†ظ„", value="image", emoji="ًں–¼ï¸ڈ")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_modal(PanelSettingsModal(select.values[0]))



@bot.tree.command(
    name="panel-setup",
    description="طھط¹ط¯ظٹظ„ ط¥ط¹ط¯ط§ط¯ط§طھ ط§ظ„ط¨ط§ظ†ظ„ ط§ظ„ظ…ظˆط­ط¯"
)
async def panel_setup(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("â‌Œ ظ‡ط°ط§ ط§ظ„ط£ظ…ط± ظ…ط®طµطµ ظ„ظ„ظ…ط´ط±ظپظٹظ† ظپظ‚ط·", ephemeral=True)
        return

    embed = discord.Embed(
        title="ًں–¥ï¸ڈ ط¥ط¹ط¯ط§ط¯ ط§ظ„ط¨ط§ظ†ظ„",
        description="ط§ط®طھط± ط§ظ„ط´ظٹط، ط§ظ„ط°ظٹ طھط±ظٹط¯ طھط¹ط¯ظٹظ„ظ‡:\n\nâœڈï¸ڈ ط§ظ„ط¹ظ†ظˆط§ظ†\nًں“‌ ط§ظ„ظˆطµظپ\nًں–¼ï¸ڈ ط§ظ„طµظˆط±ط©",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, view=PanelSettingsView(), ephemeral=True)


# ==================================
# ط§ظ„ظ‚ظˆط§ط¦ظ… ظˆط§ظ„ط¨ط§ظ†ظ„ ط§ظ„ظ…ظˆط­ط¯
# ==================================

class TicketSelect(discord.ui.Select):

    def __init__(self):

        options = []

        for ticket_id, data in database["tickets"].items():

            options.append(
                discord.SelectOption(
                    label=data["name"],
                    value=ticket_id,
                    description=data.get(
                        "panel_description",
                        data.get("description", "ظپطھط­ طھط°ظƒط±ط©")
                    )[:100],
                    emoji=data.get("emoji", "ًںژ«")
                )
            )


        if not options:

            options.append(
                discord.SelectOption(
                    label="ظ„ط§ ظٹظˆط¬ط¯ طھط°ط§ظƒط±",
                    value="none",
                    emoji="â‌Œ"
                )
            )


        # ط®ظٹط§ط± طھط­ط¯ظٹط« ط§ظ„ظ…ظ†ظٹظˆ
        options.append(
            discord.SelectOption(
                label="ًں”„ طھط­ط¯ظٹط« ط§ظ„ظ‚ط§ط¦ظ…ط©",
                value="refresh_menu",
                description="ط¥ط¹ط§ط¯ط© طھط­ظ…ظٹظ„ ط£ظ†ظˆط§ط¹ ط§ظ„طھط°ط§ظƒط±",
                emoji="ًں”„"
            )
        )


        super().__init__(
            placeholder="ًںژ« ط§ط®طھط± ظ†ظˆط¹ ط§ظ„طھط°ظƒط±ط©",
            options=options,
            custom_id="ticket_select_menu_secure"
        )


    async def callback(self, interaction: discord.Interaction):

        ticket_type = self.values[0]


        # طھط­ط¯ظٹط« ط§ظ„ظ…ظ†ظٹظˆ
        if ticket_type == "refresh_menu":

            await interaction.response.edit_message(
                view=TicketPanel()
            )

            return



        if ticket_type == "none":

            await interaction.response.send_message(
                "â‌Œ ظ„ط§ ظٹظˆط¬ط¯ ط£ظ†ظˆط§ط¹ طھط°ط§ظƒط± ط­ط§ظ„ظٹط§",
                ephemeral=True
            )

            return



        user_id = interaction.user.id

        ticket_settings = database["tickets"].get(ticket_type)



        # ظ…ظ†ط¹ ظپطھط­ ط£ظƒط«ط± ظ…ظ† طھط°ظƒط±ط©
        for t in database["open_tickets"].values():

            if t.get("owner") == user_id:

                await interaction.response.send_message(
                    "â‌Œ ظ„ط¯ظٹظƒ طھط°ظƒط±ط© ظ…ظپطھظˆط­ط© ط¨ط§ظ„ظپط¹ظ„",
                    ephemeral=True
                )

                return



        # ط·ظ„ط¨ ط³ط¨ط¨
        if ticket_settings and ticket_settings.get("ask_reason"):

            await interaction.response.send_modal(
                TicketFormModal(ticket_type)
            )

            return



        await create_ticket(
            interaction,
            ticket_type,
            None
        )



# ==================================
# View ط§ظ„ط¨ط§ظ†ظ„
# ==================================

class TicketPanel(discord.ui.View):

    def __init__(self):

        super().__init__(timeout=None)

        self.add_item(
            TicketSelect()
        )



# ==================================
# ط£ظ…ط± ط¥ط±ط³ط§ظ„ ط§ظ„ط¨ط§ظ†ظ„
# ==================================

@bot.tree.command(
    name="send-ticket-panel",
    description="ط¥ط±ط³ط§ظ„ ط¨ط§ظ†ظ„ ط§ظ„طھط°ط§ظƒط± ط§ظ„ظ…ظˆط­ط¯"
)
async def send_ticket_panel(interaction: discord.Interaction):


    if not interaction.user.guild_permissions.administrator:

        await interaction.response.send_message(
            "â‌Œ ظ‡ط°ط§ ط§ظ„ط£ظ…ط± ظ„ظ„ظ…ط´ط±ظپظٹظ† ظپظ‚ط·",
            ephemeral=True
        )

        return



    await interaction.response.defer(
        ephemeral=True
    )



    panel = database["panel"]


    old_message_id = panel.get("message_id")



    if old_message_id:

        try:

            old_message = await interaction.channel.fetch_message(
                old_message_id
            )

            await old_message.delete()


        except:

            pass



    embed = discord.Embed(

        title=panel.get(
            "title",
            "ًںژ« ظ†ط¸ط§ظ… ط§ظ„طھط°ط§ظƒط±"
        ),

        description=panel.get(
            "description",
            "ط§ط®طھط± ظ†ظˆط¹ ط§ظ„طھط°ظƒط±ط© ظ…ظ† ط§ظ„ظ‚ط§ط¦ظ…ط©"
        ),

        color=discord.Color.blue()

    )



    if panel.get("image"):

        embed.set_image(
            url=panel["image"]
        )



    message = await interaction.channel.send(

        embed=embed,

        view=TicketPanel()

    )



    database["panel"]["message_id"] = message.id

    database["panel"]["channel"] = interaction.channel.id

    save_database()



    await interaction.followup.send(

        "âœ… طھظ… ط¥ط±ط³ط§ظ„ ط¨ط§ظ†ظ„ ط§ظ„طھط°ط§ظƒط±",

        ephemeral=True

    )
# ==================================
# ظ†ط¸ط§ظ… ظ†ظ…ط§ط°ط¬ ط§ظ„طھط°ط§ظƒط± (Ticket Forms)
# ==================================

class TicketFormModal(discord.ui.Modal):

    def __init__(self, ticket_type):
        super().__init__(title="ظ…ط¹ظ„ظˆظ…ط§طھ ظپطھط­ ط§ظ„طھط°ظƒط±ط©")
        self.ticket_type = ticket_type

        self.question1 = discord.ui.TextInput(
            label="ظ…ط§ط°ط§ طھط±ظٹط¯طں",
            placeholder="ط§ظƒطھط¨ ط·ظ„ط¨ظƒ ط¨ط§ظ„طھظپطµظٹظ„",
            required=True,
            max_length=300
        )

        self.question2 = discord.ui.TextInput(
            label="ط§ظ„طھظپط§طµظٹظ„ ط§ظ„ط¥ط¶ط§ظپظٹط©",
            placeholder="ط§ظƒطھط¨ ط£ظٹ ظ…ط¹ظ„ظˆظ…ط§طھ طھط³ط§ط¹ط¯ ط§ظ„ط¥ط¯ط§ط±ط©",
            required=False,
            max_length=300
        )

        self.add_item(self.question1)
        self.add_item(self.question2)


    async def on_submit(self, interaction: discord.Interaction):

        reason = (
            f"ًں“‌ ط§ظ„ط·ظ„ط¨:\n{self.question1.value}\n\n"
            f"ًں“Œ ط§ظ„طھظپط§طµظٹظ„:\n{self.question2.value}"
        )

        await create_ticket(
            interaction,
            self.ticket_type,
            reason
        )



@bot.tree.command(
    name="ticket-form",
    description="طھظپط¹ظٹظ„ ظ†ظ…ظˆط°ط¬ ط£ط³ط¦ظ„ط© ظ„ظ†ظˆط¹ طھط°ظƒط±ط©"
)
@app_commands.describe(
    ticket_id="ظ…ط¹ط±ظپ ظ†ظˆط¹ ط§ظ„طھط°ظƒط±ط©"
)
async def ticket_form(
    interaction: discord.Interaction,
    ticket_id: str
):

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "â‌Œ ظ‡ط°ط§ ط§ظ„ط£ظ…ط± ظ„ظ„ظ…ط´ط±ظپظٹظ† ظپظ‚ط·",
            ephemeral=True
        )
        return


    if ticket_id not in database["tickets"]:
        await interaction.response.send_message(
            "â‌Œ ظ†ظˆط¹ ط§ظ„طھط°ظƒط±ط© ط؛ظٹط± ظ…ظˆط¬ظˆط¯",
            ephemeral=True
        )
        return


    database["tickets"][ticket_id]["ask_reason"] = True

    save_database()


    await interaction.response.send_message(
        embed=make_embed(
            "âœ… طھظ… طھظپط¹ظٹظ„ ط§ظ„ظ†ظ…ظˆط°ط¬",
            f"طھظ… طھظپط¹ظٹظ„ ط£ط³ط¦ظ„ط© ط§ظ„ظپطھط­ ظ„ظ†ظˆط¹ ط§ظ„طھط°ظƒط±ط©:\nًںژ« {database['tickets'][ticket_id]['name']}",
            discord.Color.green()
        ),
        ephemeral=True
    )


# ==================================
# ظ†ط¸ط§ظ… ظپطھط­ ط§ظ„طھط°ط§ظƒط± ظˆط§ظ„طھط±ط§ظ†ط³ظƒط±ظٹط¨طھ
# ==================================

async def create_transcript(channel):
    messages = []
    async for message in channel.history(limit=None, oldest_first=True):
        timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
        author = f"{message.author.name}#{message.author.discriminator}" if message.author.discriminator != "0" else message.author.name
        avatar = message.author.display_avatar.url
        content = message.content or ""
        
        embeds_html = ""
        for embed in message.embeds:
            embeds_html += f"""
            <div style="background-color: #2f3136; border-left: 4px solid #7289da; padding: 10px; margin-top: 5px; border-radius: 4px;">
                <b style="color: #ffffff;">{embed.title or ''}</b>
                <p style="color: #dcddde; white-space: pre-wrap;">{embed.description or ''}</p>
            </div>
            """

        attachments_html = ""
        for att in message.attachments:
            attachments_html += f'<br><a href="{att.url}" target="_blank" style="color: #00b0f4;">ًں“ژ {att.filename}</a>'

        messages.append(f"""
        <div style="display: flex; margin-bottom: 15px; font-family: Arial, sans-serif;">
            <img src="{avatar}" style="width: 40px; height: 40px; border-radius: 50%; margin-right: 15px;">
            <div>
                <div><b>{author}</b> <span style="font-size: 11px; color: #72767d; margin-left: 5px;">{timestamp}</span></div>
                <div style="color: #dcddde; white-space: pre-wrap; margin-top: 2px;">{content}</div>
                {embeds_html}
                {attachments_html}
            </div>
        </div>
        """)

    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Transcript - {channel.name}</title>
    </head>
    <body style="background-color: #36393f; color: #dcddde; padding: 20px;">
        <h2 style="color: #ffffff; border-bottom: 1px solid #4f545c; padding-bottom: 10px;">ًں“œ ط³ط¬ظ„ ط§ظ„طھط°ظƒط±ط©: {channel.name}</h2>
        {"".join(messages)}
    </body>
    </html>
    """

    filename = f"transcript-{channel.id}.html"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)

    return filename



async def send_open_log(interaction, channel, ticket):
    settings = database["tickets"].get(ticket["type"])
    if not settings:
        return

    log_id = settings.get("open_logs")
    if not log_id:
        return

    log = interaction.guild.get_channel(log_id)
    if log:
        embed = discord.Embed(
            title="ًںژ« ظپطھط­ طھط°ظƒط±ط©",
            description=f"ًں‘¤ ط§ظ„ط¹ط¶ظˆ:\n{interaction.user.mention}\n\nًں“پ ط§ظ„ط±ظˆظ…:\n{channel.mention}",
            color=discord.Color.green()
        )
        await log.send(embed=embed)



async def send_close_log(interaction, channel, transcript):
    ticket = database["open_tickets"].get(str(channel.id))
    if not ticket:
        return

    settings = database["tickets"].get(ticket["type"])
    if not settings:
        return

    log_id = settings.get("close_logs")
    if not log_id:
        return

    log = interaction.guild.get_channel(log_id)
    if log:
        embed = discord.Embed(
            title="ًں”’ ط¥ط؛ظ„ط§ظ‚ طھط°ظƒط±ط©",
            description=f"ًں‘¤ ط£ط؛ظ„ظ‚ظ‡ط§:\n{interaction.user.mention}\n\nًں“پ ط§ظ„ط±ظˆظ…:\n{channel.name}",
            color=discord.Color.red()
        )
        await log.send(embed=embed)
        await log.send(file=discord.File(transcript))



async def create_ticket(interaction, ticket_type, reason=None):
    settings = database["tickets"].get(ticket_type)
    if not settings:
        if not interaction.response.is_done():
            await interaction.response.send_message("â‌Œ ظ†ظˆط¹ ط§ظ„طھط°ظƒط±ط© ط؛ظٹط± ظ…ظˆط¬ظˆط¯", ephemeral=True)
        return

    category_id = settings.get("open_category")
    category = interaction.guild.get_channel(category_id) if category_id else None

    settings["counter"] += 1
    number = settings["counter"]
    channel_name = f"{settings['emoji']}-ticket-{number}"

    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    }

    for role_id in settings.get("staff_roles", []):
        role = interaction.guild.get_role(role_id)
        if role:
            overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

    channel = await interaction.guild.create_text_channel(
        name=channel_name,
        category=category,
        overwrites=overwrites
    )

    database["open_tickets"][str(channel.id)] = {
        "owner": interaction.user.id,
        "user": str(interaction.user.id),
        "type": ticket_type,
        "created": str(datetime.now()),
        "claimed": None,
        "reason": reason,
        "closed": False,
        "priority": "normal",
        "last_activity": str(datetime.now()),
        "added_members": []
    }

    database["stats"]["total_opened"] += 1
    settings["opened"] += 1
    save_database()

    colors = {
        "blue": discord.Color.blue(),
        "red": discord.Color.red(),
        "green": discord.Color.green(),
        "gold": discord.Color.gold()
    }
    embed_color = colors.get(settings.get("color"), discord.Color.blue())

    welcome_text = settings.get("welcome_message", "ط£ظ‡ظ„ط§ظ‹ {user} ًں‘‹\nط³ظٹطھظ… ط§ظ„ط±ط¯ ط¹ظ„ظٹظƒ ظ‚ط±ظٹط¨ط§ظ‹.")
    embed = discord.Embed(
        title=f"{settings['emoji']} {settings['name']}",
        description=welcome_text.replace("{user}", interaction.user.mention),
        color=embed_color
    )

    embed.add_field(name="ًں‘¤ طµط§ط­ط¨ ط§ظ„طھط°ظƒط±ط©", value=interaction.user.mention, inline=False)
    embed.add_field(name="ًں”¢ ط±ظ‚ظ… ط§ظ„طھط°ظƒط±ط©", value=f"#{number}", inline=False)

    if reason:
        embed.add_field(name="ًں“‌ ط§ظ„ط³ط¨ط¨", value=reason, inline=False)

    if settings.get("ticket_image") or settings.get("image"):
        embed.set_image(url=settings.get("ticket_image") or settings.get("image"))

    embed.set_footer(text="ظ†ط¸ط§ظ… ط§ظ„طھط°ط§ظƒط± ط§ظ„ط§ط­طھط±ط§ظپظٹ")

    await channel.send(embed=embed, view=TicketButtons())
    await send_open_log(interaction, channel, database["open_tickets"][str(channel.id)])

    if not interaction.response.is_done():
        await interaction.response.send_message(f"âœ… طھظ… ظپطھط­ ط§ظ„طھط°ظƒط±ط© {channel.mention}", ephemeral=True)


# ==================================
# ط£ط²ط±ط§ط± ظˆط£ط¯ظˆط§طھ ط¯ط§ط®ظ„ ط§ظ„طھط°ظƒط±ط©
# ==================================

class TicketButtons(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Claim",
        emoji="ًں‘‘",
        style=discord.ButtonStyle.blurple,
        custom_id="claim_button_secure"
    )
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not check_staff(interaction):
            await interaction.response.send_message("â‌Œ ظ„ظٹط³ ظ„ط¯ظٹظƒ طµظ„ط§ط­ظٹط© ظ„ط§ط³طھظ„ط§ظ… ط§ظ„طھط°ظƒط±ط©", ephemeral=True)
            return

        ticket = database["open_tickets"].get(str(interaction.channel.id))
        if not ticket:
            await interaction.response.send_message("â‌Œ ط§ظ„طھط°ظƒط±ط© ط؛ظٹط± ظ…ظˆط¬ظˆط¯ط©", ephemeral=True)
            return

        if ticket.get("claimed"):
            await interaction.response.send_message(
                "âڑ ï¸ڈ ظ‡ط°ظ‡ ط§ظ„طھط°ظƒط±ط© طھظ… ط§ط³طھظ„ط§ظ…ظ‡ط§ ظ…ط³ط¨ظ‚ط§ظ‹",
                ephemeral=True
            )
            return

        ticket["claimed"] = interaction.user.id
        
        staff = str(interaction.user.id)
        if staff not in database["stats"]["staff"]:
            database["stats"]["staff"][staff] = {
                "claimed": 0,
                "closed": 0
            }
        database["stats"]["staff"][staff]["claimed"] += 1

        database["stats"]["logs"].append({
            "user": str(interaction.user.id),
            "action": "ط§ط³طھظ„ظ… ط§ظ„طھط°ظƒط±ط©",
            "time": str(datetime.now())
        })

        save_database()
        
        button.disabled = True
        await interaction.message.edit(view=self)

        embed = make_embed(
            "ًں‘‘ طھظ… ط§ط³طھظ„ط§ظ… ط§ظ„طھط°ظƒط±ط©",
            f"ط§ظ„ط¥ط¯ط§ط±ظٹ ط§ظ„ظ…ط³ط¤ظˆظ„ ط§ظ„ط¢ظ†:\n{interaction.user.mention}",
            discord.Color.gold()
        )
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message(f"ًں‘‘ طھظ… ط§ط³طھظ„ط§ظ… ط§ظ„طھط°ظƒط±ط© ط¨ظ†ط¬ط§ط­", ephemeral=True)

    @discord.ui.button(
        label="ط¥ط؛ظ„ط§ظ‚",
        emoji="ًں”’",
        style=discord.ButtonStyle.red,
        custom_id="close_button_secure"
    )
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not check_staff(interaction):
            await interaction.response.send_message("â‌Œ ظ„ظٹط³ ظ„ط¯ظٹظƒ طµظ„ط§ط­ظٹط©", ephemeral=True)
            return

        channel_id = str(interaction.channel.id)
        if channel_id in database["open_tickets"]:
            database["open_tickets"][channel_id]["closed"] = True
            
            staff = str(interaction.user.id)
            if staff not in database["stats"]["staff"]:
                database["stats"]["staff"][staff] = {"claimed": 0, "closed": 0}
            database["stats"]["staff"][staff]["closed"] += 1

            database["stats"]["logs"].append({
                "user": str(interaction.user.id),
                "action": "ط£ط؛ظ„ظ‚ ط§ظ„طھط°ظƒط±ط©",
                "time": str(datetime.now())
            })

        save_database()

        await interaction.response.send_message(
            "ًں”’ طھظ… طھط¬ظ‡ظٹط² ط¥ط؛ظ„ط§ظ‚ ط§ظ„طھط°ظƒط±ط©\nâ­گ ط§ط®طھط± طھظ‚ظٹظٹظ… ط§ظ„ط®ط¯ظ…ط©:",
            view=RatingView(interaction.channel.id),
            ephemeral=True
        )


# ==================================
# ظ†ط¸ط§ظ… ط§ظ„طھظ‚ظٹظٹظ… ظˆط§ظ„ط¥ط؛ظ„ط§ظ‚
# ==================================

class RatingView(discord.ui.View):

    def __init__(self, ticket_channel_id):
        super().__init__(timeout=None)
        self.ticket_channel_id = ticket_channel_id

    async def save_rating(self, interaction, stars):
        ticket = database["open_tickets"].get(str(self.ticket_channel_id))
        if not ticket:
            return

        ticket_type = ticket["type"]
        ticket_settings = database["tickets"].get(ticket_type)

        if ticket_settings:
            ticket_settings["ratings"].append({
                "user": str(interaction.user.id),
                "stars": stars,
                "staff": ticket.get("claimed")
            })

        save_database()
        await send_rating_log(interaction, stars, ticket)
        
        channel = interaction.channel
        
        close_cat_id = ticket_settings.get("close_category") if ticket_settings else None
        if close_cat_id:
            close_category = interaction.guild.get_channel(close_cat_id)
            if close_category:
                try:
                    await channel.edit(category=close_category)
                except:
                    pass

        transcript = await create_transcript(channel)
        await send_close_log(interaction, channel, transcript)

        await interaction.response.send_message("â­گ طھظ… ط­ظپط¸ طھظ‚ظٹظٹظ…ظƒ ط¨ظ†ط¬ط§ط­طŒ ط³ظٹطھظ… ط­ط°ظپ ط§ظ„ط±ظˆظ… ط®ظ„ط§ظ„ 3 ط«ظˆط§ظ†ظٹ...", ephemeral=True)
        
        await asyncio.sleep(3)
        try:
            await channel.delete()
        except:
            pass

    @discord.ui.button(label="â­گ", style=discord.ButtonStyle.gray, custom_id="rating_1_sec")
    async def one(self, interaction, button):
        await self.save_rating(interaction, 1)

    @discord.ui.button(label="â­گâ­گâ­گ", style=discord.ButtonStyle.blurple, custom_id="rating_3_sec")
    async def three(self, interaction, button):
        await self.save_rating(interaction, 3)

    @discord.ui.button(
        label="â­گâ­گâ­گâ­گ",
        style=discord.ButtonStyle.blurple,
        custom_id="rating_4_sec"
    )
    async def four(self, interaction, button):
        await self.save_rating(interaction, 4)

    @discord.ui.button(label="â­گâ­گâ­گâ­گâ­گ", style=discord.ButtonStyle.green, custom_id="rating_5_sec")
    async def five(self, interaction, button):
        await self.save_rating(interaction, 5)



async def send_rating_log(interaction, stars, ticket):
    ticket_type = database["tickets"].get(ticket["type"])
    if not ticket_type:
        return

    rating_room = ticket_type.get("rating_room")
    if not rating_room:
        return

    channel = interaction.guild.get_channel(rating_room)
    if not channel:
        return

    staff = ticket.get("claimed")
    staff_text = f"<@{staff}>" if staff else "ظ„ط§ ظٹظˆط¬ط¯"

    embed = discord.Embed(title="â­گ طھظ‚ظٹظٹظ… ط¬ط¯ظٹط¯", color=discord.Color.gold())
    embed.add_field(name="ًں‘¤ ط§ظ„ط¹ط¶ظˆ", value=interaction.user.mention, inline=False)
    embed.add_field(name="â­گ ط§ظ„طھظ‚ظٹظٹظ…", value=f"{stars}/5", inline=False)
    embed.add_field(name="ًں‘‘ ط§ظ„ط¥ط¯ط§ط±ظٹ ط§ظ„ظ…ط³طھظ„ظ…", value=staff_text, inline=False)

    await channel.send(embed=embed)


# ==================================
# ط£ظˆط§ظ…ط± ط§ظ„ط¥ط¯ط§ط±ط© ط¯ط§ط®ظ„ ط§ظ„طھط°ظƒط±ط©
# ==================================

@bot.tree.command(name="claim", description="ط§ط³طھظ„ط§ظ… ط§ظ„طھط°ظƒط±ط©")
async def claim_ticket(interaction: discord.Interaction):
    if not check_staff(interaction):
        await interaction.response.send_message("â‌Œ ظ„ظٹط³ ظ„ط¯ظٹظƒ طµظ„ط§ط­ظٹط© ظ„ط§ط³طھظ„ط§ظ… ط§ظ„طھط°ظƒط±ط©", ephemeral=True)
        return

    ticket = get_ticket_from_channel(interaction.channel.id)
    if not ticket:
        await interaction.response.send_message("â‌Œ ط§ظ„طھط°ظƒط±ط© ط؛ظٹط± ظ…ظˆط¬ظˆط¯ط©", ephemeral=True)
        return

    if ticket.get("claimed"):
        await interaction.response.send_message("âڑ ï¸ڈ ظ‡ط°ظ‡ ط§ظ„طھط°ظƒط±ط© طھظ… ط§ط³طھظ„ط§ظ…ظ‡ط§ ظ…ط³ط¨ظ‚ط§ظ‹", ephemeral=True)
        return

    ticket["claimed"] = interaction.user.id
    
    staff = str(interaction.user.id)
    if staff not in database["stats"]["staff"]:
        database["stats"]["staff"][staff] = {"claimed": 0, "closed": 0}
    database["stats"]["staff"][staff]["claimed"] += 1

    database["stats"]["logs"].append({
        "user": str(interaction.user.id),
        "action": "ط§ط³طھظ„ظ… ط§ظ„طھط°ظƒط±ط©",
        "time": str(datetime.now())
    })

    save_database()
    
    embed = make_embed(
        "ًں‘‘ طھظ… ط§ط³طھظ„ط§ظ… ط§ظ„طھط°ظƒط±ط©",
        f"ط§ظ„ط¥ط¯ط§ط±ظٹ ط§ظ„ظ…ط³ط¤ظˆظ„ ط§ظ„ط¢ظ†:\n{interaction.user.mention}",
        discord.Color.gold()
    )
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message(f"ًں‘‘ طھظ… ط§ط³طھظ„ط§ظ… ط§ظ„طھط°ظƒط±ط©", ephemeral=True)



@bot.tree.command(name="close", description="ط¥ط؛ظ„ط§ظ‚ ط§ظ„طھط°ظƒط±ط©")
async def close_ticket(interaction: discord.Interaction):
    if not check_staff(interaction):
        await interaction.response.send_message("â‌Œ ظ„ط§ طھظ…ظ„ظƒ طµظ„ط§ط­ظٹط©", ephemeral=True)
        return

    channel_id = str(interaction.channel.id)
    if channel_id in database["open_tickets"]:
        database["open_tickets"][channel_id]["closed"] = True
        
        staff = str(interaction.user.id)
        if staff not in database["stats"]["staff"]:
            database["stats"]["staff"][staff] = {"claimed": 0, "closed": 0}
        database["stats"]["staff"][staff]["closed"] += 1

        database["stats"]["logs"].append({
            "user": str(interaction.user.id),
            "action": "ط£ط؛ظ„ظ‚ ط§ظ„طھط°ظƒط±ط©",
            "time": str(datetime.now())
        })

    save_database()
    await interaction.response.send_message("â­گ ظٹط±ط¬ظ‰ طھظ‚ظٹظٹظ… ط§ظ„طھط°ظƒط±ط© ظ‚ط¨ظ„ ط§ظ„ط¥ط؛ظ„ط§ظ‚", view=RatingView(interaction.channel.id), ephemeral=True)



@bot.tree.command(name="rename", description="طھط؛ظٹظٹط± ط§ط³ظ… ط§ظ„طھط°ظƒط±ط©")
@app_commands.describe(name="ط§ظ„ط§ط³ظ… ط§ظ„ط¬ط¯ظٹط¯")
async def rename_ticket(interaction: discord.Interaction, name: str):
    if not check_staff(interaction):
        await interaction.response.send_message("â‌Œ ظ„ط§ طھظ…ظ„ظƒ طµظ„ط§ط­ظٹط©", ephemeral=True)
        return

    await interaction.channel.edit(name=name)
    database["stats"]["logs"].append({
        "user": str(interaction.user.id),
        "action": f"ط؛ظٹط± ط§ط³ظ… ط§ظ„طھط°ظƒط±ط© ط¥ظ„ظ‰ {name}",
        "time": str(datetime.now())
    })
    save_database()
    await interaction.response.send_message("âœ… طھظ… طھط؛ظٹظٹط± ط§ظ„ط§ط³ظ…")



@bot.tree.command(name="priority", description="طھط­ط¯ظٹط¯ ط£ظˆظ„ظˆظٹط© ط§ظ„طھط°ظƒط±ط©")
@app_commands.choices(
    level=[
        app_commands.Choice(name="ط¹ط§ط¯ظٹ", value="normal"),
        app_commands.Choice(name="ظ…ظ‡ظ…", value="important"),
        app_commands.Choice(name="ط¹ط§ط¬ظ„", value="urgent")
    ]
)
async def priority_ticket(interaction: discord.Interaction, level: app_commands.Choice[str]):
    if not check_staff(interaction):
        await interaction.response.send_message("â‌Œ ظ„ط§ طھظ…ظ„ظƒ طµظ„ط§ط­ظٹط©", ephemeral=True)
        return

    ticket = get_ticket_from_channel(interaction.channel.id)
    ticket["priority"] = level.value
    ticket["last_activity"] = str(datetime.now())
    save_database()
    await interaction.response.send_message(f"ًں“Œ طھظ… طھط؛ظٹظٹط± ط§ظ„ط£ظˆظ„ظˆظٹط© ط¥ظ„ظ‰: {level.name}")



@bot.tree.command(name="ticket-add", description="ط¥ط¶ط§ظپط© ط¹ط¶ظˆ ظ„ظ„طھط°ظƒط±ط©")
async def ticket_add(interaction: discord.Interaction, member: discord.Member):
    if not check_staff(interaction):
        await interaction.response.send_message("â‌Œ ظ„ط§ طھظ…ظ„ظƒ طµظ„ط§ط­ظٹط©", ephemeral=True)
        return

    await interaction.channel.set_permissions(member, view_channel=True, send_messages=True)
    await interaction.response.send_message(f"âœ… طھظ…طھ ط¥ط¶ط§ظپط© {member.mention}")



@bot.tree.command(name="ticket-remove", description="ط¥ط²ط§ظ„ط© ط¹ط¶ظˆ ظ…ظ† ط§ظ„طھط°ظƒط±ط©")
async def ticket_remove(interaction: discord.Interaction, member: discord.Member):
    if not check_staff(interaction):
        await interaction.response.send_message("â‌Œ ظ„ط§ طھظ…ظ„ظƒ طµظ„ط§ط­ظٹط©", ephemeral=True)
        return

    await interaction.channel.set_permissions(member, overwrite=None)
    await interaction.response.send_message(f"âœ… طھظ…طھ ط¥ط²ط§ظ„ط© {member.mention}")



@bot.tree.command(name="lock", description="ظ‚ظپظ„ ط§ظ„ظƒطھط§ط¨ط© ظپظٹ ط§ظ„طھط°ظƒط±ط©")
async def lock_ticket(interaction: discord.Interaction):
    if not check_staff(interaction):
        await interaction.response.send_message("â‌Œ ظ„ط§ طھظ…ظ„ظƒ طµظ„ط§ط­ظٹط©", ephemeral=True)
        return

    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("ًں”’ طھظ… ظ‚ظپظ„ ط§ظ„طھط°ظƒط±ط©")



@bot.tree.command(name="unlock", description="ظپطھط­ ط§ظ„ظƒطھط§ط¨ط© ظپظٹ ط§ظ„طھط°ظƒط±ط©")
async def unlock_ticket(interaction: discord.Interaction):
    if not check_staff(interaction):
        await interaction.response.send_message("â‌Œ ظ„ط§ طھظ…ظ„ظƒ طµظ„ط§ط­ظٹط©", ephemeral=True)
        return

    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("ًں”“ طھظ… ظپطھط­ ط§ظ„طھط°ظƒط±ط©")



@bot.tree.command(name="reopen", description="ط¥ط¹ط§ط¯ط© ظپطھط­ ط§ظ„طھط°ظƒط±ط©")
async def reopen_ticket(interaction: discord.Interaction):
    if not check_staff(interaction):
        await interaction.response.send_message("â‌Œ ظ„ط§ طھظ…ظ„ظƒ طµظ„ط§ط­ظٹط©", ephemeral=True)
        return

    await interaction.channel.set_permissions(interaction.guild.default_role, view_channel=True)
    await interaction.response.send_message("ًں”„ طھظ… ط¥ط¹ط§ط¯ط© ظپطھط­ ط§ظ„طھط°ظƒط±ط©")



@bot.tree.command(name="move", description="ظ†ظ‚ظ„ ط§ظ„طھط°ظƒط±ط©")
@app_commands.describe(category="ID ط§ظ„ظƒط§طھط¬ظˆط±ظٹ ط§ظ„ط¬ط¯ظٹط¯")
async def move_ticket(interaction: discord.Interaction, category: str):
    if not check_staff(interaction):
        await interaction.response.send_message("â‌Œ ظ„ط§ طھظ…ظ„ظƒ طµظ„ط§ط­ظٹط©", ephemeral=True)
        return

    try:
        category_id = int(category)
    except:
        await interaction.response.send_message("â‌Œ ID ط؛ظٹط± طµط­ظٹط­", ephemeral=True)
        return

    new_category = interaction.guild.get_channel(category_id)
    if not new_category:
        await interaction.response.send_message("â‌Œ ظ„ظ… ظٹطھظ… ط§ظ„ط¹ط«ظˆط± ط¹ظ„ظ‰ ط§ظ„ظƒط§طھط¬ظˆط±ظٹ", ephemeral=True)
        return

    await interaction.channel.edit(category=new_category)
    await interaction.response.send_message("ًںڑڑ طھظ… ظ†ظ‚ظ„ ط§ظ„طھط°ظƒط±ط©")



@bot.tree.command(
    name="auto-move",
    description="ظ†ظ‚ظ„ ط§ظ„طھط°ظƒط±ط© طھظ„ظ‚ط§ط¦ظٹط§ظ‹ ط¥ظ„ظ‰ ظƒط§طھط¬ظˆط±ظٹ"
)
@app_commands.describe(
    category="ID ط§ظ„ظƒط§طھط¬ظˆط±ظٹ"
)
async def auto_move(
    interaction: discord.Interaction,
    category: str
):
    if not check_staff(interaction):
        await interaction.response.send_message(
            "â‌Œ ظ„ط§ طھظ…ظ„ظƒ طµظ„ط§ط­ظٹط©",
            ephemeral=True
        )
        return

    try:
        category_id = int(category)
    except:
        await interaction.response.send_message(
            "â‌Œ ID ط؛ظٹط± طµط­ظٹط­",
            ephemeral=True
        )
        return

    new_category = interaction.guild.get_channel(category_id)

    if not new_category:
        await interaction.response.send_message(
            "â‌Œ ط§ظ„ظƒط§طھط¬ظˆط±ظٹ ط؛ظٹط± ظ…ظˆط¬ظˆط¯",
            ephemeral=True
        )
        return

    await interaction.channel.edit(
        category=new_category
    )

    embed = discord.Embed(
        title="ًںڑڑ طھظ… ظ†ظ‚ظ„ ط§ظ„طھط°ظƒط±ط©",
        description=f"طھظ… ظ†ظ‚ظ„ ط§ظ„طھط°ظƒط±ط© ط¥ظ„ظ‰:\n{new_category.name}",
        color=discord.Color.blue()
    )

    await interaction.response.send_message(
        embed=embed
    )



@bot.tree.command(
    name="ticket-info",
    description="ط¹ط±ط¶ ظ…ط¹ظ„ظˆظ…ط§طھ ط§ظ„طھط°ظƒط±ط© ط§ظ„ط­ط§ظ„ظٹط©"
)
async def ticket_info(interaction: discord.Interaction):

    ticket = get_ticket_from_channel(interaction.channel.id)

    if not ticket:
        await interaction.response.send_message(
            "â‌Œ ظ‡ط°ط§ ط§ظ„ط±ظˆظ… ظ„ظٹط³ طھط°ظƒط±ط©",
            ephemeral=True
        )
        return

    settings = database["tickets"].get(ticket["type"])

    embed = discord.Embed(
        title="ًںژ« ظ…ط¹ظ„ظˆظ…ط§طھ ط§ظ„طھط°ظƒط±ط©",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="ًں‘¤ طµط§ط­ط¨ ط§ظ„طھط°ظƒط±ط©",
        value=f"<@{ticket['owner']}>",
        inline=False
    )

    embed.add_field(
        name="ًں“پ ط§ظ„ظ†ظˆط¹",
        value=settings["name"] if settings else "ط؛ظٹط± ظ…ط¹ط±ظˆظپ",
        inline=False
    )

    embed.add_field(
        name="ًں‘‘ ط§ظ„ظ…ط³طھظ„ظ…",
        value=f"<@{ticket['claimed']}>" if ticket["claimed"] else "ظ„ط§ ظٹظˆط¬ط¯",
        inline=False
    )

    embed.add_field(
        name="ًں“Œ ط§ظ„ط£ظˆظ„ظˆظٹط©",
        value=ticket.get("priority","normal"),
        inline=False
    )

    embed.add_field(
        name="ًں“… ط§ظ„طھط§ط±ظٹط®",
        value=ticket.get("created","ط؛ظٹط± ظ…ط¹ط±ظˆظپ"),
        inline=False
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )



@bot.tree.command(
    name="ticket-note",
    description="ط¥ط¶ط§ظپط© ظ…ظ„ط§ط­ط¸ط© ظ„ظ„طھط°ظƒط±ط©"
)
@app_commands.describe(
    note="ط§ظ„ظ…ظ„ط§ط­ط¸ط©"
)
async def ticket_note(
    interaction: discord.Interaction,
    note: str
):

    if not check_staff(interaction):
        await interaction.response.send_message(
            "â‌Œ ظ„ظٹط³ ظ„ط¯ظٹظƒ طµظ„ط§ط­ظٹط©",
            ephemeral=True
        )
        return

    ticket = get_ticket_from_channel(interaction.channel.id)

    if not ticket:
        await interaction.response.send_message(
            "â‌Œ ظ„ظٹط³طھ طھط°ظƒط±ط©",
            ephemeral=True
        )
        return

    ticket.setdefault("notes", [])

    ticket["notes"].append({
        "staff": interaction.user.id,
        "note": note,
        "time": str(datetime.now())
    })

    save_database()

    await interaction.response.send_message(
        "âœ… طھظ… ط­ظپط¸ ط§ظ„ظ…ظ„ط§ط­ط¸ط©",
        ephemeral=True
    )



@bot.tree.command(
    name="ticket-notes",
    description="ط¹ط±ط¶ ظ…ظ„ط§ط­ط¸ط§طھ ط§ظ„طھط°ظƒط±ط©"
)
async def ticket_notes(interaction: discord.Interaction):

    ticket = get_ticket_from_channel(interaction.channel.id)

    if not ticket:
        await interaction.response.send_message(
            "â‌Œ ظ„ظٹط³طھ طھط°ظƒط±ط©",
            ephemeral=True
        )
        return

    notes = ticket.get("notes", [])

    if not notes:
        await interaction.response.send_message(
            "ًں“­ ظ„ط§ ظٹظˆط¬ط¯ ظ…ظ„ط§ط­ط¸ط§طھ",
            ephemeral=True
        )
        return

    text = ""

    for n in notes:
        text += f"ًں‘¤ <@{n['staff']}> : {n['note']}\n"

    embed = discord.Embed(
        title="ًں“‌ ظ…ظ„ط§ط­ط¸ط§طھ ط§ظ„طھط°ظƒط±ط©",
        description=text,
        color=discord.Color.gold()
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )



@bot.tree.command(name="ticket-stats", description="ط¥ط­طµط§ط¦ظٹط§طھ ط§ظ„طھط°ط§ظƒط±")
async def ticket_stats(interaction: discord.Interaction):
    if not check_staff(interaction):
        await interaction.response.send_message("â‌Œ ظ„ط§ طھظ…ظ„ظƒ طµظ„ط§ط­ظٹط©", ephemeral=True)
        return

    opened = len(database["open_tickets"])
    closed = database.get("closed_today", 0)

    embed = discord.Embed(title="ًں“ٹ ط¥ط­طµط§ط¦ظٹط§طھ ط§ظ„طھط°ط§ظƒط±", color=discord.Color.blue())
    embed.add_field(name="ًںژ« ط§ظ„ظ…ظپطھظˆط­ط©", value=str(opened))
    embed.add_field(name="ًں”’ ط§ظ„ظ…ط؛ظ„ظ‚ط©", value=str(closed))
    await interaction.response.send_message(embed=embed)


# ==================================
# ط¥ط¹ط¯ط§ط¯ط§طھ ط§ظ„طھط°ظƒط±ط© ط§ظ„ظ…ط®طµطµط©
# ==================================

class TicketSettingsModal(discord.ui.Modal):

    def __init__(self, ticket_id, option):
        super().__init__(title="طھط¹ط¯ظٹظ„ ط¥ط¹ط¯ط§ط¯ ط§ظ„طھط°ظƒط±ط©")
        self.ticket_id = ticket_id
        self.option = option

        self.value = discord.ui.TextInput(
            label="ط§ظ„ظ‚ظٹظ…ط© ط§ظ„ط¬ط¯ظٹط¯ط©",
            placeholder="ط§ظƒطھط¨ ط§ظ„ظ‚ظٹظ…ط© ط£ظˆ ID ظ‡ظ†ط§",
            required=True,
            max_length=4000
        )
        self.add_item(self.value)

    async def on_submit(self, interaction: discord.Interaction):
        ticket = database["tickets"][self.ticket_id]
        value = self.value.value

        if self.option == "name":
            ticket["name"] = value
        elif self.option == "description":
            ticket["description"] = value
            ticket["panel_description"] = value
        elif self.option == "emoji":
            ticket["emoji"] = value
        elif self.option == "color":
            ticket["color"] = value
        elif self.option == "welcome":
            ticket["welcome_message"] = value
        elif self.option == "image":
            ticket["ticket_image"] = value
            ticket["image"] = value
        elif self.option == "open_category":
            ticket["open_category"] = int(value)
        elif self.option == "close_category":
            ticket["close_category"] = int(value)
        elif self.option == "staff_role":
            ticket["staff_roles"].append(int(value))
        elif self.option == "remove_staff_role":
            role_id = int(value)
            if role_id in ticket["staff_roles"]:
                ticket["staff_roles"].remove(role_id)

        save_database()
        await interaction.response.send_message("âœ… طھظ… ط­ظپط¸ ط§ظ„طھط¹ط¯ظٹظ„", ephemeral=True)



class TicketSettingsView(discord.ui.View):

    def __init__(self, ticket_id):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id

    @discord.ui.select(
        placeholder="ط§ط®طھط± ط¥ط¹ط¯ط§ط¯ ظ„ظ„طھط¹ط¯ظٹظ„",
        options=[
            discord.SelectOption(label="ط§ط³ظ… ط§ظ„طھط°ظƒط±ط©", value="name", emoji="ًںڈ·ï¸ڈ"),
            discord.SelectOption(label="ظˆطµظپ ط§ظ„ط¨ط§ظ†ظ„", value="description", emoji="ًں“‌"),
            discord.SelectOption(label="ط¥ظٹظ…ظˆط¬ظٹ ط§ظ„طھط°ظƒط±ط©", value="emoji", emoji="ًںک€"),
            discord.SelectOption(label="ظ„ظˆظ† ط§ظ„طھط°ظƒط±ط©", value="color", emoji="ًںژ¨"),
            discord.SelectOption(label="ط±ط³ط§ظ„ط© ط§ظ„طھط±ط­ظٹط¨", value="welcome", emoji="ًں‘‹"),
            discord.SelectOption(label="طµظˆط±ط© ط¯ط§ط®ظ„ ط§ظ„طھط°ظƒط±ط©", value="image", emoji="ًں–¼ï¸ڈ"),
            discord.SelectOption(label="ظƒط§طھط¬ظˆط±ظٹ ط§ظ„ظپطھط­", value="open_category", emoji="ًں“‚"),
            discord.SelectOption(label="ظƒط§طھط¬ظˆط±ظٹ ط§ظ„ط¥ط؛ظ„ط§ظ‚", value="close_category", emoji="ًں”’"),
            discord.SelectOption(label="ط¥ط¶ط§ظپط© ط±طھط¨ط© ط¥ط¯ط§ط±ط©", value="staff_role", emoji="ًں›،ï¸ڈ"),
            discord.SelectOption(label="ط¥ط²ط§ظ„ط© ط±طھط¨ط© ط¥ط¯ط§ط±ط©", value="remove_staff_role", emoji="â‌Œ")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_modal(TicketSettingsModal(self.ticket_id, select.values[0]))



@bot.tree.command(name="ticket-settings", description="طھط¹ط¯ظٹظ„ ط¥ط¹ط¯ط§ط¯ط§طھ ظ†ظˆط¹ طھط°ظƒط±ط©")
@app_commands.describe(ticket_id="ظ…ط¹ط±ظپ ط§ظ„طھط°ظƒط±ط©")
async def ticket_settings(interaction: discord.Interaction, ticket_id: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("â‌Œ ظ‡ط°ط§ ط§ظ„ط£ظ…ط± ظ…ط®طµطµ ظ„ظ„ظ…ط´ط±ظپظٹظ† ظپظ‚ط·", ephemeral=True)
        return

    if ticket_id not in database["tickets"]:
        await interaction.response.send_message("â‌Œ ظ†ظˆط¹ ط§ظ„طھط°ظƒط±ط© ط؛ظٹط± ظ…ظˆط¬ظˆط¯", ephemeral=True)
        return

    embed = discord.Embed(
        title="âڑ™ï¸ڈ ط¥ط¹ط¯ط§ط¯ط§طھ ط§ظ„طھط°ظƒط±ط©",
        description=f"طھط¹ط¯ظٹظ„:\nًںژ« {database['tickets'][ticket_id]['name']}",
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed, view=TicketSettingsView(ticket_id), ephemeral=True)


# ==================================
# ظ†ط¸ط§ظ… ط§ظ„ط­ظ…ط§ظٹط© ظˆ Anti-Spam ظˆط§ظ„ط®ظ„ظپظٹط§طھ
# ==================================

spam_users = {}
SPAM_LIMIT = 5
SPAM_TIME = 5


async def anti_spam(message):
    user = message.author.id
    now = asyncio.get_event_loop().time()

    if user not in spam_users:
        spam_users[user] = []

    spam_users[user].append(now)

    spam_users[user] = [
        x for x in spam_users[user]
        if now - x <= SPAM_TIME
    ]

    if len(spam_users[user]) >= SPAM_LIMIT:
        try:
            await message.delete()
        except:
            pass

        embed = discord.Embed(
            title="âڑ ï¸ڈ ط­ظ…ط§ظٹط© ط§ظ„ط³ط¨ط§ظ…",
            description=f"{message.author.mention} طھظ… ظ…ظ†ط¹ ط§ظ„ط¥ط±ط³ط§ظ„ ط§ظ„ط³ط±ظٹط¹.",
            color=discord.Color.orange()
        )

        await message.channel.send(
            embed=embed,
            delete_after=5
        )

        spam_users[user] = []


AUTO_CLOSE_TIME = 24 * 60 * 60

async def auto_close_checker():
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.now()
        for channel_id, ticket in list(database["open_tickets"].items()):
            try:
                created = datetime.fromisoformat(ticket["created"])
                if (now - created).total_seconds() >= AUTO_CLOSE_TIME:
                    channel = bot.get_channel(int(channel_id))
                    if channel:
                        embed = discord.Embed(
                            title="ًں”’ ط¥ط؛ظ„ط§ظ‚ طھظ„ظ‚ط§ط¦ظٹ",
                            description="طھظ… ط¥ط؛ظ„ط§ظ‚ ط§ظ„طھط°ظƒط±ط© ط¨ط³ط¨ط¨ ط¹ط¯ظ… ط§ظ„ظ†ط´ط§ط· ظ„ظ…ط¯ط© 24 ط³ط§ط¹ط©.",
                            color=discord.Color.red()
                        )
                        await channel.send(embed=embed)
                        try:
                            await channel.delete()
                        except:
                            pass
                    del database["open_tickets"][channel_id]
                    save_database()
            except:
                pass
        await asyncio.sleep(300)


async def database_backup():
    await bot.wait_until_ready()
    while not bot.is_closed():
        with open(BACKUP_FILE, "w", encoding="utf-8") as file:
            json.dump(
                database,
                file,
                indent=4,
                ensure_ascii=False
            )
        await asyncio.sleep(3600)


@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    channel_id = message.channel.id
    if str(channel_id) in database["open_tickets"]:
        database["open_tickets"][str(channel_id)]["last_activity"] = str(datetime.now())
        save_database()

    await anti_spam(message)
    await bot.process_commands(message)



@bot.event
async def on_guild_channel_delete(channel):
    if str(channel.id) in database["open_tickets"]:
        database["open_tickets"].pop(str(channel.id))
        database["stats"]["total_closed"] += 1
        save_database()


# ==================================
# طھط´ط؛ظٹظ„ ط§ظ„ط¨ظˆطھ ظˆط§ط³طھظ‚ط±ط§ط± ط§ظ„ظ€ Persistent Views
# ==================================

@bot.event
async def on_ready():
    print(f"âœ… Bot Online: {bot.user}")
    
    bot.add_view(TicketPanel())
    bot.add_view(TicketButtons())
    
    for channel_id in database["open_tickets"]:
        bot.add_view(RatingView(int(channel_id)))

    bot.loop.create_task(auto_close_checker())
    bot.loop.create_task(database_backup())

    try:
        synced = await bot.tree.sync()
        print(f"âœ… Synced {len(synced)} Commands")
    except Exception as e:
        print(e)


TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("â‌Œ Token not found!")
