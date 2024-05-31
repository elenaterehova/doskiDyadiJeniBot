import multiprocessing
import runpy
import threading
import time
import tkinter as tk
from doctest import master
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror
from tkinter.ttk import Style, Progressbar

import copy_dir
import run


class App(Frame):
    def __init__(self):
        super().__init__()
        self.unitUI()

    # ---------------------------КНОПКА "ЗАГРУЗИТЬ"----------------------------------------
    def waiting_window(self):
        top = tk.Toplevel(master)
        top.title('Загрузка')
        top.geometry('300x150+500+300')

        msg = Message(top, text="Идет запуск. Подождите.", width=300)
        msg.pack(pady=(30, 10))
        progressbar = Progressbar(top, orient="horizontal", mode="indeterminate")
        progressbar.start()
        progressbar.pack(fill=X, padx=20, pady=20)

        thread = threading.Thread(target=self.run_button_method)
        thread.start()
        top.after(1, self.check_if_running(thread, top))

    def run_button_method(self):
        response = run.go()
        if response is True:
            print('run success')
            return showinfo(title="Успешно!", message="Бот был запущен.")
        else:
            showerror(title="Произошла ошибка", message="Бот не был запущен.")

    def check_if_running(self, thread, top):
        if thread.is_alive():
            self.after(1, lambda: self.check_if_running(thread, top))
        else:
            top.destroy()

    # ---------------------------КНОПКА "ВНЕСТИ ДАННЫЕ"----------------------------------------
    def waiting_window_2(self):
        top2 = tk.Toplevel(master)
        top2.title('Загрузка')
        top2.geometry('300x150+500+300')

        msg2 = Message(top2, text="Идет внесение данных на сервер. Подождите.", width=300)
        msg2.pack(pady=(30, 10))
        progressbar2 = Progressbar(top2, orient="horizontal", mode="indeterminate")
        progressbar2.start()
        progressbar2.pack(fill=X, padx=20, pady=20)

        thread2 = threading.Thread(target=self.add_data)
        thread2.start()
        top2.after(1, self.check_if_running(thread2, top2))

    def add_data(self):
        response = copy_dir.add()
        if response is True:
            print('added success')
            return showinfo(title="Успешно!", message="Данные были добавлены на сервер.")
        else:
            showerror(title="Произошла ошибка", message="Данные уже есть на сервере.")

    def check_if_running_2(self, thread2, top2):
        if thread2.is_alive():
            self.after(1, lambda: self.check_if_running(thread2, top2))
        else:
            top2.destroy()

    def unitUI(self):
        first_lb = Label(text='Чтобы запустить бота на сервере, нажмите кнопку "Запустить".', justify=LEFT)
        first_lb.pack(pady=(40, 10))
        second_lb = Label(text='Чтобы внести на сервер данные, нажмите кнопку "Внести данные".', justify=LEFT)
        second_lb.pack(ipady=15)
        alert_lb = Label(text='ВНИМАНИЕ! Данные на сервер вносятся только в том случае, '
                              'если с момента блокировки аккаунта прошло 7 и более дней. '
                              'В этом случае сервер удаляет данные и присылает на почту уведомление.',
                         justify=LEFT,
                         foreground='red',
                         wraplength=300,
                         )
        alert_lb.pack(pady=15)
        run_button = ttk.Button(self, text='Запустить', command=self.waiting_window)
        run_button.pack(side=LEFT, padx=50, pady=15)
        add_data_button = ttk.Button(self, text='Внести данные', command=self.waiting_window_2)
        add_data_button.pack(side=RIGHT, padx=60, pady=15)

        self.pack()


def app_main():
    root = Tk()
    root.title('Запуск телеграм-бота на сервере')
    root.iconbitmap(default='app_icon_2.ico')
    root.geometry('400x300+400+200')
    app = App()
    root.mainloop()


if __name__ == '__main__':
    app_main()
