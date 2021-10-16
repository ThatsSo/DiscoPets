from discord.ext import commands
import random
import discord
from discord import Client, Intents, Embed
from discord.app import Option
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
import asyncio
import sqlite3
from sqlite3 import OperationalError
import datetime
import tweepy 
import math
import json

bot = commands.Bot(command_prefix='>', case_insensitive=True, help_command=None)
slash = SlashCommand(bot, sync_commands=True)
loop = asyncio.get_event_loop()
epoch = datetime.datetime.utcfromtimestamp(0)

f = open('data.json',)
data = json.load(f)
f.close()

consumer_key =str(data['consumerkey'])
consumer_secret =str(data['consumersecret'])
access_token =str(data['token'])
access_token_secret =str(data['tokensecret'])

cooldowns = {

}

cooldowns2 = {

}

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')
	game = discord.Game("Type >register to start!")
	await bot.change_presence(status=discord.Status.idle, activity=game)
	#dsn = 'Driver=SQLite3 ODBC Driver;Database=BlueDB.db'
	bot.conn = sqlite3.connect("BlueDB.db")
	bot.cur = bot.conn.cursor()

#register
@bot.command()
async def register(ctx):
	query = "INSERT OR IGNORE INTO Users (User_Id) VALUES (" + str(ctx.message.author.id) + ");"
	bot.cur.execute(query)
	await ctx.send("Registered successfully!\nGo to `>Shop` or `>Habitats` to get your first pet!\nType `>Pets` to see your pets\nUse `>Daily` to get 200 currency once a day\nUse `>Currency` to check your balance\nCheck `>help for the full list of commands")
	bot.conn.commit()

@bot.slash_command(guild_ids=[645092549366644766], name="start", description="Required to get started!")
async def register(ctx):
	query = "INSERT OR IGNORE INTO Users (User_Id) VALUES (" + str(ctx.author.id) + ");"
	bot.cur.execute(query)
	await ctx.send("Registered successfully!\nGo to `>Shop` or `>Habitats` to get your first pet!\nType `>Pets` to see your pets\nUse `>Daily` to get 200 currency once a day\nUse `>Currency` to check your balance\nCheck `>help for the full list of commands")
	bot.conn.commit()
	
#daily
@bot.command()
async def daily(ctx):
	bot.cur.execute("SELECT Last_Daily FROM Users WHERE User_ID=" + str(ctx.message.author.id) + ";")
	result = bot.cur.fetchall()
	datenow = datetime.datetime.now()
	print(datenow)
	if result[0][0] != datenow.day:
		query = "UPDATE Users SET Last_Daily=" +  str(datenow.day) + " WHERE User_ID=" + str(ctx.message.author.id) + ";"
		bot.cur.execute(query)
		query = "UPDATE Users SET Currency=Currency + 200 WHERE User_ID=" + str(ctx.message.author.id) + ";"
		bot.cur.execute(query)
		await ctx.send("Balance increased by 200!")
		bot.conn.commit()
	else:
		await ctx.send("Sorry, come back the next day!\nCurrent bot time is " + str(datenow.hour) + ":" + str(datenow.minute))
		
@bot.slash_command(guild_ids=[645092549366644766])
async def daily(ctx):
	bot.cur.execute("SELECT Last_Daily FROM Users WHERE User_ID=" + str(ctx.author.id) + ";")
	result = bot.cur.fetchall()
	datenow = datetime.datetime.now()
	if result[0][0] != datenow.day:
		query = "UPDATE Users SET Last_Daily=" +  str(datenow.day) + " WHERE User_ID=" + str(ctx.author.id) + ";"
		bot.cur.execute(query)
		query = "UPDATE Users SET Currency=Currency + 200 WHERE User_ID=" + str(ctx.author.id) + ";"
		bot.cur.execute(query)
		await ctx.send("Balance increased by 200!")
		bot.conn.commit()
	else:
		await ctx.send("Sorry, come back the next day!\nCurrent bot time is " + str(datenow.hour) + ":" + str(datenow.minute))

#currency
@bot.command()
async def currency(ctx):
	bot.cur.execute("SELECT Currency FROM Users WHERE User_ID=" + str(ctx.message.author.id) + ";")
	result = bot.cur.fetchall()
	await ctx.send("You currently have " + str(int(result[0][0])) + " currency")

@bot.slash_command(guild_ids=[645092549366644766])
async def currency(ctx):
	bot.cur.execute("SELECT Currency FROM Users WHERE User_ID=" + str(ctx.author.id) + ";")
	result = bot.cur.fetchall()
	await ctx.send("You currently have " + str(int(result[0][0])) + " currency")
		
#main
@bot.command()
async def main(ctx, arg):
	bot.cur.execute("SELECT Owner_ID FROM Pets WHERE Pet_ID=" + arg + ";")
	result = bot.cur.fetchall()
	if result[0][0] == str(ctx.message.author.id):
		query = "UPDATE Users SET Main_Pet_ID=" +  (arg) + " WHERE User_ID=" + str(ctx.message.author.id) + ";"
		bot.cur.execute(query)
		bot.conn.commit()
		await ctx.send("Pet #" + arg + " set as main pet!")
	else: 
		await ctx.send("Hey! That isn't your pet!")

@bot.slash_command(guild_ids=[645092549366644766])
async def main(ctx, pet_id: str):
	bot.cur.execute("SELECT Owner_ID FROM Pets WHERE Pet_ID=" + str(pet_id) + ";")
	result = bot.cur.fetchall()
	if result[0][0] == str(ctx.author.id):
		query = "UPDATE Users SET Main_Pet_ID=" +  str(pet_id) + " WHERE User_ID=" + str(ctx.author.id) + ";"
		bot.cur.execute(query)
		bot.conn.commit()
		await ctx.send("Pet #" + str(pet_id) + " set as main pet!")
	else: 
		await ctx.send("Hey! That isn't your pet!")
		
#pets
@bot.command()
async def pets(ctx, *arg):
	bot.cur.execute("SELECT Pet_ID, COUNT(*) FROM Pets WHERE OWNER_ID=" + str(ctx.message.author.id) + ";")
	owned = bot.cur.fetchall()
	page = int(math.ceil(int(owned[0][1]) / 12 ))
	multi = 1
	try:
		if arg[0] == "last" :
			multi = page
		else:
			multi = int(arg[0])
	except IndexError:
		pass
	start = (multi - 1) * 12
	stop = multi * 12
	bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits,Species_ID FROM Pets WHERE OWNER_ID=" + str(ctx.message.author.id) + " LIMIT " + str(start) + "," + str(stop) + ";")
	result = bot.cur.fetchall()
	embed=discord.Embed(title="Your Pets (" + str(multi) + "/" + (str(page)) + ")", color=0xFF5733)
	tally = 0
	for postpet in result:
		bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(postpet[4]) + ";")
		cmoji = bot.cur.fetchall()
		embed.add_field(name=str(cmoji[0][0]) + " " + str(postpet[1]), value="**ID #**" + str(postpet[0]) + "\n**Level:** " + str(postpet[2]) + "\n**LV Tokens: **" + str(postpet[3]), inline=True)
		tally = tally + 1
		if tally == 12:
			break
	await ctx.send(embed=embed)

@bot.slash_command(guild_ids=[645092549366644766])
async def pets(ctx, page: Option(str, "Not required", required=False)):
	bot.cur.execute("SELECT Pet_ID, COUNT(*) FROM Pets WHERE OWNER_ID=" + str(ctx.author.id) + ";")
	owned = bot.cur.fetchall()
	pageO = int(math.ceil(int(owned[0][1]) / 12 ))
	multi = 1
	try:
		if str(page) == "last" :
			multi = pageO
		else:
			multi = int(str(page))
	except IndexError:
		pass
	start = (multi - 1) * 12
	stop = multi * 12
	bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits,Species_ID FROM Pets WHERE OWNER_ID=" + str(ctx.author.id) + " LIMIT " + str(start) + "," + str(stop) + ";")
	result = bot.cur.fetchall()
	embed=discord.Embed(title="Your Pets (" + str(multi) + "/" + (str(page)) + ")", color=0xFF5733)
	tally = 0
	for postpet in result:
		bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(postpet[4]) + ";")
		cmoji = bot.cur.fetchall()
		embed.add_field(name=str(cmoji[0][0]) + " " + str(postpet[1]), value="**ID #**" + str(postpet[0]) + "\n**Level:** " + str(postpet[2]) + "\n**LV Tokens: **" + str(postpet[3]), inline=True)
		tally = tally + 1
		if tally == 12:
			break
	await ctx.send(embed=embed)
	
