import aiohttp, logging

from io import BytesIO
from PIL import Image


logger = logging.getLogger("__main__." + __name__)


class Emote:
    """Class for an emote object from ffz"""

    __slots__ = (
        "id",
        "name",
        "height",
        "width",
        "public",
        "hidden",
        "modifier",
        "offset",
        "margins",
        "css",
        "owner",
        "urls",
        "status",
        "usage_count",
        "created_at",
        "last_updated",
    )

    def __init__(self, emote: dict) -> None:
        for item in self.__slots__:
            setattr(self, item, emote[item])

    @property
    def is_wide(self):
        """Determine if an emote is wide or not based on its width

        Returns:
            bool: True if wide, False if not
        """
        if self.width > 40:
            return True
        else:
            return False

    async def load_image(self, size: str):
        print(self.name)
        url = "https:" + self.urls[size]
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                image_bytes = await response.read()
                await session.close()
        return image_bytes
