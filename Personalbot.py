import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio

# ============================================================
#   KONFIGURATION
# ============================================================

# Kanäle
RANG_LOG_KANAL_ID = 1534187183613804644
RANG_AENDERUNG_ID = 1524866437066395757

# Rollen
EINGESTELLT_ROLLE_ID = 1528863798361067592
GEKUENDIGT_ROLLE_ID = 1528863903273058416

ABMAHNUNG_1_ROLLE_ID = 1524866435313176738
ABMAHNUNG_2_ROLLE_ID = 1524866435296395333
ABMAHNUNG_3_ROLLE_ID = 1524866435296395332

# Rollen, die Slash‑Commands nutzen dürfen
ERLAUBTE_ROLLEN = [
    # Beispiel:
    # 123456789012345678,  # Teamleitung
    # 987654321098765432   # Admin
]

# ============================================================
#   BERECHTIGUNGEN
# ============================================================

def darf_nutzen(interaction):
    """Prüft, ob der Nutzer eine erlaubte Rolle hat."""
    if interaction.user.guild_permissions.administrator:
        return True
    return any(r.id in ERLAUBTE_ROLLEN for r in interaction.user.roles)

# ============================================================
#   EMBED DESIGN
# ============================================================

def make_embed(title, color, fields):
    """Erstellt ein einheitliches Embed im modernen Stil."""
    embed = discord.Embed(
        title=title,
        color=color
    )
    embed.set_footer(text="Personal-System • Automatisierte HR-Verwaltung")
    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3135/3135715.png")

    for name, value in fields:
        embed.add_field(name=name, value=value, inline=False)

    return embed

# ============================================================
#   PERSONAL‑COG
# ============================================================

