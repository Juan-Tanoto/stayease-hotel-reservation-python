# CSV FILES
ROOMS_FILE    = "rooms.csv"
GUESTS_FILE   = "guests.csv"
BOOKINGS_FILE = "bookings.csv"
PAYMENTS_FILE = "payments.csv"

# HEADERS
ROOMS_HEADERS = ["room_id", "room_type", "price_per_night", "is_available"]
GUESTS_HEADERS = ["guest_id", "name", "phone", "email"]
BOOKINGS_HEADERS = [
    "booking_id", "guest_id", "room_id", "check_in_date", "expected_check_out_date",
    "actual_check_out_date", "status", "payment_status", "total_amount" ]
PAYMENTS_HEADERS = [ "payment_id", "booking_id", "amount", "payment_date", "method"]

# ALLOWED PAYMENT
PAYMENT_METHODS = ["cash", "card", "e_wallet", "bank_transfer"]

# FILE INITIALIZER
def file_with_header_checker(file, headers):
    header_line = ",".join(headers) + "\n"
    try:
        with open(file, "r") as f:
            first_line = f.readline()
        if first_line.strip() == "":
            with open(file, "w") as f:
                f.write(header_line)
    except FileNotFoundError:
        with open(file, "w") as f:
            f.write(header_line)

# ERROR MESSAGE
def err(msg):
    print("[ERROR]", msg)

# READ CSV
def read_csv_dict(file, headers):
    file_with_header_checker(file, headers)
    rows = []
    with open(file, "r") as f:
        lines = f.readlines()

    if len(lines) <= 1:
        return rows

    for line in lines[1:]:
        line = line.strip()
        if line == "":
            continue

        values = line.split(",")

        while len(values) < len(headers):
            values.append("")
        if len(values) > len(headers):
            values = values[:len(headers)]

        row = {}
        for i in range(len(headers)):
            row[headers[i]] = values[i].strip()

        rows.append(row)
    return rows

# WRITE CSV
def write_csv_dict(file, rows, headers):
    try:
        with open(file, "w") as f:
            f.write(",".join(headers) + "\n")
            for row in rows:
                values = []
                for h in headers:
                    if h in row:
                        v = str(row[h]).strip()
                    else:
                        v = ""
                    if "," in v:
                        v = v.replace(",", " ")
                    values.append(v)
                f.write(",".join(values) + "\n")
    except:
        err("Cannot write to " + file)

# APPEND CSV
def append_csv_row(file, row, headers):
    file_with_header_checker(file, headers)
    try:
        with open(file, "a") as f:
            values = []
            for h in headers:
                if h in row:
                    v = str(row[h]).strip()
                else:
                    v = ""
                if "," in v:
                    v = v.replace(",", " ")
                values.append(v)
            f.write(",".join(values) + "\n")
    except:
        err("Cannot append to " + file)

# LOOKUP FOR BOOKING
def find_booking(booking_id):
    for b in read_csv_dict(BOOKINGS_FILE, BOOKINGS_HEADERS):
        if b["booking_id"] == booking_id:
            return b
    return None

# PAYMENT ID
def generate_payment_id():
    file_with_header_checker(PAYMENTS_FILE, PAYMENTS_HEADERS)
    with open(PAYMENTS_FILE, "r") as f:
        lines = f.readlines()
    num = len(lines)
    s = str(num)
    while len(s) < 6:
        s = "0" + s
    return "P" + s

# CALCULATE PAID AMOUNT
def calculate_paid_amount(booking_id):
    total_paid = 0.0
    for p in read_csv_dict(PAYMENTS_FILE, PAYMENTS_HEADERS):
        if p["booking_id"] == booking_id:
            try:
                total_paid += float(p["amount"])
            except:
                pass
    return total_paid

# UPDATE PAYMENT STATUS
def update_payment_status(booking_id):
    bookings = read_csv_dict(BOOKINGS_FILE, BOOKINGS_HEADERS)
    total_paid = calculate_paid_amount(booking_id)

    for b in bookings:
        if b["booking_id"] == booking_id:
            try:
                total_amount = float(b["total_amount"])
            except:
                total_amount = 0.0

            if total_paid >= total_amount > 0:
                b["payment_status"] = "paid"
            else:
                b["payment_status"] = "unpaid"
            break

    write_csv_dict(BOOKINGS_FILE, bookings, BOOKINGS_HEADERS)

