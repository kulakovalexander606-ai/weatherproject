import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "weather_data.json"

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("750x550")

        self.records = []
        self.load_from_file()

        # Поля ввода
        tk.Label(root, text="Дата (ГГГГ-ММ-ДД):").pack(pady=2)
        self.date_entry = tk.Entry(root, width=30)
        self.date_entry.pack()

        tk.Label(root, text="Температура (°C):").pack(pady=2)
        self.temp_entry = tk.Entry(root, width=30)
        self.temp_entry.pack()

        tk.Label(root, text="Описание погоды:").pack(pady=2)
        self.desc_entry = tk.Entry(root, width=50)
        self.desc_entry.pack()

        self.rain_var = tk.BooleanVar()
        self.rain_check = tk.Checkbutton(root, text="Осадки", variable=self.rain_var)
        self.rain_check.pack(pady=5)

        # Кнопки
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Добавить запись", command=self.add_record).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Сохранить в JSON", command=self.save_to_file).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Загрузить из JSON", command=self.load_from_file).pack(side=tk.LEFT, padx=5)

        # Фильтры
        filter_frame = tk.LabelFrame(root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=2)
        self.filter_date_entry = tk.Entry(filter_frame, width=20)
        self.filter_date_entry.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Температура выше (°C):").grid(row=0, column=2, padx=5, pady=2)
        self.filter_temp_entry = tk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5)

        tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=4, padx=10)
        tk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter).grid(row=0, column=5, padx=5)

        # Таблица для записей
        columns = ("date", "temperature", "description", "rain")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура")
        self.tree.heading("description", text="Описание")
        self.tree.heading("rain", text="Осадки")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.refresh_table()

    def is_valid_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_record(self):
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        rain = self.rain_var.get()

        # Валидация
        if not date or not temp or not desc:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
            return
        if not self.is_valid_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        try:
            temp_val = float(temp)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return

        record = {
            "date": date,
            "temperature": temp_val,
            "description": desc,
            "rain": "Да" if rain else "Нет"
        }
        self.records.append(record)
        self.refresh_table()
        # Очистка полей
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.rain_var.set(False)

    def refresh_table(self, records_to_show=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        data = records_to_show if records_to_show is not None else self.records
        for rec in data:
            self.tree.insert("", tk.END, values=(rec["date"], rec["temperature"], rec["description"], rec["rain"]))

    def apply_filter(self):
        filter_date = self.filter_date_entry.get().strip()
        filter_temp = self.filter_temp_entry.get().strip()

        filtered = self.records[:]
        if filter_date:
            filtered = [r for r in filtered if r["date"] == filter_date]
        if filter_temp:
            try:
                temp_threshold = float(filter_temp)
                filtered = [r for r in filtered if r["temperature"] > temp_threshold]
            except ValueError:
                messagebox.showerror("Ошибка", "Фильтр температуры должен быть числом")
                return
        self.refresh_table(filtered)

    def reset_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.refresh_table()

    def save_to_file(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_from_file(self):
        if not os.path.exists(DATA_FILE):
            messagebox.showwarning("Предупреждение", "Файл с данными не найден")
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.records = json.load(f)
            self.reset_filter()
            messagebox.showinfo("Успех", "Данные загружены из файла")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()