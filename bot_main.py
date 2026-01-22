import discord
from discord import app_commands
from discord.ext import tasks
from datetime import datetime, timedelta
import random
import io
import aiohttp
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from PIL import ImageOps
import os
from keep_alive import keep_alive
keep_alive()

TECH_SUPPORT_TRIGGERS = [
    "crash",
    "çöktü",
    "blue screen",
    "mavi ekran",
    "bsod",
    "boot",
    "açılmıyor",
    "açılmıyo",
    "dondu",
    "donuk",
    "lag giriyo",
    "lag giriyor",
    "fps drop",
    "fps düştü",
    "fps düşüşü",
]

TECH_SUPPORT_RESPONSES = [
    "aç kapa yaptın mı kral",
    "driverların güncel mi krşm",
    "hdmi kablosunu anakarta sokmadın di mi la",
    "ram indirsene",
    "kesin anakartı bozdun orosbucocu seni",
    "displayport tam takılı mı kanka",
    "windowsa güncelleme geldiyse ondandır knks",
]

MY_GUILD = discord.Object(id=1064253407172493362)


def deep_fry_logic(image_data):
    with Image.open(io.BytesIO(image_data)) as img:
        img = img.convert("RGB")

        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(10.0)

        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)

        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(3.0)

        output_buffer = io.BytesIO()
        img.save(output_buffer, format="JPEG", quality=10)
        output_buffer.seek(0)
        return output_buffer


def create_vintage_photo_logic(image_data):
    with Image.open(io.BytesIO(image_data)) as img:
        img = img.convert("RGB")

        base_width = 800
        w_percent = base_width / float(img.size[0])
        h_size = int((float(img.size[1]) * float(w_percent)))
        img_resized = img.resize((base_width, h_size), Image.NEAREST)

        enhancer = ImageEnhance.Contrast(img_resized)
        img_contrasted = enhancer.enhance(1.5)

        draw = ImageDraw.Draw(img_contrasted)
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except IOError:
            font = ImageFont.load_default()

        now = datetime.now()

        timestamp_text = now.strftime("%d/%m/2008  %I:%M %p")

        text_bbox = draw.textbbox((0, 0), timestamp_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = img_contrasted.width - text_width - 20
        y = img_contrasted.height - text_height - 20

        draw.text((x, y), timestamp_text, font=font, fill=(255, 165, 0))

        output_buffer = io.BytesIO()
        img_contrasted.save(output_buffer, format="JPEG", quality=85)
        output_buffer.seek(0)
        return output_buffer


class Client(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = app_commands.CommandTree(self)
        self.lol_start_times = {}

        self.safe_users = [905093594539515956, 691965492570619976, 1463936683354492948]

    async def setup_hook(self):
        self.check_league_playtime.start()
        self.tree.copy_global_to(guild=MY_GUILD)
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"[INFO] {current_time} | LOG KAYDI BAŞLADI")
        print(f"[DCLIENT] {current_time} | komutlar sunucuya yüklendi")

    async def on_ready(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"[DCLIENT] {current_time} | {self.user} olarak giriş yapıldı")

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing, name="League of Legends"
            )
        )

    async def on_message(self, message):
        if message.author == self.user:
            return

        msg_content = message.content.lower()

        if any(trigger in msg_content for trigger in TECH_SUPPORT_TRIGGERS):
            response = random.choice(TECH_SUPPORT_RESPONSES)
            await message.reply(response)

        if message.content == "!DEBUG-sync" and message.author.id == 691965492570619976:
            await message.channel.send("```KOMUT SENKRONİZASYON GİRİŞİMİ...```")
            try:
                self.tree.copy_global_to(guild=message.guild)
                synced = await self.tree.sync(guild=message.guild)
                await message.channel.send(
                    f"```{len(synced)} KOMUT BAŞARIYLA SENKRONİZE EDİLDİ.```"
                )
            except Exception as e:
                await message.channel.send(
                    f"```BAŞARISIZ, HATANIN DETAYLARI KONSOLA GÖNDERİLDİ.```"
                )
                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"[HATA] {current_time} | {e}")

        if (
            message.content.startswith("!DEBUG-safe ")
            and message.author.id == 384057562292813825
        ):
            if message.mentions:
                user_to_save = message.mentions[0]
                await message.channel.send(f"```KULLANICI TANIMLANIYOR...```")
                if user_to_save.id not in self.safe_users:
                    self.safe_users.append(user_to_save.id)
                    await message.channel.send(
                        f"```{user_to_save.name} SÜTTEN KULLANICILAR LİSTESİNE EKLENDİ.```"
                    )

    @tasks.loop(seconds=60)
    async def check_league_playtime(self):
        TARGET_GAME = "League of Legends"

        for guild in self.guilds:
            for member in guild.members:
                if member.bot:
                    continue

                is_bannable_league = False

                if member.activities:
                    for activity in member.activities:
                        if (
                            isinstance(activity, (discord.Game, discord.Activity))
                            and activity.name == TARGET_GAME
                        ):
                            details = getattr(activity, "details", "") or ""
                            state = getattr(activity, "state", "") or ""

                            if (
                                "Teamfight Tactics" in details
                                or "Teamfight Tactics" in state
                            ):
                                is_bannable_league = False
                                current_time = datetime.now().strftime("%H:%M:%S")
                                print(
                                    f"[MODERASYON] {current_time} | {member.name} TfT oynuyor, görmezden gelinecek"
                                )
                            else:
                                is_bannable_league = True

                            break

                if is_bannable_league:
                    if member.id in self.safe_users:
                        is_bannable_league = False

                user_id = member.id

                if is_bannable_league:
                    if user_id not in self.lol_start_times:
                        self.lol_start_times[user_id] = datetime.now()
                        current_time = datetime.now().strftime("%H:%M:%S")
                        print(
                            f"[MODERASYON] {current_time} | {member.name} LoL oynuyor, sayaç başlatıldı"
                        )
                    else:
                        limit = getattr(self, "ban_limit_minutes", 30)
                        duration = datetime.now() - self.lol_start_times[user_id]

                        if duration > timedelta(minutes=limit):
                            try:
                                current_time = datetime.now().strftime("%H:%M:%S")
                                await member.send(
                                    f"{limit} dakikadan uzun süre LoL oynadığın için ban yedin."
                                )
                                await guild.ban(member, reason="LoL Limiti Aşıldı")
                                print(
                                    f"[MODERASYON] {current_time} | {member.name} BANLANDI"
                                )
                                del self.lol_start_times[user_id]
                            except Exception as e:
                                current_time = datetime.now().strftime("%H:%M:%S")
                                print(
                                    f"[HATA] {current_time} | {member.name} banlanamadı: {e}"
                                )

                else:
                    if user_id in self.lol_start_times:
                        del self.lol_start_times[user_id]


