import httpx

class SMS:
    def __init__(self):
        self.endpoint = 'https://imis.nictanzania.co.tz/production/communication/sms_send/'

    async def send(self, to, message, client=""):
        data={
            "recipients": to,
            "message": message,
            "customer_name": client,
            "module":"Meeting App",
            "category":0
        }
        response = httpx.post(self.endpoint, data=data)
        
        # print response status code
        print(response.status_code)
        # print response body
        print(response.text)