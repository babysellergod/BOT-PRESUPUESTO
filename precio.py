import discord
from discord import app_commands
from discord.ext import commands

class Precio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.productos = {}

    @app_commands.command(name="precio", description="Calcula el precio según la cantidad y tipo de unidad")
    async def precio(self, interaction: discord.Interaction):
        modal = ProductoModal(self)
        await interaction.response.send_modal(modal)

# ---------- MODAL DEL PRODUCTO ----------
class ProductoModal(discord.ui.Modal, title="Agregar producto"):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog

        self.nombre = discord.ui.TextInput(label="Nombre del producto", placeholder="Ejemplo: Azúcar")
        self.precio = discord.ui.TextInput(label="Precio base (S/)", placeholder="Ejemplo: 10.00")
        self.tipo = discord.ui.TextInput(
            label="Tipo de medida (kg, litro o unidad)",
            placeholder="Ejemplo: kg", max_length=10
        )

        self.add_item(self.nombre)
        self.add_item(self.precio)
        self.add_item(self.tipo)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            nombre = str(self.nombre.value)
            precio = float(self.precio.value)
            tipo = self.tipo.value.lower()
            if tipo not in ["kg", "litro", "unidad"]:
                raise ValueError
        except ValueError:
            await interaction.response.send_message("⚠️ Ingresa datos válidos. Ejemplo: tipo = kg, litro o unidad.", ephemeral=True)
            return

        user_id = interaction.user.id
        self.cog.productos[user_id] = {"nombre": nombre, "precio": precio, "tipo": tipo}

        embed = discord.Embed(title="📦 Producto registrado", color=discord.Color.green())
        embed.add_field(name="🧾 Producto", value=nombre, inline=False)
        embed.add_field(name="💰 Precio base", value=f"S/ {precio:.2f} por {tipo}", inline=False)

        view = CalcularPrecioView(self.cog, nombre, precio, tipo)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# ---------- BOTÓN PARA SACAR PRECIO ----------
class CalcularPrecioView(discord.ui.View):
    def __init__(self, cog, nombre, precio, tipo):
        super().__init__(timeout=None)
        self.cog = cog
        self.nombre = nombre
        self.precio = precio
        self.tipo = tipo

    @discord.ui.button(label="📏 Sacar precio total", style=discord.ButtonStyle.primary)
    async def sacar_precio_total(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CantidadModal(self.nombre, self.precio, self.tipo)
        await interaction.response.send_modal(modal)

# ---------- MODAL DE CANTIDAD ----------
class CantidadModal(discord.ui.Modal):
    def __init__(self, nombre, precio, tipo):
        super().__init__(title="Calcular precio total")
        self.nombre = nombre
        self.precio = precio
        self.tipo = tipo

        self.cantidad = discord.ui.TextInput(label="Cantidad", placeholder="Ejemplo: 345", max_length=10)
        self.add_item(self.cantidad)

        # --- Cambia las opciones según el tipo base ---
        if tipo == "kg":
            self.unidades = ["kg", "gr"]
        elif tipo == "litro":
            self.unidades = ["L", "ml"]
        else:
            self.unidades = ["unidad"]

        # Si el producto no es por unidad, pide seleccionar unidad
        if tipo != "unidad":
            unidades_str = ", ".join(self.unidades)
            self.unidad = discord.ui.TextInput(
                label=f"Tipo de unidad ({unidades_str})",
                placeholder=f"Ejemplo: {self.unidades[0]}",
                max_length=5
            )
            self.add_item(self.unidad)
        else:
            self.unidad = None

    async def on_submit(self, interaction: discord.Interaction):
        try:
            cantidad = float(self.cantidad.value)
            unidad = self.unidad.value.lower() if self.unidad else "unidad"
        except ValueError:
            await interaction.response.send_message("⚠️ Ingresa una cantidad válida (número).", ephemeral=True)
            return

        if cantidad <= 0:
            await interaction.response.send_message("⚠️ La cantidad debe ser mayor que 0.", ephemeral=True)
            return

        # --- CONVERSIONES ---
        precio_total = None
        if self.tipo == "kg":
            if unidad == "kg":
                precio_total = self.precio * cantidad
            elif unidad == "gr":
                precio_total = self.precio * (cantidad / 1000)
        elif self.tipo == "litro":
            if unidad == "l":
                precio_total = self.precio * cantidad
            elif unidad == "ml":
                precio_total = self.precio * (cantidad / 1000)
        elif self.tipo == "unidad":
            precio_total = self.precio * cantidad

        if precio_total is None:
            await interaction.response.send_message("⚠️ Unidad incompatible con el tipo base.", ephemeral=True)
            return

        embed = discord.Embed(title="💵 Cálculo de Precio Total", color=discord.Color.blue())
        embed.add_field(name="🍬 Producto", value=self.nombre, inline=False)
        embed.add_field(name="📏 Cantidad", value=f"{cantidad} {unidad}", inline=True)
        embed.add_field(name="💰 Precio total", value=f"**S/ {precio_total:.2f}**", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

# ---------- SETUP ----------
async def setup(bot):
    await bot.add_cog(Precio(bot))
