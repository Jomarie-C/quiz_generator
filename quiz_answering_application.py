import tkinter as tk
from tkinter import messagebox
import json
import random
import os

QUIZ_FILENAME = "quiz_generator.txt"

def load_quiz_questions():
    if not os.path.exists(QUIZ_FILENAME) or os.stat(QUIZ_FILENAME).st_size == 0:
        return []
    with open(QUIZ_FILENAME, 'r', encoding='utf-8') as file:
        return [json.loads(line) for line in file if line.strip()]

class QuizAnsweringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 Take a Quiz")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        self.all_questions = load_quiz_questions()
        self.current_question = None

        self.label_question = tk.Label(root, text="", font=("Arial", 14), wraplength=450, justify="left")
        self.label_question.pack(pady=20)

        self.selected_choice = tk.StringVar()
        self.choice_buttons = {}
        for option_key in ['a', 'b', 'c', 'd']:
            radio_button = tk.Radiobutton(
                root, text="", variable=self.selected_choice, value=option_key,
                font=("Arial", 12), anchor="w", justify="left"
            )
            radio_button.pack(fill='x', padx=50, pady=2)
            self.choice_buttons[option_key] = radio_button

        self.submit_button = tk.Button(root, text="Submit Answer", command=self.check_user_answer)
        self.submit_button.pack(pady=10)

        self.quit_button = tk.Button(root, text="❌ Exit Quiz", command=root.quit)
        self.quit_button.pack()

        self.load_random_question()

    def load_random_question(self):
        if not self.all_questions:
            messagebox.showinfo("Done", "No more questions available.")
            self.root.quit()
            return

        self.current_question = random.choice(self.all_questions)
        self.label_question.config(text=self.current_question["question"])
        for option_key, text in self.current_question["choices"].items():
            self.choice_buttons[option_key].config(text=f"{option_key.upper()}) {text}")
        self.selected_choice.set(None)

    def check_user_answer(self):
        user_selection = self.selected_choice.get()
        if not user_selection:
            messagebox.showwarning("No Answer", "Please select an answer before submitting.")
            return

        correct_answer_key = self.current_question["answer"]
        if user_selection == correct_answer_key:
            messagebox.showinfo("Correct!", "🎉 That's the correct answer!")
        else:
            correct_answer_text = self.current_question["choices"][correct_answer_key]
            messagebox.showerror("Incorrect", f"❌ The correct answer was: {correct_answer_key.upper()}) {correct_answer_text}")

        self.all_questions.remove(self.current_question)
        self.load_random_question()

if __name__ == "__main__":
    root_window = tk.Tk()
    quiz_app = QuizAnsweringApp(root_window)
    root_window.mainloop()