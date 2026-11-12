# StayEase - Manager Role
# ===================================================

FILES = {
    "rooms.csv": "room_id,room_type,price_per_night,status\n",
    "bookings.csv": (
        "booking_id,guest_id,room_id,check_in_date,"
        "expected_check_out_date,actual_check_out_date,"
        "status,payment_status,total_amount\n"
    ),
    "payments.csv": "payment_id,booking_id,amount,payment_date\n"
}

# INITIALIZE FILES
def initialize_files():
    for filename, header in FILES.items():
        try:
            with open(filename, "r"):
                pass
        except FileNotFoundError:
            with open(filename, "w") as file:
                file.write(header)


# MAKING UNIQUE ID
def generate_id(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        if len(lines) <= 1:
            return 1
        last_line = lines[-1].strip()
        if not last_line:
            return 1
        last_id = int(last_line.split(",")[0])
        return last_id + 1

# ADD ROOM
def add_room():
    print("\n--- Add Room ---")

    room_type = input("Room type (Single/Double/Family): ")
    while room_type == "" or "," in room_type:
        print("Invalid input. No commas allowed.")
        room_type = input("Room type: ")

    while True:
        try:
            price = float(input("Price per night: "))
            if price < 0:
                print("Price must be positive.")
                continue

            if price.is_integer():
                price = int(price)
            break
        except ValueError:
            print("Enter a valid number.")

    room_id = generate_id("rooms.csv")
    status = "available"

    with open("rooms.csv", "a") as file:
        file.write(f"{room_id},{room_type},{price},{status}\n")

    print(f"Room added with ID {room_id}.")


# UPDATE ROOM
def update_room():
    print("\n--- Update Room ---")

    with open("rooms.csv", "r") as file:
        lines = file.readlines()

    if len(lines) <= 1:
        print("No rooms to update.")
        return

    rid = input("Enter Room ID to update: ")
    found = False

    for i in range(1, len(lines)):
        data = lines[i].strip().split(",")

        if data[0] == rid:
            found = True
            print("Press Enter to keep current value.")

            # Update Type
            new_type = input(f"Current Room type [{data[1]}]: ")
            if new_type and "," not in new_type:
                data[1] = new_type

            # Update Price
            new_price = input(f"Current Price [{data[2]}]: ")
            if new_price:
                try:
                    p = float(new_price)
                    if p.is_integer():
                        p = int(p)
                    data[2] = str(p)
                except ValueError:
                    print("Invalid price, keeping old value.")

            # Update Status
            new_status = input(f"Current Status (available/reserved/occupied) [{data[3]}]: ").lower()
            if new_status in ("available", "reserved", "occupied"):
                data[3] = new_status

            lines[i] = ",".join(data) + "\n"
            break

    if found:
        with open("rooms.csv", "w") as file:
            file.writelines(lines)
        print("Room updated.")
    else:
        print("Room ID not found.")


# REMOVE ROOM
def remove_room():
    print("\n--- Remove Room ---")

    with open("rooms.csv", "r") as file:
        lines = file.readlines()

    if len(lines) <= 1:
        print("No rooms to remove.")
        return

    rid = input("Enter Room ID to remove: ")

    new_lines = [lines[0]]
    found = False

    for i in range(1, len(lines)):
        data = lines[i].strip().split(",")
        if data[0] == rid:
            found = True
        else:
            new_lines.append(lines[i])

    if found:
        with open("rooms.csv", "w") as file:
            file.writelines(new_lines)
        print("Room removed.")
    else:
        print("Room ID not found.")

# VIEW SYSTEM SUMMARY
def view_system_summary():
    print("\n--- System Summary ---")

    total_rooms = 0
    occupied_rooms = 0
    with open("rooms.csv", "r") as file:
        lines = file.readlines()
        for line in lines[1:]:
            total_rooms += 1
            data = line.strip().split(",")
            if data[3] != "available":
                occupied_rooms += 1

    total_bookings = 0
    with open("bookings.csv", "r") as file:
        lines = file.readlines()
        # Subtract 1 for header
        if len(lines) > 0:
            total_bookings = len(lines) - 1

    total_income = 0.0
    with open("payments.csv", "r") as file:
        lines = file.readlines()
        for line in lines[1:]:
            data = line.strip().split(",")
            # data[2] is amount
            total_income += float(data[2])

    occupancy_rate = 0.0
    if total_rooms > 0:
        occupancy_rate = (occupied_rooms / total_rooms) * 100

    print(f"Total bookings: {total_bookings}")
    print(f"Total rooms: {total_rooms}")
    print(f"Occupied rooms: {occupied_rooms}")
    print(f"Occupancy rate: {occupancy_rate:.2f}%")
    print(f"Total income recorded: {total_income:.2f}")


# DAILY REPORT
def daily_performance_report():
    print("\n--- Daily Performance Report ---")
    date = input("Enter date (YYYY-MM-DD): ")

    bookings_count = 0
    checkins = 0
    checkouts = 0
    income = 0.0

    with open("bookings.csv", "r") as file:
        lines = file.readlines()
        for line in lines[1:]:
            data = line.strip().split(",")

            if data[3] == date:
                bookings_count += 1

            if data[6] in ("checked_in", "checked_out") and data[3] == date:
                checkins += 1

            if data[6] == "checked_out" and data[5] == date:
                checkouts += 1

    with open("payments.csv", "r") as file:
        lines = file.readlines()
        for line in lines[1:]:
            data = line.strip().split(",")
            # data[3] is payment_date
            if data[3] == date:
                income += float(data[2])

    print(f"Date {date}:")
    print(f" - Bookings Created: {bookings_count}")
    print(f" - Check-ins: {checkins}")
    print(f" - Check-outs: {checkouts}")
    print(f" - Income: {income:.2f}")


# MONTHLY REPORT
def monthly_performance_report():
    print("\n--- Monthly Performance Report ---")
    month = input("Enter month (YYYY-MM): ")

    bookings_count = 0
    checkins = 0
    checkouts = 0
    income = 0.0

    with open("bookings.csv", "r") as file:
        lines = file.readlines()
        for line in lines[1:]:
            data = line.strip().split(",")

            if data[3].startswith(month):
                bookings_count += 1

            if data[6] in ("checked_in", "checked_out") and data[3].startswith(month):
                checkins += 1

            if data[5] and data[6] == "checked_out" and data[5].startswith(month):
                checkouts += 1

    with open("payments.csv", "r") as file:
        lines = file.readlines()
        for line in lines[1:]:
            data = line.strip().split(",")
            # data[3] is payment_date
            if data[3].startswith(month):
                income += float(data[2])

    print(f"Month {month}:")
    print(f" - Bookings Created: {bookings_count}")
    print(f" - Check-ins: {checkins}")
    print(f" - Check-outs: {checkouts}")
    print(f" - Income: {income:.2f}")


# MANAGER MENU
def manager_menu():
    initialize_files()
    while True:
        print("\n--- Manager Menu ---")
        print("1. Add Room")
        print("2. Update Room")
        print("3. Remove Room")
        print("4. View System Summary")
        print("5. Daily Report")
        print("6. Monthly Report")
        print("0. Exit")

        choice = input("Choose: ")

        if choice == "1":
            add_room()
        elif choice == "2":
            update_room()
        elif choice == "3":
            remove_room()
        elif choice == "4":
            view_system_summary()
        elif choice == "5":
            daily_performance_report()
        elif choice == "6":
            monthly_performance_report()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")