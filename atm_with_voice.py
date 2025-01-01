import tkinter as tk
from tkinter import messagebox, simpledialog
import pyttsx3
import time
from tkinter import PhotoImage
from PIL import Image, ImageTk
import requests
from io import BytesIO
from datetime import datetime

class ATM:
    def __init__(self, balance=0, pin="1234", account_number="000123456"):
        self.balance = balance
        self.pin = pin  # Store PIN directly for validation
        self.account_number = account_number  # Store account number
        self.transaction_history = []  # To store transaction history
        self.incorrect_pin_attempts = 0  # Track incorrect PIN attempts
        self.locked = False  # Track account lock status
        self.speech_engine = pyttsx3.init()  # Initialize TTS engine
        self.last_activity_time = time.time()  # Track last activity time for session timeout

    def speak(self, text):
        """Convert text to speech."""
        self.speech_engine.say(text)
        self.speech_engine.runAndWait()

    def validate_pin(self, pin):
        """Validate the PIN directly."""
        if self.locked:
            self.speak("Your account is locked due to multiple failed attempts. Please try again later.")
            return False

        if pin == self.pin:
            self.incorrect_pin_attempts = 0
            return True
        else:
            self.incorrect_pin_attempts += 1
            if self.incorrect_pin_attempts >= 3:
                self.lock_account()
            return False

    def lock_account(self):
        """Lock the account for a certain period."""
        self.locked = True
        self.speak("Too many incorrect attempts! Your account is now locked. Please try again after 30 seconds.")
        time.sleep(30)  # Lock for 30 seconds
        self.locked = False

    def deposit(self, amount):
        """Deposit money into the account."""
        if amount > 0:
            self.balance += amount
            self.transaction_history.append(f"Deposited: ${amount}")
            message = f"You have deposited: ${amount}. Your current balance is: ${self.balance}."
            self.speak(f"You have deposited {amount} dollars.")  # Only speak the deposit amount.
            return message
        else:
            message = "Deposit amount must be positive!"
            self.speak(message)
            return message

    def withdraw(self, amount):
        """Withdraw money from the account."""
        if amount > 0:
            if amount <= self.balance:
                self.balance -= amount
                self.transaction_history.append(f"Withdrawn: ${amount}")
                message = f"You have withdrawn: ${amount}. Your current balance is: ${self.balance}."
                self.speak(f"You have withdrawn {amount} dollars.")  # Only speak the withdrawal amount.
                return message
            else:
                message = "Insufficient funds!"
                self.speak(message)
                return message
        else:
            message = "Withdrawal amount must be positive!"
            self.speak(message)
            return message

    def transfer(self, amount, to_account):
        """Transfer money to another account."""
        if amount > 0:
            if len(to_account) != 10 or not to_account.isdigit():
                message = "Account number must be exactly 10 digits."
                self.speak(message)
                return message

            if amount <= self.balance:
                self.balance -= amount
                self.transaction_history.append(f"Transferred: ${amount} to account {to_account}")
                message = f"You have transferred: ${amount} to account {to_account}. Your remaining balance is: ${self.balance}."
                self.speak(f"You have transferred {amount} dollars.")  # Only speak the transfer amount.
                return message
            else:
                message = "Insufficient funds for transfer!"
                self.speak(message)
                return message
        else:
            message = "Transfer amount must be positive!"
            self.speak(message)
            return message

    def view_transaction_history(self):
        """View the transaction history."""
        if self.transaction_history:
            message = "\n".join(self.transaction_history)
            self.speak("Here is your transaction history.")
            return message
        else:
            message = "No transactions yet!"
            self.speak(message)
            return message

    def view_account_details(self):
        """View account details."""
        message = f"Account Number: {self.account_number}\nCurrent Balance: ${self.balance}"
        return message  # Print only without speaking.

    def change_pin(self, old_pin, new_pin):
        """Allow user to change their PIN."""
        if self.validate_pin(old_pin):
            self.pin = new_pin  # Update the PIN
            self.speak("Your PIN has been changed successfully.")
            return "Your PIN has been changed successfully."
        else:
            self.speak("Incorrect current PIN. Please try again.")
            return "Incorrect current PIN. Please try again."

# GUI setup and remaining code.

