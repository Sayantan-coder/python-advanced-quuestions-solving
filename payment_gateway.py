from abc import ABC, abstractmethod
from datetime import datetime


class PaymentGateway(ABC):

    @abstractmethod
    def authenticate(self, api_key: str) -> bool:

        pass

    @abstractmethod
    def process_payment(self, amount: float, currency: str) -> dict:

        pass

    @abstractmethod
    def refund(self, transaction_id: str) -> bool:

        pass

    def generate_receipt(self, transaction: dict) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  PAYMENT RECEIPT\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  Gateway  : {self.__class__.__name__}\n"
            f"  Amount   : {transaction['amount']} {transaction['currency']}\n"
            f"  Txn ID   : {transaction['txn_id']}\n"
            f"  Status   : {transaction['status']}\n"
            f"  Time     : {timestamp}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━"
        )


class RazorpayGateway(PaymentGateway):

    def authenticate(self, api_key: str) -> bool:
        print(f"[Razorpay] Authenticating with key: {api_key[:8]}***")
        return api_key.startswith("rzp_")

    def process_payment(self, amount: float, currency: str) -> dict:
        return {
            "txn_id": "RZP_TXN_98765",
            "amount": amount,
            "currency": currency,
            "status": "SUCCESS",
            "gateway": "Razorpay",
        }

    def refund(self, transaction_id: str) -> bool:
        print(f"[Razorpay] Refunding transaction {transaction_id}")
        return True


class StripeGateway(PaymentGateway):

    def authenticate(self, api_key: str) -> bool:
        print(f"[Stripe] Authenticating with key: {api_key[:8]}***")
        return api_key.startswith("sk_")

    def process_payment(self, amount: float, currency: str) -> dict:
        return {
            "txn_id": "STR_TXN_12345",
            "amount": amount,
            "currency": currency,
            "status": "SUCCESS",
            "gateway": "Stripe",
        }

    def refund(self, transaction_id: str) -> bool:
        print(f"[Stripe] Refunding transaction {transaction_id}")
        return True


def checkout(gateway: PaymentGateway, api_key: str, amount: float):

    if not gateway.authenticate(api_key):
        print("❌ Authentication failed!")
        return

    txn = gateway.process_payment(amount, "INR")
    print(gateway.generate_receipt(txn))

    if amount > 10000:
        print(" High-value transaction — auto-refund test initiated")
        gateway.refund(txn["txn_id"])


razorpay = RazorpayGateway()
stripe = StripeGateway()

checkout(razorpay, "rzp_live_abc123", 5000.00)
print()
checkout(stripe, "sk_live_xyz789", 15000.00)
print()
