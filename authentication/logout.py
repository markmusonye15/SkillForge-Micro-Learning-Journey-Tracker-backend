from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access"]

jwt = JWTManager(app)

# In-memory blacklist
jwt_blacklist = set()

# Add logout route
@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # Unique token ID
    jwt_blacklist.add(jti)
    return jsonify({"message": "Logged out successfully"}), 200

# Check if token is blacklisted
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload["jti"] in jwt_blacklist

