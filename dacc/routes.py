from dacc import dacc, db, validate, insertion, restitution
from dacc.models import Auth
from flask import json, jsonify, request
from werkzeug.exceptions import HTTPException
from flask_httpauth import HTTPTokenAuth
from dacc import cache
from dacc.exceptions import AccessException, ValidationException

auth = HTTPTokenAuth(scheme="Bearer")


def handle_error(err, code):
    return jsonify({"error": str(err)}), code


@auth.verify_token
@cache.memoize(timeout=60)  # Cache for 1 minute
def verify_token(token):
    auth = Auth.query_by_token(token)
    return auth.org if auth else None


@dacc.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    response = e.get_response()
    response.data = json.dumps({"error": e.description})
    response.content_type = "application/json"
    return response


@dacc.route("/measure", methods=["POST"])
@auth.login_required
def add_raw_measure():
    """Add a raw measure to the database

    Returns:
        HTTP response: {"ok": true} if everything went well
    """
    try:
        measure = request.get_json()
        if validate.check_incoming_raw_measure(measure):
            insertion.insert_raw_measure(measure)
            return jsonify({"ok": True}), 201
    except ValidationException as err:
        return handle_error(err, 400)
    except Exception as err:
        return handle_error(err, 500)


@dacc.route("/aggregate", methods=["GET"])
@auth.login_required
def get_aggregated_results():
    """Get aggregated results

    Returns:
        HTTP response: [results]
    """
    try:
        params = request.get_json()
        if validate.check_restitution_params(params):
            res = restitution.get_aggregated_results(params)
            return jsonify(res), 200
    except AccessException as err:
        return handle_error(err, 403)
    except ValidationException as err:
        return handle_error(err, 400)
    except Exception as err:
        return handle_error(err, 500)


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
