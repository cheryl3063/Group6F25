from permissions_manager import PermissionManager
from sensors_listeners import SensorListener

def start_trip_recording():
    print("Trip recording started successfully! 🚗💨")

    # Initialize and start sensors
    sensors = SensorListener()
    sensors.start_listeners()

def main():
    print("=== Trip Start: Permission Check ===")
    pm = PermissionManager()

    # Ask for permissions
    pm.request_permissions()

    # Validate permissions before starting trip
    if pm.validate_permissions():
        start_trip_recording()
    else:
        print("Trip cannot start without required permissions ❌")

if __name__ == "__main__":
    main()
