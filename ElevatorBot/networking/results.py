import dataclasses
from typing import Optional

from naff import Embed

from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.errorCodesAndResponses import get_error_codes_and_responses


@dataclasses.dataclass()
class BackendResult:
    """Holds the return info"""

    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None
    message: Optional[str] = None

    __error_message: Optional[str] = None

    def __bool__(self):
        return self.success

    @property
    def embed(self) -> Embed:
        """ " Returns a nicely formatted embed, which can be returned to the user"""

        return embed_message(title="Error", description=self.error_message)

    @property
    def error_message(self) -> str:
        """Returns the corresponding error message for the error"""

        if not self.__error_message:
            if not self.error:
                self.__error_message = "Success"

            if msg := get_error_codes_and_responses().get(self.error):
                self.__error_message = msg
            elif msg := get_error_codes_and_responses().get(f"Bungie{self.error}"):
                self.__error_message = msg
            else:
                if self.message is not None:
                    self.__error_message = f"{self.error}: {self.message}"
                else:
                    self.__error_message = "Something went wrong"

        return self.__error_message

    @error_message.setter
    def error_message(self, kwargs: dict):
        """Formats the error message. See error_codes_and_responses"""

        self.__error_message = self.error_message.format(**kwargs)

    async def send_error_message(
        self,
        ctx: ElevatorInteractionContext,
        hidden: bool = False,
        **format_kwargs,
    ):
        """Sends the error message. format_kwargs are used to format the message before sending it"""

        # format it
        if format_kwargs:
            self.error_message = format_kwargs

        # do not send "NoToken" errors since they are handled elsewhere
        if self.error != "NoToken":
            await ctx.send(ephemeral=hidden, embeds=self.embed)
