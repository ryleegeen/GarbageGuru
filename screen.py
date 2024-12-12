import sys
import subprocess
import threading
import csv
import queue
from PIL import Image, ImageTk
import tkinter as tk
import time

scanner_active = False

# Initialize Tkinter app
app = tk.Tk()
app.title("Garbage Gurus Interface")
app.geometry("800x480")

# Store the current language (default to English)
current_language = "EN"

# Language dictionary for text elements
languages = {
    "EN": {"welcome": "Welcome to the Garbage Guru", "food_question": "Does your product have food in it?", "yes": "Yes", "no": "No", "thank_you": "Thank you!", "back": "Back", "scan_barcode": "Please scan your barcode"},
    "PT": {"welcome": "Bem-vindo ao Garbage Gurus", "food_question": "O produto contém alimentos?", "yes": "Sim", "no": "Não", "thank_you": "Obrigado!", "back": "Voltar", "scan_barcode": "Por favor, escaneie o seu código de barras"},
    "HI": {"welcome": "गर्बेज गुरू में आपका स्वागत है", "food_question": "क्या आपके उत्पाद में भोजन है?", "yes": "हां", "no": "नहीं", "thank_you": "धन्यवाद!", "back": "वापस", "scan_barcode": "कृपया अपना बारकोड स्कैन करें"}
}

def deactivate_scanner():
    global scanner_active
    scanner_active = False
    app.unbind("<Key>")
    
# Function to load images
def load_image(image_path, width, height):
    try:
        image = Image.open(image_path)
        image = image.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

# Function to activate landfill motor (example action for "Yes")
def activate_landfill_motor():
    deactivate_scanner()
    try:
        subprocess.run(["python3", "landfill.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while triggering landfill motor: {e}")
    show_thank_you()  # Show thank you message after action is triggered

# Function to trigger servo action based on barcode result
def trigger_servo_action(result):
    print(f"Triggering action for result: {result}")
    if result == "yes":
        print('Result is "yes" - triggering recycle action...')
        subprocess.run(['python3', 'recycle.py'])  # Trigger the recycle action
    elif result == "no":
        print('Result is "no" - triggering landfill action...')
        subprocess.run(['python3', 'landfill.py'])  # Trigger the landfill action
    else:
        print(f"Unexpected result: {result}")
    show_thank_you()  # Show thank you message after action is triggered

# Function to run barcode check and process the result
def process_barcode(barcode):
    print(f"Scanning barcode: {barcode}")

    # Now process the barcode in the same thread
    result = check_barcode_in_db(barcode)  # You would implement check_barcode_in_db to query the database

    if result == 'no':
        result = 'no'  # Could be a default action if barcode not found

    trigger_servo_action(result)  # Trigger servo action based on the barcode result

# Function to check the barcode against the internal database
def check_barcode_in_db(barcode):
    # Check the barcode database and return the result
    with open('barcode_db.csv', 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            if len(row) != 2:
                continue
            stored_barcode, result = row
            if str(barcode) == stored_barcode:
                return result
    return 'no'  # Default to "no" if not found

# Function to handle barcode scanning input
barcode_buffer = ""
def on_barcode_input(event):
    global barcode_buffer
    if not scanner_active:
        return
    if event.keysym == "Return":
        if barcode_buffer:
            process_barcode(barcode_buffer)
            barcode_buffer = ""
    else:
        barcode_buffer += event.char

# Function to scan barcode and trigger background task
def scan_barcode():
    global scanner_active
    clear_screen()
    scanner_active = True
    scanning_message = tk.Label(app, text=languages[current_language].get("scan_barcode", "Please scan your barcode"), font=("Helvetica", 18), fg="#4CAF50", bg="white")
    scanning_message.pack(pady=40)

    # Set up a Tkinter key event to capture the barcode
    app.bind("<Key>", on_barcode_input)  # Bind the key event to the function

# Show the home screen with welcome message and flag options
def show_home_screen():
    clear_screen()

    # Display background logo
    logo_img = load_image("The Garbage Gurus.5 Logo.png", 800, 480)
    if logo_img:
        logo_label = tk.Label(app, image=logo_img)
        logo_label.image = logo_img
        logo_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Display welcome message
    welcome_label = tk.Label(app, text=languages[current_language]["welcome"], font=("Helvetica", 24), fg="#4CAF50", bg="white")
    welcome_label.pack(pady=20)

    # Flag buttons for language selection, centered alignment
    flag_frame = tk.Frame(app, bg="white")
    flag_frame.pack(pady=10)

    flag_us = load_image("us_flag.png", 50, 30)
    flag_br = load_image("brazil_flag.png", 50, 30)
    flag_in = load_image("india_flag.png", 50, 30)

    if flag_us:
        us_button = tk.Button(flag_frame, image=flag_us, command=lambda: set_language("EN"))
        us_button.image = flag_us
        us_button.pack(side="left", padx=10)

    if flag_br:
        br_button = tk.Button(flag_frame, image=flag_br, command=lambda: set_language("PT"))
        br_button.image = flag_br
        br_button.pack(side="left", padx=10)

    if flag_in:
        in_button = tk.Button(flag_frame, image=flag_in, command=lambda: set_language("HI"))
        in_button.image = flag_in
        in_button.pack(side="left", padx=10)

# Set the selected language and go to the next screen
def set_language(lang):
    global current_language
    current_language = lang
    show_food_question()

# Display the "Does your product have food in it?" screen
def show_food_question():
    global scanner_active
    clear_screen()
    app.configure(bg="white")  # Set the background to white

    # Question label
    question_label = tk.Label(app, text=languages[current_language]["food_question"], font=("Helvetica", 18), fg="#4CAF50", bg="white")
    question_label.pack(pady=40)

    # Center frame for "Yes" and "No" buttons
    button_frame = tk.Frame(app, bg="white")
    button_frame.pack(pady=20)

    yes_button = tk.Button(button_frame, text=languages[current_language]["yes"], font=("Helvetica", 16), fg="#4CAF50", command=activate_landfill_motor, width=10)
    yes_button.pack(side="left", padx=10)

    no_button = tk.Button(button_frame, text=languages[current_language]["no"], font=("Helvetica", 16), fg="#4CAF50", command=scan_barcode, width=10)
    no_button.pack(side="left", padx=10)

    # Back button to return to home screen
    back_button = tk.Button(app, text=languages[current_language]["back"], font=("Helvetica", 14), command=show_home_screen)
    back_button.pack(side="bottom", pady=20)

# Display the thank you message after selection
def show_thank_you():
    clear_screen()
    thank_you_label = tk.Label(app, text=languages[current_language]["thank_you"], font=("Helvetica", 24), fg="#4CAF50", bg="white")
    thank_you_label.pack(pady=100)

    # Back button to return to home screen
    back_button = tk.Button(app, text=languages[current_language]["back"], font=("Helvetica", 14), command=show_home_screen)
    back_button.pack(side="bottom", pady=20)
    
    app.after(3000, show_home_screen)

# Utility function to clear the screen
def clear_screen():
    for widget in app.winfo_children():
        widget.destroy()

# Start by showing the home screen
show_home_screen()

# Run the app
app.mainloop()
