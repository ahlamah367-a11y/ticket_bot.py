import asyncio
import json
import os
import tempfile
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

# ==================================
# إعداد قواعد البيانات والمسارات في ذاكرة النظام
# ==================================
DATA_DIR = os.path.join(tempfile.gettempdir(), "bot_data")
try:
    os.makedirs(DATA_DIR, exist_ok=True)
except Exception as e:
    print(f"⚠️ Warning creating data directory: {e}")

DATABASE_FILE = os.path.join(DATA_DIR, "tickets_database.json")
BACKUP_FILE = os.path.join(DATA_DIR, "tickets_backup.json")

# ==================================
# إعداد البوت والنية (Intents)
# ==================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1532326696714240062


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
    try:
        with open(DATABASE_FILE, "w", encoding="utf-8") as file:
            json.dump(database, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Error saving database: {e}")


def load_database():
    if not os.path.exists(DATABASE_FILE):
        return default_database()
    try:
        with open(DATABASE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"❌ Error loading database: {e}")
        return default_database()


database = load_database()
save_database()

if "panels" not in database:
    database["panels"] = {}

for panel_id, panel in database["panels"].items():
    if "tickets" not in panel:
        panel["tickets"] = []

save_database()


# ==================================
# أدوات مساعدة وتصميم
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
    return user.id in database["stats"]["permissions"].get("managers", [])


def create_ticket_id():
    number = len(database["tickets"]) + 1
    return f"ticket_{number}"


def get_ticket(ticket_id):
    return database["tickets"].get(ticket_id)


def get_ticket_from_channel(channel_id):
    return database["open_tickets"].get(str(channel_id))


def check_staff(interaction):
    if is_manager(interaction.user):
        return True
    ticket = get_ticket_from_channel(interaction.channel.id)
    if not ticket:
        return False
    settings = database["tickets"].get(ticket["type"])
    if not settings:
        return False
    staff_roles = settings.get("staff_roles", [])
    user_roles = [role.id for role in interaction.user.roles]
    for role in staff_roles:
        if role in user_roles:
            return True
    return False


print("✅ البيانات والأجزاء الأساسية جاهزة بدون استخدام حافظة خارجي")


# ==================================
# الأوامر الإدارية للنظام
# ==================================
@bot.tree.command(name="reload-data", description="إعادة تحميل البيانات")
async def reload_data(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ للمشرفين فقط", ephemeral=True)
        return
    global database
    database = load_database()
    await interaction.response.send_message("✅ تم تحديث البيانات بنجاح", ephemeral=True)


@bot.tree.command(name="backup-tickets", description="عمل نسخة احتياطية")
async def backup_tickets(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ للمشرفين فقط", ephemeral=True)
        return
    filename = os.path.join(
        tempfile.gettempdir(), f"backup-{datetime.now().strftime('%Y-%m-%d')}.json"
    )
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(database, f, indent=4, ensure_ascii=False)
        await interaction.response.send_message(
            "✅ تم إنشاء نسخة احتياطية",
            file=discord.File(filename),
            ephemeral=True,
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ تعذر إنشاء النسخة الاحتياطية: {e}", ephemeral=True
        )


@bot.tree.command(name="restore-backup", description="استرجاع نسخة احتياطية")
async def restore_backup(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ للمشرفين فقط", ephemeral=True)
        return
    global database
    if not os.path.exists(BACKUP_FILE):
        await interaction.response.send_message("❌ لا يوجد نسخة احتياطية", ephemeral=True)
        return
    try:
        with open(BACKUP_FILE, "r", encoding="utf-8") as file:
            database = json.load(file)
        await interaction.response.send_message(
            embed=make_embed(
                "✅ تم الاسترجاع",
                "تم استرجاع بيانات التذاكر بنجاح.",
                discord.Color.green(),
            ),
            ephemeral=True,
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ خطأ أثناء الاسترجاع: {e}", ephemeral=True
        )


@bot.tree.command(name="add-manager", description="إضافة مدير لنظام التذاكر")
@app_commands.describe(member="العضو")
async def add_manager(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ للمشرفين فقط", ephemeral=True)
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


@bot.tree.command(name="ticket-auto-setup", description="إعداد نظام التذاكر تلقائياً")
async def ticket_auto_setup(interaction: discord.Interaction):
    if not is_manager(interaction.user):
        await interaction.response.send_message("❌ لا تملك صلاحية", ephemeral=True)
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
    embed.add_field(name="🎫 أنواع التذاكر", value=str(len(database["tickets"])))
    embed.add_field(name="📂 التذاكر المفتوحة", value=str(len(database["open_tickets"])))
    embed.add_field(
        name="👑 المدراء",
        value=str(len(database["stats"]["permissions"]["managers"])),
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="dashboard", description="لوحة إحصائيات التذاكر")
async def dashboard(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ للمشرفين فقط", ephemeral=True)
        return
    stats = database["stats"]
    embed = discord.Embed(title="📊 لوحة التحكم", color=discord.Color.gold())
    embed.add_field(name="🎫 إجمالي الفتح", value=str(stats["total_opened"]))
    embed.add_field(name="🔒 إجمالي الإغلاق", value=str(stats["total_closed"]))
    embed.add_field(name="👑 عدد الإداريين", value=str(len(stats["staff"])))
    embed.set_footer(text="Ticket System Professional")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="ticket-create", description="إنشاء نوع تذكرة جديد")
@app_commands.describe(name="اسم التذكرة", description="وصف التذكرة في البانل")
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
        await interaction.response.send_message("❌ هذا النوع غير موجود", ephemeral=True)
        return
    del database["tickets"][ticket_id]

    for panel_id, panel in database.get("panels", {}).items():
        if ticket_id in panel.get("tickets", []):
            panel["tickets"].remove(ticket_id)
            try:
                await refresh_panel_message(interaction.guild, panel_id)
            except Exception:
                pass
    save_database()
    await interaction.response.send_message("✅ تم حذف نوع التذكرة", ephemeral=True)


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


@bot.tree.command(name="ticket-copy", description="نسخ إعدادات تذكرة موجودة")
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
        await interaction.response.send_message("❌ التذكرة غير موجودة", ephemeral=True)
        return
    ticket["name"] = new_name
    save_database()
    await interaction.response.send_message("✅ تم تغيير الاسم", ephemeral=True)


# ==================================
# إدارة البانل والمجموعات
# ==================================
@bot.tree.command(name="add-ticket-panel", description="إنشاء بانل تذاكر جديد")
@app_commands.describe(
    title="عنوان البانل", description="وصف البانل", image="رابط صورة - اختياري"
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
            f"استخدم `/panel-add-ticket` لإضافة تذاكر إليه.",
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
            "❌ لم يتم العثور على البانل", ephemeral=True
        )
        return
    channel = interaction.guild.get_channel(panel.get("channel"))
    if channel:
        try:
            message = await channel.fetch_message(panel.get("message_id"))
            await message.delete()
        except Exception:
            pass
    del database["panels"][panel_id]
    save_database()
    await interaction.response.send_message(
        f"✅ تم حذف البانل `{panel_id}` بنجاح", ephemeral=True
    )


# ==================================
# ربط التذاكر والقوائم التفاعلية
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
@app_commands.describe(panel_id="معرف البانل", ticket_id="معرف التذكرة")
async def panel_add_ticket(
    interaction: discord.Interaction, panel_id: str, ticket_id: str
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ للمشرفين فقط.", ephemeral=True)
        return
    panel = database["panels"].get(panel_id)
    if not panel:
        await interaction.response.send_message(f"❌ البانل `{panel_id}` غير موجود.", ephemeral=True)
        return
    ticket = database["tickets"].get(ticket_id)
    if not ticket:
        await interaction.response.send_message(f"❌ التذكرة `{ticket_id}` غير موجودة.", ephemeral=True)
        return
    if ticket_id in panel.get("tickets", []):
        await interaction.response.send_message("⚠️ موجودة بالفعل داخل البانل.", ephemeral=True)
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
            f"{'🔄 تم التحديث مباشرة.' if updated else '⚠️ تمت الإضافة مع تعذر تحديث الرسالة.'}",
            discord.Color.green(),
        ),
        ephemeral=True,
    )


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
                "❌ لا توجد تذاكر مضافة حالياً.", ephemeral=True
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


class TicketPanel(discord.ui.View):
    def __init__(self, panel_id):
        super().__init__(timeout=None)
        self.panel_id = panel_id
        self.add_item(TicketSelect(panel_id))


# ==================================
# نماذج الأسئلة والترانسكريبت
# ==================================
class TicketFormModal(discord.ui.Modal):
    def __init__(self, ticket_type):
        super().__init__(title="معلومات فتح التذكرة")
        self.ticket_type = ticket_type
        self.question1 = discord.ui.TextInput(
            label="ماذا تريد؟", placeholder="اكتب طلبك بالتفصيل", required=True
        )
        self.question2 = discord.ui.TextInput(
            label="التفاصيل الإضافية",
            placeholder="اكتب أي معلومات تسهم في حل المشكلة",
            required=False,
        )
        self.add_item(self.question1)
        self.add_item(self.question2)

    async def on_submit(self, interaction: discord.Interaction):
        reason = (
            f"📜 الطلب:\n{self.question1.value}\n\n"
            f"📌 التفاصيل:\n{self.question2.value}"
        )
        await create_ticket(interaction, self.ticket_type, reason)


async def create_transcript(channel):
    messages = []
    async for message in channel.history(limit=None, oldest_first=True):
        timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
        author = f"{message.author.name}"
        avatar = message.author.display_avatar.url
        content = message.content or ""
        messages.append(
            f"<div><b>{author}</b> ({timestamp}): {content}</div>"
        )

    html_content = f"<html><body>{''.join(messages)}</body></html>"
    filename = os.path.join(tempfile.gettempdir(), f"transcript-{channel.id}.html")
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)
    return filename


async def create_ticket(interaction, ticket_type, reason=None):
    settings = database["tickets"].get(ticket_type)
    if not settings:
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

    channel = await interaction.guild.create_text_channel(
        name=channel_name, category=category, overwrites=overwrites
    )

    database["open_tickets"][str(channel.id)] = {
        "owner": interaction.user.id,
        "type": ticket_type,
        "created": str(datetime.now()),
        "claimed": None,
        "reason": reason,
        "closed": False,
    }
    database["stats"]["total_opened"] += 1
    save_database()

    embed = discord.Embed(
        title=f"{settings['emoji']} {settings['name']}",
        description=settings.get("welcome_message", "أهلاً بك 👋").replace(
            "{user}", interaction.user.mention
        ),
        color=discord.Color.blue(),
    )
    if reason:
        embed.add_field(name="السبب", value=reason, inline=False)

    await channel.send(embed=embed, view=TicketButtons())
    if not interaction.response.is_done():
        await interaction.response.send_message(
            f"✅ تم فتح التذكرة: {channel.mention}", ephemeral=True
        )


# ==================================
# تفاعلات داخل التذكرة والتقييم
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
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not check_staff(interaction):
            await interaction.response.send_message("❌ ليس لديك صلاحية", ephemeral=True)
            return
        ticket = database["open_tickets"].get(str(interaction.channel.id))
        if ticket.get("claimed"):
            await interaction.response.send_message("⚠️ مستلمة مسبقاً", ephemeral=True)
            return
        ticket["claimed"] = interaction.user.id
        save_database()
        button.disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.send_message("👑 تم استلام التذكرة", ephemeral=True)

    @discord.ui.button(
        label="إغلاق",
        emoji="🔒",
        style=discord.ButtonStyle.red,
        custom_id="close_button_secure",
    )
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not check_staff(interaction):
            await interaction.response.send_message("❌ ليس لديك صلاحية", ephemeral=True)
            return
        await interaction.response.send_message(
            "🔒 يرجى تقييم الخدمة للإغلاق:",
            view=RatingView(interaction.channel.id),
            ephemeral=True,
        )


class RatingView(discord.ui.View):
    def __init__(self, ticket_channel_id):
        super().__init__(timeout=None)
        self.ticket_channel_id = ticket_channel_id

    async def save_rating(self, interaction, stars):
        channel = interaction.channel
        await interaction.response.send_message("⭐ شكراً لتقييمك، يتم الحذف...", ephemeral=True)
        await asyncio.sleep(2)
        try:
            await channel.delete()
        except Exception:
            pass

    @discord.ui.button(label="⭐ 5", style=discord.ButtonStyle.green, custom_id="rate_5")
    async def five(self, interaction, button):
        await self.save_rating(interaction, 5)


# ==================================
# أوامر التحكم داخل التذكرة
# ==================================
@bot.tree.command(name="close", description="إغلاق التذكرة")
async def close_ticket(interaction: discord.Interaction):
    if not check_staff(interaction):
        await interaction.response.send_message("❌ لا تملك صلاحية", ephemeral=True)
        return
    await interaction.response.send_message(
        "⭐ يرجى تقييم التذكرة قبل الإغلاق",
        view=RatingView(interaction.channel.id),
        ephemeral=True,
    )


@bot.tree.command(name="rename", description="تغيير اسم التذكرة")
async def rename_ticket(interaction: discord.Interaction, name: str):
    if not check_staff(interaction):
        await interaction.response.send_message("❌ لا تملك صلاحية", ephemeral=True)
        return
    await interaction.channel.edit(name=name)
    await interaction.response.send_message("✅ تم تغيير الاسم")


# ==================================
# تشغيل الأحداث والبوت
# ==================================
@bot.event
async def on_ready():
    print(f"✅ Bot Online: {bot.user}")
    for panel_id in database.get("panels", {}):
        try:
            bot.add_view(TicketPanel(panel_id))
        except Exception:
            pass
    bot.add_view(TicketButtons())
    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"✅ Commands Synced: {len(synced)}")
    except Exception as e:
        print(f"❌ Sync Error: {e}")


TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Discord Token is missing!")
