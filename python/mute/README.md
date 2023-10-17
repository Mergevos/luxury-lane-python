# mute module

The 'mute' module provides functionality for muting and unmuting players in game. It contains commands and a system function to manage player mutes.

## Contents

1. [Commands](#commands)
2. [System Function](#system-function)

## Commands

### `mute` command

The `mute` command allows administrators to mute players in the game. It provides options to specify the mute duration and type. Players can be muted indefinitely or for a specified period in hours, days, or months.

#### Usage

```python
/mute [player_id] [duration = 0] [option = -1]
```

- `player_id`: The ID of the player to mute.
- `duration`: The mute duration (0 for permanent).
- `option`: The mute option (-1: forever, 0: hours, 1: days, 2: months).

### `unmute` command

The `unmute` command allows administrators to unmute previously muted players. It removes the mute status from a player's account and updates the database accordingly.

#### Usage

```python
/unmute [player_id]
```

- `player_id`: The ID of the player to unmute.

## System Function

### `check_for_unmute` Function

The `check_for_unmute` function is a system function that periodically checks for players with expired mute durations. When a player's mute duration has passed, the function automatically unmutes the player by deleting the mute record from the database.

This function ensures that players are unmuted once their mute duration expires.

## Usage

The 'mute' module is designed to be used within a game environment to manage player mutes. Administrators can use the provided commands to mute and unmute players as needed.

To automate the process of unmuting players with expired mute durations, the 'check_for_unmute' function is called periodically when the game mode is initialized.

For detailed information on how to use the commands and the system function, refer to the individual function documentation in the module's source code.

## Author

- [Mergevos](https://github.com/Mergevos)

## License

- [MIT License](https://github.com/Mergevos/luxury-lane-python/blob/master/LICENSE)

---

[Back to Top](#mute-module)
