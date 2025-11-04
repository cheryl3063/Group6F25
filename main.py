from permissions_manager import PermissionManager

def start_trip_recording():
    print("Trip recording started successfully! 🚗💨")

def main():
    print("=== Trip Start: Permission Check ===")
    pm = PermissionManager()
    pm.request_permissions()

    if pm.validate_permissions():
        start_trip_recording()
    else:
        print("Trip cannot start without required permissions ❌")

if __name__ == "__main__":
    main()
