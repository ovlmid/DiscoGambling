import discord
from discord.ext import commands
from discord import app_commands
from discord import Interaction
import json

import random
#Setting up the cards
cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
cards_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]

#Creating or Updating table
def table(player_first_hand, player_first_hand_total, dealer_hand, dealer_total):
  embed = discord.Embed(
    title = "BlackJack",
    description = "Your hand: \n" + ' '.join(player_first_hand) + "\n" + 
                  "Total --> " + str(player_first_hand_total) + "\n\n" +
                  "Dealer hand\n" + dealer_hand[0] + ' #' + "\n",
    color = discord.Color.red()
  )
  embed.set_footer(text="-DiscoGambling")
  return embed

#Updating table after dealer move
def end_table(player_first_hand, player_first_hand_total, dealer_hand, dealer_total):
  embed = discord.Embed(
    title = "BlackJack",
    description = "Your hand: \n" + ' '.join(player_first_hand) + "\n" + 
                  "Total: " + str(player_first_hand_total) + "\n\n" +
                  "Dealer hand\n" + ' '.join(dealer_hand) + "\n" + 
                  "Dealer total: " + str(dealer_total),
    color = discord.Color.red()
  )
  embed.set_footer(text="-DiscoGambling")
  return embed

def check_bust(total):
  if total > 21:
    return True
  else:
    return False

def check_dealer_stand(total):
  if total < 17:
    return False
  else:
    return True

def dealer_phase(id):
  with open(str(id) + ".json") as file: #Opens userid.json and store data in data
      data = json.load(file)

  while not data["dealer_bust"] and not data["dealer_stand"]:
    last_value = cards[random.randint(1,12)]
    data["dealer_hand"].append(last_value)
    data["dealer_total"] = data["dealer_total"] + cards_values[cards.index(last_value)]

    data["dealer_bust"] = check_bust(data["dealer_total"])
    data["dealer_stand"] = check_dealer_stand(data["dealer_total"])

  with open(str(id) + ".json", 'w') as file: #Updates userid.json
        json.dump(data, file)

class Buttons(discord.ui.View):
  def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

  #Button for hit
  @discord.ui.button(label="Hit",style=discord.ButtonStyle.blurple)
  async def hit(self,interaction:discord.Interaction, button:discord.ui.Button,):
      with open(str(interaction.user.id) + ".json") as file: #Opens user.id json and store data in data
        data = json.load(file)

      if not data["player_stand"] and not data["player_bust"]: #Checks if player have not busted or standed
        last_value = cards[random.randint(1, 12)] #Gets a new value
        data["player_first_hand"].append(last_value) #Appends the new value to player first hand
        data["player_first_hand_total"] = data["player_first_hand_total"] + cards_values[cards.index(last_value)] #Calculate new total first hand

        data["player_bust"] = check_bust(data["player_first_hand_total"])
        
        with open(str(interaction.user.id) + ".json", 'w') as file: #Updates userid.json
          json.dump(data, file)

        embed = table(data["player_first_hand"], data["player_first_hand_total"], data["dealer_hand"], data["dealer_total"]) #Updating table
        if not data["player_bust"]:
          await interaction.response.edit_message(embed = embed) #Posting updated table
        else:
          embed = end_table(data["player_first_hand"], data["player_first_hand_total"], data["dealer_hand"], data["dealer_total"]) #Updating table
          await interaction.response.edit_message(embed = embed, view=None) #Posting updated table
          

  #Button for stand
  @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
  async def stand(self,interaction:discord.Interaction, button:discord.ui.Button,):
      dealer_phase(interaction.user.id)
      with open(str(interaction.user.id) + ".json") as file: #Opens userid.json and store data in data
        data = json.load(file)

      data["player_stand"] = True #Sets player stand on true
      
      with open(str(interaction.user.id) + ".json", 'w') as file: #Saves new data
          json.dump(data, file)

      embed = end_table(data["player_first_hand"], data["player_first_hand_total"], data["dealer_hand"], data["dealer_total"]) #Updating table
      await interaction.response.edit_message(embed = embed, view = None)

  #Button for doubledown
  @discord.ui.button(label="Double-Down", style=discord.ButtonStyle.green)
  async def doubledown(self,interaction:discord.Interaction, button:discord.ui.Button,):
    with open(str(interaction.user.id) + ".json") as file: #Opens userid.json and store data in data
        data = json.load(file)

    if not len(data["player_first_hand"]) > 2:
        dealer_phase(interaction.user.id)
        last_value = cards[random.randint(1, 12)] #Gets a new value
        data["player_first_hand"].append(last_value) #Appends the new value to player first hand
        data["player_first_hand_total"] = data["player_first_hand_total"] + cards_values[cards.index(last_value)] #Calculate new total first hand

        data["player_bust"] = check_bust(data["player_first_hand_total"])
        data["player_stand"] = True
        with open(str(interaction.user.id) + ".json", 'w') as file: #Updates userid.json
          json.dump(data, file)

        embed = end_table(data["player_first_hand"], data["player_first_hand_total"], data["dealer_hand"], data["dealer_total"]) #Updating table
        await interaction.response.edit_message(embed = embed, view=None) #Posting updated table

  #Button for split
  @discord.ui.button(label="Split", style=discord.ButtonStyle.danger)
  async def split(self,interaction:discord.Interaction, button:discord.ui.Button,):
    with open(str(interaction.user.id) + ".json") as file: #Opens userid.json and store data in data
        data = json.load(file)
    
