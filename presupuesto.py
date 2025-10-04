import discord
from discord import app_commands
from discord.ext import commands

class Presupuesto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.presupuestos = {}  # Guarda los insumos por usuario

    @app_commands.command(name="presupuesto", description="Calcula el presupuesto de tus insumos con porcentajes fijos")
    async def presupuesto(self, interaction: discord.Interaction):
        view = PresupuestoView(self)
        await interaction.response.send_message("🧾 **Panel de Presupuesto**\nAgrega tus insumos uno por uno:", view=view, ephemeral=True)


class PresupuestoView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
        self.user_id = None

    @discord.ui.button(label="➕ Agregar insumo", style=discord.ButtonStyle.primary)
    async def agregar_insumo(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.user_id = interaction.user.id
        modal = InsumoModal(self.cog, self)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="💰 Costos totales", style=discord.ButtonStyle.success)
    async def calcular_totales(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        insumos = self.cog.presupuestos.get(user_id, [])
        if not insumos:
            await interaction.response.send_message("⚠️ No agregaste ningún insumo.", ephemeral=True)
            return

        total_insumos = sum(precio for _, precio in insumos)
        utensilios = total_insumos * 0.30
        mano_obra = total_insumos * 0.40
        otros = total_insumos * 0.30
        total_final = total_insumos + utensilios + mano_obra + otros

        desc_insumos = "\n".join([f"• {nombre}: {precio:.2f}" for nombre, precio in insumos])

        embed = discord.Embed(title="📊 Cálculo de Presupuesto", color=discord.Color.green())
        embed.add_field(name="🧾 Insumos", value=desc_insumos or "Ninguno", inline=False)
        embed.add_field(name="💵 Costos directos", value=f"{total_insumos:.2f}", inline=False)
        embed.add_field(name="🍴 Utensilios (30 %)", value=f"{utensilios:.2f}", inline=True)
        embed.add_field(name="👷 Mano de obra (40 %)", value=f"{mano_obra:.2f}", inline=True)
        embed.add_field(name="📦 Otros (30 %)", value=f"{otros:.2f}", inline=True)
        embed.add_field(name="💰 Total final", value=f"**{total_final:.2f}**", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.cog.presupuestos.pop(user_id, None)  # Limpia los insumos del usuario


class InsumoModal(discord.ui.Modal, title="Agregar insumo"):
    def __init__(self, cog, view):
        super().__init__()
        self.cog = cog
        self.view = view

        self.nombre = discord.ui.TextInput(label="Nombre del insumo", placeholder="Ejemplo: Azúcar", max_length=50)
        self.precio = discord.ui.TextInput(label="Costo (S/)", placeholder="Ejemplo: 5.50", max_length=10)

        self.add_item(self.nombre)
        self.add_item(self.precio)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            nombre = str(self.nombre.value)
            precio = float(self.precio.value)
        except ValueError:
            await interaction.response.send_message("⚠️ Ingresa un número válido en el costo.", ephemeral=True)
            return

        user_id = self.view.user_id
        if user_id not in self.cog.presupuestos:
            self.cog.presupuestos[user_id] = []
        self.cog.presupuestos[user_id].append((nombre, precio))

        await interaction.response.send_message(f"✅ Insumo agregado: **{nombre}** – S/ {precio:.2f}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Presupuesto(bot))