#pet
@bot.command()
async def pet(ctx, *arg):
	try:
		bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits,Species_ID,Owner_ID FROM Pets WHERE Pet_ID=" + str(arg[0]) + ";")
		info = bot.cur.fetchall()
		bot.cur.execute("SELECT Image_Link,Species_Name FROM Species WHERE Species_ID=" + str(info[0][4]) + ";")
		imglink = bot.cur.fetchall()
		user = await bot.fetch_user(str(info[0][5]))
		embed=discord.Embed(description="**Owner:** " + str(user) + "\n**Level:** " + str(int(info[0][2])) + " **LV Tokens: **" + str(int(info[0][3])) + "\n**ID #**" + str(info[0][0]), color=0x109319)
		embed.set_author(name=str(info[0][1]) + " the " + str(imglink[0][1]))
		embed.set_thumbnail(url=imglink[0][0])
		await ctx.send(embed=embed)
	except IndexError:
		pass
		bot.cur.execute("SELECT Main_Pet_ID FROM Users WHERE User_ID=" + str(ctx.message.author.id) + ";")
		mainpet = bot.cur.fetchall()
		bot.cur.execute("SELECT Species_ID FROM Pets WHERE Pet_ID=" + str(mainpet[0][0]) + ";")
		petspecies = bot.cur.fetchall()
		bot.cur.execute("SELECT Image_Link,Species_Name FROM Species WHERE Species_ID=" + str(petspecies[0][0]) + ";")
		imglink = bot.cur.fetchall()
		bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits FROM Pets WHERE Pet_ID=" + str(mainpet[0][0]) + ";")
		info = bot.cur.fetchall()
		user = await bot.fetch_user(str(ctx.message.author.id))
		embed=discord.Embed(description="**Owner:** " + str(user) + "\n**Level:** " + str(int(info[0][2])) + " **LV Tokens: **" + str(int(info[0][3])) + "\n**ID #**" + str(mainpet[0][0]), color=0x109319)
		embed.set_author(name=str(info[0][1]) + " the " + str(imglink[0][1]))
		embed.set_thumbnail(url=imglink[0][0])
		await ctx.send(embed=embed)
	
@bot.slash_command(guild_ids=[645092549366644766])
async def pet(ctx, pet_id: Option(str, "Not required", required=False)):
	try:
		bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits,Species_ID,Owner_ID FROM Pets WHERE Pet_ID=" + str(pet_id) + ";")
		info = bot.cur.fetchall()
		bot.cur.execute("SELECT Image_Link,Species_Name FROM Species WHERE Species_ID=" + str(info[0][4]) + ";")
		imglink = bot.cur.fetchall()
		user = await bot.fetch_user(str(info[0][5]))
		embed=discord.Embed(description="**Owner:** " + str(user) + "\n**Level:** " + str(int(info[0][2])) + " **LV Tokens: **" + str(int(info[0][3])) + "\n**ID #**" + str(info[0][0]), color=0x109319)
		embed.set_author(name=str(info[0][1]) + " the " + str(imglink[0][1]))
		embed.set_thumbnail(url=imglink[0][0])
		await ctx.send(embed=embed)
	except OperationalError:
		pass
		bot.cur.execute("SELECT Main_Pet_ID FROM Users WHERE User_ID=" + str(ctx.author.id) + ";")
		mainpet = bot.cur.fetchall()
		bot.cur.execute("SELECT Species_ID FROM Pets WHERE Pet_ID=" + str(mainpet[0][0]) + ";")
		petspecies = bot.cur.fetchall()
		bot.cur.execute("SELECT Image_Link,Species_Name FROM Species WHERE Species_ID=" + str(petspecies[0][0]) + ";")
		imglink = bot.cur.fetchall()
		bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits FROM Pets WHERE Pet_ID=" + str(mainpet[0][0]) + ";")
		info = bot.cur.fetchall()
		user = await bot.fetch_user(str(ctx.author.id))
		embed=discord.Embed(description="**Owner:** " + str(user) + "\n**Level:** " + str(int(info[0][2])) + " **LV Tokens: **" + str(int(info[0][3])) + "\n**ID #**" + str(mainpet[0][0]), color=0x109319)
		embed.set_author(name=str(info[0][1]) + " the " + str(imglink[0][1]))
		embed.set_thumbnail(url=imglink[0][0])
		await ctx.send(embed=embed)
		
#name
@bot.command()
async def name(ctx, arg, *, args):
	if len(args) <= 12:
		query = "UPDATE Pets SET Pet_Name=\"" + args + "\" WHERE Pet_ID=\"" + arg + "\" AND OWNER_ID=" + str(ctx.message.author.id) + ";"
		bot.cur.execute(query)
		bot.conn.commit()
		await ctx.send("Name changed successfully!")
	else:
		await ctx.send("Sorry! Names can be 12 characters long at most!")
		
@bot.slash_command(guild_ids=[645092549366644766])
async def name(ctx, pet_id: str, name: str):
	if len(str(name)) <= 12:
		query = "UPDATE Pets SET Pet_Name=\"" + str(name) + "\" WHERE Pet_ID=\"" + str(pet_id) + "\" AND OWNER_ID=" + str(ctx.author.id) + ";"
		bot.cur.execute(query)
		bot.conn.commit()
		await ctx.send("Name changed successfully!")
	else:
		await ctx.send("Sorry! Names can be 12 characters long at most!")

#buy
@bot.command()
async def buy(ctx, *, arg):
	bot.cur.execute("SELECT Species_ID,Cost FROM Store WHERE Species_Name LIKE \"" + arg + "\" AND Available=1;")
	purch = bot.cur.fetchall()
	bot.cur.execute("SELECT Currency FROM Users WHERE User_ID=" + str(ctx.message.author.id) + ";")
	result = bot.cur.fetchall()
	if (int(result[0][0])) >= (int(purch[0][1])):
		query = "UPDATE Users SET Currency=Currency + -" + str(purch[0][1]) + " WHERE User_ID=" + str(ctx.message.author.id) + ";"
		bot.cur.execute(query)
		query = "INSERT INTO  Pets (Species_ID,Owner_ID) VALUES (" + str(purch[0][0]) + "," + str(ctx.message.author.id) + ");"
		bot.cur.execute(query)
		bot.cur.execute("SELECT last_insert_rowid() FROM Pets;")
		CrID = bot.cur.fetchall()
		query = "UPDATE Pets SET Pet_Name= '" + str(arg) + "' WHERE Pet_ID=" + str(CrID[0][0]) + ";"
		bot.cur.execute(query)
		bot.conn.commit()
		await ctx.send((arg) + " purchased successfully!")
	else: 
		await ctx.send("Sorry, you don't have enough currency!")
		
@bot.slash_command(guild_ids=[645092549366644766])
async def buy(ctx, species_name: str):
	bot.cur.execute("SELECT Species_ID,Cost FROM Store WHERE Species_Name LIKE \"" + str(species_name) + "\" AND Available=1;")
	purch = bot.cur.fetchall()
	bot.cur.execute("SELECT Currency FROM Users WHERE User_ID=" + str(ctx.author.id) + ";")
	result = bot.cur.fetchall()
	if (int(result[0][0])) >= (int(purch[0][1])):
		query = "UPDATE Users SET Currency=Currency + -" + str(purch[0][1]) + " WHERE User_ID=" + str(ctx.author.id) + ";"
		bot.cur.execute(query)
		query = "INSERT INTO  Pets (Species_ID,Owner_ID) VALUES (" + str(purch[0][0]) + "," + str(ctx.author.id) + ");"
		bot.cur.execute(query)
		bot.cur.execute("SELECT last_insert_rowid() FROM Pets;")
		CrID = bot.cur.fetchall()
		query = "UPDATE Pets SET Pet_Name= '" + str(species_name) + "' WHERE Pet_ID=" + str(CrID[0][0]) + ";"
		bot.cur.execute(query)
		bot.conn.commit()
		await ctx.send(str(species_name) + " purchased successfully!")
	else: 
		await ctx.send("Sorry, you don't have enough currency!")
		
