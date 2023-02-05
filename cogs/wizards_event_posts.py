from .APIs.wizards import event_list_request, org_by_id
from .objects.wizards_event import WizardsEvent
from discord import Embed, Color
import datetime, os, json, asyncio, logging
from discord.ext import tasks, commands


logger = logging.getLogger("__main__." + __name__)


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead < 0:  # Target day already happened this week
        days_ahead = 7 + days_ahead
    return d + datetime.timedelta(days_ahead)


class EventPosts(commands.Cog):
    def __init__(self, lat, lng, channel, bot) -> None:
        self.lat = lat
        self.lng = lng
        self.channel = channel
        self.bot = bot
        self.event_timer.start()

    async def generate_embed(self, lat, lng):
        event_list = await event_list_request(lat, lng)
        embed = Embed(
            title="Area Events This Week",
            color=Color(15818558),
            description="Here are the events coming up this week at the WPN stores within 50 miles of New Ulm",
            timestamp=datetime.datetime.now(),
        )
        for event in event_list:
            event = WizardsEvent(event)
            org_name = await org_by_id(event.organizationId)
            dt = event.startDateTime
            t = dt.strftime("%H:%M")
            if (
                dt.strftime("%A").lower() in event.name.lower()
                or "FNM".lower() in event.name.lower()
            ):
                if event.magicformat.lower() in event.name.lower():
                    embed.add_field(
                        name=event.name,  # f"({int_to_day[dt.weekday()]})",
                        value=f"Store: {org_name} • Cost: {event.cost} • Time: {t}",
                        inline=True,
                    )
                else:
                    embed.add_field(
                        name=event.name,  # f"({int_to_day[dt.weekday()]})",
                        value=f"Store: {org_name} • Format: {event.magicformat} • Cost: {event.cost} • Time: {t}",
                        inline=True,
                    )
            else:
                embed.add_field(
                    name=dt.strftime("%A")
                    + ": "
                    + event.name,  # f"({int_to_day[dt.weekday()]})",
                    value=f"Store: {org_name} • Format: {event.magicformat} • Cost: {event.cost} • Time: {t}",
                    inline=True,
                )
        return embed

    @commands.hybrid_command(name="events")
    @commands.has_guild_permissions(administrator=True)
    async def _events(self, ctx):
        e = await self.generate_embed(self.lat, self.lng)
        await ctx.send(embed=e)

    async def _post_embed(self):
        embed = await self.generate_embed(lat=self.lat, lng=self.lng)
        channel = self.bot.get_channel(self.channel)
        await channel.send(embed=embed)

    @staticmethod
    async def _sleep_timer():
        dt = datetime.datetime.now()
        print(dt.weekday())
        nd = next_weekday(dt, 0)
        nd_fixed = nd.replace(hour=14, minute=0, second=0)
        diff = nd_fixed - dt
        logger.info("Setting message for %s", nd_fixed.isoformat())
        await asyncio.sleep(diff.total_seconds() - 30)

    @tasks.loop(seconds=30)
    async def event_timer(self):
        # // TODO Set the sleep in the timer loop the same as the before_loop function
        await self._post_embed()
        await self._sleep_timer()

    @event_timer.before_loop
    async def before_event_timer(self):
        """
        Initial sleep timer
        """
        await self._sleep_timer()
        # logger.info("twitch notifs waiting on bot")
        # await self.discord.wait_until_ready()


if os.path.isfile("./config/wizards_events.json"):
    with open("./config/wizards_events.json", "r") as f:
        config = json.load(f)

x = config["newulm"]


async def setup(bot):
    await bot.add_cog(EventPosts(x["lat"], x["lng"], x["channel"], bot))
