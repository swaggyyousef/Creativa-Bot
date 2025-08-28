import json
from discord.ext import commands
from discord import app_commands, Interaction, Embed, Color
from discord.app_commands.errors import MissingPermissions
from dotenv import load_dotenv
import discord
import io
from modules.utils.mysql import execute_query

load_dotenv()

class AutoReply(commands.Cog):
    """A cog for auto-reply commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_guild_faq(self, guild_id: int) -> list:
        """
        Retrieve the list of QA pairs for the given guild.
        Returns an empty list if no row exists.
        """
        result = execute_query(
            "SELECT qa FROM faq WHERE guild_id = %s",
            (guild_id,),
            fetch_one=True
        )
        if result and result[0] and result[0][0] and len(result) > 0:
            try:
                return json.loads(result[0][0])
            except (KeyError, json.JSONDecodeError):
                return []
        return []

    def update_guild_faq(self, guild_id: int, faq_list: list) -> None:
        """
        Update the FAQ entry for the guild. If the guild row doesn't exist, insert a new row.
        """
        faq_json = json.dumps(faq_list)
        # Check if an entry exists for this guild
        result = execute_query(
            "SELECT guild_id FROM faq WHERE guild_id = %s",
            (guild_id,),
            fetch_one=True
        )
        if result and result[0]:
            execute_query(
                "UPDATE faq SET qa = %s WHERE guild_id = %s",
                (faq_json, guild_id)
            )
        else:
            execute_query(
                "INSERT INTO faq (guild_id, qa) VALUES (%s, %s)",
                (guild_id, faq_json)
            )

    @app_commands.command(
        name="qa_add",
        description="Create a new question-answer pair"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def qa_add(self, interaction: Interaction, question: str, answer: str):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        guild_id = interaction.guild.id
        faq_list = self.get_guild_faq(guild_id)

        # Determine a new ID: if the list is empty, start at 1; otherwise use max(current IDs) + 1.
        new_id = 1
        if faq_list:
            new_id = max(item.get("id", 0) for item in faq_list) + 1

        # Append the new QA pair
        faq_list.append({
            "id": new_id,
            "question": question,
            "answer": answer
        })

        # Update (or insert) the row in the database
        self.update_guild_faq(guild_id, faq_list)
        await interaction.response.send_message(f"QA pair added with ID {new_id}.", ephemeral=True)

    @app_commands.command(
        name="qa_remove",
        description="Remove a QA pair by its ID"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def qa_remove(self, interaction: Interaction, id: int):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        guild_id = interaction.guild.id
        faq_list = self.get_guild_faq(guild_id)

        if not faq_list:
            await interaction.response.send_message("No QA pairs found.", ephemeral=True)
            return

        # Remove the pair with the matching ID
        new_faq_list = [item for item in faq_list if item.get("id") != id]

        if len(new_faq_list) == len(faq_list):
            await interaction.response.send_message(f"No QA pair found with ID {id}.", ephemeral=True)
            return

        # Update the database
        self.update_guild_faq(guild_id, new_faq_list)
        await interaction.response.send_message(f"QA pair with ID {id} has been removed.", ephemeral=True)

    @app_commands.command(
        name="qa_list",
        description="List all the QA pairs with their IDs"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def qa_list(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        guild_id = interaction.guild.id
        faq_list = self.get_guild_faq(guild_id)

        if not faq_list:
            await interaction.response.send_message("No QA pairs found.", ephemeral=True)
            return

        embeds = []
        current_embed = Embed(title="QA Pairs", color=Color.blue())
        total_char_count = 0

        # Build embed pages as before
        for item in faq_list:
            question = item.get('question', 'No question provided')
            answer = item.get('answer', 'No answer provided')
            field_name = f"ID {item.get('id')}: {question}"
            field_value = answer

            # Check if adding this field would exceed Discord's embed limits
            if (len(current_embed.fields) >= 25 or
                total_char_count + len(field_name) + len(field_value) > 6000):
                embeds.append(current_embed)
                current_embed = Embed(title="QA Pairs (continued)", color=Color.blue())
                total_char_count = 0

            current_embed.add_field(name=field_name, value=field_value, inline=False)
            total_char_count += len(field_name) + len(field_value)

        # Append the last embed if it contains any fields
        if current_embed.fields:
            embeds.append(current_embed)

        # If the QA list is too long (i.e. more than one embed is needed), send a text file instead
        if len(embeds) > 1:
            file_content = ""
            for item in faq_list:
                question = item.get('question', 'No question provided')
                answer = item.get('answer', 'No answer provided')
                file_content += f"ID {item.get('id')}: {question}\n{answer}\n\n"
            # Create an in-memory text stream for the file
            file_buffer = io.StringIO(file_content)
            file = discord.File(file_buffer, filename="qa_list.txt")
            await interaction.response.send_message(
                content="The QA list is too long; please see the attached file.",
                file=file,
                ephemeral=True
            )
        else:
            # Otherwise, send a single embed
            await interaction.response.send_message(embed=embeds[0], ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoReply(bot))
