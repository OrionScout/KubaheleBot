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
import sys
from collections import deque

keep_alive()

UYGAN_TRIGGERS = ["cagan uygan", "cağan uygan", "çagan uygan", "çağan uygan"]

CAGAN_TRIGGERS = ["cagan", "cağan", "çagan", "çağan"]

IP_DROP_TRIGGERS = [
    "bittin olum sen",
    "bittin oğlum sen",
    "bittin oglum sen",
    "bittin olm sen",
    "sen bittin olum",
    "sen bittin oğlum",
    "sen bittin oglum",
    "sen bittin olm",
]

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
    "ram indir knk",
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
            font = ImageFont.truetype("arial.ttf", 60)
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

        self.start_time = datetime.now()
        self.log_history = deque(maxlen=10)

        self.original_stdout = sys.stdout
        sys.stdout = self

        self.is_awake = True

        self.safe_users = [
            691965492570619976,
            1463936683354492948,
            384057562292813825,
            417264559645261826,
            540193259104894999,
        ]

        self.tracking_enabled = False

    def write(self, text):
        self.original_stdout.write(text)
        self.original_stdout.flush()

        if text.strip():
            clean_text = text.strip()
            self.log_history.append(f"{clean_text}")

    def flush(self):
        self.original_stdout.flush()

    async def setup_hook(self):
        self.check_league_playtime.start()
        self.tree.copy_global_to(guild=MY_GUILD)
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"[INFO] {current_time} | LOG KAYDI BAŞLADI")
        print(
            f"[UYARI] {current_time} | bot sunucusu Greenwich saatiyle çalıştığı için bütün log kayıtları Türkiye saatinden 3 saat geri gözükecektir"
        )
        print(f"[DCLIENT] {current_time} | komutlar sunucuya yüklendi")

    async def on_ready(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"[DCLIENT] {current_time} | {self.user} olarak giriş yapıldı")

        if self.is_awake:
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

        if any(trigger in msg_content for trigger in UYGAN_TRIGGERS):
            await message.reply("sey mi knk sevmeyip hala kalan ucube .d.d.d.dd.d")
            return

        if any(trigger in msg_content for trigger in CAGAN_TRIGGERS):
            await message.reply("*uzak dur")

        if any(trigger in msg_content for trigger in IP_DROP_TRIGGERS):
            panel_mesaj = """
IP: 92.28,211,263 M:43 7462 S
S Number. 6979191519182016 IPv
6: fe80:5ded: ef69 fb22:19888
UPNP Enabled W: 12 4898 DMZ: 1
0.112 42.15 MAC 5A783E7E.00 IS
P: Ucom Unversal DNS:8.8.8.8 A
LT DNS: 1.1.1.8.1 SUBNET MASK:
255.255.0.255 DNS SUFFIX: Dli
nk WAN: 100.23.10.15 N TYPE: P
rivate Nat GATEWAY: 192.168 01
UDP OPEN PORTS: 8080,80 TCP O
PEN PORTS: 443 ROUTER
VENDOR:
ERICCSON DEVICE VENDOR: WIN3 X
CONNECTION TYPE: Ethernet
ICM
PHOPS: 192.168.0.1 19216811 10
073434 host-66.12012111.ucom.c
om 36/13467.189
216.239.78111
sof02832-in-f14/1e100.net TOTA
L HOPS:8 ACTIVE SERVICES: HTTP
192.168.3.180-92.28.211.234:8
0 HTTP 192.168.3.1:443->92.28.
211.234:443 UDP 192.168.0.1.78
8->192.168.1. 1:6557 192.168.1
.1:67891->92.28.211.234:345 TC
P 192.168.54.43.7777-192.168 1
.17778 TCP 192.168.78.12:898->
192.168.89.966 EXTERNAL MAC 6
U 78:89 ER:04 MODEM JUMPS: 64
            """
            await message.channel.send(panel_mesaj)

        if message.content == "!DEBUG-sync" and message.author.id == 691965492570619976:
            await message.channel.send("```SENKRONİZASYON GİRİŞİMİ...```")
            try:
                self.tree.copy_global_to(guild=message.guild)
                synced = await self.tree.sync(guild=message.guild)
                await message.channel.send(
                    f"```{len(synced)} KOMUT VE EVENTLER BAŞARIYLA SENKRONİZE EDİLDİ.```"
                )
            except Exception as e:
                await message.channel.send(
                    f"```BAŞARISIZ, HATANIN DETAYLARI KONSOLA GÖNDERİLDİ.```"
                )
                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"[HATA] {current_time} | {e}")

        if (
            message.content == "!DEBUG-logcheck"
            and message.author.id == 691965492570619976
        ):
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"[DEBUG] {current_time} | LOG TEST MESAJI")
            await message.channel.send(
                f"```LOG TEST MESAJI GÖNDERİLDİ, LÜTFEN KONTROL EDİNİZ.```"
            )

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

    async def on_member_remove(self, member):
        KANAL_ID = 1395090932176781353

        channel = self.get_channel(KANAL_ID)

        if channel:
            message = f"{member.mention} sunucumuzdan cikmis umarim ailen kanserden olur senin o anayin"
            await channel.send(message)

    @tasks.loop(seconds=60)
    async def check_league_playtime(self):
        if not self.tracking_enabled:
            return
        
        if not self.is_awake:
            return

        if not hasattr(self, "tft_players"):
            self.tft_players = set()

        TARGET_GAME = "League of Legends"

        for guild in self.guilds:
            for member in guild.members:
                if member.bot:
                    continue

                is_bannable_league = False
                is_currently_playing_tft = False

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
                                is_currently_playing_tft = True
                                is_bannable_league = False
                            else:
                                is_bannable_league = True

                            break

                if is_currently_playing_tft:
                    if member.id not in self.tft_players:
                        current_time = datetime.now().strftime("%H:%M:%S")
                        print(
                            f"[MODERASYON] {current_time} | {member.name} TFT oynuyor, görmezden gelinecek"
                        )
                        self.tft_players.add(member.id)
                else:
                    if member.id in self.tft_players:
                        self.tft_players.discard(member.id)

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
                                await guild.ban(member, reason="LoL Limit Exceeded")
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
        status = "Render Hosting sunucu sorunu yaşıyor olabilir"

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


