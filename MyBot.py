"""
Welcome to your first Halite-II bot!

This bot's name is Settler. It's purpose is simple (don't expect it to win complex games :) ):
1. Initialize game
2. If a ship is not docked and there are unowned planets
2.a. Try to Dock in the planet if close enough
2.b If not, go towards the planet

Note: Please do not place print statements here as they are used to communicate with the Halite engine. If you need
to log anything use the logging module.
"""
# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
from collections import OrderedDict
import random

import hlt
# Then let's import the logging module so we can print out information
import logging
import numpy as np
import os
import sys

with open(os.devnull, 'w') as sys.stderr:
    import keras
    import tensorflow as tf
    from keras.models import load_model
    import h5py


VERSION = 1

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
BOT_NAME = 'ShafouBot-{}'.format(VERSION)
game = hlt.Game(BOT_NAME)
logging.info("Starting {}!".format(BOT_NAME))
# Then we print our start message to the logs
logging.info("Starting my Settler bot!")

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '99'
tf.logging.set_verbosity(tf.logging.ERROR)

NAN_VALUE = -99999
RANDOMNESS = 0
N_COLUMNS = 12
N_SHIPS_TO_TRACK = 20
N_COLUMNS_LABEL = 3

# Reset Data Files
open('ship_data{}.txt'.format(VERSION), 'w').close()
open('ship_label{}.txt'.format(VERSION), 'w').close()

model = load_model('/Users/Shafou/Documents/halite/My_Bot/data/nn.h5')


def attack_nearest_enemy_ship():
    """
    Attack nearest enemy ship
    """
    navigate_command = ship.navigate(
        ship.closest_point_to(closest_enemy_ships[0]),
        game_map,
        speed=int(hlt.constants.MAX_SPEED),
        ignore_ships=False)

    if navigate_command:
        command_queue.append(navigate_command)


def distance_nearest_empty_planet():
    """
    Calculate distance between ship and nearest empty planet
    :return: Distance between ship and nearest empty planet
    """
    closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if
                             isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and not
                             entities_by_distance[distance][0].is_owned()]
    if len(closest_empty_planets) > 0:
        return closest_empty_planets[0].calculate_distance_between(ship)
    else:
        return NAN_VALUE


def distance_nearest_enemy_ship():
    """
    Calculate distance between ship and nearest enemy ship
    :return: Distance between ship and nearest enemy ship
    """
    enemy_ships = []
    for s in all_ships:
        if s.owner != player_id:
            enemy_ships.append(s)
    closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if
                           isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and
                           entities_by_distance[distance][0] not in enemy_ships]
    if len(closest_enemy_ships) > 0:
        return closest_enemy_ships[0].calculate_distance_between(ship)
    else:
        return NAN_VALUE


def distance_nearest_own_ship():
    """
    Calculate distance between ship and nearest own ship
    :return: Distance between ship and nearest own ship
    """
    closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if
                           isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and
                           entities_by_distance[distance][0] not in own_ships]
    if len(closest_enemy_ships) > 0:
        return closest_enemy_ships[0].calculate_distance_between(ship)
    else:
        return NAN_VALUE


def n_own_and_not_own_planets(planets):
    """
    Calculates the number of owned and not owned planets by the planet owner
    :param planets: All planets on the map
    :return: Number of owned and not owned planets
    """
    n_own_planets = 0
    n_not_own_planets = 0
    for planet in planets:
        if planet.owner == player_id:
            n_own_planets += 1
        else:
            n_not_own_planets += 1
    return n_own_planets, n_not_own_planets


def n_own_and_not_own_ships(ships):
    """
    Calculates the number of owned and not owned ships by the ship owner
    :param ships: All ships on the map
    :return: Number of owned and not owned ships
    """
    n_owned_ship = 0
    n_not_owned_ship = 0
    for ship in ships:
        if ship.owner == player_id:
            n_owned_ship += 1
        else:
            n_not_owned_ship += 1
    return n_owned_ship, n_not_owned_ship


def get_ships_status(ships):
    """
    Calculates the number of ships in specific docking states
    :param ships: All ships
    :return: Docking state of ships
    """
    n_undocked = 0
    n_docking = 0
    n_docked = 0
    n_undocking = 0
    for ship in ships:
        if ship.docking_status == ship.DockingStatus.UNDOCKED:
            n_undocked += 1
        elif ship.docking_status == ship.DockingStatus.DOCKING:
            n_docking += 1
        elif ship.docking_status == ship.DockingStatus.DOCKED:
            n_docked += 1
        elif ship.docking_status == ship.DockingStatus.UNDOCKING:
            n_undocking += 1
    return n_undocked, n_docking, n_docked, n_undocking