#store
@bot.command(pass_context = True , aliases=['shop'])
async def store(ctx):
		bot.cur.execute("SELECT Cost,Species_Name,Species_ID FROM Store WHERE Available=1;")
		shop = bot.cur.fetchall()
		embed=discord.Embed(title="Available Pets", description="Type `>buy (NAME)` to spend the currency to buy a pet", color=0xFF5733)
		tally = -1
		for postshop in shop:
			bot.cur.execute("SELECT emoji FROM Species WHERE Species_Name LIKE '" + str(postshop[1]) + "';")
			cmoji = bot.cur.fetchall()
			embed.add_field(name=str(cmoji[0][0]) + " " + str(postshop[1]), value="**Cost: **" + str(int(postshop[0])), inline=True)
			tally = tally + 1
			if tally == len(shop):
				break
		await ctx.send(embed=embed)
		
@bot.slash_command(guild_ids=[645092549366644766])
async def store(ctx):
		bot.cur.execute("SELECT Cost,Species_Name,Species_ID FROM Store WHERE Available=1;")
		shop = bot.cur.fetchall()
		embed=discord.Embed(title="Available Pets", description="Type `>buy (NAME)` to spend the currency to buy a pet", color=0xFF5733)
		tally = -1
		for postshop in shop:
			bot.cur.execute("SELECT emoji FROM Species WHERE Species_Name LIKE '" + str(postshop[1]) + "';")
			cmoji = bot.cur.fetchall()
			embed.add_field(name=str(cmoji[0][0]) + " " + str(postshop[1]), value="**Cost: **" + str(int(postshop[0])), inline=True)
			tally = tally + 1
			if tally == len(shop):
				break
		await ctx.send(embed=embed)

#search
@bot.command()
async def search(ctx, *, arg):
		bot.cur.execute("SELECT Habitat_Cost,Habitat_ID FROM Habitats WHERE Habitat_Name LIKE \"" + str(arg) + "\" AND Available=1;")
		wild = bot.cur.fetchall()
		bot.cur.execute("SELECT Currency FROM Users WHERE User_ID=" + str(ctx.message.author.id) + ";")
		result = bot.cur.fetchall()
		if int(result[0][0]) >= int(wild[0][0]):
			query = "UPDATE Users SET Currency=Currency + -" + str(wild[0][0]) + " WHERE User_ID=" + str(ctx.message.author.id) + ";"
			bot.cur.execute(query)
			rng = random.random()
			if rng >= 0.9:
				luck = 4
			elif rng >= 0.7:
				luck = 3
			elif rng >= 0.4:
				luck = 2
			else:
				luck =1
			bot.cur.execute("SELECT Species_Name,Species_ID,emoji FROM Species WHERE Habitat_ID=" + str(wild[0][1]) + " AND Rarity=" + str(luck) + " ORDER BY RANDOM() LIMIT 1;")
			found = bot.cur.fetchall()
			query = "INSERT INTO Pets (Species_ID,Owner_ID) VALUES (" + str(found[0][1]) + "," + str(ctx.message.author.id) + ");"
			print(query)
			bot.cur.execute(query)
			bot.cur.execute("SELECT last_insert_rowid() FROM Pets;")
			CrID = bot.cur.fetchall()
			query = "UPDATE Pets SET Pet_Name= '" + str(found[0][0]) + "' WHERE Pet_ID=" + str(CrID[0][0]) + ";"
			bot.cur.execute(query)
			bot.conn.commit()
			await ctx.send(str(found[0][0]) + " " + str(found[0][2]) + " found successfully!")
		else:
			await ctx.send("Sorry, you don't have enough currency! You have " + str(result[0][0]) + " and that costs " + str(wild[0][0]))

@bot.slash_command(guild_ids=[645092549366644766])
async def search(ctx, habitat: str):
		bot.cur.execute("SELECT Habitat_Cost,Habitat_ID FROM Habitats WHERE Habitat_Name LIKE \"" + str(habitat) + "\" AND Available=1;")
		wild = bot.cur.fetchall()
		bot.cur.execute("SELECT Currency FROM Users WHERE User_ID=" + str(ctx.author.id) + ";")
		result = bot.cur.fetchall()
		if int(result[0][0]) >= int(wild[0][0]):
			query = "UPDATE Users SET Currency=Currency + -" + str(wild[0][0]) + " WHERE User_ID=" + str(ctx.author.id) + ";"
			bot.cur.execute(query)
			rng = random.random()
			if rng >= 0.9:
				luck = 4
			elif rng >= 0.7:
				luck = 3
			elif rng >= 0.4:
				luck = 2
			else:
				luck =1
			bot.cur.execute("SELECT Species_Name,Species_ID,emoji FROM Species WHERE Habitat_ID=" + str(wild[0][1]) + " AND Rarity=" + str(luck) + " ORDER BY RANDOM() LIMIT 1;")
			found = bot.cur.fetchall()
			query = "INSERT INTO Pets (Species_ID,Owner_ID) VALUES (" + str(found[0][1]) + "," + str(ctx.author.id) + ");"
			print(query)
			bot.cur.execute(query)
			bot.cur.execute("SELECT last_insert_rowid() FROM Pets;")
			CrID = bot.cur.fetchall()
			query = "UPDATE Pets SET Pet_Name= '" + str(found[0][0]) + "' WHERE Pet_ID=" + str(CrID[0][0]) + ";"
			bot.cur.execute(query)
			bot.conn.commit()
			await ctx.send(str(found[0][0]) + " " + str(found[0][2]) + " found successfully!")
		else:
			await ctx.send("Sorry, you don't have enough currency! You have " + str(result[0][0]) + " and that costs " + str(wild[0][0]))
			
#habitats
@bot.command(pass_context = True , aliases=['habitat'])
async def habitats(ctx):
		bot.cur.execute("SELECT Habitat_Cost,Habitat_Name FROM Habitats WHERE Available=1 ORDER BY Habitat_Cost ASC;")
		shop = bot.cur.fetchall()
		embed=discord.Embed(title="Habitats", description="Type `>search [Name]` to spend the currency to search a habitat", color=0xFF5733)
		tally = 0
		for postshop in shop:
			embed.add_field(name=str("__" + postshop[1]) + "__", value="** Cost: **" + str(int(postshop[0])), inline=False)
			tally = tally + 1
			if tally == len(shop) + 1:
				break
		await ctx.send(embed=embed)
		
@bot.slash_command(guild_ids=[645092549366644766])
async def habitats(ctx):
		bot.cur.execute("SELECT Habitat_Cost,Habitat_Name FROM Habitats WHERE Available=1 ORDER BY Habitat_Cost ASC;")
		shop = bot.cur.fetchall()
		embed=discord.Embed(title="Habitats", description="Type `>search [Name]` to spend the currency to search a habitat", color=0xFF5733)
		tally = 0
		for postshop in shop:
			embed.add_field(name=str("__" + postshop[1]) + "__", value="** Cost: **" + str(int(postshop[0])), inline=False)
			tally = tally + 1
			if tally == len(shop) + 1:
				break
		await ctx.send(embed=embed)

#release
@bot.command()
async def release(ctx, arg):
		query = "DELETE FROM Pets WHERE Pet_ID=\"" + str(arg) + "\" AND OWNER_ID=" + str(ctx.message.author.id) + ";"
		bot.cur.execute(query)
		query = "UPDATE Users SET Currency=Currency + 25 WHERE User_ID=" + str(ctx.message.author.id) + ";"
		bot.cur.execute(query)
		await ctx.send("Awful! You got 25 Currency!")
		bot.conn.commit()
		
@bot.slash_command(guild_ids=[645092549366644766])
async def release(ctx, pet_id: str):
		query = "DELETE FROM Pets WHERE Pet_ID=\"" + str(pet_id) + "\" AND OWNER_ID=" + str(ctx.author.id) + ";"
		bot.cur.execute(query)
		query = "UPDATE Users SET Currency=Currency + 25 WHERE User_ID=" + str(ctx.author.id) + ";"
		bot.cur.execute(query)
		await ctx.send("Awful! You got 25 Currency!")
		bot.conn.commit()
		
