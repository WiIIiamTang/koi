import json
import os
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, Response

from lib import miniclient, tasks

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s %(threadName)s : %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = Flask(__name__)
client = miniclient.MiniClient(
    logger=logging.getLogger("miniclient"),
    token=os.environ.get("DISCORD_AUTH_TOKEN"),
    default_channel_id=os.environ.get("NOTIF_CHANNEL_ID"),
)


@app.route("/health/healthping", methods=["GET"])
def health():
    return "OK", 200


@app.post("/prechecker/precheck/koi")
def koi_precheck():
    """
    precheck for koi
    This needs to check the headers for Bearer token and validate it
    """
    if (
        os.environ.get("AUTH_TOKEN") is None
        or request.headers.get("Authorization")
        != f"Bearer {os.environ.get('AUTH_TOKEN')}"
    ):
        return Response(
            json.dumps({"status": "error", "message": "Unauthorized"}),
            status=403,
            mimetype="application/json",
        )

    timenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # get the data from the request
    data = request.get_json()
    if type(data) is not dict:
        data = json.loads(data)
    logging.info(f"Received {data}")

    # start precheck
    tasks.notify_precheck_start(
        logger=logging.getLogger("precheck"),
        client=client,
        message=f"New commit was pushed for release: `{data['commit_sha']}` `{data['commit_message']}` - starting precheck tasks",  # noqa
    )
    save_success = tasks.save_bot_data(
        logger=logging.getLogger("precheck"), client=client
    )
    tasks.notify_precheck_end(
        logger=logging.getLogger("precheck"),
        client=client,
        message=f"Precheck tasks {'failed. Release will be aborted' if not save_success else 'succeeded, bot will restart'}",  # noqa
    )

    timefinished = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return Response(
        json.dumps(
            {
                "status": "success" if save_success else "error",
                "message": f"Precheck {'failed' if not save_success else 'succeeded'}",
                "timestarted": timenow,
                "timefinished": timefinished,
            }
        ),
        status=200
        if save_success
        else 500,  # use error code to abort if precheck fails
        mimetype="application/json",
    )


@app.post("/postchecker/postcheck/koi")
def koi_postcheck():
    """
    postcheck for koi
    This needs to check the headers for Bearer token and validate it
    """
    if (
        os.environ.get("AUTH_TOKEN") is None
        or request.headers.get("Authorization")
        != f"Bearer {os.environ.get('AUTH_TOKEN')}"
    ):
        return Response(
            json.dumps({"status": "error", "message": "Unauthorized"}),
            status=403,
            mimetype="application/json",
        )

    timenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # get the data from the request
    data = request.get_json()
    if type(data) is not dict:
        data = json.loads(data)

    logger = logging.getLogger("postcheck")

    logger.info(f"Bot is starting up at {data.get('time_started')}")
    logger.info("Waiting 20 seconds for bot to start up...")
    time.sleep(20)

    # start postcheck
    response = tasks.handle_check_bot_startup(
        logger=logging.getLogger("postcheck"), client=client
    )
    timefinished = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if response:
        client.send_message(
            channel_id=os.environ.get("NOTIF_CHANNEL_ID"),
            message="All messages will be deleted in a couple of hours. Happy release!",
        )
        return Response(
            json.dumps(
                {
                    "status": "success",
                    "message": "Postcheck successful",
                    "timestarted": timenow,
                    "timefinished": timefinished,
                }
            ),
            status=200,
            mimetype="application/json",
        )
    else:
        client.send_message(
            channel_id=os.environ.get("NOTIF_CHANNEL_ID"),
            message="I didn't detect the bot online. It looks like the release failed?",
        )
        return Response(
            json.dumps(
                {
                    "status": "error",
                    "message": "Bot not ready",
                    "timestarted": timenow,
                    "timefinished": timefinished,
                }
            ),
            status=500,
            mimetype="application/json",
        )
