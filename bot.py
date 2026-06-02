
Bot · PY
import discord
from discord.ext import commands
import asyncio
 
TOKEN = "TOKEN"
 
WAITING_CHANNEL_ID = 1486151833067192362
SUPPORT_CHANNELS = [
    1486151829724070009,
    1486151830705803274,
    1486151831863300197,
]
 
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
 
bot = commands.Bot(command_prefix="!", intents=intents)
 
# قايمة تاع الناس اللي راهم يستناو
queue = asyncio.Queue()
# قايمة تاع السوبورت channels اللي خاوية
available_support = list(SUPPORT_CHANNELS)
lock = asyncio.Lock()
 
 
async def process_queue():
    """تاع كل شخص فالقايمة يوجهه لسوبورت خاوي"""
    while True:
        member = await queue.get()
        assigned = False
 
        while not assigned:
            async with lock:
                if available_support:
                    channel_id = available_support.pop(0)
                    assigned = True
 
            if assigned:
                guild = member.guild
                support_channel = guild.get_channel(channel_id)
                if support_channel and member.voice and member.voice.channel:
                    try:
                        await member.move_to(support_channel)
                        print(f"[+] {member.name} → {support_channel.name}")
                    except Exception as e:
                        print(f"[-] غلطة مع {member.name}: {e}")
                        async with lock:
                            available_support.append(channel_id)
            else:
                # ما كاناش سوبورت خاوي، استنا شوية وعاود
                await asyncio.sleep(1)
 
        queue.task_done()
 
 
@bot.event
async def on_ready():
    print(f"[✓] البوت شغال: {bot.user}")
    bot.loop.create_task(process_queue())
 
 
@bot.event
async def on_voice_state_update(member, before, after):
    # كي يدخل واحد وايتينغ سوبورت
    if after.channel and after.channel.id == WAITING_CHANNEL_ID:
        if before.channel is None or before.channel.id != WAITING_CHANNEL_ID:
            print(f"[~] {member.name} دخل وايتينغ سوبورت")
            await queue.put(member)
 
    # كي يخرج واحد من سوبورت، نرجعو للقايمة تاع الخاوين
    if before.channel and before.channel.id in SUPPORT_CHANNELS:
        if after.channel is None or after.channel.id not in SUPPORT_CHANNELS:
            async with lock:
                if before.channel.id not in available_support:
                    available_support.append(before.channel.id)
                    print(f"[~] {before.channel.name} رجع خاوي")
 
 
bot.run(TOKEN)