# SLASH KOMUTLAR BAŞLIYOR


intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

client = Client(intents=intents)


@client.tree.command(name="ping", description="Botun gecikmesini ölç")
async def ping(interaction: discord.Interaction):
    latency_ms = round(client.latency * 1000)

    if latency_ms < 100:
        status = "Önemsiz seviyede gecikme"
    elif latency_ms < 300:
        status = "Kabul edilebilir gecikme"
    else:
        status = "Square Cloud sunucu sorunu yaşıyor olabilir"

    await interaction.response.send_message(f"{status} | Ping: **{latency_ms}ms**")


@client.tree.command(
    name="vintage", description="Foto at 2008 dijital kamera fotosu olsun"
)
@app_commands.describe(photo="İşlenecek fotoğraf")
async def vintage(interaction: discord.Interaction, photo: discord.Attachment):
    if not photo.content_type.startswith("image/"):
        await interaction.response.send_message(
            "Fotoğraf atmamışsın kral foto at", ephemeral=True
        )
        return

    await interaction.response.defer()

    try:
        image_data = await photo.read()
        processed_image_bytes = await client.loop.run_in_executor(
            None, create_vintage_photo_logic, image_data
        )
        file = discord.File(fp=processed_image_bytes, filename="vintage_2008.jpg")
        await interaction.followup.send(
            f"Buyur usta {interaction.user.mention}", file=file
        )
    except Exception as e:
        await interaction.followup.send(
            f"Foto dönüşürken sıkıntı çıktı usta, bi Eren'e danış istersen"
        )
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"[HATA] {current_time} | vintage fotoğraf hatası: {e}")


@client.tree.command(name="deepfry", description="Resim deep frylama komutu")
@app_commands.describe(photo="Deep frylanacak resim")
async def deepfry(interaction: discord.Interaction, photo: discord.Attachment):
    if not photo.content_type.startswith("image/"):
        await interaction.response.send_message(
            "Fotoğraf atmamışsın kral foto at", ephemeral=True
        )
        return

    await interaction.response.defer()

    try:
        image_data = await photo.read()
        processed_bytes = await client.loop.run_in_executor(
            None, deep_fry_logic, image_data
        )

        file = discord.File(fp=processed_bytes, filename="fried.jpg")
        await interaction.followup.send(file=file)
    except Exception as e:
        await interaction.followup.send(
            f"Foto deep frylanırken sıkıntı çıktı usta, konsola gönderiyorum hatayı Eren'e haber verirsin artık"
        )
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"[HATA] {current_time} | fotoğraf deepfry hatası: {e}")


@client.tree.command(name="avtr", description="İstediğin adamın profil fotosunu çal")
@app_commands.describe(user="Pfpsi alınacak kullanıcı")
async def avtr(interaction: discord.Interaction, user: discord.User):
    avatar_url = user.display_avatar.url

    embed = discord.Embed(
        title=f"{user.name} Kullanıcısının Profil Fotoğrafı",
        color=discord.Color.random(),
    )
    embed.set_image(url=avatar_url)

    await interaction.response.send_message(embed=embed)

try:
    token = os.environ["DISCORD_TOKEN"]
    client.run(token)
except KeyError:
    print("Error: DISCORD_TOKEN not found in environment variables.")
