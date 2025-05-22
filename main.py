import threading
from socket import *
from customtkinter import *

class RegisterWindow(CTk):
    def __init__(self):
        super().__init__()
        self.username = None
        self.title("Приэднатися")
        self.geometry("300x300")

        CTkLabel(self, text = "Вход в LogiTalk", font = ("Arial", 20, "bold")).pack(pady = 40)
        self.name_entry = CTkEntry(self, placeholder_text = "vvedi imya")
        self.name_entry.pack()

        self.host_entry = CTkEntry(self, placeholder_text= "dava host suda localhost")
        self.host_entry.pack(pady = 5)
        self.port_entry = CTkEntry(self, placeholder_text= "dava port sud 12334")
        self.port_entry.pack()

        self.submit_button = CTkButton(self, text = "Prisoedenylsa", command = self.start_chat)
        self.submit_button.pack(pady = 5)

    def start_chat(self):
        self.username = self.name_entry.get().strip()
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((self.host_entry.get(), int(self.port_entry.get())))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} prisoedebylsa k chaty!\n"
            self.sock.send(hello.encode("utf-8"))

            self.destroy()

            win = MainWindow(self.sock, self.username)
            win.mainloop()
        except Exception as e:
            print(f"Nea")


#Часть программы отвечающая за тему размер окна и всё остальное
class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('600x400')
        self.title("CTk Chat")
        set_appearance_mode("dark")
        set_default_color_theme("green")

        self.username = 'd1spent'
        self.is_show_menu = False
        self.speed_animate_menu = -5
        self.label = None

        # Кнопки их цвет и текст на них
        self.menu_frame = CTkFrame(self, width=30, height=400, fg_color="gray20", corner_radius=0)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)

        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)

        # chat
        self.chat_field = CTkTextbox(self, font=('Segoe UI', 13), state='disabled',wrap='word', corner_radius=10)

        self.chat_field.place(x=40, y=0)

        self.message_entry = CTkEntry(self, placeholder_text='Type message...', height=40, corner_radius=10)
        self.message_entry.place(x=40, y=360)

        self.send_button = CTkButton(self, text='SEND', width=80, height=40,command=self.send_message, corner_radius=10)

        self.send_button.place(x=520, y=360)

        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('localhost', 8080))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} joined to chat!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"[ERROR] Не вдалося підключитися до сервера: {e}")

        self.adaptive_ui()
# Чтоб меню оставалось на месте когда ти нажал на кнопку
    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='▶️')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='◀️')
            self.show_menu()
            # menu content
            self.label = CTkLabel(self.menu_frame, text='Name', font=('Segoe UI', 14))
            self.label.pack(pady=20)
            self.entry = CTkEntry(self.menu_frame)
            self.entry.pack(pady=10)
#Само меню
    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
            self.after(10, self.show_menu)
            if self.label and self.entry:
                self.label.destroy()
                self.entry.destroy()
#Анімащке
    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width(), y=0)
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 10,
                                  height=self.winfo_height() - 50)
        self.send_button.place(x=self.winfo_width() - 90, y=self.winfo_height() - 45)
        self.message_entry.place(x=self.menu_frame.winfo_width() + 10, y=self.send_button.winfo_y())
        self.message_entry.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width() - 20)

        self.after(100, self.adaptive_ui)
#Добаващке сообщащке
    def add_message(self, text):
        self.chat_field.configure(state='normal')
        self.chat_field.insert(END, text + '\n')
        self.chat_field.configure(state='disabled')
        self.chat_field.see(END)
#Отпровлящке сообщащке
    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"Me: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                self.add_message("[ERROR] message have not sended")
        self.message_entry.delete(0, END)
#Получащке сообщащке
    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()
#Часть для корректной работы отправки сообщений и их внешного вида тоесть чтобы можно было видеть сообщение и того кто его отправил
    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT" and len(parts) >= 3:
            author = parts[1]
            message = parts[2]
            if author != self.username:
                self.add_message(f"{author}: {message}")
        elif msg_type == "IMAGE" and len(parts) >= 4:
            author = parts[1]
            filename = parts[2]
            self.add_message(f"{author} send image: {filename}")
        else:
            self.add_message(line)


if __name__ == "__main__":
    win = MainWindow()
    RegisterWindow().mainloop()
