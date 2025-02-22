def check_bingo(bingo_card, marked_positions):
    """
    Check if the player has achieved a Bingo.
    """
    # print(f"Checking bingo for card: {bingo_card} with marked positions: {marked_positions}")
    # print(f"Number of marked positions: {len(marked_positions)}")

    for row in bingo_card:
        # print(f"Bingo card row: {row}")
        if all((row.index(location_name), col) in marked_positions for col, location_name in enumerate(row)):
            return True

    for col in range(5):
        if all((row, col) in marked_positions for row in range(5)):
            return True

    if all((i, i) in marked_positions for i in range(5)):
        return True

    if all((i, 4 - i) in marked_positions for i in range(5)):
        return True

    return False

# Example usage:
if __name__ == "__main__":
    bingo_card = [
        [1, 2, 3, 4, 5],
        [6, 7, 8, 9, 10],
        [11, 12, 13, 14, 15],
        [16, 17, 18, 19, 20],
        [21, 22, 23, 24, 25]
    ]
    marked_positions = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
    print(check_bingo(bingo_card, marked_positions))  # Output: True
