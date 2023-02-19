import json
import os
import logging
import time
from datetime import datetime, timedelta
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
    notify_precheck_start_success = tasks.notify_precheck_start(
        logger=logging.getLogger("precheck"),
        client=client,
        message=f"New commit was pushed for release: `{data['commit_sha']}` `{data['commit_message']}` - starting precheck tasks",  # noqa
        commit_sha=data["commit_sha"],
    )
    time.sleep(3)
    if notify_precheck_start_success:
        save_success = tasks.save_bot_data(
            logger=logging.getLogger("precheck"), client=client
        )
    else:
        save_success = False

    tasks.notify_precheck_end(
        logger=logging.getLogger("precheck"),
        client=client,
        message=f"Precheck tasks {'failed. Release will be aborted, Ill let bill know...' if not save_success else 'succeeded, bot will restart. Please wait while the new release is deployed'} `{data['commit_sha']}` `{data['commit_message']}`",  # noqa
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
            message="Post-setup done - it looks like everything's ok. Happy release!",
        )

        if os.environ.get("PUB_NOTIF_CHANNEL_ID") is not None:
            # Get the unix timestamp for the next month, on the 20th day.
            new_year = (datetime.now().month + 1) > 12
            next_month = (datetime.now().month + 1) % 12
            next_month = 1 if next_month == 0 else next_month

            # get the date for the 20th of the next_month
            next_month = datetime(
                datetime.now().year + 1 if new_year else datetime.now().year,
                next_month,
                20,
            ).timestamp()

            client.send_message(
                channel_id=os.environ.get("PUB_NOTIF_CHANNEL_ID"),
                message=f"billbot auto switchover complete, next scheduled downtime: <t:{int(next_month)}:F>",
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