class ATM_GUI:
    def __init__(self, root, atm):
        self.atm = atm
        self.root = root
        self.root.title("ATM System")

        # Make the window full-screen and set the background color
        self.root.attributes('-fullscreen', True)
        # Load the background image
        self.bg_image = Image.open("Integration-Security.png")
        self.bg_image = self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        # Add the image to the background
        self.bg_label = tk.Label(root, image=self.bg_photo)
        self.bg_label.place(relx=0.5, rely=0.5, anchor="center")  # Center the image

        # Create a label for background text "ATM"
        self.bg_label = tk.Label(root, text="ATM Project", font=("Arial", 100, "bold"), fg="#FFFFFF", bg="#1D3557", bd=5, relief="solid")
        self.bg_label.place(relx=0.5, rely=0.1, anchor="center")  # Position at the top center

        # Add a frame to hold all the widgets with a larger width and height
        self.frame = tk.Frame(root, bg="#1E90FF", bd=10, relief="raised", width=1800, height=700)
        self.frame.place(relx=0.5, rely=0.2, anchor="n")  # Align to the top of the window

        # Welcome message and PIN input
        self.welcome_message = tk.Label(self.frame, text="Welcome to the ATM! Please enter your PIN.", font=("Arial", 20, "bold"), fg="white", bg="#1E90FF")
        self.welcome_message.grid(row=0, column=0, columnspan=3, pady=20)

        self.atm.speak("Welcome to the ATM. Please enter your PIN.")

        self.pin_label = tk.Label(self.frame, text="Enter PIN:", font=("Arial", 14), fg="white", bg="#1E90FF")
        self.pin_label.grid(row=1, column=0, padx=10)
        self.pin_entry = tk.Entry(self.frame, show="*", font=("Arial", 14), width=20)
        self.pin_entry.grid(row=1, column=1, padx=10)

        self.login_button = tk.Button(self.frame, text="Login", font=("Arial", 14), command=self.login, bg="#32CD32", fg="white", activebackground="#3CB371", relief="flat", bd=5)
        self.login_button.grid(row=1, column=2, padx=10)

        self.message_label = tk.Label(self.frame, text="", font=("Arial", 14), fg="white", bg="#1E90FF", height=3)
        self.message_label.grid(row=2, column=0, columnspan=3, pady=10)

        # Set up buttons but disable them initially
        self.balance_button = self.create_button("Check Balance", self.check_balance)
        self.deposit_button = self.create_button("Deposit Money", self.deposit)
        self.withdraw_button = self.create_button("Withdraw Money", self.withdraw)
        self.transfer_button = self.create_button("Transfer Money", self.transfer)
        self.history_button = self.create_button("Transaction History", self.view_transaction_history)
        self.account_details_button = self.create_button("View Account Details", self.view_account_details)
        self.change_pin_button = self.create_button("Change PIN", self.change_pin)
        self.exit_button = tk.Button(self.frame, text="Exit", font=("Arial", 14), command=self.exit_program, bg="#e74c3c", fg="white", activebackground="#c0392b", relief="flat", bd=5)
        self.exit_button.grid(row=6, column=2, pady=10, sticky="e")  # Align right

        # Date and time label
        self.datetime_label = tk.Label(self.frame, text="", font=("Arial", 14), fg="white", bg="#1E90FF")
        self.datetime_label.grid(row=7, column=0, columnspan=3, pady=10)

        self.update_datetime()  # Call the function to update date and time

    def create_button(self, text, command):
        # Calculate row and column based on the total number of buttons
        row = len(self.frame.grid_slaves()) // 3 + 2  # Start from row 3 (to leave space for other widgets)
        col = len(self.frame.grid_slaves()) % 3  # Place buttons in 3 columns

        button = tk.Button(self.frame, text=text, font=("Arial", 14), command=command, state="disabled", bg="#2980b9", fg="white", activebackground="#3498db", relief="flat", bd=5)
        button.grid(row=row, column=col, pady=10, padx=10, stick="nsew")
        return button

    def update_datetime(self):
        """Update the date and time label."""
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.datetime_label.config(text=current_time)
        self.root.after(1000, self.update_datetime)  # Update every second

    def login(self):
        pin = self.pin_entry.get()
        if self.atm.validate_pin(pin):
            self.message_label.config(text="Login successful!")
            self.atm.speak("Login successful!")
            self.enable_buttons()
        else:
            self.message_label.config(text="Invalid PIN! Please try again.")
            self.atm.speak("Invalid PIN! Please try again.")
            messagebox.showerror("Error", "Invalid PIN")

    def enable_buttons(self):
        for button in [self.balance_button, self.deposit_button, self.withdraw_button, self.transfer_button, self.history_button, self.account_details_button, self.change_pin_button]:
            button.config(state="normal")

    def check_balance(self):
        message = f"Balance: ${self.atm.balance}"
        self.message_label.config(text=message)

    def deposit(self):
        amount = self.get_amount("deposit")
        if amount is not None:
            message = self.atm.deposit(amount)
            self.message_label.config(text=message)

    def withdraw(self):
        amount = self.get_amount("withdraw")
        if amount is not None:
            message = self.atm.withdraw(amount)
            self.message_label.config(text=message)

    def transfer(self):
        amount = self.get_amount("transfer")
        if amount is not None:
            to_account = simpledialog.askstring("Input", "Enter the account number to transfer to:")
            if to_account:
                message = self.atm.transfer(amount, to_account)
                self.message_label.config(text=message)

    def view_transaction_history(self):
        message = self.atm.view_transaction_history()
        self.message_label.config(text=message)

    def view_account_details(self):
        message = self.atm.view_account_details()
        self.message_label.config(text=message)

    def change_pin(self):
        old_pin = simpledialog.askstring("Input", "Enter your current PIN:")
        new_pin = simpledialog.askstring("Input", "Enter your new PIN:")
        message = self.atm.change_pin(old_pin, new_pin)
        self.message_label.config(text=message)

    def get_amount(self, action):
        try:
            amount = simpledialog.askfloat("Input", f"Enter the amount to {action}:")
            if amount is None or amount <= 0:
                raise ValueError
            return amount
        except ValueError:
            messagebox.showerror("Error", f"Invalid {action} amount.")
            return None

    def exit_program(self):
        self.root.quit()

root = tk.Tk()
atm = ATM()
atm_gui = ATM_GUI(root, atm)
root.mainloop()
