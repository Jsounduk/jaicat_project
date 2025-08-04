
import os
import requests
import json
import webbrowser
import threading
from msal import PublicClientApplication

class OneDriveClient:
    def __init__(self, client_id, tenant_id=None, authority_url=None, scopes=None):
        self.client_id = client_id
        self.tenant_id = tenant_id or "consumers"
        self.authority = authority_url or f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scopes = scopes or ["Files.ReadWrite", "offline_access", "User.Read"]
        self.access_token = None

        self.app = PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority
        )

        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(self.scopes, account=accounts[0])
        else:
            result = self.acquire_token_interactively()

        if "access_token" in result:
            self.access_token = result["access_token"]
        else:
            raise Exception("Failed to obtain access token.")

    def acquire_token_interactively(self):
        flow = self.app.initiate_device_flow(scopes=self.scopes)
        if "user_code" not in flow:
            raise Exception("Failed to create device flow")
        print(f"🔐 Go to {flow['verification_uri']} and enter code: {flow['user_code']}")
        webbrowser.open(flow['verification_uri'])
        return self.app.acquire_token_by_device_flow(flow)

    def get_headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def upload_file(self, local_path, remote_path):
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{remote_path}:/content"
        with open(local_path, "rb") as f:
            response = requests.put(url, headers=self.get_headers(), data=f)
        return response.status_code, response.json()

    def download_file(self, remote_path, local_path):
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{remote_path}:/content"
        response = requests.get(url, headers=self.get_headers())
        if response.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(response.content)
        return response.status_code

    def list_drive_items(self, folder_path="/"):
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_path}:/children"
        response = requests.get(url, headers=self.get_headers())
        return response.status_code, response.json()

    def sync_folder(self, local_folder, remote_folder):
        files = Path(local_folder).glob("*")
        for file in files:
            if file.is_file():
                self.upload_file(str(file), f"{remote_folder}/{file.name}")
