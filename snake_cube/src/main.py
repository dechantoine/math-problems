import numpy as np
import json
import logging

from params import cubes_lines, directions, first_cube_positions
from functions import index_sorted_cube, next_cube_possible_positions, next_line_possible_ranges, solve_conflicts, define_next_grids, return_unique_grids_symmetry


logging.basicConfig(filename='./tree_explore.log', encoding='utf-8', level=logging.INFO)

def explore(dict_tree):
    for key in [b for b in dict_tree.keys() if isinstance(b, int)]:
        current_grid = np.array(dict_tree[key]["grid"])
        previous_line_direction = np.array(dict_tree[key]["previous_line_direction"])
        k = dict_tree[key]["depth"]
        previous_line_length = len(cubes_lines[k])

        # stop condition
        if k < 30 :

            next_cube_possible_pos = next_cube_possible_positions(current_grid,
                                                                  previous_line_direction,
                                                                  previous_line_length)

            next_line_possible_rgs = next_line_possible_ranges(current_grid,
                                                               next_cube_possible_pos,
                                                               cubes_lines[k+1])

            next_line_solved_rgs = solve_conflicts(current_grid,
                                                   next_line_possible_rgs)

            if len(next_line_solved_rgs) > 0:

                next_grids = define_next_grids(current_grid,
                                               next_line_solved_rgs,
                                               cubes_lines[k+1])

                next_grids_cleaned = return_unique_grids_symmetry(next_grids)

                for j in range(len(next_grids_cleaned)):
                    dict_tree[key][j]= {"id": dict_tree[key]["id"] + str(j),
                                        "grid" : next_grids_cleaned[j].tolist(),
                                        "status" : "on"}

                    index_before_last_cube, index_last_cube = index_sorted_cube(next_grids_cleaned[j])[-2:]
                    dict_tree[key][j]["previous_line_direction"] = (index_last_cube - index_before_last_cube).tolist()

                    dict_tree[key][j]["depth"] = k+1

                explore(dict_tree[key])

            else :
                #dict_tree[key]["status"] = "off"
                # if no next solution is found for this grid, delete the branch
                logging.info(f'Branch {dict_tree[key]["id"]} : No correct solution for this branch, deleting branch')
                del dict_tree[key]

    # if every below branch is off, it means this branch need to be deleted
    for key in [b for b in dict_tree.keys() if isinstance(b, int)]:
        if dict_tree[key]["status"] == "off":
            logging.info(f'Branch {dict_tree[key]["id"]} : Branch status if off, deleting branch')
            del dict_tree[key]

    # if there is no more branch below, this branch is off and will be deleted in previous call
    if len([b for b in dict_tree.keys() if isinstance(b, int)])==0:
        logging.info(f'Branch {dict_tree["id"]} : No below branch, setting branch status to off')
        dict_tree["status"] : "off"

if __name__ == '__main__':
    tree = dict()

    # initialize the tree with the 4 first grids
    for j in range(len(first_cube_positions)):
        # initiate the 4*4*4 grid
        k = 0
        grid_puzzle = np.zeros(shape=[4] * 3, dtype=int)

        # place first cube
        grid_puzzle[tuple(first_cube_positions[j])] = cubes_lines[k][0]
        tree[j] = {"id" : str(j),
                   "grid": grid_puzzle.tolist(),
                   "status": "going"}

        tree[j]["previous_line_direction"] = [0, 0, 1]

        tree[j]["depth"] = k

    # explore the tree recursively
    explore(tree)

    # save the tree in a json file
    with open('./tree.json', 'w') as fp:
        json.dump(tree, fp, indent=2)

