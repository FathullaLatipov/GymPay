# payme/methods/generate_link.py
class GeneratePayLink:
    def __init__(self, user_id, amount):
        self.user_id = user_id
        self.amount = amount

    def generate_link(self):
        from urllib.parse import urlencode

        params = {
            "merchant": "ваш_merchant_id",
            "amount": self.amount * 100,  # сумма в тийинах
            "account[user_id]": self.user_id,
            "lang": "ru"
        }

        query_string = urlencode(params)
        return f"https://checkout.paycom.uz/{query_string}"
