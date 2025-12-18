# onedrive.py â€“ OneDrive Integration for Jaicat
import os
import requests
import webbrowser
from msal import PublicClientApplication

# TODO: Replace these with real values from your Azure app registration
CLIENT_ID = "YOUR_CLIENT_ID"
TENANT_ID = "YOUR_TENANT_ID"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Files.ReadWrite.All", "User.Read"]
TOKEN_CACHE_FILE = "jaicat_token.txt"


class OneDriveIntegration:
    def __init__(self):
        self.access_token = None
        self.app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
        self._load_cached_token()

    def _load_cached_token(self):
        if os.path.exists(TOKEN_CACHE_FILE):
            with open(TOKEN_CACHE_FILE, "r") as f:
                self.access_token = f.read().strip()

    def _save_token(self, token):
        with open(TOKEN_CACHE_FILE, "w") as f:
            f.write(token)

    def authenticate_user(self):
        if self.access_token:
            return self.access_token

        print("ðŸ” Authenticating with Microsoft...")
        flow = self.app.initiate_device_flow(scopes=SCOPES)

        if "user_code" not in flow:
            raise Exception("Failed to initiate device flow")

        print("ðŸ‘‰ Visit this URL to sign in:", flow["verification_uri"])
        print("ðŸ”‘ Enter the code:", flow["user_code"])
        webbrowser.open(flow["verification_uri"])

        result = self.app.acquire_token_by_device_flow(flow)

        if "access_token" in result:
            self.access_token = result["access_token"]
            self._save_token(self.access_token)
            print("âœ… Authentication successful.")
            return self.access_token
        else:
            raise Exception("âŒ Authentication failed.")

    def list_files(self):
        token = self.authenticate_user()
        url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers)

        if resp.ok:
            files = resp.json().get("value", [])
            for f in files:
                print(f"ðŸ“„ {f['name']} ({f['size']} bytes)")
            return files
        else:
            print("âŒ Failed to list files.")
            print(resp.text)
            return []

    def upload_file(self, local_path, remote_name=None):
        token = self.authenticate_user()
        if not remote_name:
            remote_name = os.path.basename(local_path)

        with open(local_path, "rb") as f:
            content = f.read()

        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{remote_name}:/content"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream"
        }

        resp = requests.put(url, headers=headers, data=content)

        if resp.ok:
            print(f"ðŸ“¤ Uploaded '{remote_name}' successfully.")
        else:
            print("âŒ Upload failed:", resp.status_code)
            print(resp.text)

    def download_file(self, remote_name, local_path):
        token = self.authenticate_user()
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{remote_name}:/content"
        headers = {"Authorization": f"Bearer {token}"}

        resp = requests.get(url, headers=headers)

        if resp.ok:
            with open(local_path, "wb") as f:
                f.write(resp.content)
            print(f"ðŸ“¥ Downloaded '{remote_name}' to '{local_path}'.")
        else:
            print("âŒ Download failed:", resp.status_code)
            print(resp.text)

    def delete_file(self, remote_name):
        token = self.authenticate_user()
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{remote_name}:/"
        headers = {"Authorization": f"Bearer {token}"}

        resp = requests.delete(url, headers=headers)

        if resp.ok:
            print(f"ðŸ—‘ï¸ Deleted '{remote_name}'.")
        else:
            print("âŒ Deletion failed:", resp.status_code)
            print(resp.text)
    def get_file_info(self, remote_name):
        token = self.authenticate_user()
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{remote_name}"
        headers = {"Authorization": f"Bearer {token}"}

        resp = requests.get(url, headers=headers)

        if resp.ok:
            file_info = resp.json()
            print(f"ðŸ“„ File Info: {file_info}")
            return file_info
        else:
            print("âŒ Failed to get file info:", resp.status_code)
            print(resp.text)
            return None
    def create_folder(self, folder_name):
        token = self.authenticate_user()
        url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
        headers = { "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"} 
        data = { "name": folder_name,
                 "folder": {},
                 "@microsoft.graph.conflictBehavior": "rename" }    
        resp = requests.post(url, headers=headers, json=data)   

        if resp.ok: 
            print(f"ðŸ“ Created folder '{folder_name}' successfully."        
                    )  
        else:
            print("âŒ Folder creation failed:", resp.status_code)
            print(resp.text)    
        return
    def move_file(self, remote_name, target_folder):
        token = self.authenticate_user()
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{remote_name}"
        headers = {"Authorization": f"Bearer {token}",
                   "Content-Type": "application/json"}
        data = {
            "parentReference": {
                "path": f"/drive/root:/{target_folder}"
            }
        }

        resp = requests.patch(url, headers=headers, json=data)

        if resp.ok:
            print(f"ðŸ“¦ Moved '{remote_name}' to '{target_folder}' successfully.")
        else:
            print("âŒ Move failed:", resp.status_code)
            print(resp.text)

        return resp
    def share_file(self, remote_name, recipient_email):
        token = self.authenticate_user()
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{remote_name}:/invite"
        headers = {"Authorization": f"Bearer {token}",
                   "Content-Type": "application/json"}
        data = {
            "emailAddress": {   
                "address": recipient_email
            },
            "role": "reader"            
            }
        resp = requests.post(url, headers=headers, json=data)
        if resp.ok:
            print(f"ðŸ”— Shared '{remote_name}' with {recipient_email} successfully.")
        else:
            print("âŒ Sharing failed:", resp.status_code)
            print(resp.text)
        return resp
    def search_files(self, query):
        token = self.authenticate_user()
        url = f"https://graph.microsoft.com/v1.0/me/drive/root/search(q='{query}')"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers)

        if resp.ok:
            results = resp.json().get("value", [])
            if results:
                print(f"ðŸ” Search results for '{query}':")
                for f in results:
                    print(f"ðŸ“„ {f['name']} ({f['size']} bytes)")
            else:
                print(f"ðŸ” No results found for '{query}'.")
            return results
        else:
            print("âŒ Search failed:", resp.status_code)
            print(resp.text)
            return []
    def get_quota_info(self):
        token = self.authenticate_user()
        url = "https://graph.microsoft.com/v1.0/me/drive"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers)

        if resp.ok:
            quota_info = resp.json().get("quota", {})
            print(f"ðŸ“Š Quota Info: {quota_info}")
            return quota_info
        else:
            print("âŒ Failed to get quota info:", resp.status_code)
            print(resp.text)
            return None
    def get_recent_files(self):
        token = self.authenticate_user()
        url = "https://graph.microsoft.com/v1.0/me/drive/recent"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers)    

        if resp.ok:
            recent_files = resp.json().get("value", [])
            if recent_files:
                print("ðŸ“‚ Recent Files:")
                for f in recent_files:
                    print(f"ðŸ“„ {f['name']} ({f['size']} bytes)")
            else:
                print("ðŸ“‚ No recent files found.")
            return recent_files
        else:
            print("âŒ Failed to get recent files:", resp.status_code)
            print(resp.text)
            return []
    def get_shared_files(self):
        token = self.authenticate_user()
        url = "https://graph.microsoft.com/v1.0/me/drive/sharedWithMe"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers)

        if resp.ok:
            shared_files = resp.json().get("value", [])
            if shared_files:
                print("ðŸ”— Shared Files:")
                for f in shared_files:
                    print(f"ðŸ“„ {f['name']} ({f['size']} bytes)")
            else:
                print("ðŸ”— No shared files found.")
            return shared_files
        else:
            print("âŒ Failed to get shared files:", resp.status_code)
            print(resp.text)
            return []
    def get_file_activity(self, remote_name):
        token = self.authenticate_user()
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{remote_name}/activities"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers)

        if resp.ok:
            file_activity = resp.json().get("value", [])
            if file_activity:
                print(f"ðŸ“Š Activity for '{remote_name}':")
                for activity in file_activity:
                    print(f"ðŸ—“ï¸ {activity['activityDateTime']}: {activity['activityType']}")
            else:
                print(f"ðŸ“Š No activity found for '{remote_name}'."  )  
            return file_activity
        else:
            print("âŒ Failed to get file activity:", resp.status_code)
            print(resp.text)
            return []
    def get_user_info(self):
        token = self.authenticate_user()
        url = "https://graph.microsoft.com/v1.0/me"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers)

        if resp.ok:
            user_info = resp.json()
            print(f"ðŸ‘¤ User Info: {user_info}")
            return user_info
        else:
            print("âŒ Failed to get user info:", resp.status_code)
            print(resp.text)
            return None
    def get_drive_info(self):
        token = self.authenticate_user()
        url = "https://graph.microsoft.com/v1.0/me/drive"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers)

        if resp.ok:
            drive_info = resp.json()
            print(f"ðŸ“‚ Drive Info: {drive_info}")
            return drive_info
        else:
            print("âŒ Failed to get drive info:", resp.status_code)
            print(resp.text)
            return None 
    def get_shared_item_info(self, shared_item_id):
        token = self.authenticate_user()
        url = f"https://graph.microsoft.com/v1.0/shares/{shared_item_id}/driveItem"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers)
        if resp.ok:
            shared_item_info = resp.json()
            print(f"ðŸ”— Shared Item Info: {shared_item_info}")
            return shared_item_info
        else:
            print("âŒ Failed to get shared item info:", resp.status_code)
            print(resp.text)
            return None
    def get_item_by_id(self, item_id):
        token = self.authenticate_user()
        url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers)

        if resp.ok:
            item_info = resp.json()
            print(f"ðŸ“„ Item Info: {item_info}")
            return item_info
        else:
            print("âŒ Failed to get item by ID:", resp.status_code)
            print(resp.text)
            return None
    def get_item_by_path(self, item_path):
        token = self.authenticate_user()
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{item_path}"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers)

        if resp.ok:
            item_info = resp.json()
            print(f"ðŸ“„ Item Info by Path: {item_info}")
            return item_info
        else:
            print("âŒ Failed to get item by path:", resp.status_code)
            print(resp.text)
            return None
    def get_item_children(self, item_id):
        token = self.authenticate_user()
        url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/children"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers)

        if resp.ok:
            children = resp.json().get("value", [])
            print(f"ðŸ“‚ Children of Item ID {item_id}:")
            for child in children:
                print(f"ðŸ“„ {child['name']} ({child['size']} bytes)")
            return children
        else:
            print("âŒ Failed to get item children:", resp.status_code)
            print(resp.text)
            return []
    def get_item_thumbnail(self, item_id, size="large"):
        token = self.authenticate_user()
        url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/thumbnails/{size}"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers)

        if resp.ok:
            thumbnail_info = resp.json()
            print(f"ðŸ“¸ Thumbnail Info: {thumbnail_info}")
            return thumbnail_info
        else:
            print("âŒ Failed to get item thumbnail:", resp.status_code)
            print(resp.text)
            return None
    def get_item_versions(self, item_id):
        token = self.authenticate_user()
        url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/versions"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers)
        if resp.ok:
            versions = resp.json().get("value", [])
            print(f"ðŸ“œ Versions of Item ID {item_id}:")
            for version in versions:
                print(f"ðŸ—“ï¸ {version['lastModifiedDateTime']}: {version['id']}")
            return versions
        else:
            print("âŒ Failed to get item versions:", resp.status_code)
            print(resp.text)
            return []
    def get_item_permissions(self, item_id):
        token = self.authenticate_user()
        url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/permissions"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers)
        if resp.ok:
            permissions = resp.json().get("value", [])
            print(f"ðŸ” Permissions for Item ID {item_id}:")
            for perm in permissions:
                print(f"ðŸ“ {perm['id']}: {perm['roles']}")
            return permissions
        else:
            print("âŒ Failed to get item permissions:", resp.status_code)
            print(resp.text)
            return []
