import tkinter as tk
from tkinter import messagebox
import json
import os

FILENAME = "quiz_generator.txt"

def load_quiz_data():
    if not os.path.exists(FILENAME) or os.stat(FILENAME).st_size == 0:
        return []
    with open(FILENAME, 'r', encoding='utf-8') as file_handle:
        return [json.loads(line) for line in file_handle if line.strip()]

def save_question_to_file(question_data):
    with open(FILENAME, 'a', encoding='utf-8') as file_handle:
        file_handle.write(json.dumps(question_data, ensure_ascii=False) + "\n")

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("\U0001F9E0 Quiz Generator Program")
        self.root.geometry("500x500")
        self.root.resizable(False, False)
        self.quiz_data = []

        self.frames = {}
        for FrameClass in (MainMenu, CreateQuiz, ManageQuiz):
            frame_instance = FrameClass(self.root, self)
            self.frames[FrameClass] = frame_instance
            frame_instance.place(relwidth=1, relheight=1)

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
        tk.Button(self, text="⚒️ Manage Questions", width=20, command=lambda: controller.show_frame(ManageQuiz)).pack(pady=10)
        tk.Button(self, text="❌ Exit", width=20, command=self.controller.root.destroy).pack(pady=10)

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
        question_text = self.entry_question.get().strip()
        choice_a = self.entry_a.get().strip()
        choice_b = self.entry_b.get().strip()
        choice_c = self.entry_c.get().strip()
        choice_d = self.entry_d.get().strip()
        correct_answer = self.var_correct.get()

        if not all([question_text, choice_a, choice_b, choice_c, choice_d, correct_answer]):
            messagebox.showwarning("Missing Info", "Please fill in all fields and select the correct answer.")
            return

        question_data = {
            "question": question_text,
            "choices": {"a": choice_a, "b": choice_b, "c": choice_c, "d": choice_d},
            "answer": correct_answer
        }

        save_question_to_file(question_data)
        messagebox.showinfo("Saved", "Question added successfully.")
        self.clear_fields()

    def clear_fields(self):
        self.entry_question.delete(0, tk.END)
        self.entry_a.delete(0, tk.END)
        self.entry_b.delete(0, tk.END)
        self.entry_c.delete(0, tk.END)
        self.entry_d.delete(0, tk.END)
        self.var_correct.set(None)

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

        tk.Button(self, text="✏️ Edit Selected", command=self.edit_selected).pack(pady=5)
        tk.Button(self, text="\U0001F5D1️ Delete Selected", command=self.delete_selected).pack(pady=5)
        tk.Button(self, text="↩️ Back to Create", command=lambda: controller.show_frame(CreateQuiz)).pack(pady=10)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        self.data = load_quiz_data()
        for index, question_item in enumerate(self.data):
            question_text = question_item['question']
            self.listbox.insert(tk.END, f"{index+1}. {question_text}")

    def edit_selected(self):
        try:
            selected_index = self.listbox.curselection()[0]
            selected_question = self.data.pop(selected_index)
        except IndexError:
            messagebox.showwarning("No Selection", "Please select a question to edit.")
            return

        create_quiz_frame = self.controller.frames[CreateQuiz]
        create_quiz_frame.entry_question.delete(0, tk.END)
        create_quiz_frame.entry_question.insert(0, selected_question['question'])

        create_quiz_frame.entry_a.delete(0, tk.END)
        create_quiz_frame.entry_a.insert(0, selected_question['choices']['a'])

        create_quiz_frame.entry_b.delete(0, tk.END)
        create_quiz_frame.entry_b.insert(0, selected_question['choices']['b'])

        create_quiz_frame.entry_c.delete(0, tk.END)
        create_quiz_frame.entry_c.insert(0, selected_question['choices']['c'])

        create_quiz_frame.entry_d.delete(0, tk.END)
        create_quiz_frame.entry_d.insert(0, selected_question['choices']['d'])

        create_quiz_frame.var_correct.set(selected_question['answer'])

        with open(FILENAME, 'w', encoding='utf-8') as file_handle:
            for question_item in self.data:
                file_handle.write(json.dumps(question_item, ensure_ascii=False) + "\n")

        self.controller.show_frame(CreateQuiz)

    def delete_selected(self):
        try:
            selected_index = self.listbox.curselection()[0]
        except IndexError:
            messagebox.showwarning("No Selection", "Please select a question to delete.")
            return

        confirm_delete = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this question?")
        if confirm_delete:
            self.data.pop(selected_index)
            with open(FILENAME, 'w', encoding='utf-8') as file_handle:
                for question_item in self.data:
                    file_handle.write(json.dumps(question_item, ensure_ascii=False) + "\n")
            self.refresh_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()