from flask import json, jsonify, request
from werkzeug.exceptions import HTTPException


def handle_error(err, code):
    return jsonify({"error": str(err)}), code


@dacc.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    response = e.get_response()
    response.data = json.dumps({"error": e.description})
    response.content_type = "application/json"
    return response


@dacc.route("/")
def index():
    return "Hello, World!"


@dacc.route("/contribute", methods=["POST"])
def contribute():
    request_data = request.get_json()
    print(request_data)
    return "ok"


@dacc.route("/status")
def status():
    status = {}

    # Check database
    try:
        # to check database we will execute raw query
        db.session.execute("SELECT 1")
        status["db"] = {"status": "ok"}
    except Exception as e:
        status["db"] = {"status": "ko", "error": str(e)}

    # Compute global status
    status["global_status"] = (
        "ko"
        if "ko" in [status[key].get("status", "ko") for key in status.keys()]
        else "ok"
    )
    return jsonify(status)
