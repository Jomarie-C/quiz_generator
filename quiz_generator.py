import tkinter as tk
from tkinter import messagebox
import json
import os
import random

FILENAME = "quiz_generator.txt"

def load_quiz_data():
    if not os.path.exists(FILENAME) or os.stat(FILENAME).st_size == 0:
        return []
    with open(FILENAME, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def save_question_to_file(data):
    with open(FILENAME, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("\U0001F9E0 Quiz Generator Program")
        self.root.geometry("500x500")
        self.root.resizable(False, False)
        self.quiz_data = []

        self.frames = {}
        for F in (MainMenu, CreateQuiz, TakeQuiz, ManageQuiz):
            frame = F(self.root, self)
            self.frames[F] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame(MainMenu)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()

    def refresh_quiz_data(self):
        self.quiz_data = load_quiz_data()

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="\U0001F9E0 QUIZ GENERATOR", font=("Arial", 18)).pack(pady=30)

        tk.Button(self, text="\U0001F4DA Create Quiz", width=20, command=lambda: controller.show_frame(CreateQuiz)).pack(pady=10)
        tk.Button(self, text="\U0001F4DD Take Quiz", width=20, command=self.go_to_quiz).pack(pady=10)
        tk.Button(self, text="❌ Exit", width=20, command=parent.quit).pack(pady=10)

    def go_to_quiz(self):
        self.controller.refresh_quiz_data()
        if not self.controller.quiz_data:
            response = messagebox.askyesno("No Quiz Found", "No quiz available. Do you want to create one?")
            if response:
                self.controller.show_frame(CreateQuiz)
        else:
            self.controller.show_frame(TakeQuiz)

class CreateQuiz(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="⚒️ Create a Quiz Question", font=("Arial", 14)).pack(pady=10)

        self.entry_question = self.create_labeled_entry("Question:")
        self.entry_a = self.create_labeled_entry("Choice A:")
        self.entry_b = self.create_labeled_entry("Choice B:")
        self.entry_c = self.create_labeled_entry("Choice C:")
        self.entry_d = self.create_labeled_entry("Choice D:")

        self.var_correct = tk.StringVar()
        tk.Label(self, text="Correct Answer:", font=('Arial', 12)).pack(pady=5)
        for choice in ['a', 'b', 'c', 'd']:
            tk.Radiobutton(self, text=f"{choice.upper()}", variable=self.var_correct, value=choice).pack(anchor="w", padx=100)

        tk.Button(self, text="✅ Save Question", command=self.save_question, bg="green", fg="white").pack(pady=10)
        tk.Button(self, text="⚒️ Manage Questions", command=lambda: controller.show_frame(ManageQuiz)).pack(pady=2)
        tk.Button(self, text="↩️ Return to Menu", command=lambda: controller.show_frame(MainMenu)).pack(pady=5)

    def create_labeled_entry(self, label_text):
        tk.Label(self, text=label_text).pack()
        entry = tk.Entry(self, width=50)
        entry.pack(pady=2)
        return entry

    def save_question(self):
        question = self.entry_question.get().strip()
        option_a = self.entry_a.get().strip()
        option_b = self.entry_b.get().strip()
        option_c = self.entry_c.get().strip()
        option_d = self.entry_d.get().strip()
        correct = self.var_correct.get()

        if not all([question, option_a, option_b, option_c, option_d, correct]):
            messagebox.showwarning("Missing Info", "Please fill in all fields and select the correct answer.")
            return

        quiz_data = {
            "question": question,
            "choices": {"a": option_a, "b": option_b, "c": option_c, "d": option_d},
            "answer": correct
        }

        save_question_to_file(quiz_data)
        messagebox.showinfo("Saved", "Question added successfully.")

        self.entry_question.delete(0, tk.END)
        self.entry_a.delete(0, tk.END)
        self.entry_b.delete(0, tk.END)
        self.entry_c.delete(0, tk.END)
        self.entry_d.delete(0, tk.END)
        self.var_correct.set(None)

class TakeQuiz(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_question = None

        self.lbl_question = tk.Label(self, text="", font=("Arial", 14), wraplength=450, justify="left")
        self.lbl_question.pack(pady=20)

        self.var_choice = tk.StringVar()
        self.buttons = {}
        for opt in ['a', 'b', 'c', 'd']:
            button = tk.Radiobutton(self, text="", variable=self.var_choice, value=opt, anchor="w", justify="left")
            button.pack(fill='x', padx=50, pady=2)
            self.buttons[opt] = button

        tk.Button(self, text="Submit Answer", command=self.check_answer).pack(pady=10)
        tk.Button(self, text="↩️ Return to Menu", command=self.back_to_menu).pack()

    def load_new_question(self):
        self.controller.refresh_quiz_data()
        if not self.controller.quiz_data:
            messagebox.showinfo("Done", "No more questions.")
            self.back_to_menu()
            return

        self.current_question = random.choice(self.controller.quiz_data)
        self.lbl_question.config(text=self.current_question["question"])
        for key in self.buttons:
            self.buttons[key].config(text=f"{key.upper()}) {self.current_question['choices'][key]}")
        self.var_choice.set(None)

    def check_answer(self):
        selected = self.var_choice.get()
        if not selected:
            messagebox.showwarning("No Answer", "Please select an answer.")
            return
        correct = self.current_question["answer"]
        if selected == correct:
            messagebox.showinfo("Correct!", "\U0001F389 You got it right!")
        else:
            correct_text = self.current_question["choices"][correct]
            messagebox.showerror("Incorrect", f"☹️ Correct answer was: {correct.upper()}) {correct_text}")
        self.load_new_question()

    def back_to_menu(self):
        self.controller.show_frame(MainMenu)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.load_new_question()

class ManageQuiz(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="\U0001F4CB Manage Questions", font=('Arial', 14)).pack(pady=10)

        self.container = tk.Frame(self)
        self.container.pack(fill='both', expand=True)

        self.scrollbar = tk.Scrollbar(self.container)
        self.scrollbar.pack(side='right', fill='y')

        self.listbox = tk.Listbox(self.container, yscrollcommand=self.scrollbar.set, width=80)
        self.listbox.pack(padx=10, pady=10, fill='both', expand=True)
        self.scrollbar.config(command=self.listbox.yview)

        self.btn_edit = tk.Button(self, text="✏️ Edit Selected", command=self.edit_selected)
        self.btn_delete = tk.Button(self, text="\U0001F5D1️ Delete Selected", command=self.delete_selected)
        self.btn_back = tk.Button(self, text="↩️ Back to Create", command=lambda: controller.show_frame(CreateQuiz))

        self.btn_edit.pack(pady=5)
        self.btn_delete.pack(pady=5)
        self.btn_back.pack(pady=10)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        self.data = load_quiz_data()
        for idx, item in enumerate(self.data):
            qtext = item['question']
            self.listbox.insert(tk.END, f"{idx+1}. {qtext}")

    def edit_selected(self):
        try:
            idx = self.listbox.curselection()[0]
            question = self.data[idx]
        except IndexError:
            messagebox.showwarning("No Selection", "Please select a question to edit.")
            return

        frame = self.controller.frames[CreateQuiz]
        frame.entry_question.delete(0, tk.END)
        frame.entry_question.insert(0, question['question'])

        frame.entry_a.delete(0, tk.END)
        frame.entry_a.insert(0, question['choices']['a'])

        frame.entry_b.delete(0, tk.END)
        frame.entry_b.insert(0, question['choices']['b'])

        frame.entry_c.delete(0, tk.END)
        frame.entry_c.insert(0, question['choices']['c'])

        frame.entry_d.delete(0, tk.END)
        frame.entry_d.insert(0, question['choices']['d'])

        frame.var_correct.set(question['answer'])

        self.data.pop(idx)
        with open(FILENAME, 'w', encoding='utf-8') as f:
            for item in self.data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        self.controller.show_frame(CreateQuiz)

    def delete_selected(self):
        try:
            idx = self.listbox.curselection()[0]
        except IndexError:
            messagebox.showwarning("No Selection", "Please select a question to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this question?")
        if confirm:
            self.data.pop(idx)
            with open(FILENAME, 'w', encoding='utf-8') as f:
                for item in self.data:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
            self.refresh_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
