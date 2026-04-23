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
        
        # Файл для избранного
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()
        
        # Создание GUI
        self.create_widgets()
        
        # Привязка событий
        self.search_entry.bind("<Return>", lambda event: self.search_users())
        
    def create_widgets(self):
        # Верхняя панель поиска
        search_frame = ttk.Frame(self.root, padding="10")
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="Введите имя пользователя GitHub:").pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_button = ttk.Button(search_frame, text="🔍 Поиск", command=self.search_users)
        self.search_button.pack(side=tk.LEFT)
        
        # Панель с вкладками
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка результатов поиска
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="📋 Результаты поиска")
        
        # Таблица результатов
        columns = ("Аватар", "Логин", "ID", "Тип", "Действия")
        self.results_tree = ttk.Treeview(self.results_frame, columns=columns, show="headings", height=15)
        
        self.results_tree.heading("Аватар", text="Аватар")
        self.results_tree.heading("Логин", text="Логин")
        self.results_tree.heading("ID", text="ID")
        self.results_tree.heading("Тип", text="Тип")
        self.results_tree.heading("Действия", text="Действия")
        
        self.results_tree.column("Аватар", width=60)
        self.results_tree.column("Логин", width=150)
        self.results_tree.column("ID", width=80)
        self.results_tree.column("Тип", width=100)
        self.results_tree.column("Действия", width=100)
        
        scrollbar = ttk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Вкладка избранного
        self.favorites_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.favorites_frame, text="⭐ Избранное")
        
        # Таблица избранного
        fav_columns = ("Аватар", "Логин", "ID", "Тип", "Действия")
        self.fav_tree = ttk.Treeview(self.favorites_frame, columns=fav_columns, show="headings", height=15)
        
        self.fav_tree.heading("Аватар", text="Аватар")
        self.fav_tree.heading("Логин", text="Логин")
        self.fav_tree.heading("ID", text="ID")
        self.fav_tree.heading("Тип", text="Тип")
        self.fav_tree.heading("Действия", text="Действия")
        
        self.fav_tree.column("Аватар", width=60)
        self.fav_tree.column("Логин", width=150)
        self.fav_tree.column("ID", width=80)
        self.fav_tree.column("Тип", width=100)
        self.fav_tree.column("Действия", width=100)
        
        fav_scrollbar = ttk.Scrollbar(self.favorites_frame, orient=tk.VERTICAL, command=self.fav_tree.yview)
        self.fav_tree.configure(yscrollcommand=fav_scrollbar.set)
        
        self.fav_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        fav_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Загрузка избранного при запуске
        self.refresh_favorites()
    
    def load_favorites(self):
        """Загрузка избранных пользователей из JSON файла"""
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_favorites(self):
        """Сохранение избранных пользователей в JSON файл"""
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)
    
    def search_users(self):
        """Поиск пользователей через GitHub API"""
        username = self.search_entry.get().strip()
        
        # Проверка на пустое поле
        if not username:
            messagebox.showwarning("Предупреждение", "Поле поиска не может быть пустым!")
            return
        
        self.status_var.set(f"Поиск пользователей по запросу: {username}...")
        self.search_button.config(state=tk.DISABLED)
        
        try:
            # GitHub API поиск пользователей
            url = f"https://api.github.com/search/users?q={username}&per_page=30"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('items', [])
                
                # Очистка таблицы результатов
                for item in self.results_tree.get_children():
                    self.results_tree.delete(item)
                
                if not users:
                    self.status_var.set("Пользователи не найдены")
                    messagebox.showinfo("Информация", "Пользователи не найдены")
                else:
                    for user in users:
                        # Проверка, в избранном ли пользователь
                        is_fav = any(fav['login'] == user['login'] for fav in self.favorites)
                        fav_text = "★ Удалить" if is_fav else "☆ Добавить"
                        
                        self.results_tree.insert("", tk.END, values=(
                            "🖼️",  # Placeholder для аватара
                            user['login'],
                            user['id'],
                            user['type'],
                            fav_text
                        ), tags=(user['login'],))
                    
                    self.status_var.set(f"Найдено пользователей: {len(users)}")
                    
                    # Привязка обработчика клика для действий
                    self.results_tree.bind("<ButtonRelease-1>", self.on_result_click)
            else:
                messagebox.showerror("Ошибка", f"Ошибка API GitHub: {response.status_code}")
                self.status_var.set("Ошибка при выполнении поиска")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка соединения: {str(e)}")
            self.status_var.set("Ошибка сети")
        finally:
            self.search_button.config(state=tk.NORMAL)
    
    def on_result_click(self, event):
        """Обработка клика по результатам поиска"""
        region = self.results_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.results_tree.identify_column(event.x)
            if column == "#5":  # Колонка "Действия"
                item = self.results_tree.identify_row(event.y)
                if item:
                    values = self.results_tree.item(item, "values")
                    login = values[1]
                    self.toggle_favorite_from_results(login, item)
    
    def toggle_favorite_from_results(self, login, item):
        """Добавление/удаление из избранного из результатов поиска"""
        if any(fav['login'] == login for fav in self.favorites):
            # Удаление из избранного
            self.favorites = [fav for fav in self.favorites if fav['login'] != login]
            self.save_favorites()
            self.results_tree.item(item, values=(
                self.results_tree.item(item, "values")[0],
                login,
                self.results_tree.item(item, "values")[2],
                self.results_tree.item(item, "values")[3],
                "☆ Добавить"
            ))
            self.status_var.set(f"Пользователь {login} удалён из избранного")
        else:
            # Добавление в избранное
            try:
                # Получение дополнительной информации о пользователе
                url = f"https://api.github.com/users/{login}"
                response = requests.get(url)
                if response.status_code == 200:
                    user_data = response.json()
                    favorite_user = {
                        "login": user_data['login'],
                        "id": user_data['id'],
                        "type": user_data['type'],
                        "avatar_url": user_data.get('avatar_url', ''),
                        "html_url": user_data.get('html_url', ''),
                        "name": user_data.get('name', ''),
                        "company": user_data.get('company', ''),
                        "blog": user_data.get('blog', ''),
                        "location": user_data.get('location', ''),
                        "email": user_data.get('email', ''),
                        "bio": user_data.get('bio', ''),
                        "public_repos": user_data.get('public_repos', 0),
                        "followers": user_data.get('followers', 0),
                        "following": user_data.get('following', 0),
                        "created_at": user_data.get('created_at', ''),
                        "added_to_favorites": datetime.now().isoformat()
                    }
                    self.favorites.append(favorite_user)
                    self.save_favorites()
                    self.results_tree.item(item, values=(
                        self.results_tree.item(item, "values")[0],
                        login,
                        self.results_tree.item(item, "values")[2],
                        self.results_tree.item(item, "values")[3],
                        "★ Удалить"
                    ))
                    self.refresh_favorites()
                    self.status_var.set(f"Пользователь {login} добавлен в избранное")
                else:
                    messagebox.showerror("Ошибка", f"Не удалось получить данные пользователя {login}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")
    
    def refresh_favorites(self):
        """Обновление таблицы избранного"""
        for item in self.fav_tree.get_children():
            self.fav_tree.delete(item)
        
        for fav in self.favorites:
            self.fav_tree.insert("", tk.END, values=(
                "⭐",
                fav['login'],
                fav['id'],
                fav['type'],
                "🗑️ Удалить"
            ), tags=(fav['login'],))
        
        # Привязка обработчика клика для избранного
        self.fav_tree.bind("<ButtonRelease-1>", self.on_fav_click)
    
    def on_fav_click(self, event):
        """Обработка клика по избранному"""
        region = self.fav_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.fav_tree.identify_column(event.x)
            if column == "#5":  # Колонка "Действия"
                item = self.fav_tree.identify_row(event.y)
                if item:
                    values = self.fav_tree.item(item, "values")
                    login = values[1]
                    self.remove_from_favorites(login, item)
            elif column in ["#2", "#3", "#4"]:  # Клик по информации о пользователе
                item = self.fav_tree.identify_row(event.y)
                if item:
                    values = self.fav_tree.item(item, "values")
                    login = values[1]
                    self.show_user_details(login)
    
    def remove_from_favorites(self, login, item):
        """Удаление пользователя из избранного"""
        if messagebox.askyesno("Подтверждение", f"Удалить пользователя {login} из избранного?"):
            self.favorites = [fav for fav in self.favorites if fav['login'] != login]
            self.save_favorites()
            self.fav_tree.delete(item)
            self.status_var.set(f"Пользователь {login} удалён из избранного")
            
            # Обновление кнопки в результатах поиска, если открыта эта вкладка
            for child in self.results_tree.get_children():
                if self.results_tree.item(child, "values")[1] == login:
                    self.results_tree.item(child, values=(
                        self.results_tree.item(child, "values")[0],
                        login,
                        self.results_tree.item(child, "values")[2],
                        self.results_tree.item(child, "values")[3],
                        "☆ Добавить"
                    ))
                    break
    
    def show_user_details(self, login):
        """Показ детальной информации о пользователе"""
        user_data = next((fav for fav in self.favorites if fav['login'] == login), None)
        if user_data:
            details = f"""
📊 Детальная информация о пользователе: {user_data['login']}

👤 Имя: {user_data.get('name', 'Не указано')}
🔗 Профиль: {user_data.get('html_url', 'Не указано')}
🏢 Компания: {user_data.get('company', 'Не указано')}
📍 Локация: {user_data.get('location', 'Не указано')}
📧 Email: {user_data.get('email', 'Не указано')}
📝 Bio: {user_data.get('bio', 'Не указано')}

📚 Публичные репозитории: {user_data.get('public_repos', 0)}
👥 Подписчики: {user_data.get('followers', 0)}
👤 Подписки: {user_data.get('following', 0)}
📅 Дата регистрации: {user_data.get('created_at', 'Не указано')[:10]}
⭐ Добавлен в избранное: {user_data.get('added_to_favorites', 'Не указано')[:19]}
            """
            messagebox.showinfo(f"Информация о {login}", details)

def main():
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()

if __name__ == "__main__":
    main()