#evolve
@bot.command()
async def evolve(ctx, arg):
		bot.cur.execute("SELECT Species_ID,Pet_Level FROM Pets WHERE Pet_ID=\"" + str(arg) + "\" AND OWNER_ID=" + str(ctx.message.author.id) + ";")
		evoble = bot.cur.fetchall()
		bot.cur.execute("SELECT EvoLevel,Species_Name FROM Species WHERE Species_ID=" + str(evoble[0][0]) + ";")
		evolevel = bot.cur.fetchall()
		bot.cur.execute("SELECT Pet_Name FROM Pets WHERE Pet_ID='" + str(arg) + "';")
		namec = bot.cur.fetchall()
		if int(evoble[0][1]) >= int(evolevel[0][0]):
			bot.cur.execute("SELECT Species_ID,Species_Name FROM Species WHERE EvoFrom=" + str(evoble[0][0]) + " ORDER BY RANDOM() LIMIT 1;")
			evo = bot.cur.fetchall()
			query = "UPDATE Pets SET Species_ID=" + str(evo[0][0]) + " WHERE Pet_ID=\"" + str(arg) + "\" AND OWNER_ID=" + str(ctx.message.author.id) + ";"
			bot.cur.execute(query)
			await ctx.send("Congratulations! Your pet evolved into a " + str(evo[0][1]))
			bot.conn.commit()
			if str(evolevel[0][1]).lower() == str(namec[0][0]).lower(): 
				query = "UPDATE Pets SET Pet_Name= '" + str(evo[0][1]) + "' WHERE Pet_ID=\"" + str(arg) + "\" AND OWNER_ID=" + str(ctx.message.author.id) + ";"
				bot.cur.execute(query)
		else:
			await ctx.send("Sorry! That pet needs to be level " + str(int(evolevel[0][0])))

@bot.slash_command(guild_ids=[645092549366644766])
async def evolve(ctx, pet_id: str):
		bot.cur.execute("SELECT Species_ID,Pet_Level FROM Pets WHERE Pet_ID=\"" + str(pet_id) + "\" AND OWNER_ID=" + str(ctx.author.id) + ";")
		evoble = bot.cur.fetchall()
		bot.cur.execute("SELECT EvoLevel,Species_Name FROM Species WHERE Species_ID=" + str(evoble[0][0]) + ";")
		evolevel = bot.cur.fetchall()
		bot.cur.execute("SELECT Pet_Name FROM Pets WHERE Pet_ID='" + str(pet_id) + "';")
		namec = bot.cur.fetchall()
		if int(evoble[0][1]) >= int(evolevel[0][0]):
			bot.cur.execute("SELECT Species_ID,Species_Name FROM Species WHERE EvoFrom=" + str(evoble[0][0]) + " ORDER BY RANDOM() LIMIT 1;")
			evo = bot.cur.fetchall()
			query = "UPDATE Pets SET Species_ID=" + str(evo[0][0]) + " WHERE Pet_ID=\"" + str(pet_id) + "\" AND OWNER_ID=" + str(ctx.author.id) + ";"
			bot.cur.execute(query)
			await ctx.send("Congratulations! Your pet evolved into a " + str(evo[0][1]))
			bot.conn.commit()
			if str(evolevel[0][1]).lower() == str(namec[0][0]).lower(): 
				query = "UPDATE Pets SET Pet_Name= '" + str(evo[0][1]) + "' WHERE Pet_ID=\"" + str(pet_id) + "\" AND OWNER_ID=" + str(ctx.author.id) + ";"
				bot.cur.execute(query)
		else:
			await ctx.send("Sorry! That pet needs to be level " + str(int(evolevel[0][0])))

#dex			
@bot.command(pass_context = True , aliases=['species'])
async def dex(ctx, *, arg):
		bot.cur.execute("SELECT Species_Name,Species_ID,Image_Link,EvoLevel,Artist FROM Species WHERE Species_Name LIKE '" + str(arg) + "';")
		dex = bot.cur.fetchall()
		bot.cur.execute("SELECT Pet_ID, COUNT(*) FROM Pets WHERE Species_ID=" + str(dex[0][1]) + ";")
		exist = bot.cur.fetchall()
		user = await bot.fetch_user(str(dex[0][4]))
		if dex[0][3] is not None:
			doesEvolve = "This pet evolves at level "
			embed=discord.Embed(title=str(arg), description=doesEvolve + str(dex[0][3]) + "\nNumber in existence: " + str(exist[0][1]) + "\n Artist: " + str(user), color=0x109319)
			embed.set_thumbnail(url=dex[0][2])
			await ctx.send(embed=embed)
		else:
			embed=discord.Embed(title=str(arg), description="This pet does not evolve. \nNumber in existence: " + str(exist[0][1]) + "\n Artist: " + str(user), color=0x109319)
			embed.set_thumbnail(url=dex[0][2])
			await ctx.send(embed=embed)

@bot.slash_command(guild_ids=[645092549366644766])
async def dex(ctx, species: str):
		bot.cur.execute("SELECT Species_Name,Species_ID,Image_Link,EvoLevel FROM Species WHERE Species_Name LIKE '" + str(species) + "';")
		dex = bot.cur.fetchall()
		bot.cur.execute("SELECT Pet_ID, COUNT(*) FROM Pets WHERE Species_ID=" + str(dex[0][1]) + ";")
		exist = bot.cur.fetchall()
		user = await bot.fetch_user(str(dex[0][4]))
		if dex[0][3] is not None:
			doesEvolve = "This pet evolves at level "
			embed=discord.Embed(title=str(species), description=doesEvolve + str(dex[0][3]) + "\nNumber in existence: " + str(exist[0][1]) + "\n Artist: " + str(user), color=0x109319)
			embed.set_thumbnail(url=dex[0][2])
			await ctx.send(embed=embed)
		else:
			embed=discord.Embed(title=str(species), description="This pet does not evolve. \nNumber in existence: " + str(exist[0][1]) + "\n Artist: " + str(user), color=0x109319)
			embed.set_thumbnail(url=dex[0][2])
			await ctx.send(embed=embed)
			
#help
@bot.command()
async def help(ctx):
	embed=discord.Embed(title="Help Commands:", description="What would you like help with? Use one of the help commands for more info")
	embed.add_field(name=">helpstart", value="How to get started", inline=False)
	embed.add_field(name=">helppets", value="How to get new pets", inline=False)
	embed.add_field(name=">helpteam", value="How to manage your team", inline=False)
	embed.add_field(name=">helpmanage", value="How to manage your pets", inline=False)
	embed.add_field(name=">helplevel", value="How to get levels and currency, as well as an explanation of LV Tokens", inline=False)
	embed.add_field(name=">helpinfo", value="For other commands, like the leaderboard and the dex", inline=False)
	await ctx.send(embed=embed)

@bot.slash_command(guild_ids=[645092549366644766])
async def help(ctx):
	embed=discord.Embed(title="Help Commands:", description="What would you like help with? Use one of the help commands for more info")
	embed.add_field(name=">helpstart", value="How to get started", inline=False)
	embed.add_field(name=">helppets", value="How to get new pets", inline=False)
	embed.add_field(name=">helpteam", value="How to manage your team", inline=False)
	embed.add_field(name=">helpmanage", value="How to manage your pets", inline=False)
	embed.add_field(name=">helplevel", value="How to get levels and currency, as well as an explanation of LV Tokens", inline=False)
	embed.add_field(name=">helpinfo", value="For other commands, like the leaderboard and the dex", inline=False)
	await ctx.send(embed=embed)

@bot.command()
async def helpstart(ctx):
	embed=discord.Embed(title="Getting Started:", description="Note: No commands need brackets")
	embed.add_field(name=">Register", value="Use this command to get started! You can't get any pets until you've registered", inline=False)
	embed.add_field(name=">Help", value="Brings up this command", inline=False)
	await ctx.send(embed=embed)
			
@bot.slash_command(guild_ids=[645092549366644766])
async def helpstart(ctx):
	embed=discord.Embed(title="Getting Started:", description="Note: No commands need brackets")
	embed.add_field(name=">Register", value="Use this command to get started! You can't get any pets until you've registered", inline=False)
	embed.add_field(name=">Help", value="Brings up this command", inline=False)
	await ctx.send(embed=embed)

@bot.command()
async def helppets(ctx):
	embed=discord.Embed(title="Getting Pets:")
	embed.add_field(name=">Shop", value="Opens the shop to buy pets for currency", inline=False)
	embed.add_field(name=">Habitats", value="Shows you a list of habitats you can search for pets", inline=False)
	await ctx.send(embed=embed)
			
@bot.slash_command(guild_ids=[645092549366644766])
async def helppets(ctx):
	embed=discord.Embed(title="Getting Pets:")
	embed.add_field(name=">Shop", value="Opens the shop to buy pets for currency", inline=False)
	embed.add_field(name=">Habitats", value="Shows you a list of habitats you can search for pets", inline=False)
	await ctx.send(embed=embed)

