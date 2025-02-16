import discord
from discord import app_commands
from discord.ext import commands
import wikipedia
import asyncio
import json
import urllib.parse

class ArticleView(discord.ui.View):
    def __init__(self, page, interaction):
        super().__init__(timeout=300)
        self.page = page
        self.paragraphs = page.content.split('\n\n')
        self.current_paragraph = 0
        self.original_interaction = interaction
        
        # Add paragraph selector
        options = []
        for i, p in enumerate(self.paragraphs[:25]):  # Discord limits to 25 options
            desc = p[:97] + "..." if len(p) > 100 else p
            options.append(discord.SelectOption(
                label=f"Paragraph {i+1}",
                description=desc,
                value=str(i)
            ))
        
        self.paragraph_select = discord.ui.Select(
            placeholder="Jump to paragraph...",
            options=options
        )
        self.paragraph_select.callback = self.paragraph_select_callback
        self.add_item(self.paragraph_select)

        # Add references button if available
        if page.references:
            references_button = discord.ui.Button(
                label=f"View References ({len(page.references)})",
                style=discord.ButtonStyle.secondary,
                custom_id="references"
            )
            references_button.callback = self.show_references
            self.add_item(references_button)

        # Add images button if available
        if page.images:
            images_button = discord.ui.Button(
                label=f"View Images ({len(page.images)})",
                style=discord.ButtonStyle.secondary,
                custom_id="images"
            )
            images_button.callback = self.show_images
            self.add_item(images_button)

    async def show_references(self, interaction: discord.Interaction):
        refs = self.page.references[:10]  # Limit to first 10 references
        embed = discord.Embed(
            title=f"References for {self.page.title}",
            description="\n\n".join(f"{i+1}. {ref}" for i, ref in enumerate(refs)),
            color=discord.Color.blue()
        )
        if len(self.page.references) > 10:
            embed.set_footer(text=f"Showing 10 of {len(self.page.references)} references")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def show_images(self, interaction: discord.Interaction):
        images = self.page.images[:10]  # Limit to first 10 images
        embed = discord.Embed(
            title=f"Images in {self.page.title}",
            description="\n".join(f"{i+1}. {img}" for i, img in enumerate(images)),
            color=discord.Color.blue()
        )
        if len(self.page.images) > 10:
            embed.set_footer(text=f"Showing 10 of {len(self.page.images)} images")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def paragraph_select_callback(self, interaction: discord.Interaction):
        selected_index = int(self.paragraph_select.values[0])
        self.current_paragraph = selected_index
        await self.update_paragraph(interaction)

    async def update_paragraph(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=self.page.title,
            description=self.paragraphs[self.current_paragraph],
            color=discord.Color.from_rgb(255, 255, 255)
        )
        embed.set_footer(text=f"Paragraph {self.current_paragraph + 1}/{len(self.paragraphs)}")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Next Paragraph", style=discord.ButtonStyle.primary)
    async def next_paragraph(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_paragraph < len(self.paragraphs) - 1:
            self.current_paragraph += 1
            await self.update_paragraph(interaction)
        else:
            button.disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send("No more paragraphs to display.", ephemeral=True)

    @discord.ui.button(label="Stop Reading", style=discord.ButtonStyle.danger)
    async def stop_reading(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Article reading stopped.", view=None, embed=None)
        self.stop()

class SearchView(discord.ui.View):
    def __init__(self, query: str, results: list, current_page: int = 0):
        super().__init__(timeout=300)
        self.query = query
        self.all_results = results
        self.current_page = current_page
        self.results_per_page = 5
        self.update_buttons()

    def update_buttons(self):
        # Clear existing buttons
        self.clear_items()
        
        # Add article buttons for current page
        start_idx = self.current_page * self.results_per_page
        current_results = self.all_results[start_idx:start_idx + self.results_per_page]
        
        for title in current_results:
            button = discord.ui.Button(label=title, style=discord.ButtonStyle.secondary)
            button.callback = lambda i, t=title: self.handle_article(i, t)
            self.add_item(button)

        # Add navigation buttons if needed
        if self.current_page > 0:
            prev_button = discord.ui.Button(label="Previous Results", style=discord.ButtonStyle.primary)
            prev_button.callback = self.previous_page
            self.add_item(prev_button)

        if (self.current_page + 1) * self.results_per_page < len(self.all_results):
            next_button = discord.ui.Button(label="More Results", style=discord.ButtonStyle.primary)
            next_button.callback = self.next_page
            self.add_item(next_button)

    async def handle_article(self, interaction: discord.Interaction, title: str):
        try:
            # Clean up the title for better API compatibility
            cleaned_title = title.replace(" (company)", "").strip()
            page = wikipedia.page(cleaned_title, auto_suggest=False)
            
            view = ArticleView(page, interaction)
            embed = discord.Embed(
                title=page.title,
                description=page.content.split('\n\n')[0],
                color=discord.Color.from_rgb(255, 255, 255)
            )
            embed.set_footer(text=f"Paragraph 1/{len(page.content.split('\n\n'))}")
            
            await interaction.response.edit_message(content=None, embed=embed, view=view)
        except Exception as e:
            await interaction.response.send_message(f"Error loading article: {str(e)}", ephemeral=True)

    async def previous_page(self, interaction: discord.Interaction):
        self.current_page = max(0, self.current_page - 1)
        self.update_buttons()
        await self.update_message(interaction)

    async def next_page(self, interaction: discord.Interaction):
        if (self.current_page + 1) * self.results_per_page < len(self.all_results):
            self.current_page += 1
            self.update_buttons()
            await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        start_idx = self.current_page * self.results_per_page
        current_results = self.all_results[start_idx:start_idx + self.results_per_page]
        
        embed = discord.Embed(
            title="Search Results",
            description="\n".join(f"{i+1}. {title}" for i, title in enumerate(current_results, start=start_idx + 1)),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Page {self.current_page + 1}/{(len(self.all_results) + self.results_per_page - 1) // self.results_per_page}")
        
        await interaction.response.edit_message(embed=embed, view=self)

class WikiBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = WikiBot()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.change_presence(activity=discord.Game(name="Reading Wiki Articles"))

@client.tree.command(name="search", description="Search Wikipedia articles")
async def search(interaction: discord.Interaction, query: str):
    try:
        # Get more results for pagination
        results = wikipedia.search(query, results=15)
        
        if not results:
            try:
                suggested = wikipedia.suggest(query)
                if suggested:
                    results = wikipedia.search(suggested, results=15)
            except:
                pass

        if not results:
            embed = discord.Embed(
                title="Error",
                description="No results found.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        view = SearchView(query, results)
        
        embed = discord.Embed(
            title="Search Results",
            description="\n".join(f"{i+1}. {title}" for i, title in enumerate(results[:5], start=1)),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Page 1/{(len(results) + 4) // 5}")
        
        await interaction.response.send_message(embed=embed, view=view)

    except Exception as e:
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="article", description="View article content")
async def article(interaction: discord.Interaction, title: str):
    try:
        page = wikipedia.page(title)
        view = ArticleView(page, interaction)
        
        embed = discord.Embed(
            title=page.title,
            description=page.content.split('\n\n')[0],
            color=discord.Color.from_rgb(255, 255, 255)
        )
        embed.set_footer(text=f"Paragraph 1/{len(page.content.split('\n\n'))}")
        
        await interaction.response.send_message(embed=embed, view=view)

    except wikipedia.exceptions.DisambiguationError as e:
        embed = discord.Embed(
            title="Disambiguation Error",
            description=str(e),
            color=discord.Color.yellow()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="Error",
            description=f"Error loading article: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

@client.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(client.latency * 1000)}ms")

@client.tree.command(name="about", description="About WikiBot")
async def about(interaction: discord.Interaction):
    embed = discord.Embed(
        title="About WikiBot",
        description="A Discord bot for searching and reading Wikipedia articles",
        color=discord.Color.blue()
    )
    embed.add_field(name="Developer", value="@DaManMikey")
    embed.add_field(name="Website", value="[nexas-development.vercel.app](https://nexas-development.vercel.app)")
    embed.add_field(name="GitHub", value="[GitHub/@DaDevMikey](https://github.com/DaDevMikey)")
    
    await interaction.response.send_message(embed=embed)

client.run('YOUR_BOT_TOKEN')  # Replace with your actual bot token
