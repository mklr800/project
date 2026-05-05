import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Загрузка избранных пользователей
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Метка и поле поиска
        ttk.Label(main_frame, text="Поиск пользователя GitHub:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(main_frame, textvariable=self.search_var, width=40, font=("Arial", 11))
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Кнопка поиска
        self.search_btn = ttk.Button(main_frame, text="🔍 Поиск", command=self.search_user, style="Accent.TButton")
        self.search_btn.grid(row=0, column=2, pady=5, padx=5)
        
        # Кнопка "Показать избранных"
        self.favorites_btn = ttk.Button(main_frame, text="⭐ Избранные", command=self.show_favorites)
        self.favorites_btn.grid(row=0, column=3, pady=5, padx=5)
        
        # Разделитель
        ttk.Separator(main_frame, orient='horizontal').grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        # Фрейм для результатов
        results_frame = ttk.LabelFrame(main_frame, text="Результаты поиска", padding="10")
        results_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Список результатов с прокруткой
        list_frame = ttk.Frame(results_frame)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.results_listbox = tk.Listbox(
            list_frame, 
            height=15, 
            font=("Arial", 10),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        self.results_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.results_listbox.yview)
        
        # Привязка события выбора элемента
        self.results_listbox.bind('<<ListboxSelect>>', self.on_select)
        
        # Фрейм для деталей пользователя
        details_frame = ttk.LabelFrame(main_frame, text="Детали пользователя", padding="10")
        details_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        details_frame.columnconfigure(1, weight=1)
        
        # Метки для отображения информации
        self.details_text = tk.Text(details_frame, height=8, font=("Arial", 10), wrap=tk.WORD)
        self.details_text.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Кнопка добавления в избранное
        self.fav_btn = ttk.Button(details_frame, text="❤️ Добавить в избранное", command=self.add_to_favorites)
        self.fav_btn.grid(row=1, column=0, pady=10)
        
        # Кнопка удаления из избранного
        self.remove_fav_btn = ttk.Button(details_frame, text="🗑️ Удалить из избранного", command=self.remove_from_favorites)
        self.remove_fav_btn.grid(row=1, column=1, pady=10)
        
        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # Хранение текущих данных пользователя
        self.current_user = None
        
        # Стили
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="#0078D4")
        
    def load_favorites(self):
        """Загрузка избранных пользователей из JSON файла"""
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def save_favorites(self):
        """Сохранение избранных пользователей в JSON файл"""
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)
    
    def search_user(self):
        """Поиск пользователя на GitHub"""
        username = self.search_var.get().strip()
        
        # Проверка на пустое поле ввода
        if not username:
            messagebox.showwarning("Предупреждение", "Поле поиска не может быть пустым!")
            self.status_var.set("Ошибка: поле поиска пустое")
            return
        
        self.status_var.set(f"Поиск пользователя {username}...")
        self.search_btn.config(state=tk.DISABLED)
        
        try:
            # Запрос к GitHub API
            response = requests.get(f"https://api.github.com/users/{username}", timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                self.display_user_info(user_data)
                self.status_var.set(f"Найден пользователь: {user_data.get('login')}")
            elif response.status_code == 404:
                messagebox.showerror("Ошибка", f"Пользователь '{username}' не найден!")
                self.status_var.set("Пользователь не найден")
                self.clear_details()
            else:
                messagebox.showerror("Ошибка", f"Ошибка API: {response.status_code}")
                self.status_var.set("Ошибка при запросе к API")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка соединения: {str(e)}")
            self.status_var.set("Ошибка соединения")
        finally:
            self.search_btn.config(state=tk.NORMAL)
    
    def display_user_info(self, user_data):
        """Отображение информации о пользователе"""
        self.current_user = user_data
        
        # Очистка текста
        self.details_text.delete(1.0, tk.END)
        
        # Формирование информации
        info = f"Логин: {user_data.get('login', 'N/A')}\n"
        info += f"Имя: {user_data.get('name', 'Не указано')}\n"
        info += f"Компания: {user_data.get('company', 'Не указана')}\n"
        info += f"Блог: {user_data.get('blog', 'Не указан')}\n"
        info += f"Локация: {user_data.get('location', 'Не указана')}\n"
        info += f"Email: {user_data.get('email', 'Не указан')}\n"
        info += f"Биография: {user_data.get('bio', 'Не указана')}\n"
        info += f"Публичные репозитории: {user_data.get('public_repos', 0)}\n"
        info += f"Подписчики: {user_data.get('followers', 0)}\n"
        info += f"Подписки: {user_data.get('following', 0)}\n"
        info += f"Аккаунт создан: {user_data.get('created_at', 'N/A')[:10]}\n"
        info += f"Профиль: {user_data.get('html_url', 'N/A')}"
        
        self.details_text.insert(1.0, info)
        
        # Добавление в список результатов
        self.add_to_search_history(user_data.get('login'))
        
        # Подсветка кнопки избранного
        if self.is_favorite(user_data.get('login')):
            self.fav_btn.config(state=tk.DISABLED, text="✓ В избранном")
        else:
            self.fav_btn.config(state=tk.NORMAL, text="❤️ Добавить в избранное")
    
    def add_to_search_history(self, username):
        """Добавление пользователя в историю поиска"""
        items = list(self.results_listbox.get(0, tk.END))
        if username not in items:
            self.results_listbox.insert(0, username)
            if self.results_listbox.size() > 20:
                self.results_listbox.delete(tk.END)
    
    def on_select(self, event):
        """Обработка выбора пользователя из списка"""
        selection = self.results_listbox.curselection()
        if selection:
            username = self.results_listbox.get(selection[0])
            self.search_var.set(username)
            self.search_user()
    
    def add_to_favorites(self):
        """Добавление текущего пользователя в избранное"""
        if not self.current_user:
            messagebox.showwarning("Предупреждение", "Нет выбранного пользователя!")
            return
        
        username = self.current_user.get('login')
        
        if self.is_favorite(username):
            messagebox.showinfo("Информация", "Пользователь уже в избранном!")
            return
        
        # Сохраняем информацию о пользователе в избранное
        favorite_data = {
            'login': username,
            'name': self.current_user.get('name', ''),
            'avatar_url': self.current_user.get('avatar_url', ''),
            'html_url': self.current_user.get('html_url', ''),
            'added_at': datetime.now().isoformat()
        }
        
        self.favorites.append(favorite_data)
        self.save_favorites()
        
        self.fav_btn.config(state=tk.DISABLED, text="✓ В избранном")
        self.status_var.set(f"Пользователь {username} добавлен в избранное")
        messagebox.showinfo("Успех", f"Пользователь {username} добавлен в избранное!")
    
    def remove_from_favorites(self):
        """Удаление текущего пользователя из избранного"""
        if not self.current_user:
            messagebox.showwarning("Предупреждение", "Нет выбранного пользователя!")
            return
        
        username = self.current_user.get('login')
        
        if not self.is_favorite(username):
            messagebox.showinfo("Информация", "Пользователь не в избранном!")
            return
        
        self.favorites = [f for f in self.favorites if f.get('login') != username]
        self.save_favorites()
        
        self.fav_btn.config(state=tk.NORMAL, text="❤️ Добавить в избранное")
        self.status_var.set(f"Пользователь {username} удалён из избранного")
        messagebox.showinfo("Успех", f"Пользователь {username} удалён из избранного!")
    
    def is_favorite(self, username):
        """Проверка, находится ли пользователь в избранном"""
        return any(f.get('login') == username for f in self.favorites)
    
    def show_favorites(self):
        """Отображение окна с избранными пользователями"""
        favorites_window = tk.Toplevel(self.root)
        favorites_window.title("Избранные пользователи GitHub")
        favorites_window.geometry("600x400")
        
        main_frame = ttk.Frame(favorites_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        if not self.favorites:
            ttk.Label(main_frame, text="Список избранных пуст", font=("Arial", 12)).pack(pady=50)
        else:
            # Создание списка
            scrollbar = ttk.Scrollbar(main_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            listbox = tk.Listbox(main_frame, font=("Arial", 10), yscrollcommand=scrollbar.set)
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=listbox.yview)
            
            for fav in self.favorites:
                display_text = f"{fav.get('login')}"
                if fav.get('name'):
                    display_text += f" - {fav.get('name')}"
                display_text += f" (добавлен: {fav.get('added_at', '')[:10]})"
                listbox.insert(tk.END, display_text)
            
            # Функция для открытия профиля
            def open_profile():
                selection = listbox.curselection()
                if selection:
                    fav = self.favorites[selection[0]]
                    self.search_var.set(fav.get('login'))
                    self.search_user()
                    favorites_window.destroy()
            
            open_btn = ttk.Button(main_frame, text="Открыть профиль", command=open_profile)
            open_btn.pack(pady=10)
    
    def clear_details(self):
        """Очистка деталей пользователя"""
        self.details_text.delete(1.0, tk.END)
        self.current_user = None
        self.fav_btn.config(state=tk.NORMAL, text="❤️ Добавить в избранное")

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
