# StayEase - Receptionist Role

FILES = {
    "rooms.csv": "room_id,room_type,price_per_night,status\n",
    "guests.csv": "guest_id,name,phone,email\n",
    "bookings.csv": (
        "booking_id,guest_id,room_id,check_in_date,"
        "expected_check_out_date,actual_check_out_date,"
        "status,payment_status,total_amount\n"
    )
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

# GENERATE UNIQUE ID
def generate_id(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        if len(lines) <= 1:
            return 1
        last_id = int(lines[-1].split(",")[0])
        return last_id + 1

# REGISTER GUEST
def register_guest():
    print("\n--- Register Guest ---")
    name = input("Name: ")
    phone = input("Phone: ")
    email = input("Email: ")

    guest_id = generate_id("guests.csv")

    with open("guests.csv", "a") as file:
        file.write(f"{guest_id},{name},{phone},{email}\n")

    print(f"Guest registered successfully, GuestID = {guest_id}.")


# VIEW AVAILABLE ROOMS
def view_room_availability():
    print("\n--- Available Rooms ---")
    with open("rooms.csv", "r") as file:
        for line in file.readlines()[1:]:
            data = line.strip().split(",")
            if data[3] == "available":
                print(f"{data[0]} | {data[1]} | RM{data[2]}")


# CREATE BOOKING (UNPAID)
def create_booking():
    print("\n--- Create Booking ---")

    guest_id = input("Guest ID: ")
    room_type = input("Room type (single/double/family): ").lower()
    check_in_date = input("Check-in date (YYYY-MM-DD): ")
    expected_check_out_date = input("Expected check-out date (YYYY-MM-DD): ")

    try:
        nights = int(input("Number of nights: "))
    except ValueError:
        print("Invalid number.")
        return

    # Verify guest exists
    with open("guests.csv", "r") as file:
        for line in file.readlines()[1:]:
            if line.split(",")[0] == guest_id:
                break
        else:
            print("Guest not found.")
            return

    room_id = None
    price_per_night = 0

    with open("rooms.csv", "r") as file:
        rooms = file.readlines()

    for r in rooms[1:]:
        data = r.strip().split(",")
        if data[1].lower() == room_type and data[3] == "available":
            room_id = data[0]
            price_per_night = float(data[2])
            break

    if room_id is None:
        print("No available room.")
        return

    total_amount = price_per_night * nights
    booking_id = generate_id("bookings.csv")

    with open("bookings.csv", "a") as file:
        file.write(
            f"{booking_id},{guest_id},{room_id},{check_in_date},"
            f"{expected_check_out_date},,"
            f"pending,unpaid,{total_amount}\n"
        )

    # Reserve room
    for i in range(1, len(rooms)):
        r = rooms[i].strip().split(",")
        if r[0] == room_id:
            r[3] = "reserved"
            rooms[i] = ",".join(r) + "\n"
            break

    with open("rooms.csv", "w") as file:
        file.writelines(rooms)

    print(f"Booking created. Booking ID: {booking_id}")
    print(f"Total payment required: RM{total_amount}")
    print("Guest must pay accountant BEFORE check-in.")


# CHECK-IN (PAID ONLY)
def check_in():
    print("\n--- Check-in ---")
    booking_id = input("Booking ID: ")

    with open("bookings.csv", "r") as file:
        bookings = file.readlines()

    for i in range(1, len(bookings)):
        b = bookings[i].strip().split(",")

        if b[0] == booking_id:
            if b[6] == "checked_in":
                print("Guest already checked in.")
                return
            if b[7] != "paid":
                print("Payment not completed.")
                return

            room_id = b[2]
            b[6] = "checked_in"
            bookings[i] = ",".join(b) + "\n"
            break
    else:
        print("Booking not found.")
        return

    with open("bookings.csv", "w") as file:
        file.writelines(bookings)

    with open("rooms.csv", "r") as file:
        rooms = file.readlines()

    for i in range(1, len(rooms)):
        r = rooms[i].strip().split(",")
        if r[0] == room_id:
            r[3] = "occupied"
            rooms[i] = ",".join(r) + "\n"
            break

    with open("rooms.csv", "w") as file:
        file.writelines(rooms)

    print("Check-in successful.")


# CHECK-OUT (LATE STAY HANDLING)
def check_out():
    print("\n--- Check-out ---")
    booking_id = input("Booking ID: ")
    actual_check_out_date = input("Actual check-out date (YYYY-MM-DD): ")

    try:
        actual_nights = int(input("Actual nights stayed: "))
    except ValueError:
        print("Invalid input.")
        return

    with open("bookings.csv", "r") as file:
        bookings = file.readlines()

    for i in range(1, len(bookings)):
        b = bookings[i].strip().split(",")

        if b[0] == booking_id and b[6] == "checked_in":
            room_id = b[2]
            total_amount = float(b[8])

            price_per_night = None
            with open("rooms.csv", "r") as rf:
                for r in rf.readlines()[1:]:
                    r_data = r.strip().split(",")
                    if r_data[0] == room_id:
                        price_per_night = float(r_data[2])
                        break

            if price_per_night is None:
                print("Room price not found.")
                return

            expected_nights = int(total_amount / price_per_night)

            if actual_nights > expected_nights:
                extra_nights = actual_nights - expected_nights
                extra_amount = extra_nights * price_per_night
                total_amount += extra_amount

                b[7] = "unpaid"
                b[8] = str(total_amount)
                bookings[i] = ",".join(b) + "\n"

                with open("bookings.csv", "w") as file:
                    file.writelines(bookings)

                print("Late stay detected.")
                print(f"Outstanding payment: RM{extra_amount}")
                print("Guest must pay accountant before checkout.")
                return

            if b[7] != "paid":
                print("Outstanding payment.")
                return

            b[5] = actual_check_out_date
            b[6] = "checked_out"
            bookings[i] = ",".join(b) + "\n"
            break
    else:
        print("Booking not found.")
        return

    with open("bookings.csv", "w") as file:
        file.writelines(bookings)

    with open("rooms.csv", "r") as file:
        rooms = file.readlines()

    for i in range(1, len(rooms)):
        r = rooms[i].strip().split(",")
        if r[0] == room_id:
            r[3] = "available"
            rooms[i] = ",".join(r) + "\n"
            break

    with open("rooms.csv", "w") as file:
        file.writelines(rooms)

    print("Check-out completed.")

def cancel_booking():
    print("\n--- Cancel Booking ---")
    booking_id = input("Enter booking ID: ")

    # Read all bookings
    with open("bookings.csv", "r") as file:
        bookings = file.readlines()

    room_id = None
    new_bookings = [bookings[0]]  # keep header

    for booking in bookings[1:]:
        b = booking.strip().split(",")
        if b[0] == booking_id:
            room_id = b[2]  # store the room to free it later
            continue
        new_bookings.append(booking)

    if room_id is None:
        print("Booking not found.")
        return

    # Write updated bookings back to file
    with open("bookings.csv", "w") as file:
        file.writelines(new_bookings)

    # Free the room
    with open("rooms.csv", "r") as file:
        rooms = file.readlines()

    for i in range(1, len(rooms)):
        room = rooms[i].strip().split(",")
        if room[0] == room_id:
            room[3] = "available"
            rooms[i] = ",".join(room) + "\n"
            break

    with open("rooms.csv", "w") as file:
        file.writelines(rooms)

    print("Booking deleted successfully.")



# MENU
def receptionist_menu():
    while True:
        print("\n--- Receptionist Menu ---")
        print("1. Register Guest")
        print("2. View Available Rooms")
        print("3. Create Booking")
        print("4. Check-in")
        print("5. Check-out")
        print("6. Cancel Booking")
        print("0. Back")

        choice = input("Choose: ")

        if choice == "1":
            register_guest()
        elif choice == "2":
            view_room_availability()
        elif choice == "3":
            create_booking()
        elif choice == "4":
            check_in()
        elif choice == "5":
            check_out()
        elif choice == "6":
            cancel_booking()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


# START SYSTEM
initialize_files()
