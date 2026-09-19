from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp

N = 15
CELL = dp(22)
PAD = dp(20)
BOARD_PX = CELL * (N - 1) + PAD * 2


class Board(Widget):
    def __init__(self, status_label, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (BOARD_PX, BOARD_PX)
        self.board = [[0] * N for _ in range(N)]
        self.black_turn = True
        self.game_over = False
        self.win_line = None
        self.status = status_label
        self.bind(pos=self.redraw, size=self.redraw)
        self.redraw()

    def reset(self):
        self.board = [[0] * N for _ in range(N)]
        self.black_turn = True
        self.game_over = False
        self.win_line = None
        self.status.text = "黑棋回合"
        self.redraw()

    def redraw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.91, 0.72, 0.42, 1)
            Rectangle(pos=self.pos, size=self.size)
            Color(0, 0, 0, 1)
            for i in range(N):
                x = self.x + PAD + i * CELL
                y = self.y + PAD
                Line(points=[x, y, x, y + (N - 1) * CELL], width=1)
                Line(points=[self.x + PAD, y + i * CELL,
                             self.x + PAD + (N - 1) * CELL, y + i * CELL], width=1)
            for i in range(N):
                for j in range(N):
                    v = self.board[i][j]
                    if v == 0:
                        continue
                    cx = self.x + PAD + i * CELL
                    cy = self.y + PAD + j * CELL
                    if v == 1:
                        Color(0, 0, 0, 1)
                    else:
                        Color(1, 1, 1, 1)
                    Ellipse(pos=(cx - CELL * 0.42, cy - CELL * 0.42),
                            size=(CELL * 0.84, CELL * 0.84))
            if self.win_line:
                Color(1, 0, 0, 1)
                Line(points=self.win_line, width=3)

    def on_touch_down(self, touch):
        if self.game_over:
            return True
        if not self.collide_point(*touch.pos):
            return False
        i = round((touch.x - self.x - PAD) / CELL)
        j = round((touch.y - self.y - PAD) / CELL)
        if 0 <= i < N and 0 <= j < N and self.board[i][j] == 0:
            self.board[i][j] = 1 if self.black_turn else 2
            line = self.check_win(i, j, self.board[i][j])
            if line:
                self.game_over = True
                self.win_line = line
                self.status.text = ("黑棋" if self.black_turn else "白棋") + "获胜！"
            else:
                self.black_turn = not self.black_turn
                self.status.text = "黑棋回合" if self.black_turn else "白棋回合"
            self.redraw()
        return True

    def check_win(self, x, y, c):
        dirs = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in dirs:
            cells = [(x, y)]
            for s in (1, -1):
                k = 1
                while True:
                    nx, ny = x + dx * k * s, y + dy * k * s
                    if 0 <= nx < N and 0 <= ny < N and self.board[nx][ny] == c:
                        cells.append((nx, ny))
                        k += 1
                    else:
                        break
            if len(cells) >= 5:
                xs = [self.x + PAD + a * CELL for a, b in cells]
                ys = [self.y + PAD + b * CELL for a, b in cells]
                return [min(xs), min(ys), max(xs), max(ys)]
        return None


class GomokuApp(App):
    def build(self):
        self.title = "五子棋"
        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        self.status = Label(text="黑棋回合", size_hint=(1, None), height=dp(40),
                            font_size=dp(20), color=(1, 1, 1, 1))
        root.add_widget(self.status)
        self.board = Board(self.status)
        root.add_widget(self.board)
        btn = Button(text="重新开始", size_hint=(1, None), height=dp(50))
        btn.bind(on_release=lambda *a: self.board.reset())
        root.add_widget(btn)

        with root.canvas.before:
            Color(0.15, 0.15, 0.2, 1)
            self.bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_bg, size=self.update_bg)
        return root

    def update_bg(self, *args):
        self.bg.pos = self.root.pos
        self.bg.size = self.root.size


if __name__ == "__main__":
    Window.clearcolor = (0.15, 0.15, 0.2, 1)
    GomokuApp().run()