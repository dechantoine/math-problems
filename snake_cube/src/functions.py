import numpy as np
from params import cubes_lines, directions, symmetries
# get index of the last placed cube (x,y,z)
def index_sorted_cube(grid):
    return np.array(np.unravel_index(np.argsort(grid.flat), grid.shape)).T


def next_cube_possible_positions(grid, previous_line_dir, previous_line_len):
    argmax_index = index_sorted_cube(grid)[-1]
    # list of the directly adjacent positions from the last placed cube not in the direction of the previous line
    if previous_line_len > 1 :
        next_cube_possible_pos = argmax_index + directions[(directions!=previous_line_dir).any(axis=1) &
                                                       (directions!=-previous_line_dir).any(axis=1)]
    else:
        next_cube_possible_pos = np.array([argmax_index + previous_line_dir])

    # keep only those inside the 4*4*4 grid boundaries
    next_cube_possible_pos = next_cube_possible_pos[(next_cube_possible_pos.max(axis=1)<=3)
                                                    & (next_cube_possible_pos.min(axis=1)>=0),:]
    return next_cube_possible_pos


def next_line_possible_ranges(grid, next_cube_possible_pos, line):
    argmax_index = index_sorted_cube(grid)[-1]
    # list all possible directions for next line
    next_line_possible_directions = np.array([directions[(directions!=(next_cube_possible_pos[i]
                                                                       - argmax_index)).any(axis=1) &
                                                         (directions!=-(next_cube_possible_pos[i]
                                                                        - argmax_index)).any(axis=1)]
                                              for i in range(len(next_cube_possible_pos))])

    # list possible ranges for next line
    if len(next_line_possible_directions)>0 and len(next_cube_possible_pos)>0 :
        next_line_possible_ranges = np.concatenate([np.moveaxis(np.array([next_cube_possible_pos[j] +
                                                                          (next_line_possible_directions[j])*i
                                                                          for i in range(len(line))]),1,0)
                                                    for j in range(len(next_cube_possible_pos))])

        # keep only unique - useful only if line = 1 cube
        next_line_possible_ranges = np.unique(next_line_possible_ranges, axis=0)

        # keep only those inside the 4*4*4 grid boundaries
        next_line_possible_ranges = next_line_possible_ranges[(next_line_possible_ranges.max(axis=(1,2))<=3) &
                                                              (next_line_possible_ranges.min(axis=(1,2))>=0)]

    else :
        next_line_possible_ranges = np.array([])

    return next_line_possible_ranges


def solve_conflicts(grid, next_line_possible_rang):
    # inspecting each range occupation on grid and keeping only those not conflicting already placed cubes
    next_line_solved = next_line_possible_rang[[grid[tuple(next_line_possible_rang[i].T.reshape(3,-1))].max()==0
                                                for i in range(len(next_line_possible_rang))]]
    return next_line_solved


def define_next_grids(grid, next_line_solved, line):
    # define next grids
    next_grids = np.tile(grid, (len(next_line_solved),1,1,1))
    for i in range(len(next_line_solved)):
        next_grids[i][tuple(next_line_solved[i].T.reshape(3,-1))] = line
    return next_grids


def return_unique_grids_symmetry(grids):
    grids_symmetries = np.concatenate([np.array([np.flip(grids[j], axis=s)
                                                 for s in symmetries])
                                       for j in range(len(grids))], axis=0)
    new_grids = grids.copy()
    for i in range(len(grids)):
        if (grids[i]==grids_symmetries).all((1,2,3)).any():
            new_grids = np.delete(new_grids,i,0)
            grids_symmetries = np.delete(grids_symmetries,list(range(i*6,(i+1)*6)),0)
    return new_grids