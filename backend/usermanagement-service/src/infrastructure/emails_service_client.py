import httpx


class EmailsServiceClient:
    """Client for interacting with the emails-service API"""

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def send_registration_email(self, email: str, username: str):
        url = f"{self.base_url}/emails/send"
        payload = {"email": email}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        return response.json()
