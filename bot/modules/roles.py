import discord
from discord.ext import commands
from utils import checks
import datetime
from utils import reaction_menu
import asyncio

header = "=====================================================\n" \
         "All Roles on this server which can be assigned.\n" \
         "Click the reaction to select a role, which will be added or removed.\n" \
         "Click the arrows to move page\n" \
         "====================================================="


class Roles:

    def __init__(self, bot):
        self.bot = bot
        self.roles.enabled = bot.modules["roles"]

    @commands.group(invoke_without_command=True)
    async def roles(self, ctx):
        """Shows roles on the server that can be assigned"""
        server = await self.bot.get_server_data(ctx.guild.id)
        options = server["roles"]
        if len(options) == 0:
            await ctx.send("No roles available")
            return
        choices = await reaction_menu.start_reaction_menu(self.bot, list(options.values()), ctx.author, ctx.channel, count=-1, timeout=60, per_page=10, header=header, return_from=list(options), allow_none=True)
        if choices is None:
            return
        roles = ctx.author.roles
        r_add = ""
        r_remove = ""
        for role in ctx.guild.roles:
            if str(role.id) in choices and role not in ctx.author.roles:
                roles.append(role)
                r_add += "{}, ".format(role.name)
            elif str(role.id) in choices and role in ctx.author.roles:
                roles.remove(role)
                r_remove += "{}, ".format(role.name)
        if r_add != "":
            r_add = r_add[:-2]
        else:
            r_add = "None"
        if r_remove != "":
            r_remove = r_remove[:-2]
        else:
            r_remove = "None"
        await ctx.author.edit(roles=roles)
        msg = await ctx.send("```\nRoles Added: {}\nRoles Removed: {}\n```".format(r_add, r_remove))
        self.bot.cmd_log(ctx, "Roles")
        await asyncio.sleep(20)
        await msg.delete()

    @roles.command()
    @checks.perms_manage_roles()
    async def add(self, ctx, role: discord.Role = None):
        """Adds a role to the list that can be assigned"""
        if role is None:
            return
        if role.position >= ctx.author.top_role.position:
            await ctx.send("Unable to add role due to Hierarchy")
        else:
            server = await self.bot.get_server_data(ctx.guild.id)
            server["roles"][role.id] = role.name
            await self.bot.update_server_data(ctx.guild.id, server)
            await ctx.send("Added {} to the role list".format(role.name))
        self.bot.cmd_log(ctx, "Added new role ({}) to roles list".format(role.name))

    @roles.command()
    @checks.perms_manage_roles()
    async def remove(self, ctx, role: discord.Role = None):
        """Removes a role from the list that can be assigned"""
        if role is None:
            return
        if role.position >= ctx.author.top_role.position:
            await ctx.send("Unable to remove role due to Hierarchy")
        else:
            server = await self.bot.get_server_data(ctx.guild.id)
            del server["roles"][str(role.id)]
            await self.bot.update_server_data(ctx.guild.id, server)
            await ctx.send("Removed {} from the role list".format(role.name))
        self.bot.cmd_log(ctx, "Removed role ({}) to roles list".format(role.name))


def setup(bot):
    bot.add_cog(Roles(bot))
