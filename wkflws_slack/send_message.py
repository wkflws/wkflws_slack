import json
from typing import Any

from slack_sdk.web.async_client import AsyncWebClient
from wkflws.logging import getLogger

logger = getLogger("wkflws_slack.send_message")
logger.setLevel(10)


async def send_message(
    message: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    """Process some incoming data."""
    # All debugging information MUST be output in stderr. you can just use the logging
    # module or if you are a die hard print debugger use this instead:
    # print(pformat(message), file=sys.stderr)

    try:
        api_token = context["Task"]["slack_bot_token"]
    except KeyError:
        raise ValueError("'slack_bot_token' undefined!") from None

    try:
        channel: str = message["channel"]
    except KeyError:
        raise ValueError("'channel' missing from Parameters") from None

    try:
        slack_msg = message["message"]
    except KeyError:
        raise ValueError("'message' missing from Parameters") from None

    optional_params = {}
    if "username" in message:
        optional_params["username"] = message["username"]

    if "icon_emoji" in message:
        optional_params["icon_emoji"] = message["icon_emoji"]

    if "icon_url" in message:
        optional_params["icon_url"] = message["icon_url"]

    client = AsyncWebClient(token=api_token)
    logger.info(f"Sending message '{slack_msg}' to {channel}")
    response = await client.chat_postMessage(
        channel=channel,
        text=slack_msg,
        **optional_params,
    )

    return response.data  # type:ignore # this is a dict


if __name__ == "__main__":
    import asyncio
    import sys

    # message is the input to your function. This is the output from the previous
    # function plus any transformations the user defined in their workflow. Parameters
    # should be documented in the parameters.json file so they can be used in the UI.
    try:
        message = json.loads(sys.argv[1])
    except IndexError:
        raise ValueError("missing required `message` argument") from None

    # this contains some contextual information about the workflow and the current
    # state. required secrets should be defined in the README so users can write their
    # lookup class with this node's unique requirements in mind.
    try:
        context = json.loads(sys.argv[2])
    except IndexError:
        raise ValueError("missing `context` argument") from None

    output = asyncio.run(send_message(message, context))

    # Non-zero exit codes indicate to the executor there was an unrecoverable error and
    # workflow execution should terminate.
    if output is None:
        logger.error("Received null output.")
        sys.exit(1)

    # The output of your function is input for a potential next state. It must be in
    # JSON format and be the only thing output on stdout. This value is picked up by the
    # executor and processed.
    print(json.dumps(output))
