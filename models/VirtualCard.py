from models.User import User


class VirtualCard:
    def __init__(
        self,
        virtual_card_id,
        display_name,
        card_holder: User,
        recipient: User,
        balance_cents,
    ):
        self.virtual_card_id = virtual_card_id
        self.display_name = display_name
        self.card_holder = card_holder
        self.recipient = recipient
        self.balance_cents = balance_cents

    def serialize(self):
        return {
            "virtual_card_id": self.virtual_card_id,
            "display_name": self.display_name,
            "card_holder": self.card_holder.serialize(),
            "recipient": self.recipient.serialize(),
            "balance_cents": self.balance_cents,
        }
