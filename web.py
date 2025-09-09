#!/bin/env python3
import sys, os
from flask import Flask, jsonify

# Add .lib to sys.path so Python can find api.py
sys.path.append(os.path.join(os.getcwd(), ".lib"))

from api import user_info, post_info

app = Flask(__name__)

@app.route("/")
def index():
    return {"message": "Instagram scraper API running"}

@app.route("/user/<username>")
def get_user(username):
    try:
        # call your existing function
        data = user_info(username)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/user/<username>/posts")
def get_user_posts(username):
    try:
        # first load user info (so globals are set properly)
        user_info(username)
        data = post_info()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
