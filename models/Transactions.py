class Transaction:
    def __init__(self, billing_amount_cents, status, merchant_name):
        self.billing_amount_cents = billing_amount_cents
        self.status = status
        self.merchantName = merchant_name

    def serialize(self):
        return {
            "billing_amount_cents": self.billing_amount_cents,
            "status": self.status,
            "merchantName": self.merchantName,
        }


class TransactionDetailed(Transaction):
    def __init__(
        self,
        transaction_id,
        billing_amount_cents,
        status,
        merchant_name,
        authed_at,
        virtual_card_id,
        card_type,
        recipient_name,
        name_on_card,
    ):
        super().__init__(billing_amount_cents, status, merchant_name)
        self.transaction_id = transaction_id
        self.virtual_card_id = virtual_card_id
        self.card_type = card_type
        self.recipient_name = recipient_name
        self.name_on_card = name_on_card
        self.authed_at = authed_at

    def serialize(self):
        return {
            "transaction_id": self.transaction_id,
            "billing_amount_cents": self.billing_amount_cents,
            "status": self.status,
            "merchantName": self.merchantName,
            "authed_at": self.authed_at,
            "virtual_card_id": self.virtual_card_id,
            "card_type": self.card_type,
            "recipient_name": self.recipient_name,
            "name_on_card": self.name_on_card,
        }
