# main.py - combine the three modules
# import manager
import receptionist
import accountant
import manager

def main_menu():
    while True:
        print("\n=== StayEase Hotel System ===")
        print("1. Manager")
        print("2. Receptionist")
        print("3. Accountant")
        print("0. Exit")
        choice = input("Select role: ").strip()
        if choice == '1':
            manager.manager_menu()
        elif choice == '2':
            receptionist.receptionist_menu()
        elif choice == '3':
            accountant.accountant_menu()
        elif choice == '0':
            print("Thank You! Hope You Enjoy!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main_menu()