# ACCOUNTANT FEATURES
# ---------------------------
# RECORD PAYMENT (1)
def record_payment_flow():
    print("\n--- Record Payment ---")

    while True:
        booking_id = input("Booking ID: ").strip()
        if booking_id != "":
            break
        err("Booking ID required.")

    booking = find_booking(booking_id)
    if booking is None:
        err("Booking not found.")
        return

    try:
        total_amount = float(booking["total_amount"])
    except:
        total_amount = 0.0

    paid_amount = calculate_paid_amount(booking_id)
    outstanding = total_amount - paid_amount

    if outstanding <= 0:
        err("This booking is already fully paid.")
        return

    print("Outstanding Amount: MYR %.2f" % outstanding)

    # AMOUNT INPUT (LIMIT OVERPAYMENT INPUT)
    while True:
        amount = input("Amount: ").strip()
        try:
            given = float(amount)
            if given <= 0:
                err("Amount must be greater than zero.")
                continue

            if given >= outstanding:
                recorded_amount = outstanding
                changes = given - outstanding
            else:
                recorded_amount = given
                changes = 0.0

            amount = "%.2f" % recorded_amount
            break
        except:
            err("Invalid amount.")

    while True:
        payment_date = input("Payment Date (YYYY-MM-DD): ").strip()
        if len(payment_date) == 10 and payment_date[4] == "-" and payment_date[7] == "-":
            break
        err("Invalid date format.")

    while True:
        method = input("Method (cash/card/e_wallet/bank_transfer): ").strip().lower()
        if method in PAYMENT_METHODS:
            break
        err("Invalid method.")

    payment_id = generate_payment_id()

    append_csv_row(PAYMENTS_FILE, {
        "payment_id": payment_id,
        "booking_id": booking_id,
        "amount": amount,
        "payment_date": payment_date,
        "method": method},
                   PAYMENTS_HEADERS)

    update_payment_status(booking_id)
    print("Payment recorded successfully.")

    if changes > 0:
        print("Changes to return: MYR %.2f" %changes)

    if input("Show receipt now? (y/n): ").lower() == "y":
        print_receipt_by_booking_id(booking_id)

# RECEIPT (2)
def print_receipt_by_booking_id(booking_id):
    b = find_booking(booking_id)
    if b is None:
        err("Booking not found.")
        return

    update_payment_status(booking_id)
    b = find_booking(booking_id)

    guest = None
    for g in read_csv_dict(GUESTS_FILE, GUESTS_HEADERS):
        if g["guest_id"] == b["guest_id"]:
            guest = g
            break

    room = None
    for r in read_csv_dict(ROOMS_FILE, ROOMS_HEADERS):
        if r["room_id"] == b["room_id"]:
            room = r
            break

    try:
        total = float(b["total_amount"])
    except:
        total = 0.0

    paid = calculate_paid_amount(booking_id)
    outstanding = total - paid

    print("\n==============================================")
    print("StayEase Hotel - PAYMENT RECEIPT")
    print("Booking ID:", booking_id)
    print("Guest:", guest["name"] if guest else "Unknown")
    print("Room:", room["room_type"] if room else "Unknown")
    print("Check-in:", b["check_in_date"])
    print("Expected Check-out:", b["expected_check_out_date"])
    print("Actual Check-out:", b["actual_check_out_date"])
    print("Payment Status:", b["payment_status"])
    print("Total Amount: MYR %.2f" % total)
    print("Paid Amount:  MYR %.2f" % paid)
    print("Outstanding: MYR %.2f" % outstanding)
    print("==============================================")

# INCOME & OUTSTANDING REPORT (3)
def income_outstanding_report_flow():
    bookings = read_csv_dict(BOOKINGS_FILE, BOOKINGS_HEADERS)

    total_income = 0.0
    total_outstanding = 0.0

    print("\n=================== INCOME & OUTSTANDING REPORT ===================")

    if not bookings:
        print("[INFO] No bookings found.")
        print("===================================================================")
        return

    for b in bookings:
        try:
            total = float(b["total_amount"])
        except:
            total = 0.0

        paid = calculate_paid_amount(b["booking_id"])
        outstanding = total - paid

        total_income += paid
        total_outstanding += outstanding

        print(f"Booking ID: {b['booking_id']} | Total: {total:.2f} | Paid: {paid:.2f} | Outstanding: {outstanding:.2f}")
        print("-------------------------------------------------------------------")

    print("Total Income:      MYR %.2f" % total_income)
    print("Total Outstanding: MYR %.2f" % total_outstanding)
    print("===================================================================")

# MONTHLY SUMMARY (4)
def monthly_financial_summary_flow():
    print("\n--- Monthly Financial Summary ---")
    month_input = input("Enter month (YYYY-MM): ").strip()

    try:
        year_input = month_input[:4]
        month_only_input = month_input[5:7]
    except:
        err("Invalid month format. Use YYYY-MM.")
        return

    total = 0.0
    payments = read_csv_dict(PAYMENTS_FILE, PAYMENTS_HEADERS)

    for p in payments:
        date_str = p["payment_date"]
        if len(date_str) >= 7:
            year = date_str[:4]
            month_only = date_str[5:7]
            if year == year_input and month_only == month_only_input:
                try:
                    total += float(p["amount"])
                except:
                    pass

    print("Total income for", month_input, ": MYR %.2f" % total)

# ---------- MENU ----------
def accountant_menu():
    while True:
        print("\n=== Accountant Menu ===")
        print("1) Record Guest Payment")
        print("2) Show Receipt")
        print("3) Income & Outstanding Report")
        print("4) Monthly Financial Summary")
        print("0) Back")

        choice = input("Choose: ").strip()

        if choice == "1":
            record_payment_flow()
        elif choice == "2":
            bid = input("Enter booking ID: ").strip()
            print_receipt_by_booking_id(bid)
        elif choice == "3":
            income_outstanding_report_flow()
        elif choice == "4":
            monthly_financial_summary_flow()
        elif choice == "0":
            break
        else:
            err("Invalid option.")