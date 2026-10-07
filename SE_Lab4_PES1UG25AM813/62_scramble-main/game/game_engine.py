import random
import pygame
from game.text_box import TextBox

ROUND_TIME = 20  # seconds per round
TILE = 44
GAP = 8
DRAG_THRESHOLD = 6  # pixels before a press counts as a drag instead of a click


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.words = ["PYTHON", "PYGAME", "PLANET", "ROCKET", "GALAXY", "STREAM", "PUZZLE", "ALGORITHM"]
        self.secret_word = ""
        self.scrambled_word = ""

        self.score = 0
        self.revealed_letters = []
        self.feedback_msg = "Unscramble the letters above!"
        self.feedback_color = (210, 215, 225)

        # Layout
        self.pool_y = 95
        self.rack_y = 150
        self.hint_y = 200
        self.input_y = 255

        self.input_box = TextBox(width // 2 - 130, self.input_y, 160, 46)
        self.submit_btn = pygame.Rect(width // 2 + 45, self.input_y, 95, 46)
        self.hint_btn = pygame.Rect(width // 2 + 150, self.input_y, 95, 46)

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_word = pygame.font.SysFont(None, 44)
        self.font_tile = pygame.font.SysFont(None, 36)
        self.font_msg = pygame.font.SysFont(None, 26)
        self.font_btn = pygame.font.SysFont(None, 24)

        self.pool = []      # fixed slots; None = tile moved out
        self.rack = []      # fixed slots; None = empty
        self.drag = None    # {"src": ("pool"|"rack", idx), "letter": str, "start": pos, "pos": pos}
        self.round_start = 0

        self.next_round()

    # ---------- round logic ----------
    def scramble_string(self, word):
        letters = list(word)
        while True:
            random.shuffle(letters)
            shuffled = "".join(letters)
            if shuffled != word or len(word) <= 1:
                return shuffled

    def reset_tiles(self):
        self.pool = list(self.scrambled_word)
        self.rack = [None] * len(self.scrambled_word)
        self.drag = None

    def next_round(self):
        self.secret_word = random.choice(self.words)
        self.scrambled_word = self.scramble_string(self.secret_word)
        self.reset_tiles()
        self.revealed_letters = []
        self.input_box.clear()
        self.round_start = pygame.time.get_ticks()

    def time_left(self):
        elapsed = (pygame.time.get_ticks() - self.round_start) / 1000
        return max(0.0, ROUND_TIME - elapsed)

    def use_hint(self):
        for index in range(len(self.secret_word)):
            if index not in self.revealed_letters:
                self.revealed_letters.append(index)
                self.score = max(0, self.score - 0.25)  # small penalty per hint
                self.feedback_msg = f"Hint: letter {index + 1} revealed."
                self.feedback_color = (100, 200, 255)
                return

        self.feedback_msg = "All letters have already been revealed!"
        self.feedback_color = (240, 170, 50)

    def submit_guess(self):
        typed = self.input_box.text.strip().upper()
        guess = typed if typed else "".join(c for c in self.rack if c)
        if not guess:
            self.feedback_msg = "Type a word before submitting!"
            self.feedback_color = (240, 170, 50)
            return

        if guess == self.secret_word:
            self.score += 1
            self.feedback_msg = f"CORRECT! '{self.secret_word}' is right."
            self.feedback_color = (80, 230, 110)
            self.next_round()
        else:
            self.feedback_msg = "WRONG GUESS! Try again."
            self.feedback_color = (240, 80, 80)
            self.input_box.clear()
            self.reset_tiles()

    # ---------- tiles ----------
    def _slot_rects(self, y):
        n = len(self.scrambled_word)
        total = n * TILE + (n - 1) * GAP
        x = self.width // 2 - total // 2
        return [pygame.Rect(x + i * (TILE + GAP), y, TILE, TILE) for i in range(n)]

    def _first_empty(self, slots):
        for i, v in enumerate(slots):
            if v is None:
                return i
        return None

    def _press_tile(self, pos):
        for kind, slots, y in (("pool", self.pool, self.pool_y), ("rack", self.rack, self.rack_y)):
            for i, r in enumerate(self._slot_rects(y)):
                if slots[i] is not None and r.collidepoint(pos):
                    self.drag = {"src": (kind, i), "letter": slots[i], "start": pos, "pos": pos}
                    slots[i] = None
                    return True
        return False

    def _put_back(self):
        kind, i = self.drag["src"]
        (self.pool if kind == "pool" else self.rack)[i] = self.drag["letter"]

    def _release_tile(self, pos):
        d = self.drag
        self.drag = None
        kind, i = d["src"]
        letter = d["letter"]
        moved = abs(pos[0] - d["start"][0]) + abs(pos[1] - d["start"][1]) > DRAG_THRESHOLD

        if not moved:  # plain click: toggle between pool and rack
            if kind == "pool":
                j = self._first_empty(self.rack)
                if j is not None:
                    self.rack[j] = letter
                    return
            else:
                j = self._first_empty(self.pool)
                if j is not None:
                    self.pool[j] = letter
                    return
            (self.pool if kind == "pool" else self.rack)[i] = letter
            return

        # dropped on a rack slot
        for j, r in enumerate(self._slot_rects(self.rack_y)):
            if r.collidepoint(pos):
                occupant = self.rack[j]
                self.rack[j] = letter
                if occupant is not None:  # swap into the tile's origin slot
                    (self.pool if kind == "pool" else self.rack)[i] = occupant
                return

        # dropped on the pool row: send tile back to the pool
        pool_zone = pygame.Rect(0, self.pool_y - 10, self.width, TILE + 20)
        if pool_zone.collidepoint(pos) and kind == "rack":
            j = self._first_empty(self.pool)
            if j is not None:
                self.pool[j] = letter
                return

        (self.pool if kind == "pool" else self.rack)[i] = letter  # cancel

    # ---------- loop ----------
    def handle_event(self, event):
        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.submit_guess()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_btn.collidepoint(event.pos):
                self.submit_guess()
            elif self.hint_btn.collidepoint(event.pos):
                self.use_hint()
            else:
                self._press_tile(event.pos)
        elif event.type == pygame.MOUSEMOTION and self.drag:
            self.drag["pos"] = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.drag:
            self._release_tile(event.pos)

    def update(self):
        if self.time_left() <= 0:
            missed = self.secret_word
            self.next_round()
            self.feedback_msg = f"TIME'S UP! The word was '{missed}'."
            self.feedback_color = (240, 80, 80)

    # ---------- drawing ----------
    def _draw_button(self, screen, rect, label, fill):
        pygame.draw.rect(screen, fill, rect, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), rect, width=2, border_radius=6)
        txt = self.font_btn.render(label, True, (255, 255, 255))
        screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

    def _draw_tile(self, screen, rect, ch, fill):
        pygame.draw.rect(screen, fill, rect, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), rect, width=2, border_radius=6)
        t = self.font_tile.render(ch, True, (255, 255, 255))
        screen.blit(t, (rect.centerx - t.get_width() // 2, rect.centery - t.get_height() // 2))

    def render(self, screen):
        screen.fill((26, 30, 38))

        title_surf = self.font_title.render("Word Scramble Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 15))

        score_surf = self.font_msg.render(f"Score: {self.score:g}", True, (255, 220, 80))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 52))

        # Timer bar
        bar_w, bar_h = 300, 10
        bar_x = self.width // 2 - bar_w // 2
        frac = self.time_left() / ROUND_TIME
        color = (80, 230, 110) if frac > 0.5 else (240, 170, 50) if frac > 0.25 else (240, 80, 80)
        pygame.draw.rect(screen, (60, 66, 80), (bar_x, 76, bar_w, bar_h), border_radius=5)
        pygame.draw.rect(screen, color, (bar_x, 76, int(bar_w * frac), bar_h), border_radius=5)

        # Pool tiles (top) and rack slots (below)
        for r, ch in zip(self._slot_rects(self.pool_y), self.pool):
            if ch is not None:
                self._draw_tile(screen, r, ch, (60, 110, 180))
        for r, ch in zip(self._slot_rects(self.rack_y), self.rack):
            pygame.draw.rect(screen, (70, 76, 92), r, width=2, border_radius=6)
            if ch is not None:
                self._draw_tile(screen, r, ch, (50, 150, 85))

        # Hint display
        hint_display = ""
        for index, letter in enumerate(self.secret_word):
            hint_display += (letter if index in self.revealed_letters else "_") + " "
        hint_surf = self.font_word.render(hint_display.strip(), True, (255, 220, 80))
        screen.blit(hint_surf, (self.width // 2 - hint_surf.get_width() // 2, self.hint_y))

        self.input_box.render(screen)
        self._draw_button(screen, self.submit_btn, "SUBMIT", (50, 150, 85))
        self._draw_button(screen, self.hint_btn, "HINT", (60, 110, 180))

        feedback_surf = self.font_msg.render(self.feedback_msg, True, self.feedback_color)
        screen.blit(feedback_surf, (self.width // 2 - feedback_surf.get_width() // 2, self.input_y + 65))

        # Dragged tile on top
        if self.drag:
            mx, my = self.drag["pos"]
            self._draw_tile(screen, pygame.Rect(mx - TILE // 2, my - TILE // 2, TILE, TILE),
                            self.drag["letter"], (90, 140, 210))