@client.tree.command(name="pfp", description="İstediğin kişinin profil fotosuna bak")
@app_commands.describe(user="Pfpsi alınacak kullanıcı")
async def pfp(interaction: discord.Interaction, user: discord.User):
    avatar_url = user.display_avatar.url

    embed = discord.Embed(
        title=f"{user.name} Kullanıcısının Profil Fotoğrafı",
        color=discord.Color.random(),
    )
    embed.set_image(url=avatar_url)

    await interaction.response.send_message(embed=embed)


@client.tree.command(name="durum", description="Botun durumu hakkında bilgiler")
async def durum(interaction: discord.Interaction):
    uptime = datetime.now() - client.start_time
    uptime_str = str(uptime).split(".")[0].replace("days", "gün").replace("day", "gün")
    ping = round(client.latency * 1000)

    if client.log_history:
        recent_logs = "\n".join(client.log_history)
    else:
        recent_logs = "Henüz log mesajı yok."

    if client.tracking_enabled:
        takip_durumu = ":red_circle: **AKTİF**"
    else:
        takip_durumu = ":green_circle: **KAPALI**"

    drembed = discord.Embed(
        title="Sistem Durumu",
        color=discord.Color.green(),
        timestamp=datetime.now(),
        description=f"""
# :stopwatch: Çalışma Süresi: {uptime_str}
# :shield: LoL Takibi: {takip_durumu}
# :signal_strength: Ping: {ping}ms
""",
    )

    drembed.set_thumbnail(url=client.user.display_avatar.url)

    drembed.add_field(
        name="""
Son Güncellemede Değişenler :memo:
(10.02.2026 | 19:08)
""",
        value="""
- Hosting kaynaklı LoL takip "amnezi"si düzeltildi.
- /kapan ve /açıl komutları eklendi.
- Bota frontal lob lobotomisi uygulandı. (Grok moment)
""",
    )

    drembed.add_field(
        name="Son 10 Log Kaydı :scroll:",
        value=f"```diff\n{recent_logs}\n```",
        inline=False,
    )

    await interaction.response.send_message(embed=drembed)


@client.tree.command(name="loltakibi", description="LoL banlama sistemini aç/kapa")
@app_commands.describe(state="LoL takibini AÇ veya KAPA")
@app_commands.choices(
    state=[
        app_commands.Choice(name="AÇ", value="on"),
        app_commands.Choice(name="KAPA", value="off"),
    ]
)
async def tracking_switch(
    interaction: discord.Interaction, state: app_commands.Choice[str]
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "you aint sneaky lil bro :v: :joy:", ephemeral=True
        )
        return

    if state.value == "on":
        client.tracking_enabled = True
        await interaction.response.send_message(
            ":white_check_mark: LoL Takibi **AÇIK.**"
        )
    else:
        client.tracking_enabled = False
        client.lol_start_times.clear()
        await interaction.response.send_message(
            ":x: LoL Takibi **KAPALI.** Ama hele bi açılsın..."
        )


@client.tree.command(name="kapan", description="Botu komaya sok")
async def uyu(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Gerekli izin(ler) eksik: Yönetici", ephemeral=True
        )
        return

    client.is_awake = False

    await client.change_presence(status=discord.Status.invisible)
    await interaction.response.send_message("```KAPANIYOR...```")

@client.tree.command(name="açıl", description="Botu uyandır")
async def uyan(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return

    client.is_awake = True
    
    await interaction.response.send_message("```AÇILIYOR...```")
    
    try:
        current_time = datetime.now().strftime("%H:%M:%S")
        synced = await client.tree.sync()
        await interaction.followup.send(f"```{len(synced)} KOMUT VE EVENTLER BAŞARIYLA SENKRONİZE EDİLDİ.```")
        print(f"[INFO] {current_time} | komutlar ve eventler /uyan komutu ile senkronize edildi")

    except Exception as e:
        await interaction.followup.send(f"```AÇILIŞ SENKRONİZASYONU BAŞARISIZ.```")
        print(f"[HATA] {current_time} | {e}")
    
    await client.change_presence(status=discord.Status.online, activity=discord.Game(name="League of Legends"))
    await interaction.followup.send("```BOT AÇIK. DURUMU GÖRMEK İÇİN: /durum```")


try:
    token = os.environ["DISCORD_TOKEN"]
    client.run(token)
except KeyError:
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"[HATA] {current_time} | DISCORD_TOKEN çevre değişkenlerinde bulunamadı")