def pct_owned_planets(planets):
    """
    Calculates the percentage of planets that are owned
    :param planets: All planets on the map
    :return: Percentage of ships that are owned
    """
    n_owned_planets, _ = n_own_and_not_own_planets(planets)
    return float(n_owned_planets) / float(len(planets))


def pct_owned_ships(ships):
    """
    Calculates the percentage of ships that are owned
    :param ships: All ships on the map
    :return: Percentage of ships that are owned
    """
    n_owned_ships, _ = n_own_and_not_own_ships(ships)
    return float(n_owned_ships) / float(len(ships))

n_turn = 0
all_ships_data = []

while True:
    # TURN START
    logging.info('------- TURN {} START -------'.format(n_turn))
    game_map = game.update_map()

    player_id = game_map.get_me()

    command_queue = []
    planned_ships = []

    ship_counter = 0
    # FOR EVERY SHIP
    for ship in game_map.get_me().all_ships():

        ship_counter += 1

        if ship_counter < N_SHIPS_TO_TRACK:

            all_ships = game_map._all_ships()
            n_all_ships = len(all_ships)
            own_ships = game_map.get_me().all_ships()
            n_own_ships = len(own_ships)
            all_planets = game_map.all_planets()
            n_all_planets = len(all_planets)

            entities_by_distance = game_map.nearby_entities_by_distance(ship)
            entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

            closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if
                                   isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and
                                   entities_by_distance[distance][0] not in own_ships]
            closest_own_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if
                                   isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and
                                   entities_by_distance[distance][0].is_owned() and (
                                       entities_by_distance[distance][0].owner.id == game_map.get_me().id)]
            closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if
                                     isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and not
                                     entities_by_distance[distance][0].is_owned()]

            # PCT OF OWNED PLANETS
            p_owned_planets = pct_owned_planets(all_planets)
            # PCT OF OWNED SHIPS
            p_owned_ships = pct_owned_ships(all_ships)
            # SHIPS DOCKING STATUS
            n_undocked, n_docking, n_docked, n_undocking = get_ships_status(all_ships)
            # DISTANCE NEAREST EMPTY PLANET
            dist_nearest_empty_planet = distance_nearest_empty_planet()
            # DISTANCE NEAREST OWN SHIP
            dist_nearest_own_ship = distance_nearest_own_ship()
            # DISTANCE NEAREST ENEMY SHIP
            dist_nearest_enemy_ship = distance_nearest_enemy_ship()

            ship_data_array = [n_all_ships, n_own_ships, n_all_planets, p_owned_planets, p_owned_ships,
                               n_undocked, n_docking, n_docked, n_undocking, dist_nearest_empty_planet,
                               dist_nearest_own_ship, dist_nearest_enemy_ship]

            # with open(os.devnull, 'w') as sys.stderr:
            #     import numpy as np
            np_ship_data = np.array(ship_data_array)
            #
            np_ship_data = np_ship_data.reshape(1, 12)

            command = model.predict(np_ship_data)
            command = np.argmax(command)

            r = random.randint(0, 101)
            if r < RANDOMNESS:
                command = random.randint(0, 3)

            for planet in game_map.all_planets():

                if ship in planned_ships:
                    continue

                if ship.docking_status != ship.DockingStatus.UNDOCKED:
                    continue

                """
                Attack closest enemy ship
                """
                if command == 0:
                    if not isinstance(closest_enemy_ships[0], int):
                        navigate_command = ship.navigate(
                            ship.closest_point_to(closest_enemy_ships[0]),
                            game_map,
                            speed=int(hlt.constants.MAX_SPEED),
                            ignore_ships=False)

                        if navigate_command and ship not in planned_ships:
                            command_queue.append(navigate_command)
                            planned_ships.append(ship)
                elif command == 1:  # Mine closest already owned planet
                    try:
                        if not isinstance(closest_own_planets[0], int):
                            target = closest_own_planets[0]
                            if len(target._docked_ship_ids) < target.num_docking_spots:
                                if ship.can_dock(target) and ship not in planned_ships:
                                    command_queue.append(ship.dock(target))
                                    planned_ships.append(ship)
                                else:
                                    navigate_command = ship.navigate(
                                        ship.closest_point_to(target),
                                        game_map,
                                        speed=int(hlt.constants.MAX_SPEED),
                                        ignore_ships=False)

                                    if navigate_command and ship not in planned_ships:
                                        command_queue.append(navigate_command)
                                        planned_ships.append(ship)
                    except Exception:
                        # attack closest enemy ship
                        if not isinstance(closest_enemy_ships[0], int):
                            navigate_command = ship.navigate(
                                ship.closest_point_to(closest_enemy_ships[0]),
                                game_map,
                                speed=int(hlt.constants.MAX_SPEED),
                                ignore_ships=False)

                            if navigate_command and ship not in planned_ships:
                                command_queue.append(navigate_command)
                                planned_ships.append(ship)
                        elif not isinstance(closest_empty_planets[0], int):  # Go to closest empty planet
                            target = closest_empty_planets[0]
                            if ship.can_dock(target) and ship not in planned_ships:
                                command_queue.append(ship.dock(target))
                                planned_ships.append(ship)
                            else:
                                navigate_command = ship.navigate(
                                    ship.closest_point_to(target),
                                    game_map,
                                    speed=int(hlt.constants.MAX_SPEED),
                                    ignore_ships=False)

                                if navigate_command and ship not in planned_ships:
                                    command_queue.append(navigate_command)
                                    planned_ships.append(ship)
                        elif not isinstance(closest_enemy_ships[0], int):  # attack closest enemy ship
                            navigate_command = ship.navigate(
                                ship.closest_point_to(closest_enemy_ships[0]),
                                game_map,
                                speed=int(hlt.constants.MAX_SPEED),
                                ignore_ships=False)

                            if navigate_command and ship not in planned_ships:
                                command_queue.append(navigate_command)
                                planned_ships.append(ship)
                # FIND AND MINE AN EMPTY PLANET #
                elif command == 2:
                    '''
                    type: 2
                    Mine an empty planet.
                     '''
                    try:
                        if not isinstance(closest_empty_planets[0], int):
                            target = closest_empty_planets[0]

                            if ship.can_dock(target) and ship not in planned_ships:
                                command_queue.append(ship.dock(target))
                                planned_ships.append(ship)
                            else:
                                navigate_command = ship.navigate(
                                    ship.closest_point_to(target),
                                    game_map,
                                    speed=int(hlt.constants.MAX_SPEED),
                                    ignore_ships=False)

                                if navigate_command and ship not in planned_ships:
                                    command_queue.append(navigate_command)
                                    planned_ships.append(ship)
                    except Exception:
                        # attack!
                        if not isinstance(closest_enemy_ships[0], int):
                            navigate_command = ship.navigate(
                                ship.closest_point_to(closest_enemy_ships[0]),
                                game_map,
                                speed=int(hlt.constants.MAX_SPEED),
                                ignore_ships=False)

                            if navigate_command and ship not in planned_ships:
                                command_queue.append(navigate_command)
                                planned_ships.append(ship)

            ship_data_string = ''
            counter = 0
            for s in ship_data_array:
                ship_data_string += str(s)
                if counter < N_COLUMNS - 1:
                    ship_data_string += ','
                    counter += 1

            with open('ship_data{}.txt'.format(VERSION), 'a') as f:
                f.writelines(ship_data_string + '\n')

            command_one_hot = [0, 0, 0]
            if command == 0:
                command_one_hot[0] = 1
            elif command == 1:
                command_one_hot[1] = 1
            elif command == 2:
                command_one_hot[2] = 1

            counter = 0
            command_label_string = ''
            for i in command_one_hot:
                command_label_string += str(i)
                if counter < N_COLUMNS_LABEL - 1:
                    command_label_string += ','
                    counter += 1

            with open('ship_label{}.txt'.format(VERSION), 'a') as f:
                f.writelines(command_label_string + '\n')
        else:
            own_ships = game_map.get_me().all_ships()
            entities_by_distance = game_map.nearby_entities_by_distance(ship)
            entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

            closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if
                                   isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and
                                   entities_by_distance[distance][0] not in own_ships]
            attack_nearest_enemy_ship()

    # Send our set of commands to the Halite engine for this turn
    game.send_command_queue(command_queue)
    n_turn += 1
    # TURN END

# GAME END
