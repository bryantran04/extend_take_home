from flask import Flask, Response, request
from redis import Redis
from dotenv import dotenv_values
import dotenv
import requests
import json
import os
from models.User import User
from models.VirtualCard import VirtualCard
from models.Transactions import Transaction, TransactionDetailed
from collections import defaultdict
import copy


dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

app = Flask(__name__)
redis = Redis(host="redis", port=6379)


class ExtendClient:
    def __init__(self):
        self.access_token = None
        self.refreh_token

    def sign_in(self):
        pass


@app.route("/")
def hello():
    redis.incr("hits")
    counter = str(redis.get("hits"), "utf-8")
    return "This webpage has been viewed " + counter + " time(s)"


@app.route("/credit_card/sign_in", methods=["POST"])
def sign_in():

    data = {
        "email": os.environ.get("EMAIL"),
        "password": os.environ.get("PASSWORD"),
    }
    url = os.environ.get("BASE_URL") + "signin"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.paywithextend.v2021-03-12+json",
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        response_json = response.json()
        refresh_token, access_token = (
            response_json["refreshToken"],
            response_json["token"],
        )
        user_id = response_json["user"]["id"]

        os.environ["REFESH_TOKEN"] = refresh_token
        os.environ["ACCESS_TOKEN"] = access_token
        os.environ["USER_ID"] = user_id

        dotenv.set_key(dotenv_file, "REFESH_TOKEN", os.environ["REFESH_TOKEN"])
        dotenv.set_key(dotenv_file, "TOKEN", os.environ["ACCESS_TOKEN"])
        dotenv.set_key(dotenv_file, "USER_ID", os.environ["USER_ID"])

        return response_json
    else:
        return response.text, 401


@app.route("/credit_card/get_user_info", methods=["GET"])
def get_users():
    user_id = os.environ.get("USER_ID")
    access_token = os.environ.get("ACCESS_TOKEN")
    url = os.environ.get("BASE_URL") + f"users/{user_id}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.paywithextend.v2021-03-12+json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return url


@app.route("/credit_card/get_virtual_cards", methods=["GET"])
def get_virtual_cards():
    access_token = os.environ.get("ACCESS_TOKEN")
    url = os.environ.get("BASE_URL") + f"virtualcards"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.paywithextend.v2021-03-12+json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(url, headers=headers)
    virutal_cards = []
    if response.status_code == 200:
        for virtual_card in response.json().get("virtualCards"):
            recipient = virtual_card.get("recipient")
            card_holder = virtual_card.get("cardholder")

            recipient_min = User(
                user_id=recipient.get("id"),
                first_name=recipient.get("firstName"),
                last_name=recipient.get("lastName"),
            )
            card_holder_min = User(
                user_id=recipient.get("id"),
                first_name=card_holder.get("firstName"),
                last_name=card_holder.get("lastName"),
            )

            virtual_card_min = VirtualCard(
                virtual_card_id=virtual_card.get("id"),
                display_name=virtual_card.get("displayName"),
                card_holder=copy.deepcopy(card_holder_min),
                recipient=copy.deepcopy(recipient_min),
                balance_cents=virtual_card.get("balanceCents"),
            )
            virutal_cards.append(virtual_card_min.serialize())
            return {"virtual_cards": virutal_cards}

    else:
        return url


def get_virtual_card_ids():
    access_token = os.environ.get("ACCESS_TOKEN")
    url = os.environ.get("BASE_URL") + f"virtualcards"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.paywithextend.v2021-03-12+json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(url, headers=headers)

    virtual_card_ids = []
    if response.status_code == 200:
        for virtual_card in response.json().get("virtualCards"):
            virtual_card_ids.append(virtual_card.get("id"))
            return {"virtual_card_ids": virtual_card_ids}


@app.route("/credit_card/transactions", methods=["GET"])
def get_transactions():
    access_token = os.environ.get("ACCESS_TOKEN")
    virtual_card_ids = get_virtual_card_ids()["virtual_card_ids"]

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.paywithextend.v2021-03-12+json",
        "Authorization": f"Bearer {access_token}",
    }

    res = {"transactions": []}

    for virtual_card_id in virtual_card_ids:
        url = (
            os.environ.get("BASE_URL")
            + f"virtualcards/{virtual_card_id}/transactions?status=PENDING,CLEARED,DECLINED"
        )
        response = requests.get(url, headers=headers)
        res["transactions"].append(
            {
                "virtual_credit_card_id": virtual_card_id,
                "virtual_credit_card_transactions": [],
            }
        )
        if response.status_code == 200:
            for transaction in response.json()["transactions"]:
                cur_transaction = Transaction(
                    billing_amount_cents=transaction.get("clearingBillingAmountCents"),
                    status=transaction.get("status"),
                    merchant_name=transaction.get("merchantName"),
                )

                res["transactions"][-1]["virtual_credit_card_transactions"].append(
                    cur_transaction.serialize()
                )

    return res


@app.route("/credit_card/transaction/<transaction_id>", methods=["GET"])
def get_transaction(transaction_id):
    access_token = os.environ.get("ACCESS_TOKEN")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.paywithextend.v2021-03-12+json",
        "Authorization": f"Bearer {access_token}",
    }

    url = os.environ.get("BASE_URL") + f"transactions/{transaction_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return TransactionDetailed(
            transaction_id=response.json().get("id"),
            billing_amount_cents=response.json().get("clearingBillingAmountCents"),
            status=response.json().get("status"),
            merchant_name=response.json().get("merchantName"),
            authed_at=response.json().get("authedAt"),
            virtual_card_id=response.json().get("virtualCardId"),
            card_type=response.json().get("type"),
            recipient_name=response.json().get("recipientName"),
            name_on_card=response.json().get("nameOnCard"),
        ).serialize()
    else:
        return response.json(), response.status_code


@app.route("/credit_card/transactions_detailed", methods=["GET"])
def get_transactions_detailed():

    access_token = os.environ.get("ACCESS_TOKEN")
    virtual_card_ids = get_virtual_card_ids()["virtual_card_ids"]

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.paywithextend.v2021-03-12+json",
        "Authorization": f"Bearer {access_token}",
    }

    res = {"transactions": []}

    for virtual_card_id in virtual_card_ids:
        url = (
            os.environ.get("BASE_URL")
            + f"virtualcards/{virtual_card_id}/transactions?status=PENDING,CLEARED,DECLINED"
        )
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            for transaction in response.json()["transactions"]:
                res["transactions"].append(get_transaction(transaction.get("id")))
    return res


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