class Personal(commands.Cog):
    """Enthält alle Personal‑Funktionen wie Einstellen, Kündigen usw."""

    def __init__(self, bot):
        self.bot = bot

    async def kanal_pruefen(self, interaction):
        if interaction.channel.id != RANG_AENDERUNG_ID:
            await interaction.response.send_message(
                "❌ Dieser Befehl darf nur im **Rang‑Änderungs‑Kanal** genutzt werden.",
                ephemeral=True
            )
            return False
        return True

    async def rechte_pruefen(self, interaction):
        if not darf_nutzen(interaction):
            await interaction.response.send_message(
                "❌ Du hast **keine Berechtigung**, diesen Befehl zu nutzen.",
                ephemeral=True
            )
            return False
        return True

    # ============================================================
    #   EINSTELLEN
    # ============================================================

    @app_commands.command(name="einstellen", description="Mitarbeiter einstellen")
    async def einstellen(self, interaction: discord.Interaction, mitarbeiter: discord.Member, rang: discord.Role):

        if not await self.rechte_pruefen(interaction): return
        if not await self.kanal_pruefen(interaction): return

        await mitarbeiter.add_roles(rang)

        eingestellt = interaction.guild.get_role(EINGESTELLT_ROLLE_ID)
        if eingestellt:
            await mitarbeiter.add_roles(eingestellt)

        kanal = interaction.guild.get_channel(RANG_LOG_KANAL_ID)

        embed = make_embed(
            "✅ Einstellung",
            discord.Color.green(),
            [
                ("👤 Mitarbeiter", mitarbeiter.mention),
                ("🎖️ Rang", rang.mention)
            ]
        )

        if kanal:
            await kanal.send(embed=embed)

        await interaction.response.send_message("✅ Mitarbeiter eingestellt.", ephemeral=True)

    # ============================================================
    #   BEFÖRDERN
    # ============================================================

    @app_commands.command(name="befoerdern", description="Mitarbeiter befördern")
    async def befoerdern(self, interaction: discord.Interaction, mitarbeiter: discord.Member, alter_rang: discord.Role, neuer_rang: discord.Role):

        if not await self.rechte_pruefen(interaction): return
        if not await self.kanal_pruefen(interaction): return

        await mitarbeiter.remove_roles(alter_rang)
        await mitarbeiter.add_roles(neuer_rang)

        kanal = interaction.guild.get_channel(RANG_LOG_KANAL_ID)

        embed = make_embed(
            "📈 Beförderung",
            discord.Color.green(),
            [
                ("👤 Mitarbeiter", mitarbeiter.mention),
                ("⬅️ Alter Rang", alter_rang.mention),
                ("➡️ Neuer Rang", neuer_rang.mention)
            ]
        )

        if kanal:
            await kanal.send(embed=embed)

        await interaction.response.send_message("📈 Mitarbeiter befördert.", ephemeral=True)

    # ============================================================
    #   DEGRADIEREN
    # ============================================================

    @app_commands.command(name="degradieren", description="Mitarbeiter degradieren")
    async def degradieren(self, interaction: discord.Interaction, mitarbeiter: discord.Member, alter_rang: discord.Role, neuer_rang: discord.Role):

        if not await self.rechte_pruefen(interaction): return
        if not await self.kanal_pruefen(interaction): return

        await mitarbeiter.remove_roles(alter_rang)
        await mitarbeiter.add_roles(neuer_rang)

        kanal = interaction.guild.get_channel(RANG_LOG_KANAL_ID)

        embed = make_embed(
            "📉 Degradierung",
            discord.Color.red(),
            [
                ("👤 Mitarbeiter", mitarbeiter.mention),
                ("⬅️ Alter Rang", alter_rang.mention),
                ("➡️ Neuer Rang", neuer_rang.mention)
            ]
        )

        if kanal:
            await kanal.send(embed=embed)

        await interaction.response.send_message("📉 Mitarbeiter degradiert.", ephemeral=True)

    # ============================================================
    #   KÜNDIGEN
    # ============================================================

    @app_commands.command(name="kuendigen", description="Mitarbeiter kündigen")
    async def kuendigen(self, interaction: discord.Interaction, mitarbeiter: discord.Member, grund: str):

        if not await self.rechte_pruefen(interaction): return
        if not await self.kanal_pruefen(interaction): return

        gekuendigt = interaction.guild.get_role(GEKUENDIGT_ROLLE_ID)

        for rolle in list(mitarbeiter.roles):
            if rolle.is_default():
                continue
            try:
                await mitarbeiter.remove_roles(rolle)
            except:
                pass

        if gekuendigt:
            await mitarbeiter.add_roles(gekuendigt)

        kanal = interaction.guild.get_channel(RANG_LOG_KANAL_ID)

        embed = make_embed(
            "❌ Kündigung",
            discord.Color.red(),
            [
                ("👤 Mitarbeiter", mitarbeiter.mention),
                ("📝 Grund", grund)
            ]
        )

        if kanal:
            await kanal.send(embed=embed)

        await interaction.response.send_message("❌ Mitarbeiter gekündigt.", ephemeral=True)

    # ============================================================
    #   ABMAHNUNG
    # ============================================================

    @app_commands.command(name="abmahnung", description="Mitarbeiter abmahnen")
    async def abmahnung(self, interaction: discord.Interaction, mitarbeiter: discord.Member, grund: str):

        if not await self.rechte_pruefen(interaction): return
        if not await self.kanal_pruefen(interaction): return

        rolle1 = interaction.guild.get_role(ABMAHNUNG_1_ROLLE_ID)
        rolle2 = interaction.guild.get_role(ABMAHNUNG_2_ROLLE_ID)
        rolle3 = interaction.guild.get_role(ABMAHNUNG_3_ROLLE_ID)

        stufe = "⚠️ 1. Abmahnung"

        if rolle1 and rolle1 not in mitarbeiter.roles:
            await mitarbeiter.add_roles(rolle1)

        elif rolle2 and rolle2 not in mitarbeiter.roles:
            if rolle1:
                await mitarbeiter.remove_roles(rolle1)
            await mitarbeiter.add_roles(rolle2)
            stufe = "⚠️ 2. Abmahnung"

        elif rolle3 and rolle3 not in mitarbeiter.roles:
            if rolle2:
                await mitarbeiter.remove_roles(rolle2)
            await mitarbeiter.add_roles(rolle3)
            stufe = "⚠️ 3. Abmahnung"

        kanal = interaction.guild.get_channel(RANG_LOG_KANAL_ID)

        embed = make_embed(
            "⚠️ Abmahnung",
            discord.Color.orange(),
            [
                ("👤 Mitarbeiter", mitarbeiter.mention),
                ("📋 Stufe", stufe),
                ("📝 Grund", grund)
            ]
        )

        if kanal:
            await kanal.send(embed=embed)

        await interaction.response.send_message(f"⚠️ {stufe} vergeben.", ephemeral=True)

# ============================================================
#   BOT‑START
# ============================================================

TOKEN = os.getenv("TOKEN")
intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    application_id=1534199436945920132
)

@bot.event
async def on_ready():
    print(f"Bot ist online als {bot.user}")
    await bot.tree.sync()

async def main():
    async with bot:
        await bot.add_cog(Personal(bot))
        await bot.start(TOKEN)

asyncio.run(main())

