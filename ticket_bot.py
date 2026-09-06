import json
import os
import random
import asyncio
from datetime import datetime, timedelta
import discord
from discord import app_commands
from discord.ext import commands

# ==================================
# إعداد البوت
# ==================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1532326696714240062

# ==================================
# قاعدة البيانات وإعداداتها
# ==================================
# حفظ الملفات مباشرة في مجلد البوت الحالي
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(BASE_DIR, "tickets_database.json")
DATABASE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tickets_database.json")

def default_ticket():
    return {
        "name": "تذكرة جديدة",
        "description": "اضغط لفتح التذكرة",
        "panel_description": "اضغط لفتح التذكرة",
        "emoji": "🎫",
        "color": "blue",
        "welcome_message": "أهلاً {user} 👋\nسيتم الرد عليك قريباً.",
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
        "last_activity": None,
    }


def default_database():
    return {
        "tickets": {},
        "panel": {
            "title": "🎫 نظام التذاكر",
            "description": "اختر نوع التذكرة من القائمة بالأسفل",
            "image": None,
            "channel": None,
            "message_id": None,
        },
        "panels": {},
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
            "permissions": {"managers": [], "setup_admins": []},
        },
        "auto_setup": {},
    }


def save_database():
    with open(DATABASE_FILE, "w", encoding="utf-8") as file:
        json.dump(database, file, indent=4, ensure_ascii=False)


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

save_database()

# دعم البانلات المتعددة وربط كل بانل بتذاكره الخاصة
if "panels" not in database:
    database["panels"] = {}

for panel_id, panel in database["panels"].items():
    if "tickets" not in panel:
        panel["tickets"] = []

save_database()


# ==================================
# أدوات مساعدة وتصميم موحد
# ==================================
def make_embed(title, description, color=discord.Color.blue()):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now(),
    )
    embed.set_footer(text="🎫 Professional Ticket System")
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


print("✅ الأجزاء الأساسية وقواعد البيانات جاهزة")


# ==================================
# إنشاء أنواع التذاكر والأوامر الإدارية (مع حماية المشرفين)
# ==================================
@bot.tree.command(name="reload-data", description="إعادة تحميل قاعدة البيانات")
async def reload_data(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ للمشرفين فقط", ephemeral=True
        )
        return
    global database
    database = load_database()
    await interaction.response.send_message(
        "✅ تم تحديث البيانات", ephemeral=True
    )


@bot.tree.command(name="backup-tickets", description="عمل نسخة احتياطية")
async def backup_tickets(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ للمشرفين فقط", ephemeral=True
        )
        return
    filename = f"backup-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(database, f, indent=4, ensure_ascii=False)
    await interaction.response.send_message(
        "✅ تم إنشاء نسخة احتياطية",
        file=discord.File(filename),
        ephemeral=True,
    )


@bot.tree.command(name="restore-backup", description="استرجاع نسخة احتياطية")
async def restore_backup(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ للمشرفين فقط", ephemeral=True
        )
        return
    global database
    if not os.path.exists(BACKUP_FILE):
        await interaction.response.send_message(
            "❌ لا يوجد نسخة احتياطية", ephemeral=True
        )
        return
    with open(BACKUP_FILE, "r", encoding="utf-8") as file:
        database = json.load(file)
    await interaction.response.send_message(
        embed=make_embed(
            "✅ تم الاسترجاع",
            "تم استرجاع قاعدة بيانات التذاكر بنجاح.",
            discord.Color.green(),
        ),
        ephemeral=True,
    )


@bot.tree.command(name="add-manager", description="إضافة مدير لنظام التذاكر")
@app_commands.describe(member="العضو")
async def add_manager(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ للمشرفين فقط", ephemeral=True
        )
        return
    database["stats"]["permissions"]["managers"].append(member.id)
    save_database()
    database["stats"]["logs"].append(
        {
            "user": str(interaction.user.id),
            "action": f"أضاف المدير {member.id}",
            "time": str(datetime.now()),
        }
    )
    await interaction.response.send_message(
        embed=make_embed(
            "👑 تم إضافة مدير",
            f"{member.mention} أصبح مدير نظام التذاكر.",
            discord.Color.green(),
        )
    )


@bot.tree.command(
    name="ticket-auto-setup", description="إعداد نظام التذاكر تلقائياً"
)
async def ticket_auto_setup(interaction: discord.Interaction):
    if not is_manager(interaction.user):
        await interaction.response.send_message(
            "❌ لا تملك صلاحية", ephemeral=True
        )
        return
    guild = interaction.guild
    open_category = await guild.create_category("🎫 التذاكر المفتوحة")
    close_category = await guild.create_category("🔒 التذاكر المغلقة")
    logs = await guild.create_text_channel("📜-ticket-logs")

    database["panel"]["channel"] = logs.id
    database["auto_setup"] = {
        "open_category": open_category.id,
        "close_category": close_category.id,
        "logs": logs.id,
    }
    save_database()
    await interaction.response.send_message(
        embed=make_embed(
            "✅ تم الإعداد",
            "تم إنشاء نظام التذاكر بالكامل.",
            discord.Color.green(),
        ),
        ephemeral=True,
    )


@bot.tree.command(name="ticket-system-info", description="معلومات النظام")
async def ticket_system_info(interaction: discord.Interaction):
    embed = make_embed("🤖 حالة النظام", "")
    embed.add_field(
        name="🎫 أنواع التذاكر", value=str(len(database["tickets"]))
    )
    embed.add_field(
        name="📂 التذاكر المفتوحة", value=str(len(database["open_tickets"]))
    )
    embed.add_field(
        name="👑 المدراء",
        value=str(len(database["stats"]["permissions"]["managers"])),
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="dashboard", description="لوحة إحصائيات التذاكر")
async def dashboard(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ للمشرفين فقط", ephemeral=True
        )
        return
    stats = database["stats"]
    embed = discord.Embed(title="📊 لوحة التحكم", color=discord.Color.gold())
    embed.add_field(name="🎫 إجمالي الفتح", value=str(stats["total_opened"]))
    embed.add_field(name="🔒 إجمالي الإغلاق", value=str(stats["total_closed"]))
    embed.add_field(name="👑 عدد الإداريين", value=str(len(stats["staff"])))
    embed.set_footer(text="Ticket System Professional")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="ticket-create", description="إنشاء نوع تذكرة جديد")
