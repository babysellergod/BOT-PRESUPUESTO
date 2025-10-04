import discord
from discord import app_commands
from discord.ext import commands

class Presupuesto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.presupuestos = {}  # Guarda insumos por usuario
        self.resultados = {}    # Guarda el total calculado por usuario

    @app_commands.command(name="presupuesto", description="Calcula el presupuesto de tus insumos con porcentajes fijos")
    async def presupuesto(self, interaction: discord.Interaction):
        view = PresupuestoView(self)
        await interaction.response.send_message(
            "🧾 **Panel de Presupuesto**\nAgrega tus insumos uno por uno:",
            view=view, ephemeral=True
        )

# ---------- INTERFAZ PRINCIPAL ----------
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

        desc_insumos = "\n".join([f"• {nombre}: S/ {precio:.2f}" for nombre, precio in insumos])

        embed = discord.Embed(title="📊 Cálculo de Presupuesto", color=discord.Color.green())
        embed.add_field(name="🧾 Insumos", value=desc_insumos or "Ninguno", inline=False)
        embed.add_field(name="💵 Costos directos", value=f"S/ {total_insumos:.2f}", inline=False)
        embed.add_field(name="🍴 Utensilios (30 %)", value=f"S/ {utensilios:.2f}", inline=True)
        embed.add_field(name="👷 Mano de obra (40 %)", value=f"S/ {mano_obra:.2f}", inline=True)
        embed.add_field(name="📦 Otros (30 %)", value=f"S/ {otros:.2f}", inline=True)
        embed.add_field(name="💰 Total final", value=f"**S/ {total_final:.2f}**", inline=False)

        view = PrecioUnitarioView(self.cog, total_final, insumos)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        # Guarda los resultados para el cálculo posterior
        self.cog.resultados[user_id] = total_final
        self.cog.presupuestos.pop(user_id, None)

# ---------- MODAL DE INSUMOS ----------
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

# ---------- BOTÓN Y MODAL DE PRECIO UNITARIO ----------
class PrecioUnitarioView(discord.ui.View):
    def __init__(self, cog, total_final, insumos):
        super().__init__(timeout=None)
        self.cog = cog
        self.total_final = total_final
        self.insumos = insumos

    @discord.ui.button(label="💸 Precio Unitario", style=discord.ButtonStyle.secondary)
    async def calcular_precio_unitario(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = PrecioUnitarioModal(self.total_final, self.insumos)
        await interaction.response.send_modal(modal)

class PrecioUnitarioModal(discord.ui.Modal, title="Calcular Precio Unitario"):
    def __init__(self, total_final, insumos):
        super().__init__()
        self.total_final = total_final
        self.insumos = insumos

        self.cantidad = discord.ui.TextInput(
            label="Cantidad de unidades producidas",
            placeholder="Ejemplo: 10", max_length=10
        )
        self.ganancia = discord.ui.TextInput(
            label="Porcentaje de ganancia (%)",
            placeholder="Ejemplo: 25", max_length=10
        )
        self.add_item(self.cantidad)
        self.add_item(self.ganancia)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            cantidad = int(self.cantidad.value)
            ganancia = float(self.ganancia.value)
        except ValueError:
            await interaction.response.send_message("⚠️ Ingresa valores válidos (números).", ephemeral=True)
            return

        if cantidad <= 0:
            await interaction.response.send_message("⚠️ La cantidad debe ser mayor que cero.", ephemeral=True)
            return

        precio_unitario = self.total_final / cantidad
        precio_final_con_ganancia = precio_unitario * (1 + ganancia / 100)

        desc_insumos = "\n".join([f"• {nombre}: S/ {precio:.2f}" for nombre, precio in self.insumos])

        embed = discord.Embed(title="💸 Precio Unitario Final", color=discord.Color.blue())
        embed.add_field(name="🧾 Insumos", value=desc_insumos or "Ninguno", inline=False)
        embed.add_field(name="🔹 Costo total (sin ganancia)", value=f"S/ {self.total_final:.2f}", inline=False)
        embed.add_field(name="📦 Cantidad de unidades", value=f"{cantidad}", inline=True)
        embed.add_field(name="📈 Ganancia", value=f"{ganancia:.0f} %", inline=True)
        embed.add_field(name="💰 Precio unitario con ganancia", value=f"**S/ {precio_final_con_ganancia:.2f}**", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

# ---------- SETUP ----------
async def setup(bot):
    await bot.add_cog(Presupuesto(bot))
