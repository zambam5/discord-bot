import aiohttp, logging, asyncio, datetime


class WizardsEvent:
    def __init__(self, event: dict) -> None:
        for item in event:
            if item == "cost":
                setattr(self, "_cost", event[item])
            elif item == "format":
                setattr(self, "_format", event[item])
            else:
                setattr(self, item, event[item])

    @property
    def cost(self):
        c = "{:.2f}".format(self._cost / 100)
        return f"${c}"

    @property
    def magicformat(self):
        if self._format == "COMMANDER2":
            return "Commander"
        elif self._format == "BOOSTER_DRAFT":
            return "Draft"
        elif self._format == "SEALED_DECK":
            return "Sealed"
        else:
            f = self._format[0].upper() + self._format[1:].lower()
            return f
