import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class PacmanGame:
    def __init__(self):
        self.board = [
            "####################",
            "#........#.........#",
            "#.##.###.#.###.##.#",
            "#.................#",
            "#.##.#.#####.#.##.#",
            "#....#...#...#....#",
            "####.###.#.###.####",
            "#....#.......#....#",
            "#.##.#.#####.#.##.#",
            "#.................#",
            "#.##.###.#.###.##.#",
            "#........P........#",
            "####################"
        ]
        self.score = 0
        self.player_pos = [11, 10]  # Starting position
        self.game_over = False

    def move_player(self, direction):
        if self.game_over:
            return False

        new_pos = self.player_pos.copy()
        if direction == "UP":
            new_pos[0] -= 1
        elif direction == "DOWN":
            new_pos[0] += 1
        elif direction == "LEFT":
            new_pos[1] -= 1
        elif direction == "RIGHT":
            new_pos[1] += 1

        # Проверка на столкновение со стеной
        if self.board[new_pos[0]][new_pos[1]] != "#":
            # Обновление очков если собрана точка
            if self.board[new_pos[0]][new_pos[1]] == ".":
                self.score += 10
                row = list(self.board[new_pos[0]])
                row[new_pos[1]] = " "
                self.board[new_pos[0]] = "".join(row)

            # Обновление старой позиции
            row = list(self.board[self.player_pos[0]])
            row[self.player_pos[1]] = " "
            self.board[self.player_pos[0]] = "".join(row)

            # Обновление новой позиции
            self.player_pos = new_pos
            row = list(self.board[self.player_pos[0]])
            row[self.player_pos[1]] = "P"
            self.board[self.player_pos[0]] = "".join(row)

            return True
        return False

    def get_board_display(self):
        display = ""
        for row in self.board:
            display += row.replace("#", "⬛").replace(".", "•").replace("P", "😀").replace(" ", "⬜") + "\n"
        return f"{display}\nScore: {self.score}"

class GameManager:
    def __init__(self):
        self.games = {}

    def get_game(self, user_id: int) -> PacmanGame:
        if user_id not in self.games:
            self.games[user_id] = PacmanGame()
        return self.games[user_id]

    def remove_game(self, user_id: int):
        if user_id in self.games:
            del self.games[user_id]

game_manager = GameManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    game = game_manager.get_game(user_id)
    
    keyboard = [
        [
            InlineKeyboardButton("⬆️", callback_data="UP"),
        ],
        [
            InlineKeyboardButton("⬅️", callback_data="LEFT"),
            InlineKeyboardButton("➡️", callback_data="RIGHT"),
        ],
        [
            InlineKeyboardButton("⬇️", callback_data="DOWN"),
        ],
        [
            InlineKeyboardButton("New Game", callback_data="NEW_GAME"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        game.get_board_display(),
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == "NEW_GAME":
        game_manager.remove_game(user_id)
        game = game_manager.get_game(user_id)
    else:
        game = game_manager.get_game(user_id)
        game.move_player(query.data)

    keyboard = [
        [
            InlineKeyboardButton("⬆️", callback_data="UP"),
        ],
        [
            InlineKeyboardButton("⬅️", callback_data="LEFT"),
            InlineKeyboardButton("➡️", callback_data="RIGHT"),
        ],
        [
            InlineKeyboardButton("⬇️", callback_data="DOWN"),
        ],
        [
            InlineKeyboardButton("New Game", callback_data="NEW_GAME"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=game.get_board_display(),
        reply_markup=reply_markup
    )

def main():
    # Замените "YOUR_BOT_TOKEN" на токен вашего бота
    import os
application = Application.builder().token(os.getenv('7858082895:AAFCHht4jHj-w6VZDZq7UlUcvG0NKUleu-I')).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()

if __name__ == "__main__":
    main()
