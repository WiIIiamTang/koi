import json
import os
import time
import logging
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
    token=os.environ.get("AUTH_TOKEN"),
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
    tasks.notify_precheck_start(
        client,
        f"New commit was pushed for release: {data['commit_message']} - starting precheck tasks",
    )
    timefinished = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return Response(
        json.dumps(
            {
                "status": "success",
                "message": "Precheck successful",
                "timestarted": timenow,
                "timefinished": timefinished,
            }
        ),
        status=200,
        mimetype="application/json",
    )
