import os
import requests
from models.User import User
from models.VirtualCard import VirtualCard
from models.Transactions import Transaction, TransactionDetailed
from collections import defaultdict
import copy
import json


class ExtendClient:
    def __init__(self):
        self.access_token = None
        self.refreh_token = None
        self.user_id = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.paywithextend.v2021-03-12+json",
        }
        self.data = {
            "email": os.environ.get("EMAIL"),
            "password": os.environ.get("PASSWORD"),
        }
        self.base_url = os.environ.get("BASE_URL")

    def sign_in(self):
        url = self.base_url + "signin"

        response = requests.post(url, headers=self.headers, json=self.data)

        if response.status_code == 200:
            response_json = response.json()
            refresh_token, access_token = (
                response_json["refreshToken"],
                response_json["token"],
            )
            self.refreh_token = refresh_token
            self.access_token = access_token
            self.user_id = response_json["user"]["id"]
            self.headers["Authorization"] = f"Bearer {access_token}"

            return response_json
        else:
            return response.json(), response.status_code

    def get_users(self):
        url = self.base_url + f"users/{self.user_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.json(), response.status_code

    def get_virtual_cards(self):
        url = self.base_url + f"virtualcards"

        response = requests.get(url, headers=self.headers)
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
            return response.json(), response.status_code

    def get_virtual_card_ids(self):
        url = self.base_url + f"virtualcards"

        response = requests.get(url, headers=self.headers)

        virtual_card_ids = []
        if response.status_code == 200:
            for virtual_card in response.json().get("virtualCards"):
                virtual_card_ids.append(virtual_card.get("id"))
                return {"virtual_card_ids": virtual_card_ids}
        else:
            return {"error": response.json()}

    def get_transactions(self):
        get_virtual_card_ids_response = self.get_virtual_card_ids()
        if "virtual_card_ids" in get_virtual_card_ids_response:
            virtual_card_ids = get_virtual_card_ids_response["virtual_card_ids"]
        else:
            return get_virtual_card_ids_response["error"]

        res = {"transactions": []}
        for virtual_card_id in virtual_card_ids:
            url = (
                self.base_url
                + f"virtualcards/{virtual_card_id}/transactions?status=PENDING,CLEARED,DECLINED"
            )
            response = requests.get(url, headers=self.headers)
            res["transactions"].append(
                {
                    "virtual_credit_card_id": virtual_card_id,
                    "virtual_credit_card_transactions": [],
                }
            )
            if response.status_code == 200:
                for transaction in response.json()["transactions"]:
                    cur_transaction = Transaction(
                        billing_amount_cents=transaction.get(
                            "clearingBillingAmountCents"
                        ),
                        status=transaction.get("status"),
                        merchant_name=transaction.get("merchantName"),
                    )
                    res["transactions"][-1]["virtual_credit_card_transactions"].append(
                        cur_transaction.serialize()
                    )
        return res

    def get_transaction(self, transaction_id):
        url = self.base_url + f"transactions/{transaction_id}"
        response = requests.get(url, headers=self.headers)

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

    def get_transaction_detailed(self):

        virtual_card_ids = self.get_virtual_card_ids()["virtual_card_ids"]

        res = {"transactions": []}

        for virtual_card_id in virtual_card_ids:
            url = (
                self.base_url
                + f"virtualcards/{virtual_card_id}/transactions?status=PENDING,CLEARED,DECLINED"
            )
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                for transaction in response.json()["transactions"]:
                    res["transactions"].append(
                        self.get_transaction(transaction.get("id"))
                    )
        return res
