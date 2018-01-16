import os
import time

ship_requirement = 20
damage_requirement = 1250
GAMES_TO_PLAY = 10


def get_ships(data):
    return int(data.split("producing ")[1].split(" ships")[0])


def get_damage(data):
    return int(data.split("dealing ")[1].split(" damage")[0])


def get_rank(data):
    return int(data.split("rank #")[1].split(" and")[0])


player_1_wins = 0
player_2_wins = 0

damage_player_1 = []
ships_player_1 = []
damage_player_2 = []
ships_player_2 = []

with open('ship_label_all.txt', 'a') as f:
    f.write('attack_ship,mine_own_planet,mine_empty_planet\n')

with open('ship_data_all.txt', 'a') as f:
    f.write('n_all_ships,n_own_ships,n_all_planets,p_owned_planets,p_owned_ships,n_undocked,n_docking,'
            ' n_docked,n_undocking,dist_nearest_empty_planet,dist_nearest_own_ship,dist_nearest_enemy_ship\n',)

for num in range(GAMES_TO_PLAY):
    try:
        print("Currently on: {}".format(num))
        if player_1_wins > 0 or player_2_wins > 0:
            p1_pct = round(player_1_wins / (player_1_wins + player_2_wins) * 100.0, 2)
            p2_pct = round(player_2_wins / (player_1_wins + player_2_wins) * 100.0, 2)
            print("Player 1 win: {}%; Player 2 win: {}%.".format(p1_pct, p2_pct))

        open('data.gameout', 'w').close()
        os.system('./halite -d "240 160" "python3 MyBot.py" "python3 MyBot-2.py" >> data.gameout')

        with open('data.gameout', 'r') as f:
            contents = f.readlines()
            shafouBot1 = contents[-2]
            shafouBot2 = contents[-1]
            print(shafouBot1)
            print(shafouBot2)

            shafouBot1_ships = get_ships(shafouBot1)
            ships_player_1.append(shafouBot1_ships)
            shafouBot1_dmg = get_damage(shafouBot1)
            damage_player_1.append(shafouBot1_dmg)
            shafouBot1_rank = get_rank(shafouBot1)

            shafouBot2_ships = get_ships(shafouBot2)
            ships_player_2.append(shafouBot2_ships)
            shafouBot2_dmg = get_damage(shafouBot2)
            damage_player_2.append(shafouBot2_dmg)
            shafouBot2_rank = get_rank(shafouBot2)

            print("shafouBot1 rank: {} ships: {} dmg: {}".format(shafouBot1_rank, shafouBot1_ships, shafouBot1_dmg))
            print("shafouBot2 rank: {} ships: {} dmg: {}".format(shafouBot2_rank, shafouBot2_ships, shafouBot2_dmg))

        if shafouBot1_rank == 1:
            print("shafouBot-1 won")
            player_1_wins += 1
            if shafouBot1_ships >= ship_requirement and shafouBot1_dmg >= damage_requirement:
                with open("ship_data1.txt", "r") as f:
                    input_lines = f.readlines()
                with open("ship_data_all.txt", "a") as f:
                    for l in input_lines:
                        f.write(l)

                with open("ship_label1.txt", "r") as f:
                    output_lines = f.readlines()
                with open("ship_label_all.txt", "a") as f:
                    for l in output_lines:
                        f.write(l)

        elif shafouBot2_rank == 1:
            print("shafouBot-2 won")
            player_2_wins += 1
            if shafouBot2_ships >= ship_requirement and shafouBot2_dmg >= damage_requirement:
                with open("ship_data2.txt", "r") as f:
                    input_lines = f.readlines()

                with open("ship_label2.txt", "r") as f:
                    output_lines = f.readlines()

                if len(input_lines) == len(output_lines):
                    with open("ship_data_all.txt", "a") as f:
                        for l in input_lines:
                            f.write(l)
                    with open("ship_label_all.txt", "a") as f:
                        for l in output_lines:
                            f.write(l)

        #time.sleep(2)
    except Exception as e:
        print(str(e))
        time.sleep(2)

mean_damage_player1 = sum(damage_player_1) / len(damage_player_1)
print('Mean damage player1: {}'. format(mean_damage_player1))

mean_damage_player2 = sum(damage_player_2) / len(damage_player_2)
print('Mean damage player2: {}'. format(mean_damage_player2))

mean_ships_player1 = sum(ships_player_1) / len(ships_player_1)
print('Mean ships player1: {}'. format(mean_ships_player1))

mean_ships_player2 = sum(ships_player_2) / len(ships_player_2)
print('Mean ships player2: {}'. format(mean_ships_player2))
