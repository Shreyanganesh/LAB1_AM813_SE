def format_player_name(name):
    """
    Title-cases a player name and cuts it to 10 characters for the scoreboard.
    Returns an empty string for None, empty, or non-string inputs.
    """
    if not isinstance(name, str) or not name.strip():
        return ""
    return name.strip().title()[:10]


def parse_frame(text):
    """
    Converts frame notation into pins knocked down: 'X' -> (10, 0),
    '7/' -> (7, 3), '45' -> (4, 5).
    Returns (0, 0) for invalid or empty input.
    """
    if not isinstance(text, str) or not text.strip():
        return 0, 0
    text = text.strip().upper()
    if text == 'X':
        return 10, 0
    if len(text) < 2:
        # Single character that is not 'X' – invalid frame
        return 0, 0
    try:
        first = int(text[0])
    except ValueError:
        return 0, 0
    if text[1] == '/':
        return first, 10 - first
    try:
        second = int(text[1])
    except ValueError:
        return 0, 0
    return first, second


def parse_scoreboard(text):
    """
    Parses 'Asha:150,Ravi:132' into a {name: score} dictionary.
    Returns an empty dict for None, empty, or malformed input.
    Skips individual entries that are malformed.
    """
    if not isinstance(text, str) or not text.strip():
        return {}
    scores = {}
    for entry in text.split(','):
        entry = entry.strip()
        if ':' not in entry:
            continue
        parts = entry.split(':', 1)
        name = parts[0].strip()
        score_str = parts[1].strip()
        if not name or not score_str:
            continue
        try:
            scores[name] = int(score_str)
        except ValueError:
            continue
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
