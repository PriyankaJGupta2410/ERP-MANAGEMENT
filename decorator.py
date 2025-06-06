from functools import wraps
from flask import request,jsonify
import jwt
import os


############################## TOKEN ###########################
def authentication(socket_handler):
    @wraps(socket_handler)
    def wrapper(*args, **kwargs):
        try:
            token = None
            if "x-access-token" in request.headers:
                token = request.headers["x-access-token"]
            if not token:
                return jsonify({"message": "Authentication token missing"}), 401
            decoded_token = jwt.decode(
                token, os.environ.get("JWT_SECRET_KEY"), algorithms=["HS256"]
            )

            kwargs["current_user_id"] = str(decoded_token.get("_id"))

            return socket_handler(*args, **kwargs)
        except Exception as ex:
            return jsonify({"message": str(ex)}), 401
    return wrapper