@bot.command()
async def helpteam(ctx):
	embed=discord.Embed(title="Your Team:", description="The team is mostly for easily displaying your favorite pets! This is unrelated to your \"main\" pet")
	embed.add_field(name=">Team", value="Displays your team. You can't bring up your team until you've assigned pets to all 3 slots", inline=False)
	embed.add_field(name=">Team [#1-3] [Your Pets ID]", value="Assigns the selected pet to one of the 3 slots on your team", inline=False)
	embed.add_field(name=">Team @User", value="Displays another user's team", inline=False)
	embed.add_field(name=">Toggle", value="Decides if LV Tokens you get from the exchange are given to your main pet, or spread across your team", inline=False)
	await ctx.send(embed=embed)
			
@bot.slash_command(guild_ids=[645092549366644766])
async def helpteam(ctx):
	embed=discord.Embed(title="Your Team:", description="The team is mostly for easily displaying your favorite pets! This is unrelated to your \"main\" pet")
	embed.add_field(name=">Team", value="Displays your team. You can't bring up your team until you've assigned pets to all 3 slots", inline=False)
	embed.add_field(name=">Team [#1-3] [Your Pets ID]", value="Assigns the selected pet to one of the 3 slots on your team", inline=False)
	embed.add_field(name=">Team @User", value="Displays another user's team", inline=False)
	embed.add_field(name=">Toggle", value="Decides if LV Tokens you get from the exchange are given to your main pet, or spread across your team", inline=False)
	await ctx.send(embed=embed)

@bot.command()
async def helpmanage(ctx):
	embed=discord.Embed(title="Managing Pets:", description="Don't forget to read >helpteam to learn how to manage your team!")
	embed.add_field(name=">Pets [Page #]", value="Shows all of your pets in pages of 12! You can use >Pets Last to see the last page of your pets", inline=False)
	embed.add_field(name=">Pet [Pet ID]", value="Leave the ID blank to show your main pet, or add a pet's ID to show that pet", inline=False)
	embed.add_field(name=">Main [Pet ID]", value="Selects your main pet, this should usually be the pet you are trying to level", inline=False)
	embed.add_field(name=">Name [Pet ID] [Name]", value="Renames a selected pet! Names can be up to 12 characters long", inline=False)
	embed.add_field(name=">Release [Pet ID]", value="Releases a pet! Be careful, this is irreversible!", inline=False)
	embed.add_field(name=">Evolve [ID]", value="Evolves a selected pet if it's the right level! You can find out if a pet evolves in the dex, read >helpinfo for more information", inline=False)
	await ctx.send(embed=embed)
	
@bot.slash_command(guild_ids=[645092549366644766])
async def helpmanage(ctx):
	embed=discord.Embed(title="Managing Pets:", description="Don't forget to read >helpteam to learn how to manage your team!")
	embed.add_field(name=">Pets [Page #]", value="Shows all of your pets in pages of 12! You can use >Pets Last to see the last page of your pets", inline=False)
	embed.add_field(name=">Pet [Pet ID]", value="Leave the ID blank to show your main pet, or add a pet's ID to show that pet", inline=False)
	embed.add_field(name=">Main [Pet ID]", value="Selects your main pet, this should usually be the pet you are trying to level", inline=False)
	embed.add_field(name=">Name [Pet ID] [Name]", value="Renames a selected pet! Names can be up to 12 characters long", inline=False)
	embed.add_field(name=">Release [Pet ID]", value="Releases a pet! Be careful, this is irreversible!", inline=False)
	embed.add_field(name=">Evolve [ID]", value="Evolves a selected pet if it's the right level! You can find out if a pet evolves in the dex, read >helpinfo for more information", inline=False)
	await ctx.send(embed=embed)	
	
@bot.command()
async def helplevel(ctx):
	embed=discord.Embed(title="Levels and Currency:", description="Credits are used when a stranger levels  your pet through the exchange!  You can get more credits by using the exchange yourself The exchange is the main way to level pets.")
	embed.add_field(name=">Currency", value="Shows how much currency you currently have", inline=False)
	embed.add_field(name=">Daily", value="Gives you 200 currency, once per day", inline=False)
	embed.add_field(name=">ex", value="Also known as >Exchange, levels a random in exchange for a LV token and some currency", inline=False)
	embed.add_field(name=">Level [Pet ID]", value="Lets you level another person's pet. You can level each of their pets once per day. This is a social feature, encouraging you to level other people's pets in exchange for them leveling your's", inline=False)
	await ctx.send(embed=embed)

@bot.slash_command(guild_ids=[645092549366644766])
async def helplevel(ctx):
	embed=discord.Embed(title="Levels and Currency:", description="Credits are used when a stranger levels  your pet through the exchange!  You can get more credits by using the exchange yourself The exchange is the main way to level pets.")
	embed.add_field(name=">Currency", value="Shows how much currency you currently have", inline=False)
	embed.add_field(name=">Daily", value="Gives you 200 currency, once per day", inline=False)
	embed.add_field(name=">ex", value="Also known as >Exchange, levels a random in exchange for a LV token and some currency", inline=False)
	embed.add_field(name=">Level [Pet ID]", value="Lets you level another person's pet. You can level each of their pets once per day. This is a social feature, encouraging you to level other people's pets in exchange for them leveling your's", inline=False)
	await ctx.send(embed=embed)

@bot.command()
async def helpinfo(ctx):
	embed=discord.Embed(title="Other Commands:")
	embed.add_field(name=">Dex [Species Name]", value="Shows you the dex entry for a pet, including the level it evolves at as well as the artist", inline=False)
	embed.add_field(name=">Leaderboard", value="Or >lb for short, shows you the top 10 highest level pets", inline=False)
	embed.add_field(name=">Leaderboard [Species]", value="Can also be abbreviated to >lb, shows you the top 3 highest leveled pets of a species", inline=False)
	embed.add_field(name=">Invite", value="A link to invite the bot to your own server", inline=False)
	embed.add_field(name=">Server", value="A link to the DiscoPets Discord", inline=False)
	await ctx.send(embed=embed)
	
@bot.slash_command(guild_ids=[645092549366644766])
async def helpinfo(ctx):
	embed=discord.Embed(title="Other Commands:")
	embed.add_field(name=">Dex [Species Name]", value="Shows you the dex entry for a pet, including the level it evolves at as well as the artist", inline=False)
	embed.add_field(name=">Leaderboard", value="Or >lb for short, shows you the top 10 highest level pets", inline=False)
	embed.add_field(name=">Leaderboard [Species]", value="Can also be abbreviated to >lb, shows you the top 3 highest leveled pets of a species", inline=False)
	embed.add_field(name=">Invite", value="A link to invite the bot to your own server", inline=False)
	embed.add_field(name=">Server", value="A link to the DiscoPets Discord", inline=False)
	await ctx.send(embed=embed)

#invite
@bot.command()
async def invite(ctx):
			await ctx.send("https://discord.com/api/oauth2/authorize?client_id=643192969796780043&permissions=2048&scope=bot%20applications.commands")
			
@bot.slash_command(guild_ids=[645092549366644766])
async def invite(ctx):
			await ctx.send("https://discord.com/api/oauth2/authorize?client_id=643192969796780043&permissions=2048&scope=bot%20applications.commands")

#server
@bot.command()
async def server(ctx):
			await ctx.send("https://discord.gg/SpjpfaA")
			
@bot.slash_command(guild_ids=[645092549366644766])
async def server(ctx):
			await ctx.send("https://discord.gg/SpjpfaA")

#level	
@bot.command()
async def level(ctx, arg):
	bot.cur.execute("SELECT Pet_ID,Owner_ID,Pet_Level FROM Pets WHERE Pet_ID=" + arg + ";")
	info = bot.cur.fetchall()
	datenow = datetime.datetime.now()
	if info[0][1] == str(ctx.author.id):
		await ctx.send("Sorry! This function is used for leveling other people's pets, to encourage them to level yours!")
	else:
		query = "INSERT OR IGNORE INTO Level (UserID,PetID) VALUES (" + str(ctx.message.author.id) + "," + str(info[0][0]) + ");"
		bot.cur.execute(query)
		bot.cur.execute("SELECT LastLevel FROM Level WHERE UserID=" + str(ctx.message.author.id) + " AND PetID=" + arg + ";")
		LastLevel = bot.cur.fetchall()
		if LastLevel[0][0] != datenow.day:
			bot.cur.execute("SELECT Pet_ID,Pet_Name,Species_ID,Owner_ID FROM Pets WHERE Pet_ID=" + str(arg) + ";")
			clicked = bot.cur.fetchall()
			bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(clicked[0][2]) + ";")
			cmoji = bot.cur.fetchall()
			query = "UPDATE Pets SET Pet_Level=Pet_Level + 1 WHERE Pet_ID=" + str(arg) + ";"
			bot.cur.execute(query)
			bot.cur.execute("SELECT Pet_Level FROM Pets WHERE Pet_ID=" + arg + ";")
			lvl = bot.cur.fetchall()
			query = "UPDATE Level SET LastLevel=" +  str(datenow.day) + " WHERE UserID=" + str(ctx.message.author.id) + " AND PetID=" + arg + ";"
			bot.cur.execute(query)
			bot.conn.commit()
			await ctx.send("You leveled up <@" + clicked[0][3] + ">'s " + str(cmoji[0][0]) + " `ID:`" + str(clicked[0][0]) + " **" + str(clicked[0][1]) + "** to " + str(lvl[0][0]))
		else:
			await ctx.send("Sorry, come back the next day!\nCurrent bot time is " + str(datenow.hour) + ":" + str(datenow.minute))

