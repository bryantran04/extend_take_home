from flask import Flask, Response, request
from redis import Redis
from dotenv import dotenv_values
import dotenv
import json
import os
from ExtendClient import ExtendClient


dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

app = Flask(__name__)

extend_client = ExtendClient()


@app.route("/credit_card/sign_in", methods=["POST"])
def sign_in():
    return extend_client.sign_in()


@app.route("/credit_card/get_user_info", methods=["GET"])
def get_users():
    return extend_client.get_users()


@app.route("/credit_card/get_virtual_cards", methods=["GET"])
def get_virtual_cards():
    return extend_client.get_virtual_cards()


@app.route("/credit_card/transactions_min", methods=["GET"])
def get_transactions():
    return extend_client.get_transactions()


@app.route("/credit_card/transaction/<transaction_id>", methods=["GET"])
def get_transaction(transaction_id):
    return extend_client.get_transaction(transaction_id)


@app.route("/credit_card/transactions_detailed", methods=["GET"])
def get_transactions_detailed():
    return extend_client.get_transaction_detailed()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