class BlackJack(commands.Cog):

  def __init__(self, bot):  #Setting the bot
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    print("BlackJack cog has been loaded")

  @commands.command()
  async def sync(self, ctx) -> None:
    fmt = await ctx.bot.tree.sync(guild=ctx.guild)

    await ctx.send(f"Synced {len(fmt)} commands to the current guild.")
    return

  @commands.command()
  async def unsync(self, ctx) -> None:
    ctx.bot.tree.clear_commands(guild=ctx.guild)
    fmt = await ctx.bot.tree.sync(guild=ctx.guild)
    await ctx.send(f"Unsynced {len(fmt)} commands to the current guild.")
    return

  #Command
  @app_commands.command(name="blackjack",
                        description="Play a game of blackjack")
  async def blackjack(self, interaction: discord.Interaction):
    print("/blackjack has been triggered") #logs

    #Creating json data
    data = {
        #Player hands
        "player_first_hand": [cards[random.randint(1,12)], cards[random.randint(1,12)]],
        "player_second_hand": ['A'],
  
        #Player totals
        "player_first_hand_total": 2,
        "player_second_hand_total": 2,
  
        #Player events:
        "player_first_hand_bust": False,
        "player_second_hand_bust": False,
        "player_bust": False,
  
        "player_first_hand_stand": False,
        "player_second_hand_stand": False,
        "player_stand": False,
  
        "player_doubledown": False,
        "player_split": False,
  
        #Dealer hands
        "dealer_hand": [cards[random.randint(1,12)], cards[random.randint(1,12)]],
  
        #Deaer totals
        "dealer_total": 2,
  
        #Dealer events
        "dealer_stand": False,
        "dealer_bust": False
      }

    data["player_first_hand_total"] = cards_values[cards.index(data["player_first_hand"][0])] + cards_values[cards.index(data["player_first_hand"][1])]
    data["dealer_total"] = cards_values[cards.index(data["dealer_hand"][0])] + cards_values[cards.index(data["dealer_hand"][1])]
    
    #Storing variables
    with open(str(interaction.user.id) + ".json", 'w') as f:
      json.dump(data, f) #Dumping data

    embed = table(data["player_first_hand"], data["player_first_hand_total"], data["dealer_hand"], data["dealer_total"])
    await interaction.response.send_message(embed = embed, view=Buttons())


async def setup(bot):
  await bot.add_cog(BlackJack(bot),
                    guilds=[discord.Object(id=1031340606112411728)])
