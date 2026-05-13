from abc import ABC, abstractmethod
from datetime import datetime


class NotificationService(ABC):

    def __init__(self, service_name):
        self.__service_name = service_name  # Private Attribute
        self.__sent_count = 0
        self.__last_sent = None

    # Used Getter method to access the Encapsulated property
    @property
    def service_name(self):
        return self.__service_name

    @property
    def sent_count(self):
        return self.__sent_count

    @property
    def last_sent(self):
        return self.__last_sent

    # Define Private Method to track Internally
    def __record_send(self):
        self.__sent_count += 1
        self.__last_sent = datetime.now().strftime("%H:%M:%S")

    def dispatch(self, recipient, message):

        result = self.send(recipient, message)
        self.__record_send()
        return result

    @abstractmethod
    def send(self, recipient, message):
        pass

    @abstractmethod
    def get_status(self) -> dict:
        pass


class EmailService(NotificationService):
    def __init__(self, smtp_server):
        super().__init__("Email")
        self.__smtp = smtp_server

    def send(self, recipient, message):
        return f" [EMAIL via {self.__smtp}] To: {recipient} | {message}"

    def get_status(self):
        return {
            "service": self.service_name,
            "smtp": self.__smtp,
            "sent": self.sent_count,
        }


class SMSService(NotificationService):
    def __init__(self, phone_gateway):
        super().__init__("SMS")
        self.__gateway = phone_gateway

    def send(self, recipient, message):
        return f" [SMS via {self.__gateway}] To: {recipient} | {message[:160]}"

    def get_status(self):
        return {
            "service": self.service_name,
            "gateway": self.__gateway,
            "sent": self.sent_count,
        }


class WhatsAppService(NotificationService):
    def __init__(self, api_token):
        super().__init__("WhatsApp")
        self.__token = api_token[:8] + "***"  # Masking for saftey Purpose

    def send(self, recipient, message):
        return f" [WhatsApp | token={self.__token}] To: {recipient} | {message}"

    def get_status(self):
        return {
            "service": self.service_name,
            "token": self.__token,
            "sent": self.sent_count,
        }


class PushNotificationService(NotificationService):
    def __init__(self, app_id):
        super().__init__("Push")
        self.__app_id = app_id

    def send(self, recipient, message):
        return f" [PUSH | app={self.__app_id}] To: {recipient} | {message}"

    def get_status(self):
        return {
            "service": self.service_name,
            "app_id": self.__app_id,
            "sent": self.sent_count,
        }


def notify_user(service: NotificationService, user: str, msg: str):

    print(service.dispatch(user, msg))
    print(f"   └─ Total sent by {service.service_name}: {service.sent_count}\n")


services = [
    EmailService("smtp.gmail.com"),
    SMSService("Twilio"),
    WhatsAppService("wa_token_abc123xyz"),
    PushNotificationService("com.myapp.android"),
]

for svc in services:
    notify_user(svc, "banerjee@gmail.com", "Your order has been shipped! ")


notify_user(services[0], "Rahul@example.com", "Flash sale ends in 2 hours! ")
notify_user(services[0], "ghosh@example.com", "Your OTP is 483921")

print(" Service Status Reports:")
for svc in services:
    print(f"   {svc.get_status()}")