@app_commands.describe(
    name="اسم التذكرة", description="وصف التذكرة في البانل"
)
async def ticket_create(
    interaction: discord.Interaction, name: str, description: str
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ هذا الأمر مخصص للمشرفين فقط", ephemeral=True
        )
        return
    ticket_id = create_ticket_id()
    database["tickets"][ticket_id] = default_ticket()
    database["tickets"][ticket_id]["name"] = name
    database["tickets"][ticket_id]["description"] = description
    database["tickets"][ticket_id]["panel_description"] = description
    save_database()
    await interaction.response.send_message(
        f"✅ تم إنشاء نوع تذكرة جديد\n🎫 الاسم: {name}\n🆔 المعرف: `{ticket_id}`",
        ephemeral=True,
    )


@bot.tree.command(name="ticket-delete", description="حذف نوع تذكرة")
@app_commands.describe(ticket_id="معرف التذكرة")
async def ticket_delete(interaction: discord.Interaction, ticket_id: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ هذا الأمر مخصص للمشرفين فقط", ephemeral=True
        )
        return
    if ticket_id not in database["tickets"]:
        await interaction.response.send_message(
            "❌ هذا النوع غير موجود", ephemeral=True
        )
        return
    del database["tickets"][ticket_id]

    # إزالة التذكرة من جميع البانلات التي كانت تحتوي عليها
    for panel_id, panel in database.get("panels", {}).items():
        if ticket_id in panel.get("tickets", []):
            panel["tickets"].remove(ticket_id)
            try:
                await refresh_panel_message(interaction.guild, panel_id)
            except:
                pass
    save_database()
    await interaction.response.send_message(
        "✅ تم حذف نوع التذكرة", ephemeral=True
    )


