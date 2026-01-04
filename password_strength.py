import math
import re
import tkinter as tk
from tkinter import messagebox, ttk

# small sample blacklist (you can expand this file or load from a list)
COMMON_PASSWORDS = {
    "123456", "password", "123456789", "12345678", "qwerty", "abc123",
    "111111", "1234567", "iloveyou", "admin", "welcome", "letmein"
}

def char_pool_size(password: str) -> int:
    """Estimate pool size based on character classes used."""
    pool = 0
    if re.search(r"[a-z]", password):
        pool += 26
    if re.search(r"[A-Z]", password):
        pool += 26
    if re.search(r"[0-9]", password):
        pool += 10
    # Approx count of special characters
    if re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\\[\];']", password):
        pool += 32
    return pool if pool > 0 else 1

def estimate_entropy(password: str) -> float:
    """Estimate Shannon entropy."""
    pool = char_pool_size(password)
    return len(password) * math.log2(pool)

def has_repeated_sequence(password: str) -> bool:
    """Detect repeated substrings or long runs of the same character."""
    if re.search(r"(.)\1\1", password):  # aaa
        return True
    for size in range(2, min(6, len(password)//2 + 1)):
        for i in range(len(password) - 2 * size + 1):
            if password[i:i+size] == password[i+size:i+2*size]:
                return True
    return False

def score_and_feedback(password: str):
    lower_pw = password.lower().strip()

    if lower_pw in COMMON_PASSWORDS:
        return {
            "score": 5,
            "label": "Very Weak",
            "entropy": estimate_entropy(password),
            "suggestions": ["This password is commonly used — don't use it."]
        }

    entropy = estimate_entropy(password)
    suggestions = []

    if entropy < 28:
        label = "Very Weak"
        score = 10
        suggestions.append("Make it longer (>= 12 chars).")
    elif entropy < 36:
        label = "Weak"
        score = 30
        suggestions.append("Add more character types.")
    elif entropy < 60:
        label = "Fair"
        score = 55
        suggestions.append("Use more symbols or numbers.")
    elif entropy < 128:
        label = "Strong"
        score = 80
    else:
        label = "Very Strong"
        score = 95

    if has_repeated_sequence(password):
        score -= 20
        suggestions.append("Avoid repeated sequences like 'aaaa' or 'abcabc'.")

    if password.isdigit() or password.isalpha():
        score -= 10
        suggestions.append("Mix letters, digits, and symbols.")

    if len(password) >= 20:
        suggestions.append("Nice — long passphrase is good!")

    suggestions = list(dict.fromkeys(suggestions))
    score = max(0, min(100, score))

    return {
        "score": score,
        "label": label,
        "entropy": round(entropy, 2),
        "suggestions": suggestions
    }


# ==========================
#   TKINTER GUI STARTS HERE
# ==========================

def check_password():
    pw = entry.get().strip()

    if pw == "":
        messagebox.showwarning("Input Error", "Please enter a password.")
        return

    result = score_and_feedback(pw)

    # update labels
    label_score_value.config(text=str(result["score"]))
    label_entropy_value.config(text=str(result["entropy"]))
    label_strength_value.config(text=result["label"])

    # update suggestions listbox
    suggestion_list.delete(0, tk.END)
    for s in result["suggestions"]:
        suggestion_list.insert(tk.END, f"- {s}")


# create main window
root = tk.Tk()
root.title("Password Strength Checker")
root.geometry("500x400")
root.resizable(False, False)

# Title
title_label = tk.Label(root, text="Password Strength Checker", font=("Arial", 18, "bold"))
title_label.pack(pady=10)

# Password entry
frame_input = tk.Frame(root)
frame_input.pack(pady=10)

entry_label = tk.Label(frame_input, text="Enter Password:", font=("Arial", 12))
entry_label.grid(row=0, column=0, padx=5)

entry = tk.Entry(frame_input, width=30, show="*")
entry.grid(row=0, column=1, padx=5)

btn_check = tk.Button(root, text="Check Password", font=("Arial", 12), command=check_password)
btn_check.pack(pady=10)

# Result display
frame_results = tk.Frame(root)
frame_results.pack(pady=10)

label_strength = tk.Label(frame_results, text="Strength:", font=("Arial", 12, "bold"))
label_strength.grid(row=0, column=0, sticky="w")
label_strength_value = tk.Label(frame_results, text="—", font=("Arial", 12))
label_strength_value.grid(row=0, column=1, sticky="w")

label_entropy = tk.Label(frame_results, text="Entropy:", font=("Arial", 12, "bold"))
label_entropy.grid(row=1, column=0, sticky="w")
label_entropy_value = tk.Label(frame_results, text="—", font=("Arial", 12))
label_entropy_value.grid(row=1, column=1, sticky="w")

label_score = tk.Label(frame_results, text="Score (0–100):", font=("Arial", 12, "bold"))
label_score.grid(row=2, column=0, sticky="w")
label_score_value = tk.Label(frame_results, text="—", font=("Arial", 12))
label_score_value.grid(row=2, column=1, sticky="w")

# Suggestions box
suggestion_label = tk.Label(root, text="Suggestions:", font=("Arial", 12, "bold"))
suggestion_label.pack()

suggestion_list = tk.Listbox(root, width=60, height=6)
suggestion_list.pack(pady=5)

# Start GUI
root.mainloop()
