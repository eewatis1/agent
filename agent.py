import tkinter as tk
import threading
import time
import pyautogui
from io import BytesIO
from google import genai
from PIL import Image

# 1. Сюди вставляєш свій скопійований ключ
API_KEY = ""
client = genai.Client(api_key=API_KEY)

class AssistantModal:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Assistant")
        
        # Налаштування вікна: напівпрозоре, без стандартних рамок, завжди зверху
        self.root.geometry("400x200+10+10") # Розмір 400x200, зліва вгорі (10, 10)
        self.root.attributes("-topmost", True) # ЗАВЖДИ ПОВЕРХ УСІХ ВІКОН
        self.root.attributes("-alpha", 0.85)   # Прозорість 85%
        self.root.overrideredirect(True)       # Прибрати хрестик і рамку (максимальний статус інкогніто)

        # Текстове поле для виведення відповіді
        self.text_label = tk.Label(root, text="Чекаю запуску тесту...", fg="white", bg="#222222", 
                                   font=("Arial", 11, "bold"), wraplength=380, justify="left")
        self.text_label.pack(expand=True, fill="both")

        # Дозволяємо перетягувати вікно мишкою за будь-яке місце
        self.text_label.bind("<Button-1>", self.start_move)
        self.text_label.bind("<B1-Motion>", self.do_move)

        # Запускаємо цикл аналізу екрана в окремому потоці, щоб вікно не зависало
        threading.Thread(target=self.analyze_screen_loop, daemon=True).start()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def analyze_screen_loop(self):
        while True:
            try:
                self.text_label.config(text="📸 Дивлюсь на екран...")
                
                # Робимо скриншот усього екрана (або потрібної зони)
                screenshot = pyautogui.screenshot()
                
                # Конвертуємо в формат, який розуміє SDK Gemini
                img_byte_arr = BytesIO()
                screenshot.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()
                image_part = Image.open(BytesIO(img_byte_arr))

                # Відправляємо запит до моделі Gemini 2.5 Flash
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[
                        image_part, 
                        "Знайди на екрані питання тесту. Напиши ТІЛЬКИ коротку правильну відповідь або літеру варіанту. Без зайвих слів."
                    ]
                )

                # Оновлюємо текст у модалці
                self.text_label.config(text=f"🤖 Відповідь:\n{response.text.strip()}")
            
            except Exception as e:
                self.text_label.config(text=f"Помилка: {str(e)}")

            # Затримка між знімками екрана (наприклад, кожні 7 секунд)
            time.sleep(7)

if __name__ == "__main__":
    root = tk.Tk()
    app = AssistantModal(root)
    root.mainloop()