@bot.tree.command(name="tickets-list", description="عرض أنواع التذاكر")
async def tickets_list(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ هذا الأمر مخصص للمشرفين فقط", ephemeral=True
        )
        return
    if not database["tickets"]:
        await interaction.response.send_message(
            "❌ لا يوجد أنواع تذاكر حالياً", ephemeral=True
        )
        return
    embed = discord.Embed(title="🎫 أنواع التذاكر", color=discord.Color.blue())
    for ticket_id, data in database["tickets"].items():
        embed.add_field(
            name=f"{data['emoji']} {data['name']}",
            value=f"🆔 `{ticket_id}`\n📜 {data.get('description', data.get('panel_description', ''))}",
            inline=False,
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(
    name="ticket-copy", description="نسخ إعدادات تذكرة موجودة بالكامل"
)
@app_commands.describe(ticket_id="معرف التذكرة المراد نسخها")
async def ticket_copy(interaction: discord.Interaction, ticket_id: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ هذا الأمر مخصص للمشرفين فقط", ephemeral=True
        )
        return
    original_ticket = get_ticket(ticket_id)
    if not original_ticket:
        await interaction.response.send_message(
            "❌ التذكرة المراد نسخها غير موجودة", ephemeral=True
        )
        return
    new_id = create_ticket_id()
    copied_data = json.loads(json.dumps(original_ticket))
    copied_data["name"] = f"{copied_data['name']} (نسخة)"
    copied_data["counter"] = 0
    copied_data["opened"] = 0
    copied_data["closed"] = 0
    copied_data["ratings"] = []
    database["tickets"][new_id] = copied_data
    save_database()
    await interaction.response.send_message(
        f"✅ تم نسخ التذكرة بنجاح!\n🆔 المعرف الجديد: `{new_id}`",
        ephemeral=True,
    )


@bot.tree.command(name="ticket-rename-type", description="تغيير اسم نوع التذكرة")
@app_commands.describe(ticket_id="معرف التذكرة", new_name="الاسم الجديد")
async def ticket_rename_type(
    interaction: discord.Interaction, ticket_id: str, new_name: str
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ هذا الأمر مخصص للمشرفين فقط", ephemeral=True
        )
        return
    ticket = get_ticket(ticket_id)
    if not ticket:
        await interaction.response.send_message(
            "❌ التذكرة غير موجودة", ephemeral=True
        )
        return
    ticket["name"] = new_name
    save_database()
    await interaction.response.send_message(
        "✅ تم تغيير الاسم", ephemeral=True
    )


# ==================================
# إعدادات البانل والمودال (البانلات المتعددة)
# ==================================
@bot.tree.command(name="add-ticket-panel", description="إنشاء بانل تذاكر جديد")
@app_commands.describe(
    title="عنوان البانل",
    description="وصف البانل",
    image="رابط صورة البانل - اختياري",
)
async def add_ticket_panel(
    interaction: discord.Interaction,
    title: str,
    description: str,
    image: str = None,
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ هذا الأمر للمشرفين فقط", ephemeral=True
        )
        return
    await interaction.response.defer(ephemeral=True)

    panel_number = 1
    while f"panel_{panel_number}" in database["panels"]:
        panel_number += 1
    panel_id = f"panel_{panel_number}"

    database["panels"][panel_id] = {
        "title": title,
        "description": description,
        "image": image,
        "channel": interaction.channel.id,
        "message_id": None,
        "created_by": interaction.user.id,
        "created_at": str(datetime.now()),
        "tickets": [],
    }
    save_database()

    embed = discord.Embed(
        title=title, description=description, color=discord.Color.blue()
    )
    if image:
        embed.set_image(url=image)

    message = await interaction.channel.send(
        embed=embed, view=TicketPanel(panel_id)
    )
    database["panels"][panel_id]["message_id"] = message.id
    save_database()

    await interaction.followup.send(
        embed=make_embed(
            "✅ تم إنشاء البانل",
            f"تم إنشاء البانل بنجاح.\n\n"
            f"🆔 **المعرف:** `{panel_id}`\n"
            f"📌 **البانل:** {message.jump_url}\n\n"
            f"🎫 حالياً لا توجد تذاكر داخل هذا البانل.\n"
            f"استخدم `/panel-add-ticket` لإضافة تذكرة إليه.",
            discord.Color.green(),
        ),
        ephemeral=True,
    )


@bot.tree.command(name="panels-list", description="عرض جميع بانلات التذاكر")
async def panels_list(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ هذا الأمر للمشرفين فقط", ephemeral=True
        )
        return
    if not database.get("panels"):
        await interaction.response.send_message(
            "❌ لا يوجد أي بانلات حالياً", ephemeral=True
        )
        return
    embed = discord.Embed(
        title="🖥️ جميع بانلات التذاكر", color=discord.Color.blue()
    )
    for panel_id, panel in database["panels"].items():
        channel = interaction.guild.get_channel(panel.get("channel"))
        channel_text = channel.mention if channel else "❌ الروم غير موجود"
        embed.add_field(
            name=f"🆔 {panel_id}",
            value=(
                f"📌 **العنوان:** {panel.get('title', 'بدون عنوان')}\n"
                f"📜 **الوصف:** {panel.get('description', 'بدون وصف')}\n"
                f"📍 **الروم:** {channel_text}\n"
                f"🔗 [فتح البانل](https://discord.com/channels/"
                f"{interaction.guild.id}/"
                f"{panel.get('channel')}/"
                f"{panel.get('message_id')})"
            ),
            inline=False,
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="delete-ticket-panel", description="حذف بانل تذاكر معين")
@app_commands.describe(panel_id="معرف البانل مثل panel_1")
async def delete_ticket_panel(interaction: discord.Interaction, panel_id: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ هذا الأمر للمشرفين فقط", ephemeral=True
        )
        return
    panel = database["panels"].get(panel_id)
    if not panel:
        await interaction.response.send_message(
            "❌ لم يتم العثور على هذا البانل", ephemeral=True
        )
        return
    channel = interaction.guild.get_channel(panel.get("channel"))
    if channel:
        try:
            message = await channel.fetch_message(panel.get("message_id"))
            await message.delete()
        except:
            pass
    del database["panels"][panel_id]
    save_database()
    await interaction.response.send_message(
        f"✅ تم حذف البانل `{panel_id}` بنجاح", ephemeral=True
    )


# ==================================
# ربط التذاكر بالبانلات
# ==================================
async def refresh_panel_message(guild, panel_id):
    panel = database["panels"].get(panel_id)
    if not panel:
        return False
    channel = guild.get_channel(panel.get("channel"))
    if not channel:
        return False
    try:
        message = await channel.fetch_message(panel.get("message_id"))
        await message.edit(view=TicketPanel(panel_id))
        return True
    except Exception as e:
        print(f"Panel refresh error: {e}")
        return False


@bot.tree.command(
    name="panel-add-ticket", description="إضافة نوع تذكرة إلى بانل معين"
)
@app_commands.describe(
    panel_id="معرف البانل مثل panel_1",
    ticket_id="معرف نوع التذكرة مثل ticket_1",
)
async def panel_add_ticket(
    interaction: discord.Interaction, panel_id: str, ticket_id: str
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ هذا الأمر للمشرفين فقط.", ephemeral=True
        )
        return
    panel = database["panels"].get(panel_id)
    if not panel:
        await interaction.response.send_message(
            f"❌ البانل `{panel_id}` غير موجود.", ephemeral=True
        )
        return
    ticket = database["tickets"].get(ticket_id)
    if not ticket:
        await interaction.response.send_message(
            f"❌ نوع التذكرة `{ticket_id}` غير موجود.", ephemeral=True
        )
        return
    if ticket_id in panel.get("tickets", []):
        await interaction.response.send_message(
            f"⚠️ التذكرة **{ticket['name']}** موجودة بالفعل داخل `{panel_id}`.",
            ephemeral=True,
        )
        return
    panel.setdefault("tickets", [])
    panel["tickets"].append(ticket_id)
    save_database()
    updated = await refresh_panel_message(interaction.guild, panel_id)
    await interaction.response.send_message(
        embed=make_embed(
            "✅ تمت إضافة التذكرة",
            f"🎫 **التذكرة:** {ticket['name']}\n"
            f"🆔 **المعرف:** `{ticket_id}`\n\n"
            f"🖥️ **البانل:** `{panel_id}`\n\n"
            f"{'🔄 تم تحديث البانل مباشرة.' if updated else '⚠️ تمت الإضافة ولكن تعذر تحديث رسالة البانل.'}",
            discord.Color.green(),
        ),
        ephemeral=True,
    )


@bot.tree.command(
    name="panel-remove-ticket", description="إزالة نوع تذكرة من بانل معين"
)
@app_commands.describe(
    panel_id="معرف البانل", ticket_id="معرف نوع التذكرة"
)
async def panel_remove_ticket(
    interaction: discord.Interaction, panel_id: str, ticket_id: str
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ هذا الأمر للمشرفين فقط.", ephemeral=True
        )
        return
    panel = database["panels"].get(panel_id)
    if not panel:
        await interaction.response.send_message(
            f"❌ البانل `{panel_id}` غير موجود.", ephemeral=True
        )
        return
    if ticket_id not in panel.get("tickets", []):
        await interaction.response.send_message(
            "❌ هذه التذكرة غير موجودة داخل هذا البانل.", ephemeral=True
        )
        return
    panel["tickets"].remove(ticket_id)
    save_database()
    updated = await refresh_panel_message(interaction.guild, panel_id)
    ticket = database["tickets"].get(ticket_id)
    ticket_name = ticket["name"] if ticket else ticket_id
    await interaction.response.send_message(
        embed=make_embed(
            "✅ تمت إزالة التذكرة",
            f"🎫 **التذكرة:** {ticket_name}\n"
            f"🆔 **المعرف:** `{ticket_id}`\n"
            f"🖥️ **البانل:** `{panel_id}`\n\n"
            f"{'🔄 تم تحديث البانل.' if updated else '⚠️ تمت الإزالة ولكن تعذر تحديث البانل.'}",
            discord.Color.green(),
        ),
        ephemeral=True,
    )


@bot.tree.command(
    name="panel-tickets", description="عرض التذاكر الموجودة داخل بانل معين"
)
@app_commands.describe(panel_id="معرف البانل مثل panel_1")
async def panel_tickets(interaction: discord.Interaction, panel_id: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ هذا الأمر للمشرفين فقط.", ephemeral=True
        )
        return
    panel = database["panels"].get(panel_id)
    if not panel:
        await interaction.response.send_message(
            f"❌ البانل `{panel_id}` غير موجود.", ephemeral=True
        )
        return
    ticket_ids = panel.get("tickets", [])
    if not ticket_ids:
        await interaction.response.send_message(
            f"📍 البانل `{panel_id}` لا يحتوي على أي تذاكر.", ephemeral=True
        )
        return
    embed = discord.Embed(
        title=f"🎫 تذاكر {panel_id}", color=discord.Color.blue()
    )
    text = ""
    for ticket_id in ticket_ids:
        ticket = database["tickets"].get(ticket_id)
        if ticket:
            text += (
                f"{ticket.get('emoji', '🎫')} "
                f"**{ticket['name']}**\n"
                f"🆔 `{ticket_id}`\n\n"
            )
    if not text:
        text = "❌ لا توجد تذاكر صالحة."
    embed.description = text
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ==================================
# القوائم والبانل الموحد
# ==================================
class TicketSelect(discord.ui.Select):
    def __init__(self, panel_id):
        self.panel_id = panel_id
        panel = database["panels"].get(panel_id)
        options = []
        if panel:
            panel_tickets = panel.get("tickets", [])
            for ticket_id in panel_tickets:
                data = database["tickets"].get(ticket_id)
                if not data:
                    continue
                options.append(
                    discord.SelectOption(
                        label=data["name"][:100],
                        value=ticket_id,
                        description=data.get(
                            "panel_description",
                            data.get("description", "فتح تذكرة"),
                        )[:100],
                        emoji=data.get("emoji", "🎫"),
                    )
                )
        if not options:
            options.append(
                discord.SelectOption(
                    label="لا توجد تذاكر",
                    value="none",
                    description="لا توجد تذاكر مضافة لهذا البانل",
                    emoji="❌",
                )
            )
        options.append(
            discord.SelectOption(
                label="تحديث القائمة",
                value="refresh_menu",
                description="إعادة تحميل أنواع التذاكر",
                emoji="🔄",
            )
        )
        super().__init__(
            placeholder="🎫 اختر نوع التذكرة",
            options=options,
            custom_id=f"ticket_select_{panel_id}",
        )

    async def callback(self, interaction: discord.Interaction):
        ticket_type = self.values[0]
        if ticket_type == "refresh_menu":
            await interaction.response.edit_message(
                view=TicketPanel(self.panel_id)
            )
            return
        if ticket_type == "none":
            await interaction.response.send_message(
                "❌ لا توجد تذاكر مضافة لهذا البانل حالياً.",
                ephemeral=True,
            )
            return
        user_id = interaction.user.id
        ticket_settings = database["tickets"].get(ticket_type)
        if not ticket_settings:
            await interaction.response.send_message(
                "❌ نوع التذكرة لم يعد موجوداً.", ephemeral=True
            )
            return
        for t in database["open_tickets"].values():
            if t.get("owner") == user_id:
                await interaction.response.send_message(
                    "❌ لديك تذكرة مفتوحة بالفعل.", ephemeral=True
                )
                return
        if ticket_settings.get("ask_reason"):
            await interaction.response.send_modal(
                TicketFormModal(ticket_type)
            )
            return
        await create_ticket(interaction, ticket_type, None)


# ==================================
# View البانل
# ==================================
class TicketPanel(discord.ui.View):
    def __init__(self, panel_id):
        super().__init__(timeout=None)
        self.panel_id = panel_id
        self.add_item(TicketSelect(panel_id))


# ==================================
# نظام نماذج التذاكر (Ticket Forms)
# ==================================
class TicketFormModal(discord.ui.Modal):
    def __init__(self, ticket_type):
        super().__init__(title="معلومات فتح التذكرة")
        self.ticket_type = ticket_type
        self.question1 = discord.ui.TextInput(
            label="ماذا تريد؟",
            placeholder="اكتب طلبك بالتفصيل",
            required=True,
            max_length=300,
        )
        self.question2 = discord.ui.TextInput(
            label="التفاصيل الإضافية",
            placeholder="اكتب أي معلومات تساعد الإدارة",
            required=False,
            max_length=300,
        )
        self.add_item(self.question1)
        self.add_item(self.question2)

    async def on_submit(self, interaction: discord.Interaction):
        reason = (
            f"📜 الطلب:\n{self.question1.value}\n\n"
            f"📌 التفاصيل:\n{self.question2.value}"
        )
        await create_ticket(interaction, self.ticket_type, reason)


@bot.tree.command(
    name="ticket-form", description="تفعيل نموذج أسئلة لنوع تذكرة"
)
@app_commands.describe(ticket_id="معرف نوع التذكرة")
async def ticket_form(interaction: discord.Interaction, ticket_id: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ هذا الأمر للمشرفين فقط", ephemeral=True
        )
        return
    if ticket_id not in database["tickets"]:
        await interaction.response.send_message(
            "❌ نوع التذكرة غير موجود", ephemeral=True
        )
        return
    database["tickets"][ticket_id]["ask_reason"] = True
    save_database()
    await interaction.response.send_message(
        embed=make_embed(
            "✅ تم تفعيل النموذج",
            f"تم تفعيل أسئلة الفتح لنوع التذكرة:\n🎫 {database['tickets'][ticket_id]['name']}",
            discord.Color.green(),
        ),
        ephemeral=True,
    )


# ==================================
# نظام فتح التذاكر والترانسكريبت
# ==================================
async def create_transcript(channel):
    messages = []
    async for message in channel.history(limit=None, oldest_first=True):
        timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
        author = (
            f"{message.author.name}#{message.author.discriminator}"
            if message.author.discriminator != "0"
            else message.author.name
        )
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
            attachments_html += f'<br><a href="{att.url}" target="_blank" style="color: #00b0f4;">📎 {att.filename}</a>'

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
        <h2 style="color: #ffffff; border-bottom: 1px solid #4f545c; padding-bottom: 10px;">📜 سجل التذكرة: {channel.name}</h2>
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
            title="🎫 فتح تذكرة",
            description=f"👤 العضو:\n{interaction.user.mention}\n\n📌 الروم:\n{channel.mention}",
            color=discord.Color.green(),
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
            title="🔒 إغلاق تذكرة",
            description=f"👤 أغلقتها:\n{interaction.user.mention}\n\n📌 الروم:\n{channel.name}",
            color=discord.Color.red(),
        )
        await log.send(embed=embed)
        await log.send(file=discord.File(transcript))