@bot.slash_command(guild_ids=[645092549366644766])
async def level(ctx, pet_id: str):
	bot.cur.execute("SELECT Pet_ID,Owner_ID,Pet_Level FROM Pets WHERE Pet_ID=" + pet_id + ";")
	info = bot.cur.fetchall()
	datenow = datetime.datetime.now()
	if info[0][1] == str(ctx.author.id):
		await ctx.send("Sorry! This function is used for leveling other people's pets, to encourage them to level yours!")
	else:
		query = "INSERT OR IGNORE INTO Level (UserID,PetID) VALUES (" + str(ctx.author.id) + "," + str(info[0][0]) + ");"
		bot.cur.execute(query)
		bot.cur.execute("SELECT LastLevel FROM Level WHERE UserID=" + str(ctx.author.id) + " AND PetID=" + pet_id + ";")
		LastLevel = bot.cur.fetchall()
		if LastLevel[0][0] != datenow.day:
			bot.cur.execute("SELECT Pet_ID,Pet_Name,Species_ID,Owner_ID FROM Pets WHERE Pet_ID=" + str(pet_id) + ";")
			clicked = bot.cur.fetchall()
			bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(clicked[0][2]) + ";")
			cmoji = bot.cur.fetchall()
			query = "UPDATE Pets SET Pet_Level=Pet_Level + 1 WHERE Pet_ID=" + str(pet_id) + ";"
			bot.cur.execute(query)
			bot.cur.execute("SELECT Pet_Level FROM Pets WHERE Pet_ID=" + pet_id + ";")
			lvl = bot.cur.fetchall()
			query = "UPDATE Level SET LastLevel=" +  str(datenow.day) + " WHERE UserID=" + str(ctx.author.id) + " AND PetID=" + pet_id + ";"
			bot.cur.execute(query)
			bot.conn.commit()
			await ctx.send("You leveled up <@" + clicked[0][3] + ">'s " + str(cmoji[0][0]) + " `ID:`" + str(clicked[0][0]) + " **" + str(clicked[0][1]) + "** to " + str(lvl[0][0]))
		else:
			await ctx.send("Sorry, come back the next day!\nCurrent bot time is " + str(datenow.hour) + ":" + str(datenow.minute))

#leaderboards
@bot.command(pass_context = True , aliases=['leaderboards', 'lb'])
async def leaderboard(ctx, *arg):
	try:
			bot.cur.execute("SELECT Species_ID FROM Species WHERE Species_Name LIKE '" + str(arg[0]) + "';")
			spec = bot.cur.fetchall()
			bot.cur.execute("SELECT Pet_ID,Pet_Name,Species_ID,Owner_ID,Pet_Level FROM Pets WHERE Species_ID=" + str(spec[0][0]) + " ORDER BY Pet_Level DESC LIMIT 3;")
			lb = bot.cur.fetchall()
			embed=discord.Embed(title="Leaderboard", description="The highest level " + str(arg[0]) + " in all of DiscoPets", color=0xFF5733)
			tally = 1
			for postlb in lb:
				bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(postlb[2]) + ";")
				cmoji = bot.cur.fetchall()
				user = await bot.fetch_user(str(lb[tally - 1][3]))
				embed.add_field(name="#" + str(tally) + ": " + str(cmoji[0][0]) + " " + str(postlb[1]) + "(#" + str(postlb[0]) + ")", value="**Level: **" + str(postlb[4]) + "\n**Owner:** " + str(user), inline=False)
				tally = tally + 1
				if tally == 4:
					break
			await ctx.send(embed=embed)	
	except IndexError:
		pass
		bot.cur.execute("SELECT Pet_ID,Pet_Name,Species_ID,Owner_ID,Pet_Level FROM Pets WHERE (Pet_level)>10 ORDER BY Pet_Level DESC LIMIT 10;")
		lb = bot.cur.fetchall()
		embed=discord.Embed(title="Leaderboard", description="The highest level pets in all of DiscoPets", color=0xFF5733)
		tally = 1
		for postlb in lb:
			bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(postlb[2]) + ";")
			cmoji = bot.cur.fetchall()
			user = await bot.fetch_user(str(lb[tally - 1][3]))
			embed.add_field(name="#" + str(tally) + ": " + str(cmoji[0][0]) + " " + str(postlb[1]) + "(#" + str(postlb[0]) + ")", value="**Level: **" + str(postlb[4]) + "\n**Owner:** " + str(user), inline=False)
			tally = tally + 1
			if tally == 11:
				break
		await ctx.send(embed=embed)	

@bot.slash_command(guild_ids=[645092549366644766])
async def leaderboard(ctx, species: Option(str, "Not required", required=False)):
	try:
			bot.cur.execute("SELECT Species_ID FROM Species WHERE Species_Name LIKE '" + str(species) + "';")
			spec = bot.cur.fetchall()
			bot.cur.execute("SELECT Pet_ID,Pet_Name,Species_ID,Owner_ID,Pet_Level FROM Pets WHERE Species_ID=" + str(spec[0][0]) + " ORDER BY Pet_Level DESC LIMIT 3;")
			lb = bot.cur.fetchall()
			embed=discord.Embed(title="Leaderboard", description="The highest level " + str(species) + " in all of DiscoPets", color=0xFF5733)
			tally = 1
			for postlb in lb:
				bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(postlb[2]) + ";")
				cmoji = bot.cur.fetchall()
				user = await bot.fetch_user(str(lb[tally - 1][3]))
				embed.add_field(name="#" + str(tally) + ": " + str(cmoji[0][0]) + " " + str(postlb[1]) + "(#" + str(postlb[0]) + ")", value="**Level: **" + str(postlb[4]) + "\n**Owner:** " + str(user), inline=False)
				tally = tally + 1
				if tally == 4:
					break
			await ctx.send(embed=embed)	
	except IndexError:
		pass
		bot.cur.execute("SELECT Pet_ID,Pet_Name,Species_ID,Owner_ID,Pet_Level FROM Pets WHERE (Pet_level)>10 ORDER BY Pet_Level DESC LIMIT 10;")
		lb = bot.cur.fetchall()
		embed=discord.Embed(title="Leaderboard", description="The highest level pets in all of DiscoPets", color=0xFF5733)
		tally = 1
		for postlb in lb:
			bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(postlb[2]) + ";")
			cmoji = bot.cur.fetchall()
			user = await bot.fetch_user(str(lb[tally - 1][3]))
			embed.add_field(name="#" + str(tally) + ": " + str(cmoji[0][0]) + " " + str(postlb[1]) + "(#" + str(postlb[0]) + ")", value="**Level: **" + str(postlb[4]) + "\n**Owner:** " + str(user), inline=False)
			tally = tally + 1
			if tally == 11:
				break
		await ctx.send(embed=embed)	
		
