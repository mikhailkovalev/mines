import os.path
import tkinter as tk
from abc import abstractmethod
from functools import partial
from collections import namedtuple

from PIL import Image, ImageTk

from renderers import TkRenderContext
from game_managers import LevelEnum


class Window:
    def __init__(self):
        self.game_manager = None
        self.render_context = self.create_render_context()

    @abstractmethod
    def create_render_context(self):
        pass

    @abstractmethod
    def bind_manager(self, game_manager):
        pass

    @abstractmethod
    def _update_board(self, time_info, mines_info, game_active, user_won):
        pass

    def update_board(self):
        if self.game_manager is not None:
            self._update_board(
                self.game_manager.get_time_info(),
                self.game_manager.get_mines_info(),
                self.game_manager.game_active,
                self.game_manager.user_won,
            )

    def get_render_context(self):
        return self.render_context


LabeledWidget = namedtuple('LabeledWidget', ('label', 'widget'))


class TkWindow(Window):
    def __init__(self):
        self.font = ('arial', 8)
        self._create_widgets()
        self.level_radio_buttons = None
        super().__init__()

    def create_render_context(self):
        return TkRenderContext(self.canvas)

    def _update_board(self, time_info, mines_info, game_active, user_won):
        if not game_active:
            if user_won:
                win_info = 'You Win!'
            else:
                win_info = 'You Loose!'
        else:
            win_info = ''

        board_label_text = '{:03d}; Time: {:03d}\t{}'.format(
            mines_info, time_info, win_info)
        self.board_label.configure(
            text=board_label_text
        )
        self.root.after(500, self.update_board)

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

        label_factory = partial(
            tk.Label,
            master=self.custom_group,
            font=self.font
        )

        spinbox_factory = partial(
            tk.Spinbox,
            master=self.custom_group,
            from_=10,
            to=30,
            width=3
        )

        param_names = ('Width', 'Height', 'Mines Count')

        self.custom_params_editors = tuple(
            LabeledWidget(
                label=label_factory(text=name),
                widget=spinbox_factory(),
            )
            for name in param_names
        )

        for idx, labeled_widget in enumerate(self.custom_params_editors):
            labeled_widget.label.grid(column=0, row=idx, sticky='w')
            labeled_widget.widget.grid(column=1, row=idx)

    def _create_level_group(self):
        self.level_group = tk.LabelFrame(
            self.left_frame, text='Level', font=self.font, padx=5)
        self.level_group.pack(side='top', anchor='w')

        self.level_intvar = tk.IntVar()
        self.level_intvar.set(1)

    def _create_right_frame(self):
        self.right_frame = tk.Frame(self.root, bd=5)
        self.right_frame.pack(side='right', anchor='n')

        self.board_label = tk.Label(self.right_frame, font=('arial', 14))
        self.board_label.pack(side='top', anchor='w')

        self.canvas = tk.Canvas(self.right_frame)
        self.canvas.pack(side='bottom', anchor='w')

    def bind_manager(self, game_manager):
        self.game_manager = game_manager
        self.new_game_button.configure(command=game_manager.new_game)
        self.canvas.bind('<Button-1>', game_manager.mouse_click)
        self.canvas.bind('<Button-2>', game_manager.mouse_click)
        self.canvas.bind('<Button-3>', game_manager.mouse_click)

        radio_button_fabric = partial(
            tk.Radiobutton,
            master=self.level_group,
            font=self.font,
            variable=self.level_intvar,
            command=self.change_level
        )

        def create_radio_button(text, value):
            radio_button = radio_button_fabric(
                text=text, value=value)
            radio_button.pack(side='top', anchor='w')
            return radio_button

        self.level_radio_buttons = tuple(
            create_radio_button(game_manager.level_names[v], v.value)
            for v in LevelEnum
        )

    def change_level(self):
        pass

    def run(self):
        self.root.after(0, self.update_board)
        self.game_manager.field.render()
        self.root.mainloop()