async def create_ticket(interaction, ticket_type, reason=None):
    settings = database["tickets"].get(ticket_type)
    if not settings:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ نوع التذكرة غير موجود", ephemeral=True
            )
        return
    category_id = settings.get("open_category")
    category = (
        interaction.guild.get_channel(category_id) if category_id else None
    )

    settings["counter"] += 1
    number = settings["counter"]
    channel_name = f"{settings['emoji']}-ticket-{number}"

    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(
            view_channel=False
        ),
        interaction.user: discord.PermissionOverwrite(
            view_channel=True, send_messages=True, read_message_history=True
        ),
    }

    for role_id in settings.get("staff_roles", []):
        role = interaction.guild.get_role(role_id)
        if role:
            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
            )

    channel = await interaction.guild.create_text_channel(
        name=channel_name, category=category, overwrites=overwrites
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
        "added_members": [],
    }
    database["stats"]["total_opened"] += 1
    settings["opened"] += 1
    save_database()

    colors = {
        "blue": discord.Color.blue(),
        "red": discord.Color.red(),
        "green": discord.Color.green(),
        "gold": discord.Color.gold(),
    }
    embed_color = colors.get(settings.get("color"), discord.Color.blue())

    welcome_text = settings.get(
        "welcome_message", "أهلاً {user} 👋\nسيتم الرد عليك قريباً."
    )
    embed = discord.Embed(
        title=f"{settings['emoji']} {settings['name']}",
        description=welcome_text.replace("{user}", interaction.user.mention),
        color=embed_color,
    )
    embed.add_field(
        name="👤 صاحب التذكرة", value=interaction.user.mention, inline=False
    )
    embed.add_field(name="🔢 رقم التذكرة", value=f"#{number}", inline=False)

    if reason:
        embed.add_field(name="📜 السبب", value=reason, inline=False)

    if settings.get("ticket_image") or settings.get("image"):
        embed.set_image(
            url=settings.get("ticket_image") or settings.get("image")
        )

    embed.set_footer(text="نظام التذاكر الاحترافي")

    await channel.send(embed=embed, view=TicketButtons())
    await send_open_log(
        interaction, channel, database["open_tickets"][str(channel.id)]
    )

    if not interaction.response.is_done():
        await interaction.response.send_message(
            f"✅ تم فتح التذكرة {channel.mention}", ephemeral=True
        )


