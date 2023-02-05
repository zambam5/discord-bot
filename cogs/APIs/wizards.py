import aiohttp, datetime, logging, time, os, asyncio, pytz


async def event_list_request(lat: float, lng: float):
    dt = datetime.datetime.now(tz=pytz.UTC)
    event_list = []
    url = f"https://api.tabletop.wizards.com/event-reservations-service/events/search?lat={lat}&lng={lng}&tag=magic:_the_gathering&searchType=magic-events&maxMeters=80467&page=0pageSize=90&sort=date&sortDirection=asc"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            response = await res.json()
            for event in response["results"]:
                event_dt = datetime.datetime.fromisoformat(event["startDatetime"])
                local = event_dt.astimezone(tz=pytz.timezone("America/Chicago"))
                if event_dt > dt + datetime.timedelta(days=7):
                    break
                else:
                    event["startDateTime"] = local
                    event_list.append(event)
    return event_list


async def org_by_id(org_id):
    url = f"https://api.tabletop.wizards.com/event-reservations-service/Organizations/by-ids?ids={org_id}"
    name = ""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            response = await res.json()
            name = response[0]["name"]
    return name


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    x = loop.run_until_complete(event_list_request(44.2754558, -94.43879))
    print(x)
