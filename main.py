import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import signal
import serial
import time

# Configurações da porta serial (Arduino)
port = "COM5"  # Altere para a porta correta do Arduino
baudrate = 9600

try:
    arduino = serial.Serial(port, baudrate, timeout=1)
    time.sleep(2)  # Tempo para o Arduino resetar
except serial.SerialException:
    arduino = None


class WaveformApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de Sinais")

        # Fechar corretamente a aplicação ao fechar a janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Frequência e duty cycle iniciais
        self.square_freq = 15.0
        self.square_duty = 100.0

        # Criação dos gráficos
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(5, 4))
        self.fig.tight_layout(pad=4)

        # Tempo para exibir dois ciclos da onda senoidal de 15 Hz
        self.x = np.linspace(0, 2 / 15, 1000)  # Dois ciclos de 15 Hz
        self.sin_wave_15hz = np.sin(2 * np.pi * 15 * self.x)  # Onda senoidal com 15 Hz
        self.sin_wave_20hz = np.sin(2 * np.pi * 20 * self.x)  # Onda senoidal com 20 Hz
        self.square_wave = signal.square(
            2 * np.pi * self.square_freq * self.x, duty=self.square_duty / 100.0
        )

        # Gráfico da onda senoidal de 15 Hz e 20 Hz
        (self.line1,) = self.ax1.plot(
            self.x, self.sin_wave_15hz, label="Onda Senoidal (15 Hz)", color="blue"
        )
        (self.line3,) = self.ax1.plot(
            self.x, self.sin_wave_20hz, label="Onda Senoidal (20 Hz)", color="red"
        )

        # Gráfico da onda quadrada
        (self.line2,) = self.ax2.plot(
            self.x,
            self.square_wave,
            label=f"Onda Quadrada ({self.square_freq:.1f} Hz, Duty: {self.square_duty:.1f}%)",
        )

        self.ax1.set_ylim(-1.5, 1.5)
        self.ax2.set_ylim(-0.1, 1.1)
        self.ax1.legend()
        self.ax2.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        # Frame para os controles
        self.control_frame = ttk.Frame(root)
        self.control_frame.pack(pady=10)

        # Entrada de frequência e botões
        self.freq_label = ttk.Label(self.control_frame, text="Frequência (Hz):")
        self.freq_label.grid(row=0, column=0, padx=5)

        self.freq_var = tk.StringVar(value=str(self.square_freq))
        self.freq_entry = ttk.Entry(
            self.control_frame, textvariable=self.freq_var, width=10
        )
        self.freq_entry.grid(row=0, column=1)
        self.freq_entry.bind(
            "<Return>", self.update_plot_event
        )  # Atualiza e envia ao pressionar Enter

        # Botão para aumentar a frequência (em linha)
        self.increase_button = ttk.Button(
            self.control_frame, text="+", command=self.increase_frequency
        )
        self.increase_button.grid(row=0, column=2, padx=5)

        # Botão para reduzir a frequência (em linha)
        self.decrease_button = ttk.Button(
            self.control_frame, text="-", command=self.decrease_frequency
        )
        self.decrease_button.grid(row=0, column=3, padx=5)

        # Entrada de duty cycle e botões
        self.duty_label = ttk.Label(self.control_frame, text="Duty Cycle (%):")
        self.duty_label.grid(row=1, column=0, padx=5)

        self.duty_var = tk.StringVar(value=str(self.square_duty))
        self.duty_entry = ttk.Entry(
            self.control_frame, textvariable=self.duty_var, width=10
        )
        self.duty_entry.grid(row=1, column=1)
        self.duty_entry.bind(
            "<Return>", self.update_plot_event
        )  # Atualiza e envia ao pressionar Enter

        # Botão para aumentar o duty cycle (em linha)
        self.increase_duty_button = ttk.Button(
            self.control_frame, text="+", command=self.increase_duty
        )
        self.increase_duty_button.grid(row=1, column=2, padx=5)

        # Botão para reduzir o duty cycle (em linha)
        self.decrease_duty_button = ttk.Button(
            self.control_frame, text="-", command=self.decrease_duty
        )
        self.decrease_duty_button.grid(row=1, column=3, padx=5)

        # Botão para tentar a comunicação com o Arduino
        self.connect_button = ttk.Button(
            self.control_frame, text="Conectar Arduino", command=self.connect_arduino
        )
        self.connect_button.grid(row=2, column=1, columnspan=3, pady=10)

        # Atualiza a interface
        self.update_plot()

    def connect_arduino(self):
        global arduino
        try:
            arduino = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)
            print("Conectado ao Arduino!")
        except serial.SerialException:
            print("Erro ao conectar ao Arduino.")

    def update_plot(self):
        # Atualiza a onda quadrada
        try:
            self.square_freq = float(self.freq_var.get())
            self.square_duty = float(self.duty_var.get())
        except ValueError:
            pass

        self.square_wave = signal.square(
            2 * np.pi * self.square_freq * self.x, duty=self.square_duty / 100.0
        )
        self.line2.set_ydata(self.square_wave)
        self.ax2.legend(
            [
                f"Onda Quadrada ({self.square_freq:.1f} Hz, Duty: {self.square_duty:.1f}%)"
            ]
        )

        self.canvas.draw()

        # Envia os valores para o Arduino, se estiver conectado
        if arduino and arduino.is_open:
            arduino.write(f"{self.square_freq},{self.square_duty}\n".encode())
            print(f"Enviado para o Arduino: {self.square_freq},{self.square_duty}")

    def update_plot_event(self, event):
        """Atualiza o gráfico e envia os valores ao Arduino quando Enter é pressionado nas caixas de texto."""
        self.update_plot()

    def increase_frequency(self):
        try:
            current_freq = float(self.freq_var.get())
            current_freq = round(current_freq + 0.1, 1)  # Incremento com arredondamento
            self.freq_var.set(f"{current_freq:.1f}")
        except ValueError:
            self.freq_var.set("1.0")
        self.update_plot()

    def decrease_frequency(self):
        try:
            current_freq = float(self.freq_var.get())
            if current_freq > 0.1:
                current_freq = round(
                    current_freq - 0.1, 1
                )  # Decremento com arredondamento
            self.freq_var.set(f"{current_freq:.1f}")
        except ValueError:
            self.freq_var.set("1.0")
        self.update_plot()

    def increase_duty(self):
        try:
            current_duty = float(self.duty_var.get())
            if current_duty < 100:
                current_duty += 5
            self.duty_var.set(str(current_duty))
        except ValueError:
            self.duty_var.set("50.0")
        self.update_plot()

    def decrease_duty(self):
        try:
            current_duty = float(self.duty_var.get())
            if current_duty > 0:
                current_duty -= 5
            self.duty_var.set(str(current_duty))
        except ValueError:
            self.duty_var.set("50.0")
        self.update_plot()

    def on_closing(self):
        # Encerra a conexão serial se estiver aberta
        if arduino and arduino.is_open:
            arduino.close()
            print("Conexão com o Arduino encerrada.")
        self.root.destroy()


# Inicialização da interface Tkinter
root = tk.Tk()
app = WaveformApp(root)
root.mainloop()
