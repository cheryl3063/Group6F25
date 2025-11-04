import json
import os

class PermissionManager:
    def __init__(self):
        self.permissions_file = "permissions.json"
        self.permissions = {
            "location": False,
            "motion": False
        }
        self.load_permissions()

    def load_permissions(self):
        """Load permission state from file if it exists."""
        if os.path.exists(self.permissions_file):
            with open(self.permissions_file, "r") as file:
                self.permissions = json.load(file)

    def save_permissions(self):
        """Save current permission state to file."""
        with open(self.permissions_file, "w") as file:
            json.dump(self.permissions, file, indent=4)

    def request_permissions(self):
        """Simulate user granting or denying permissions."""
        print("=== Requesting Permissions ===")
        for key in self.permissions:
            if not self.permissions[key]:
                answer = input(f"Grant {key} permission? (y/n): ").strip().lower()
                self.permissions[key] = True if answer == "y" else False
        self.save_permissions()

    def validate_permissions(self):
        """Check if all permissions are granted."""
        missing = [perm for perm, granted in self.permissions.items() if not granted]
        if missing:
            print(f"Missing permissions: {', '.join(missing)}")
            return False
        print("All permissions granted ✅")
        return True
