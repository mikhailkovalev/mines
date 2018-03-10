import os.path
import tkinter as tk
from PIL import Image, ImageTk


class MainWindow:
    def __init__(self, game_manager):
        self.font = ('arial', 8)
        self._create_widgets()

        self._bind_manager(game_manager)

    def _set_icon(self):
        icon_path = os.path.join(
            os.path.dirname(__file__), 'res', 'icon.png')
        self.icon = ImageTk.PhotoImage(Image.open(icon_path))
        self.root.tk.call('wm', 'iconphoto', self.root._w, self.icon)

    def _create_widgets(self):
        self.root = tk.Tk()
        self.root.title('Mines')
        self._set_icon()

        self._create_left_frame()
        self._create_right_frame()

    def _create_left_frame(self):
        self.left_frame = tk.Label(self.root, bd=5)
        self.left_frame.pack(side='left', anchor='n')

        self.new_game_button = tk.Button(
            self.left_frame, text='New Game', font=self.font, padx=5)
        self.new_game_button.pack(anchor='nw', side='top')

        self._create_level_group()
        self._create_custom_group()

    def _create_custom_group(self):
        self.custom_group = tk.LabelFrame(
            self.left_frame, text='Custom Settings', font=self.font, padx=5)
        self.custom_group.pack(side='top', anchor='w')

        self.width_label = tk.Label(
            self.custom_group, text='Width', font=self.font)
        self.width_label.grid(column=0, row=0, sticky='w')
        
        self.height_label = tk.Label(
            self.custom_group, text='Height', font=self.font)
        self.height_label.grid(column=0, row=1, sticky='w')
        
        self.mines_count_label = tk.Label(
            self.custom_group, text='Mines Count', font=self.font)
        self.mines_count_label.grid(column=0, row=2, sticky='w')

        self.width_spinbox = tk.Spinbox(
            self.custom_group, from_=10, to=30, width=3)
        self.width_spinbox.grid(column=1, row=0)

        self.height_spinbox = tk.Spinbox(
            self.custom_group, from_=10, to=30, width=3)
        self.height_spinbox.grid(column=1, row=1)

        self.mines_count_spinbox = tk.Spinbox(
            self.custom_group, from_=10, to=30, width=3)
        self.mines_count_spinbox.grid(column=1, row=2)

    def _create_level_group(self):
        self.level_group = tk.LabelFrame(
            self.left_frame, text='Level', font=self.font, padx=5)
        self.level_group.pack(side='top', anchor='w')

        self.level_intvar = tk.IntVar()
        self.level_intvar.set(1)

        self.easy_radio_button = tk.Radiobutton(
            self.level_group, text='Rookie', font=self.font,
            variable=self.level_intvar, value=1)
        self.easy_radio_button.pack(side='top', anchor='w')

        self.middle_radio_button = tk.Radiobutton(
            self.level_group, text='Veteran', font=self.font,
            variable=self.level_intvar, value=2)
        self.middle_radio_button.pack(side='top', anchor='w')

        self.hard_radio_button = tk.Radiobutton(
            self.level_group, text='Warrior', font=self.font,
            variable=self.level_intvar, value=3)
        self.hard_radio_button.pack(side='top', anchor='w')

        self.custom_radio_button = tk.Radiobutton(
            self.level_group, text='Custom', font=self.font,
            variable=self.level_intvar, value=4)
        self.custom_radio_button.pack(side='top', anchor='w')

    def _create_right_frame(self):
        self.right_frame = tk.Label(self.root, bd=5)
        self.right_frame.pack(side='right', anchor='n')

        self.status_label = tk.Label(self.right_frame, font=('arial', 14))
        self.status_label.pack(side='top', anchor='w')

        self.canvas = tk.Canvas(self.right_frame)
        self.canvas.pack()

    def _bind_manager(self, game_manager):
        self.game_manager = game_manager
        game_manager.render_context.canvas = self.canvas
        self.new_game_button.configure(command=game_manager.new_game)
        self.canvas.bind('<Button-1>', game_manager.left_button_click)
        self.canvas.bind('<Button-3>', game_manager.right_button_click)
        self.canvas.bind('<Button-2>', game_manager.middle_button_click)

    def update_board(self):
        pass

    def run(self):
        self.game_manager.field.render()
        self.root.mainloop()