#team
@bot.command()
async def team(ctx, *arg):
	id = 0
	try:
		teamowner = str(arg[0])
		id = teamowner.translate({ ord(c): None for c in "<@!>" })
	except IndexError:
		pass
	if int(id) >= 10000000000000000:
		user = await bot.fetch_user(id)
		embed=discord.Embed(title=str(user) + "'s Team", color=0xFF5733)
		bot.cur.execute("SELECT slot1,slot2,slot3 FROM USers WHERE USER_ID=" + id + ";")
		team = bot.cur.fetchall()
		bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits,Species_ID FROM Pets WHERE PET_ID=" + str(team[0][0]) + ";")
		result1 = bot.cur.fetchall()
		bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(result1[0][4]) + ";")
		cmoji1 = bot.cur.fetchall()
		embed.add_field(name=str(cmoji1[0][0]) + " " + str(result1[0][1]), value="**ID #**" + str(result1[0][0]) + "\n**Level:** " + str(result1[0][2]) + "\n**LV Tokens: **" + str(result1[0][3]), inline=True)
		bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits,Species_ID FROM Pets WHERE PET_ID=" + str(team[0][1]) + ";")
		result2 = bot.cur.fetchall()
		bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(result2[0][4]) + ";")
		cmoji2 = bot.cur.fetchall()
		embed.add_field(name=str(cmoji2[0][0]) + " " + str(result2[0][1]), value="**ID #**" + str(result2[0][0]) + "\n**Level:** " + str(result2[0][2]) + "\n**LV Tokens: **" + str(result2[0][3]), inline=True)
		bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits,Species_ID FROM Pets WHERE PET_ID=" + str(team[0][2]) + ";")
		result3 = bot.cur.fetchall()
		bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(result3[0][4]) + ";")
		cmoji3 = bot.cur.fetchall()
		embed.add_field(name=str(cmoji3[0][0]) + " " + str(result3[0][1]), value="**ID #**" + str(result3[0][0]) + "\n**Level:** " + str(result3[0][2]) + "\n**LV Tokens: **" + str(result3[0][3]), inline=True)		
		await ctx.send(embed=embed)
	else:
		try:
			bot.cur.execute("SELECT OWNER_ID FROM Pets WHERE Pet_ID=" + str(arg[1]) + ";")
			own = bot.cur.fetchall()
			if str(ctx.message.author.id) == str(own[0][0]):
				bot.cur.execute("SELECT Pet_ID FROM Pets WHERE Pet_ID=" + str(arg[1]) + " AND OWNER_ID=" + str(ctx.message.author.id) + ";")
				select = bot.cur.fetchall()
				query = "UPDATE Users SET slot" + arg[0] + "=" + arg[1] + " WHERE USER_ID=" + str(ctx.message.author.id) + ";"
				bot.cur.execute(query)
				bot.conn.commit()
				await ctx.send("Set pet " + arg[1] + " to team slot " + arg[0] + ".")
			else:
				await ctx.send("That's not your pet!")
		except IndexError:
			pass
			try:
				embed=discord.Embed(title="Your Team", color=0xFF5733)
				bot.cur.execute("SELECT slot1,slot2,slot3 FROM USers WHERE USER_ID=" + str(ctx.message.author.id) + ";")
				team = bot.cur.fetchall()
				bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits,Species_ID FROM Pets WHERE PET_ID=" + str(team[0][0]) + ";")
				result1 = bot.cur.fetchall()
				bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(result1[0][4]) + ";")
				cmoji1 = bot.cur.fetchall()
				embed.add_field(name=str(cmoji1[0][0]) + " " + str(result1[0][1]), value="**ID #**" + str(result1[0][0]) + "\n**Level:** " + str(result1[0][2]) + "\n**LV Tokens: **" + str(result1[0][3]), inline=True)
				bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits,Species_ID FROM Pets WHERE PET_ID=" + str(team[0][1]) + ";")
				result2 = bot.cur.fetchall()
				bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(result2[0][4]) + ";")
				cmoji2 = bot.cur.fetchall()
				embed.add_field(name=str(cmoji2[0][0]) + " " + str(result2[0][1]), value="**ID #**" + str(result2[0][0]) + "\n**Level:** " + str(result2[0][2]) + "\n**LV Tokens: **" + str(result2[0][3]), inline=True)
				bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits,Species_ID FROM Pets WHERE PET_ID=" + str(team[0][2]) + ";")
				result3 = bot.cur.fetchall()
				bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(result3[0][4]) + ";")
				cmoji3 = bot.cur.fetchall()
				embed.add_field(name=str(cmoji3[0][0]) + " " + str(result3[0][1]), value="**ID #**" + str(result3[0][0]) + "\n**Level:** " + str(result3[0][2]) + "\n**LV Tokens: **" + str(result3[0][3]), inline=True)		
				await ctx.send(embed=embed)
			except OperationalError:
				pass
				await ctx.send("You don't have three pets assigned yet!")
			
@bot.slash_command(guild_ids=[645092549366644766])
async def team(ctx, slot: Option(str, "Not required", required=False), pet_id: Option(str, "Not required", required=False)):
	try:
		bot.cur.execute("SELECT OWNER_ID FROM Pets WHERE Pet_ID=" + str(pet_id) + ";")
		own = bot.cur.fetchall()
		if str(ctx.author.id) == str(own[0][0]):
			bot.cur.execute("SELECT Pet_ID FROM Pets WHERE Pet_ID=" + str(pet_id) + " AND OWNER_ID=" + str(ctx.author.id) + ";")
			select = bot.cur.fetchall()
			query = "UPDATE Users SET slot" + str(slot) + "=" + str(pet_id) + " WHERE USER_ID=" + str(ctx.author.id) + ";"
			bot.cur.execute(query)
			bot.conn.commit()
			await ctx.send("Set pet " + str(pet_id) + " to team slot " + str(slot) + ".")
		else:
			await ctx.send("That's not your pet!")
	except OperationalError:
		pass
		try:
			embed=discord.Embed(title="Your Team", color=0xFF5733)
			bot.cur.execute("SELECT slot1,slot2,slot3 FROM USers WHERE USER_ID=" + str(ctx.author.id) + ";")
			team = bot.cur.fetchall()
			bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits,Species_ID FROM Pets WHERE PET_ID=" + str(team[0][0]) + ";")
			result1 = bot.cur.fetchall()
			bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(result1[0][4]) + ";")
			cmoji1 = bot.cur.fetchall()
			embed.add_field(name=str(cmoji1[0][0]) + " " + str(result1[0][1]), value="**ID #**" + str(result1[0][0]) + "\n**Level:** " + str(result1[0][2]) + "\n**LV Tokens: **" + str(result1[0][3]), inline=True)
			bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits,Species_ID FROM Pets WHERE PET_ID=" + str(team[0][1]) + ";")
			result2 = bot.cur.fetchall()
			bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(result2[0][4]) + ";")
			cmoji2 = bot.cur.fetchall()
			embed.add_field(name=str(cmoji2[0][0]) + " " + str(result2[0][1]), value="**ID #**" + str(result2[0][0]) + "\n**Level:** " + str(result2[0][2]) + "\n**LV Tokens: **" + str(result2[0][3]), inline=True)
			bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits,Species_ID FROM Pets WHERE PET_ID=" + str(team[0][2]) + ";")
			result3 = bot.cur.fetchall()
			bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID=" + str(result3[0][4]) + ";")
			cmoji3 = bot.cur.fetchall()
			embed.add_field(name=str(cmoji3[0][0]) + " " + str(result3[0][1]), value="**ID #**" + str(result3[0][0]) + "\n**Level:** " + str(result3[0][2]) + "\n**LV Tokens: **" + str(result3[0][3]), inline=True)		
			await ctx.send(embed=embed)
		except OperationalError:
			pass
			await ctx.send("You don't have three pets assigned yet!")
			
#teamtoggle	
@bot.command()
async def toggle(ctx):
	bot.cur.execute("SELECT teamtoggle FROM Users WHERE User_ID=" + str(ctx.message.author.id) + ";")
	toggle = bot.cur.fetchall()
	if toggle[0][0] == 0:
		query = "UPDATE Users SET teamtoggle=1 WHERE User_ID=" + str(ctx.message.author.id) + ";"
		bot.cur.execute(query)
		await ctx.send("Your team is now sharing LV Tokens!")
		bot.conn.commit()
	elif toggle[0][0] == 1:
		query = "UPDATE Users SET teamtoggle=0 WHERE User_ID=" + str(ctx.message.author.id) + ";"
		bot.cur.execute(query)
		await ctx.send("Your team is no longer sharing LV Tokens, all of them you earn will go to your main pet")
		bot.conn.commit()

@bot.slash_command(guild_ids=[645092549366644766])
async def toggle(ctx):
	bot.cur.execute("SELECT teamtoggle FROM Users WHERE User_ID=" + str(ctx.author.id) + ";")
	toggle = bot.cur.fetchall()
	if toggle[0][0] == 0:
		query = "UPDATE Users SET teamtoggle=1 WHERE User_ID=" + str(ctx.author.id) + ";"
		bot.cur.execute(query)
		await ctx.send("Your team is now sharing LV Tokens!")
		bot.conn.commit()
	elif toggle[0][0] == 1:
		query = "UPDATE Users SET teamtoggle=0 WHERE User_ID=" + str(ctx.author.id) + ";"
		bot.cur.execute(query)
		await ctx.send("Your team is no longer sharing LV Tokens, all of them you earn will go to your main pet")
		bot.conn.commit()
		
