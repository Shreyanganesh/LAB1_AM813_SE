def format_player_name(name):
    """
    Title-cases a player name and cuts it to 10 characters for the scoreboard.
    Assumes name is a non-empty string.
    """
    return name.strip().title()[:10]

def parse_frame(text):
    """
    Converts frame notation into pins knocked down: 'X' -> (10, 0),
    '7/' -> (7, 3), '45' -> (4, 5).
    Assumes text is a valid frame.
    """
    text = text.strip().upper()
    if text == 'X':
        return 10, 0
    first = int(text[0])
    if text[1] == '/':
        return first, 10 - first
    return first, int(text[1])

def parse_scoreboard(text):
    """
    Parses 'Asha:150,Ravi:132' into a {name: score} dictionary.
    Assumes every entry is written as 'name:score'.
    """
    scores = {}
    for entry in text.split(','):
        name, score = entry.split(':')
        scores[name.strip()] = int(score)
    return scores

def main():
    print("==== Running format_player_name ====")
    value = input("Enter a player name for the scoreboard: ")
    print("Scoreboard name:", format_player_name(value))

    print("\n==== Running parse_frame ====")
    value = input("Enter a frame as X (strike), 7/ (spare) or two digits (e.g. 45): ")
    print("Pins (first roll, second roll):", parse_frame(value))

    print("\n==== Running parse_scoreboard ====")
    value = input("Enter scores as NAME:SCORE separated by commas (e.g. Asha:150,Ravi:132): ")
    print("Scoreboard:", parse_scoreboard(value))

if __name__ == "__main__":
    main()
