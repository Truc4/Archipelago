import random
from typing import List
from BaseClasses import MultiWorld

def generate_bingo_board(multiworld: MultiWorld, player_id: int) -> List[List[str]]:
    """
    Generate a 5x5 Bingo board from the location checks of the given player in the MultiWorld instance.

    :param multiworld: MultiWorld instance containing the game worlds and locations.
    :param player_id: ID of the player for whom to generate the Bingo board.
    :return: 2D list representing the Bingo board.
    """
    location_checks = [location.name for location in multiworld.get_locations(player_id)]
    # print(f"Location checks for player {player_id}: {location_checks}")

    if len(location_checks) < 25:
        raise ValueError("Not enough location checks to generate a Bingo board.")

    selected_checks = random.sample(location_checks, 25)
    # print(f"Selected location checks for Bingo board: {selected_checks}")

    bingo_board = [selected_checks[i:i + 5] for i in range(0, 25, 5)]
    return bingo_board

# Example usage:
if __name__ == "__main__":
    # Assuming `multiworld` is an instance of MultiWorld and `player_id` is the ID of the player
    # multiworld = ...
    # player_id = ...
    # bingo_board = generate_bingo_board(multiworld, player_id)
    # for row in bingo_board:
    #     print(row)
    pass