# ==================================
# أزرار وأدوات داخل التذكرة
# ==================================
class TicketButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Claim",
        emoji="👑",
        style=discord.ButtonStyle.blurple,
        custom_id="claim_button_secure",
    )
    async def claim(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not check_staff(interaction):
            await interaction.response.send_message(
                "❌ ليس لديك صلاحية لاستلام التذكرة", ephemeral=True
            )
            return
        ticket = database["open_tickets"].get(str(interaction.channel.id))
        if not ticket:
            await interaction.response.send_message(
                "❌ التذكرة غير موجودة", ephemeral=True
            )
            return
        if ticket.get("claimed"):
            await interaction.response.send_message(
                "⚠️ هذه التذكرة تم استلامها مسبقاً", ephemeral=True
            )
            return
        ticket["claimed"] = interaction.user.id
        staff = str(interaction.user.id)
        if staff not in database["stats"]["staff"]:
            database["stats"]["staff"][staff] = {"claimed": 0, "closed": 0}
        database["stats"]["staff"][staff]["claimed"] += 1
        database["stats"]["logs"].append(
            {
                "user": str(interaction.user.id),
                "action": "استلم التذكرة",
                "time": str(datetime.now()),
            }
        )
        save_database()

        button.disabled = True
        await interaction.message.edit(view=self)

        embed = make_embed(
            "👑 تم استلام التذكرة",
            f"الإداري المسؤول الآن:\n{interaction.user.mention}",
            discord.Color.gold(),
        )
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message(
            f"👑 تم استلام التذكرة بنجاح", ephemeral=True
        )

    @discord.ui.button(
        label="إغلاق",
        emoji="🔒",
        style=discord.ButtonStyle.red,
        custom_id="close_button_secure",
    )
    async def close(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not check_staff(interaction):
            await interaction.response.send_message(
                "❌ ليس لديك صلاحية", ephemeral=True
            )
            return
        channel_id = str(interaction.channel.id)
        if channel_id in database["open_tickets"]:
            database["open_tickets"][channel_id]["closed"] = True
            staff = str(interaction.user.id)
            if staff not in database["stats"]["staff"]:
                database["stats"]["staff"][staff] = {"claimed": 0, "closed": 0}
            database["stats"]["staff"][staff]["closed"] += 1
            database["stats"]["logs"].append(
                {
                    "user": str(interaction.user.id),
                    "action": "أغلق التذكرة",
                    "time": str(datetime.now()),
                }
            )
            save_database()

        await interaction.response.send_message(
            "🔒 تم تجهيز إغلاق التذكرة\n⭐ اختر تقييم الخدمة:",
            view=RatingView(interaction.channel.id),
            ephemeral=True,
        )


# ==================================
# نظام التقييم والإغلاق
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
            ticket_settings["ratings"].append(
                {
                    "user": str(interaction.user.id),
                    "stars": stars,
                    "staff": ticket.get("claimed"),
                }
            )
            save_database()
        await send_rating_log(interaction, stars, ticket)

        channel = interaction.channel
        close_cat_id = (
            ticket_settings.get("close_category") if ticket_settings else None
        )
        if close_cat_id:
            close_category = interaction.guild.get_channel(close_cat_id)
            if close_category:
                try:
                    await channel.edit(category=close_category)
                except:
                    pass

        transcript = await create_transcript(channel)
        await send_close_log(interaction, channel, transcript)

        await interaction.response.send_message(
            "⭐ تم حفظ تقييمك بنجاح، سيتم حذف الروم خلال 3 ثواني...",
            ephemeral=True,
        )
        await asyncio.sleep(3)
        try:
            await channel.delete()
        except:
            pass

    @discord.ui.button(
        label="⭐", style=discord.ButtonStyle.gray, custom_id="rating_1_sec"
    )
    async def one(self, interaction, button):
        await self.save_rating(interaction, 1)

    @discord.ui.button(
        label="⭐⭐⭐",
        style=discord.ButtonStyle.blurple,
        custom_id="rating_3_sec",
    )
    async def three(self, interaction, button):
        await self.save_rating(interaction, 3)

    @discord.ui.button(
        label="⭐⭐⭐⭐",
        style=discord.ButtonStyle.blurple,
        custom_id="rating_4_sec",
    )
    async def four(self, interaction, button):
        await self.save_rating(interaction, 4)

    @discord.ui.button(
        label="⭐⭐⭐⭐⭐",
        style=discord.ButtonStyle.green,
        custom_id="rating_5_sec",
    )
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
    staff_text = f"<@{staff}>" if staff else "لا يوجد"
    embed = discord.Embed(title="⭐ تقييم جديد", color=discord.Color.gold())
    embed.add_field(
        name="👤 العضو", value=interaction.user.mention, inline=False
    )
    embed.add_field(name="⭐ التقييم", value=f"{stars}/5", inline=False)
    embed.add_field(name="👑 الإداري المستلم", value=staff_text, inline=False)
    await channel.send(embed=embed)


# ==================================
# أوامر الإدارة داخل التذكرة
# ==================================
@bot.tree.command(name="claim", description="استلام التذكرة")
async def claim_ticket(interaction: discord.Interaction):
    if not check_staff(interaction):
        await interaction.response.send_message(
            "❌ ليس لديك صلاحية لاستلام التذكرة", ephemeral=True
        )
        return
    ticket = get_ticket_from_channel(interaction.channel.id)
    if not ticket:
        await interaction.response.send_message(
            "❌ التذكرة غير موجودة", ephemeral=True
        )
        return
    if ticket.get("claimed"):
        await interaction.response.send_message(
            "⚠️ هذه التذكرة تم استلامها مسبقاً", ephemeral=True
        )
        return
    ticket["claimed"] = interaction.user.id
    staff = str(interaction.user.id)
    if staff not in database["stats"]["staff"]:
        database["stats"]["staff"][staff] = {"claimed": 0, "closed": 0}
    database["stats"]["staff"][staff]["claimed"] += 1
    database["stats"]["logs"].append(
        {
            "user": str(interaction.user.id),
            "action": "استلم التذكرة",
            "time": str(datetime.now()),
        }
    )
    save_database()
    embed = make_embed(
        "👑 تم استلام التذكرة",
        f"الإداري المسؤول الآن:\n{interaction.user.mention}",
        discord.Color.gold(),
    )
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message(
        f"👑 تم استلام التذكرة", ephemeral=True
    )


@bot.tree.command(name="close", description="إغلاق التذكرة")
async def close_ticket(interaction: discord.Interaction):
    if not check_staff(interaction):
        await interaction.response.send_message(
            "❌ لا تملك صلاحية", ephemeral=True
        )
        return
    channel_id = str(interaction.channel.id)
    if channel_id in database["open_tickets"]:
        database["open_tickets"][channel_id]["closed"] = True
        staff = str(interaction.user.id)
        if staff not in database["stats"]["staff"]:
            database["stats"]["staff"][staff] = {"claimed": 0, "closed": 0}
        database["stats"]["staff"][staff]["closed"] += 1
        database["stats"]["logs"].append(
            {
                "user": str(interaction.user.id),
                "action": "أغلق التذكرة",
                "time": str(datetime.now()),
            }
        )
        save_database()
    await interaction.response.send_message(
        "⭐ يرجى تقييم التذكرة قبل الإغلاق",
        view=RatingView(interaction.channel.id),
        ephemeral=True,
    )


@bot.tree.command(name="rename", description="تغيير اسم التذكرة")
@app_commands.describe(name="الاسم الجديد")
async def rename_ticket(interaction: discord.Interaction, name: str):
    if not check_staff(interaction):
        await interaction.response.send_message(
            "❌ لا تملك صلاحية", ephemeral=True
        )
        return
    await interaction.channel.edit(name=name)
    database["stats"]["logs"].append(
        {
            "user": str(interaction.user.id),
            "action": f"غير اسم التذكرة إلى {name}",
            "time": str(datetime.now()),
        }
    )
    save_database()
    await interaction.response.send_message("✅ تم تغيير الاسم")


@bot.tree.command(name="priority", description="تحديد أولوية التذكرة")
@app_commands.choices(
    level=[
        app_commands.Choice(name="عادي", value="normal"),
        app_commands.Choice(name="مهم", value="important"),
        app_commands.Choice(name="عاجل", value="urgent"),
    ]
)
async def priority_ticket(
    interaction: discord.Interaction, level: app_commands.Choice[str]
):
    if not check_staff(interaction):
        await interaction.response.send_message(
            "❌ لا تملك صلاحية", ephemeral=True
        )
        return
    ticket = get_ticket_from_channel(interaction.channel.id)
    ticket["priority"] = level.value
    ticket["last_activity"] = str(datetime.now())
    save_database()
    await interaction.response.send_message(
        f"📌 تم تغيير الأولوية إلى: {level.name}"
    )


@bot.tree.command(name="ticket-add", description="إضافة عضو للتذكرة")
async def ticket_add(
    interaction: discord.Interaction, member: discord.Member
):
    if not check_staff(interaction):
        await interaction.response.send_message(
            "❌ لا تملك صلاحية", ephemeral=True
        )
        return
    await interaction.channel.set_permissions(
        member, view_channel=True, send_messages=True
    )
    await interaction.response.send_message(f"✅ تمت إضافة {member.mention}")


@bot.tree.command(name="ticket-remove", description="إزالة عضو من التذكرة")
async def ticket_remove(
    interaction: discord.Interaction, member: discord.Member
):
    if not check_staff(interaction):
        await interaction.response.send_message(
            "❌ لا تملك صلاحية", ephemeral=True
        )
        return
    await interaction.channel.set_permissions(member, overwrite=None)
    await interaction.response.send_message(f"✅ تمت إزالة {member.mention}")


@bot.tree.command(name="lock", description="قفل الكتابة في التذكرة")
async def lock_ticket(interaction: discord.Interaction):
    if not check_staff(interaction):
        await interaction.response.send_message(
            "❌ لا تملك صلاحية", ephemeral=True
        )
        return
    await interaction.channel.set_permissions(
        interaction.guild.default_role, send_messages=False
    )
    await interaction.response.send_message("🔒 تم قفل التذكرة")


@bot.tree.command(name="unlock", description="فتح الكتابة في التذكرة")
async def unlock_ticket(interaction: discord.Interaction):
    if not check_staff(interaction):
        await interaction.response.send_message(
            "❌ لا تملك صلاحية", ephemeral=True
        )
        return
    await interaction.channel.set_permissions(
        interaction.guild.default_role, send_messages=True
    )
    await interaction.response.send_message("🔓 تم فتح التذكرة")


@bot.tree.command(name="reopen", description="إعادة فتح التذكرة")
async def reopen_ticket(interaction: discord.Interaction):
    if not check_staff(interaction):
        await interaction.response.send_message(
            "❌ لا تملك صلاحية", ephemeral=True
        )
        return
    await interaction.channel.set_permissions(
        interaction.guild.default_role, view_channel=True
    )
    await interaction.response.send_message("🔄 تم إعادة فتح التذكرة")


@bot.tree.command(name="move", description="نقل التذكرة")
@app_commands.describe(category="ID الكاتجوري الجديد")
async def move_ticket(interaction: discord.Interaction, category: str):
    if not check_staff(interaction):
        await interaction.response.send_message(
            "❌ لا تملك صلاحية", ephemeral=True
        )
        return
    try:
        category_id = int(category)
    except:
        await interaction.response.send_message(
            "❌ ID غير صحيح", ephemeral=True
        )
        return
    new_category = interaction.guild.get_channel(category_id)
    if not new_category:
        await interaction.response.send_message(
            "❌ لم يتم العثور على الكاتجوري", ephemeral=True
        )
        return
    await interaction.channel.edit(category=new_category)
    await interaction.response.send_message("🚚 تم نقل التذكرة")


@bot.tree.command(
    name="auto-move", description="نقل التذكرة تلقائياً إلى كاتجوري"
)
@app_commands.describe(category="ID الكاتجوري")
async def auto_move(interaction: discord.Interaction, category: str):
    if not check_staff(interaction):
        await interaction.response.send_message(
            "❌ لا تملك صلاحية", ephemeral=True
        )
        return
    try:
        category_id = int(category)
    except:
        await interaction.response.send_message(
            "❌ ID غير صحيح", ephemeral=True
        )
        return
    new_category = interaction.guild.get_channel(category_id)
    if not new_category:
        await interaction.response.send_message(
            "❌ الكاتجوري غير موجود", ephemeral=True
        )
        return
    await interaction.channel.edit(category=new_category)
    embed = discord.Embed(
        title="🚚 تم نقل التذكرة",
        description=f"تم نقل التذكرة إلى:\n{new_category.name}",
        color=discord.Color.blue(),
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="ticket-info", description="عرض معلومات التذكرة الحالية")
async def ticket_info(interaction: discord.Interaction):
    ticket = get_ticket_from_channel(interaction.channel.id)
    if not ticket:
        await interaction.response.send_message(
            "❌ هذا الروم ليس تذكرة", ephemeral=True
        )
        return
    settings = database["tickets"].get(ticket["type"])
    embed = discord.Embed(title="🎫 معلومات التذكرة", color=discord.Color.blue())
    embed.add_field(
        name="👤 صاحب التذكرة", value=f"<@{ticket['owner']}>", inline=False
    )
    embed.add_field(
        name="📌 النوع",
        value=settings["name"] if settings else "غير معروف",
        inline=False,
    )
    embed.add_field(
        name="👑 المستلم",
        value=f"<@{ticket['claimed']}>" if ticket["claimed"] else "لا يوجد",
        inline=False,
    )
    embed.add_field(
        name="📌 الأولوية",
        value=ticket.get("priority", "normal"),
        inline=False,
    )
    embed.add_field(
        name="📅 التاريخ",
        value=ticket.get("created", "غير معروف"),
        inline=False,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="ticket-note", description="إضافة ملاحظة للتذكرة")
@app_commands.describe(note="الملاحظة")
async def ticket_note(interaction: discord.Interaction, note: str):
    if not check_staff(interaction):
        await interaction.response.send_message(
            "❌ ليس لديك صلاحية", ephemeral=True
        )
        return
    ticket = get_ticket_from_channel(interaction.channel.id)
    if not ticket:
        await interaction.response.send_message(
            "❌ ليست تذكرة", ephemeral=True
        )
        return
    ticket.setdefault("notes", [])
    ticket["notes"].append(
        {"staff": interaction.user.id, "note": note, "time": str(datetime.now())}
    )
    save_database()
    await interaction.response.send_message(
        "✅ تم حفظ الملاحظة", ephemeral=True
    )


@bot.tree.command(name="ticket-notes", description="عرض ملاحظات التذكرة")
async def ticket_notes(interaction: discord.Interaction):
    ticket = get_ticket_from_channel(interaction.channel.id)
    if not ticket:
        await interaction.response.send_message(
            "❌ ليست تذكرة", ephemeral=True
        )
        return
    notes = ticket.get("notes", [])
    if not notes:
        await interaction.response.send_message(
            "📖 لا يوجد ملاحظات", ephemeral=True
        )
        return
    text = ""
    for n in notes:
        text += f"👤 <@{n['staff']}> : {n['note']}\n"
    embed = discord.Embed(
        title="📜 ملاحظات التذكرة", description=text, color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="ticket-stats", description="إحصائيات التذاكر")
async def ticket_stats(interaction: discord.Interaction):
    if not check_staff(interaction):
        await interaction.response.send_message(
            "❌ لا تملك صلاحية", ephemeral=True
        )
        return
    opened = len(database["open_tickets"])
    closed = database.get("closed_today", 0)
    embed = discord.Embed(title="📊 إحصائيات التذاكر", color=discord.Color.blue())
    embed.add_field(name="🎫 المفتوحة", value=str(opened))
    embed.add_field(name="🔒 المغلقة", value=str(closed))
    await interaction.response.send_message(embed=embed)


# ==================================
# إعدادات التذكرة المخصصة
# ==================================
class TicketSettingsModal(discord.ui.Modal):
    def __init__(self, ticket_id, option):
        super().__init__(title="تعديل إعداد التذكرة")
        self.ticket_id = ticket_id
        self.option = option
        self.value = discord.ui.TextInput(
            label="القيمة الجديدة",
            placeholder="اكتب القيمة أو ID هنا",
            required=True,
            max_length=4000,
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
        await interaction.response.send_message(
            "✅ تم حفظ التعديل", ephemeral=True
        )


class TicketSettingsView(discord.ui.View):
    def __init__(self, ticket_id):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id

    @discord.ui.select(
        placeholder="اختر إعداد للتعديل",
        options=[
            discord.SelectOption(
                label="اسم التذكرة", value="name", emoji="🏷️"
            ),
            discord.SelectOption(
                label="وصف البانل", value="description", emoji="📜"
            ),
            discord.SelectOption(
                label="إيموجي التذكرة", value="emoji", emoji="😀"
            ),
            discord.SelectOption(
                label="لون التذكرة", value="color", emoji="🎨"
            ),
            discord.SelectOption(
                label="رسالة الترحيب", value="welcome", emoji="👋"
            ),
            discord.SelectOption(
                label="صورة داخل التذكرة", value="image", emoji="🖼️"
            ),
            discord.SelectOption(
                label="كاتجوري الفتح", value="open_category", emoji="📂"
            ),
            discord.SelectOption(
                label="كاتجوري الإغلاق", value="close_category", emoji="🔒"
            ),
            discord.SelectOption(
                label="إضافة رتبة إدارة", value="staff_role", emoji="🛡️"
            ),
            discord.SelectOption(
                label="إزالة رتبة إدارة", value="remove_staff_role", emoji="❌"
            ),
        ],
    )
    async def select_callback(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        await interaction.response.send_modal(
            TicketSettingsModal(self.ticket_id, select.values[0])
        )


@bot.tree.command(name="ticket-settings", description="تعديل إعدادات نوع تذكرة")
@app_commands.describe(ticket_id="معرف التذكرة")
async def ticket_settings(interaction: discord.Interaction, ticket_id: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ هذا الأمر مخصص للمشرفين فقط", ephemeral=True
        )
        return
    if ticket_id not in database["tickets"]:
        await interaction.response.send_message(
            "❌ نوع التذكرة غير موجود", ephemeral=True
        )
        return
    embed = discord.Embed(
        title="⚙️ إعدادات التذكرة",
        description=f"تعديل:\n🎫 {database['tickets'][ticket_id]['name']}",
        color=discord.Color.gold(),
    )
    await interaction.response.send_message(
        embed=embed, view=TicketSettingsView(ticket_id), ephemeral=True
    )


# ==================================
# نظام الحماية و Anti-Spam والخلفيات
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
    spam_users[user] = [x for x in spam_users[user] if now - x <= SPAM_TIME]
    if len(spam_users[user]) >= SPAM_LIMIT:
        try:
            await message.delete()
        except:
            pass
        embed = discord.Embed(
            title="⚠️ حماية السبام",
            description=f"{message.author.mention} تم منع الإرسال السريع.",
            color=discord.Color.orange(),
        )
        await message.channel.send(embed=embed, delete_after=5)
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
                            title="🔒 إغلاق تلقائي",
                            description="تم إغلاق التذكرة بسبب عدم النشاط لمدة 24 ساعة.",
                            color=discord.Color.red(),
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
            json.dump(database, file, indent=4, ensure_ascii=False)
        await asyncio.sleep(3600)


@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return
    channel_id = message.channel.id
    if str(channel_id) in database["open_tickets"]:
        database["open_tickets"][str(channel_id)]["last_activity"] = str(
            datetime.now()
        )
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
# تشغيل البوت واستقرار الـ Persistent Views
# ==================================
@bot.event
async def on_ready():
    print(f"✅ Bot Online: {bot.user}")
    for panel_id in database.get("panels", {}):
        try:
            bot.add_view(TicketPanel(panel_id))
        except Exception as e:
            print(f"❌ Failed to load panel {panel_id}: {e}")
    bot.add_view(TicketButtons())
    for channel_id in database["open_tickets"]:
        bot.add_view(RatingView(int(channel_id)))

    bot.loop.create_task(auto_close_checker())
    bot.loop.create_task(database_backup())

    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"✅ Guild Synced: {len(synced)} Commands")
    except Exception as e:
        print(f"❌ Sync Error: {type(e).__name__}: {e}")


TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Token not found!")