#test	
@bot.command(pass_context = True)
async def test(ctx, arg):
	id = arg.translate({ ord(c): None for c in "<@!>" })
	print(id)

#exchange	
@bot.command(pass_context = True , aliases=['ex'])
async def exchange(ctx):
		if ctx.message.author.id not in cooldowns: 
			cooldowns[ctx.message.author.id] = datetime.datetime(2005, 5, 17)
		datenow = datetime.datetime.now()
		print(datenow)
		time_diff = (datenow - cooldowns[ctx.message.author.id])
		cd = datetime.timedelta(seconds=2)
		print(time_diff)
		if time_diff >= cd:
			cooldowns[ctx.message.author.id] = datetime.datetime.now()
			num1 = random.random() * 10
			num2 = random.random() * 10
			answer = round(num1) + round(num2)
			uid = await bot.fetch_user(ctx.message.author.id)
			await ctx.send(str(uid) + ", what is " + str(round(num1)) + " + " + str(round(num2)) + "?\nAnswers must start with an =")
			query = "UPDATE Users SET math=" + str(answer) + " WHERE User_ID=" + str(ctx.message.author.id) + ";"
			bot.cur.execute(query)
			bot.conn.commit()
		else:
			await ctx.send("Slow down! You can only use that command once every 3 seconds. It's only been " + str(time_diff) + " seconds")
			
@bot.slash_command(guild_ids=[645092549366644766])
async def exchange(ctx):
		if ctx.author.id not in cooldowns: 
			cooldowns[ctx.author.id] = datetime.datetime(2005, 5, 17)
		datenow = datetime.datetime.now()
		print(datenow)
		time_diff = (datenow - cooldowns[ctx.author.id])
		cd = datetime.timedelta(seconds=2)
		print(time_diff)
		if time_diff >= cd:
			cooldowns[ctx.author.id] = datetime.datetime.now()
			num1 = random.random() * 10
			num2 = random.random() * 10
			answer = round(num1) + round(num2)
			uid = await bot.fetch_user(ctx.author.id)
			await ctx.send(str(uid) + ", what is " + str(round(num1)) + " + " + str(round(num2)) + "?\nAnswers must start with an =")
			query = "UPDATE Users SET math=" + str(answer) + " WHERE User_ID=" + str(ctx.author.id) + ";"
			bot.cur.execute(query)
			bot.conn.commit()
		else:
			await ctx.send("Slow down! You can only use that command once every 3 seconds. It's only been " + str(time_diff) + " seconds")
			
#answer
@bot.event
async def on_message(message):
	basemsg = message.content
	msg = basemsg.split(" ")
	basemsgL = basemsg.lower()
	msgL = basemsgL.split(" ")
	if msg[0][0]  == "=":
		try:
			ans = msg[0][1]
		except IndexError:
			pass
		try:
			ans = msg[1]
		except IndexError:
			pass
		try:
			ansplit = (msg[0][1],msg[0][2])
			ans = "".join(ansplit)
		except IndexError:
			pass
		print(ans)
		bot.cur.execute("SELECT math,teamtoggle FROM Users WHERE User_ID=" + str(message.author.id) + ";")
		math1 = bot.cur.fetchall()
		if ans == str(math1[0][0]):
			if int(math1[0][1]) == 0:
				bot.cur.execute("SELECT Main_Pet_ID FROM Users WHERE User_ID=" + str(message.author.id) + ";")
				mainpet = bot.cur.fetchall()
				bot.cur.execute("SELECT Pet_ID,Pet_Name,Species_ID FROM Pets WHERE (Credits)>0 AND OWNER_ID!=" + str(message.author.id) + " ORDER BY RANDOM() LIMIT 1;")
				clicked = bot.cur.fetchall()
				bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID='" + str(clicked[0][2]) + "';")
				cmoji = bot.cur.fetchall()
				query = "UPDATE Pets SET Pet_Level=Pet_Level + 1 WHERE Pet_ID=" + str(clicked[0][0]) + ";"
				bot.cur.execute(query)
				bot.cur.execute("SELECT Pet_Level FROM Pets WHERE Pet_ID=" + str(clicked[0][0]) + ";")
				lvl = bot.cur.fetchall()
				query = "UPDATE Pets SET Credits=Credits + -1 WHERE Pet_ID=" + str(clicked[0][0]) + ";"
				bot.cur.execute(query)
				query = "UPDATE Pets SET Credits=Credits + 1 WHERE Pet_ID=" + str(mainpet[0][0]) + ";"
				bot.cur.execute(query)
				query = "UPDATE Users SET Currency=Currency + 10 WHERE User_ID=" + str(message.author.id) + ";"
				bot.cur.execute(query)
				query = "UPDATE Users SET math=null WHERE User_ID=" + str(message.author.id) + ";"
				bot.cur.execute(query)
				bot.conn.commit()
				await message.channel.send("You leveled up " + str(cmoji[0][0]) + " `ID:`" + str(clicked[0][0]) + " **" + str(clicked[0][1]) + "** to level " + str(lvl[0][0]) + ".\nYour main pet gained 1 LV Token and you got 10 currency!")
			elif int(math1[0][1]) == 1:
				bot.cur.execute("SELECT slot1,slot2,slot3 FROM USers WHERE USER_ID=" + str(message.author.id) + ";")
				team = bot.cur.fetchall()
				bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits,Species_ID FROM Pets WHERE PET_ID=" + str(team[0][0]) + ";")
				result1 = bot.cur.fetchall()
				bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits,Species_ID FROM Pets WHERE PET_ID=" + str(team[0][1]) + ";")
				result2 = bot.cur.fetchall()
				bot.cur.execute("SELECT Pet_ID,Pet_Name,Pet_Level,Credits,Species_ID FROM Pets WHERE PET_ID=" + str(team[0][2]) + ";")
				result3 = bot.cur.fetchall()
				randopet = (result1[0][0], result2[0][0], result3[0][0]) 
				teampet = random.choice(randopet)
				bot.cur.execute("SELECT Pet_ID,Pet_Name,Species_ID FROM Pets WHERE (Credits)>0 AND OWNER_ID!=" + str(message.author.id) + " ORDER BY RANDOM() LIMIT 1;")
				clicked = bot.cur.fetchall()
				bot.cur.execute("SELECT emoji FROM Species WHERE Species_ID='" + str(clicked[0][2]) + "';")
				cmoji = bot.cur.fetchall()
				query = "UPDATE Pets SET Pet_Level=Pet_Level + 1 WHERE Pet_ID=" + str(clicked[0][0]) + ";"
				bot.cur.execute(query)
				bot.cur.execute("SELECT Pet_Level FROM Pets WHERE Pet_ID=" + str(clicked[0][0]) + ";")
				lvl = bot.cur.fetchall()
				query = "UPDATE Pets SET Credits=Credits + -1 WHERE Pet_ID=" + str(clicked[0][0]) + ";"
				bot.cur.execute(query)
				query = "UPDATE Pets SET Credits=Credits + 1 WHERE Pet_ID=" + str(teampet) + ";"
				bot.cur.execute(query)
				query = "UPDATE Users SET Currency=Currency + 10 WHERE User_ID=" + str(message.author.id) + ";"
				bot.cur.execute(query)
				query = "UPDATE Users SET math=null WHERE User_ID=" + str(message.author.id) + ";"
				bot.cur.execute(query)
				bot.conn.commit()
				await message.channel.send("You leveled up " + str(cmoji[0][0]) + " `ID:`" + str(clicked[0][0]) + " **" + str(clicked[0][1]) + "** to level " + str(lvl[0][0]) + ".\nPet #" + str(teampet) + " gained 1 LV Token and you got 10 currency!")
		else:
			await message.channel.send("Sorry! That's wrong!")
	elif msgL[0]  == ".":
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
		auth.set_access_token(access_token, access_token_secret) 
		api = tweepy.API(auth) 
		print (str(message.author.id))
		if str(message.author.id) == "105584573747863552":
			api.update_status(status = basemsg[1:]) 
	await bot.process_commands(message)
	
bot.run(str(data['bot']))