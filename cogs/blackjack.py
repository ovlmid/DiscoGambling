import discord
from discord.ext import commands
from discord import app_commands
from discord import Interaction
import json

import random
#Setting up the cards
cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
cards_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]


#Function di update the blackjack table
def update_table(first_hand, first_hand_total, dealer_hand, dealer_total):
  embed = discord.Embed(
    title="BlackJack",  #Creating Embed table
    description="Your cards: \n" + ' '.join(first_hand) + "\nTotal = " +
    str(first_hand_total) + "\n\n" + "Dealer cards: \n" +
    ' '.join(dealer_hand) + "\nTotal = " + str(dealer_total))
  return embed


class Buttons(discord.ui.View):

  def __init__(self, *, timeout=180):
    super().__init__(timeout=timeout)

  @discord.ui.button(label="Hit", style=discord.ButtonStyle.red)
  async def hit(
    self,
    interaction: discord.Interaction,
    button: discord.ui.Button,
  ):
    with open(str(interaction.user.id) + ".json") as f:
      data = json.load(f)
    print('hit button pressed')

    # while not data["player_stand"] or not data["player_bust"]:
    #   if not data["first_hand_stand"] or not data["first_hand_bust"]:
    #     data["player_last_value"] = cards[random.randint(1, 12)]
    #     data["first_hand"].append(data["player_last_value"])
    #     data["first_hand_total"] = data["first_hand_total"] + cards_values[
    #       cards.index(data["player_last_value"])]

    #     embed = update_table(data["first_hand"], data["first_hand_total"],
    #                          data["dealer_hand"], data["dealer_total"])
    #     await interaction.response.edit_message(embed=embed)
    await interaction.response.send_message("ok")

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
    print("ok")
    #Initializing player
    first_hand = [  #First hand of the player in case of split or main hand
      Buttons.cards[random.randint(0, 12)],
      Buttons.cards[random.randint(0, 12)]
    ]

    second_hand = [first_hand[1]]  #Second hand of the player in case of split
    first_hand_total = Buttons.cards_values[Buttons.cards.index(
      first_hand[0])] + Buttons.cards_values[Buttons.cards.index(
        first_hand[1])]  #First hand or main total value
    second_hand_total = Buttons.cards_values[Buttons.cards.index(
      second_hand[0])]  #Second hand total value
    player_last_value = 0  #Player last value

    #Initializing dealer
    dealer_hand = [
      Buttons.cards[random.randint(0, 12)],
      Buttons.cards[random.randint(0, 12)]
    ]  #Dealer hand

    dealer_total = Buttons.cards_values[Buttons.cards.index(
      dealer_hand[0])] + Buttons.cards_values[Buttons.cards.index(
        dealer_hand[1])]  #Dealer hand total value

    #Player booleans
    first_hand_stand = False  #Main or first hand stands
    first_hand_bust = False  #Main or first hand busts
    first_hand_doubledown = False  #Main or first hand doubledown

    second_hand_stand = False  #Second hand stands
    second_hand_bust = False  #Second hand busts
    second_hand_doubledown = False  #Second hand doubledown

    player_stand = False  #Use this in case not split
    player_bust = False  #Use this in case not split

    split = False  #Player split

    #Dealer booleans
    dealer_stand = False  #Dealer stands
    dealer_bust = False  #Dealer bust

    #Embed
    embed = discord.Embed(
      title="BlackJack",  #Creating Embed table
      description="Your cards: \n" + ' '.join(first_hand) + "\nTotal = " +
      str(first_hand_total) + "\n\n" + "Dealer cards: \n" +
      ' '.join(dealer_hand) + "\nTotal = " + str(dealer_total))

    with open(str(interaction.user.id) + ".json", 'w') as f:
      data = {
        #player data
        "first_hand": first_hand,
        "second_hand": second_hand,
        "first_hand_total": first_hand_total,
        "second_hand_total": second_hand_total,
        "player_last_value": player_last_value,
        "first_hand_stand": first_hand_stand,
        "second_hand_stand": second_hand_stand,
        "player_stand": player_stand,
        "first_hand_bust": first_hand_bust,
        "second_hand_bust": second_hand_bust,
        "player_bust": player_bust,
        "first_hand_doubledown": first_hand_doubledown,
        "second_hand_doubledown": second_hand_doubledown,
        "split": split,

        #dealer data
        "dealer_hand": dealer_hand,
        "dealer_total": dealer_total,
        "dealer_bust": dealer_bust,
        "dealer_stand": dealer_stand
      }
      json.dump(data, f)

    await interaction.response.send_message(embed=embed, view=Buttons())


async def setup(bot):
  await bot.add_cog(BlackJack(bot),
                    guilds=[discord.Object(id=1031340606112411728)])
