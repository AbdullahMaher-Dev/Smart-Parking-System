import json
import tkinter as tk
from tkinter import messagebox, simpledialog
import os

# ------------------ FILE PATH ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "parking_data.json")

# ------------------ FILE HANDLING ------------------
def sync_spots_with_users(data):
    used_spots = {user["spot"] for user in data["users"]}
    for spot in data["spots"]:
        spot["occupied"] = spot["number"] in used_spots

def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            sync_spots_with_users(data)
            return data
    except FileNotFoundError:
        return {"users": [], "spots": []}

def save_data(data):
    sync_spots_with_users(data)
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# ------------------ USER FUNCTIONS ------------------
def add_user(data, name, plate):
    name = name.strip()
    plate = plate.strip()

    if not name or not plate:
        return "Name and plate cannot be empty."

    for user in data["users"]:
        if user["plate"] == plate:
            return "Car already parked."

    used_spots = {user["spot"] for user in data["users"]}

    for spot in data["spots"]:
        if not spot["occupied"] and spot["number"] not in used_spots:
            data["users"].append({
                "name": name,
                "plate": plate,
                "spot": spot["number"]
            })
            sync_spots_with_users(data)
            return f"Car parked at spot {spot['number']}"

    return "No available spots."

def edit_user(data, plate):
    for user in data["users"]:
        if user["plate"] == plate:
            new_name = simpledialog.askstring("Edit Name", "Enter new name:")
            new_plate = simpledialog.askstring("Edit Plate", "Enter new plate:")

            if new_plate:
                for u in data["users"]:
                    if u["plate"] == new_plate and u != user:
                        return "Plate already exists."

            if new_name:
                user["name"] = new_name.strip()
            if new_plate:
                user["plate"] = new_plate.strip()

            return "Car updated."
    return "Car not found."

def delete_user(data, plate):
    for user in data["users"]:
        if user["plate"] == plate:
            data["users"].remove(user)
            sync_spots_with_users(data)
            return "Car removed."
    return "Car not found."

def view_users(data):
    if not data["users"]:
        return "No parked cars."
    return "\n".join(
        f"{u['name']} - {u['plate']} - Spot: {u['spot']}"
        for u in data["users"]
    )

def search_users(data, query):
    result = [
        f"{u['name']} - {u['plate']} - Spot: {u['spot']}"
        for u in data["users"]
        if query.lower() in u["name"].lower()
        or query.lower() in u["plate"].lower()
    ]
    return "\n".join(result) if result else "No matching results."

# ------------------ SPOT FUNCTIONS ------------------
def add_spot(data, spot_number):
    spot_number = spot_number.strip()

    for spot in data["spots"]:
        if spot["number"] == spot_number:
            return "Spot already exists."

    data["spots"].append({"number": spot_number, "occupied": False})
    return "Spot added."

def delete_spot(data, spot_number):
    for spot in data["spots"]:
        if spot["number"] == spot_number:
            if spot["occupied"]:
                return "Spot is occupied."
            data["spots"].remove(spot)
            return "Spot deleted."
    return "Spot not found."

def edit_spot(data, spot_number):
    for spot in data["spots"]:
        if spot["number"] == spot_number:
            new_number = simpledialog.askstring("Edit Spot", "Enter new spot number:")
            if not new_number:
                return "Invalid number."

            for s in data["spots"]:
                if s["number"] == new_number:
                    return "Spot already exists."

            for user in data["users"]:
                if user["spot"] == spot_number:
                    user["spot"] = new_number

            spot["number"] = new_number
            return "Spot updated."
    return "Spot not found."

def view_spots(data, is_admin):
    if not data["spots"]:
        return "No spots added."

    lines = []
    for spot in data["spots"]:
        status = "Occupied" if spot["occupied"] else "Available"
        line = f"Spot {spot['number']}: {status}"

        if is_admin and spot["occupied"]:
            for user in data["users"]:
                if user["spot"] == spot["number"]:
                    line += f" by {user['name']} ({user['plate']})"

        lines.append(line)

    return "\n".join(lines)

# ------------------ GUI ------------------
def start_gui(is_admin):
    data = load_data()

    def reload_data():
        data.clear()
        data.update(load_data())

    def handle_add():
        msg = add_user(data, entry_name.get(), entry_plate.get())
        save_data(data)
        messagebox.showinfo("Add Car", msg)

    def handle_edit():
        reload_data()
        plate = simpledialog.askstring("Edit Car", "Enter plate:")
        if plate:
            msg = edit_user(data, plate)
            save_data(data)
            messagebox.showinfo("Edit Car", msg)

    def handle_delete():
        reload_data()
        plate = simpledialog.askstring("Delete Car", "Enter plate:")
        if plate:
            msg = delete_user(data, plate)
            save_data(data)
            messagebox.showinfo("Delete Car", msg)

    def handle_view():
        reload_data()
        messagebox.showinfo("View Cars", view_users(data))

    def handle_search():
        reload_data()
        q = simpledialog.askstring("Search", "Enter name or plate:")
        if q:
            messagebox.showinfo("Search", search_users(data, q))

    def handle_view_spots():
        reload_data()
        messagebox.showinfo("View Spots", view_spots(data, is_admin))

    def handle_spots():
        if not is_admin:
            messagebox.showinfo("Denied", "Admin only.")
            return

        reload_data()
        action = simpledialog.askstring("Manage Spots", "Add, Delete or Edit?")
        number = simpledialog.askstring("Spot Number", "Enter spot number:")
        if not action or not number:
            return

        action = action.lower()
        if action == "add":
            msg = add_spot(data, number)
        elif action == "delete":
            msg = delete_spot(data, number)
        elif action == "edit":
            msg = edit_spot(data, number)
        else:
            msg = "Invalid action."

        save_data(data)
        messagebox.showinfo("Spots", msg)

    def handle_exit():
        save_data(data)
        root.destroy()

    root = tk.Tk()
    root.title("Parking System")
    root.geometry("400x420")

    tk.Label(root, text="Owner Name:").pack()
    entry_name = tk.Entry(root)
    entry_name.pack()

    tk.Label(root, text="Plate Number:").pack()
    entry_plate = tk.Entry(root)
    entry_plate.pack()

    for text, cmd in [
        ("Add Car", handle_add),
        ("Edit Car", handle_edit),
        ("Delete Car", handle_delete),
        ("View Cars", handle_view),
        ("Search Cars", handle_search),
        ("View Spots", handle_view_spots),
        ("Manage Spots", handle_spots),
        ("Save & Exit", handle_exit),
    ]:
        tk.Button(root, text=text, command=cmd).pack(pady=2)

    root.mainloop()

# ------------------ LOGIN ------------------
def login_gui():
    win = tk.Tk()
    win.title("Login")
    win.geometry("300x200")

    tk.Label(win, text="Username:").pack()
    u = tk.Entry(win)
    u.pack()

    tk.Label(win, text="Password:").pack()
    p = tk.Entry(win, show="*")
    p.pack()

    def login():
        if u.get() == "admin" and p.get() == "1234":
            win.destroy()
            start_gui(True)
        elif u.get() == "user" and p.get() == "0000":
            win.destroy()
            start_gui(False)
        else:
            messagebox.showerror("Error", "Invalid credentials")

    tk.Button(win, text="Login", command=login).pack(pady=20)
    win.mainloop()

# ------------------ MAIN ------------------
login_gui()
