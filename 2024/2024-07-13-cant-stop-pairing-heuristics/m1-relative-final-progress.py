import random

def relative_final_progress(game, options):
    max_progress = 0
    best_option = options[0]
    for option in options:
        progress = sum(game.columns.get(column, 0) / game.get_column_length(column) for column in option)
        if progress > max_progress:
            max_progress = progress
            best_option = option
    return best_option

class CantStopGame:
    def __init__(self):
        self.columns = {i: 0 for i in range(2, 13)}
        self.completed_columns = set()

    def get_options(self, input_pairs):
        # Handle both single columns and pairs of columns as options
        options = []
        for pair in input_pairs.split():
            if ',' in pair:
                columns = tuple(map(int, pair.split(',')))
                if all(2 <= col <= 12 for col in columns):
                    options.append(columns)
                else:
                    print(f"Invalid pair: {pair}")
            elif len(pair) == 2:
                col1, col2 = int(pair[0]), int(pair[1])
                if 2 <= col1 <= 12 and 2 <= col2 <= 12:
                    options.append((col1, col2))
                else:
                    print(f"Invalid pair: {pair}")
            elif len(pair) == 3:
                # Treat as individual columns
                col1, col2 = int(pair[0]), int(pair[1:])
                if 2 <= col1 <= 12:
                    options.append((col1,))
                if 2 <= col2 <= 12:
                    options.append((col2,))
            else:
                col = int(pair)
                if 2 <= col <= 12:
                    options.append((col,))
                else:
                    print(f"Invalid column: {col}")
        return options

    def make_progress(self, option, steps=1):
        if len(option) == 2 and option[0] == option[1]:
            # Double progress for pairs like (5, 5)
            column = option[0]
            self.columns[column] += 2 * steps
            if self.columns[column] >= self.get_column_length(column):
                self.completed_columns.add(column)
        else:
            for column in option:
                if column in self.completed_columns:
                    continue
                self.columns[column] += steps
                if self.columns[column] >= self.get_column_length(column):
                    self.completed_columns.add(column)

    def get_column_length(self, column):
        lengths = {2: 3, 3: 5, 4: 7, 5: 9, 6: 11, 7: 13, 8: 11, 9: 9, 10: 7, 11: 5, 12: 3}
        return lengths[column]

    def print_board(self):
        print("Your Progress:")
        for column in range(2, 13):
            print(f"Column {column}: {self.columns[column]}/{self.get_column_length(column)}")

    def get_board_state(self):
        return " ".join(str(self.columns[i]) for i in range(2, 13))

    def play_turn(self):
        while True:
            try:
                # Input board state from user
                board_state = input("Enter your board state (format: 0 0 0 0 0 0 0 0 0 0 0): ")
                board_values = list(map(int, board_state.split()))
                if len(board_values) != 11:
                    raise ValueError
                self.columns = {i+2: board_values[i] for i in range(11)}
                break
            except ValueError:
                print("Invalid input. Please enter 11 integers separated by spaces.")

        self.print_board()

        while True:
            # Input possible column pairs directly from user
            user_input = input("Enter possible columns (format: 8,7 96 410 5): ")
            options = self.get_options(user_input)
            if not options:
                print("No valid options provided. Please try again.")
                continue

            # Evaluate the best option from all given choices
            best_option = relative_final_progress(self, options)
            print(f"Best option: {best_option}")

            self.make_progress(best_option)

            action = input("Did you bust (b), stop (s), or continue (c)? ")
            if action == 'b':
                print("Busted. Turn ends.")
                break
            elif action == 's':
                print("Stopped. Final board state:")
                print(self.get_board_state())
                break
            elif action == 'c':
                continue
            else:
                print("Invalid input. Please enter 'b', 's', or 'c'.")

if __name__ == "__main__":
    game = CantStopGame()
    game.play_turn()
