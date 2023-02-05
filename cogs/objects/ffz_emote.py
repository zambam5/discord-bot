import aiohttp, logging, asyncio

from io import BytesIO


logger = logging.getLogger("__main__." + __name__)


class Emote:
    """Class for an emote object from ffz"""

    def __init__(self, emote: dict) -> None:
        for item in emote:
            setattr(self, item, emote[item])

    @property
    def is_wide(self) -> bool:
        """Determine if an emote is wide or not based on its width
        self.width is an int

        Returns:
            bool: True if wide, False if not
        """
        return self.width > 40

    async def load_image(self, size: str):
        print(self.name)
        url = "https:" + self.urls[size]
        semaphore = asyncio.Semaphore(10)
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    image_bytes = await response.read()
        return image_bytes
