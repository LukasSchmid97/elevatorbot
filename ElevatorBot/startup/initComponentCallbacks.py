from dis_snek.models import ComponentCommand

from ElevatorBot.components.checks import check_pending
from ElevatorBot.components.componentCallbacks import ComponentCallbacks
from ElevatorBot.elevator import ElevatorSnake


def add_component_callbacks(client: ElevatorSnake):
    """Add global custom component callbacks"""

    # get all functions from the class. Magic
    for custom_id in [k for k in ComponentCallbacks.__dict__ if not k.startswith("__")]:
        component = ComponentCommand(
            name=f"ComponentCallback::{custom_id}",
            callback=getattr(ComponentCallbacks, custom_id),
            listeners=[custom_id],
        )

        # add my pending check to all of them
        component.checks.append(check_pending)

        client.add_component_callback(component)
