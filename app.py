import json
import os
import time
from dotenv import load_dotenv
from flask import Flask, request, Response

load_dotenv()

app = Flask(__name__)


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

    time.sleep(10)

    return Response(
        json.dumps({"status": "success", "message": "Precheck successful"}),
        status=200,
        mimetype="application/json",
    )
