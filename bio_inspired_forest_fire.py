# Name: forest_fire
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
import numpy as np
import math
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, randomise2d
import capyle.utils as utils


def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "forest_fire"
    config.dimensions = 2
    config.states = (1, 2, 3, 4, 5, 6, 7)
    config.num_generations = 1000
    #chaparral = 1
    #dense forest = 2
    #lake = 3
    #canyon = 4
    #town = 5
    #fire = 6
    #burnt = 7
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    # config.state_colors = [(0,0,0),(1,1,1)]
    config.grid_dims = (50,50)
    config.state_colors = [(0,0.6,0.1),(0,0.2,0),(0,0,1),(0.5,0.5,0.5),(0.3,0.3,0.3),(1,0,0),(0,0,0)]
    config.wrap = False
    config.initial_grid = np.full((50,50),1)
    for i in range(10,15):
        for j in range(5,15):
            config.initial_grid[i][j] = 3
    for i in range(30,40):
        for j in range(15,25):
            config.initial_grid[i][j] = 2
    for i in range(5,35):
        for j in range(32,35):
            config.initial_grid[i][j] = 4
    for j in range(0,3):
        config.initial_grid[49][j] = 5
    config.initial_grid[0][49] = 6
    config.initial_grid[0][0] = 6

    # ----------------------------------------------------------------------
    # the GUI calls this to pass the user defined config
    # into the main system with an extra argument
    # do not change
    if len(args) == 2:
        config.save()
        sys.exit()
    return config


def transition_function(grid, neighbourstates, neighbourcounts, fire_chance_chap,
                        fire_chance_df, fire_chance_canyon, burnt_up_chap, 
                        burnt_up_df, burnt_up_canyon, wind):
    """Function to apply the transition rules
    and return the new grid"""
    chaparral, dense_forest, lake, canyon, town, fire, burnt = neighbourcounts
    
    N, E, S, W, NE, NW, SE, SW = neighbourstates
    
    chaparral = (grid == 1)
    dense_forest = (grid == 2)
    lake = (grid == 3)
    canyon = (grid == 4)
    
    fire_neighbour = (fire > 0)
    
    #chaparral
    chaparral_fire = chaparral & fire_neighbour
    fire_chance_chap[chaparral_fire] += 1
    chap_on_fire = (fire_chance_chap > 10)
    burnt_up_chap[chap_on_fire] -= 1
    chap_burnt_out = (burnt_up_chap < 70)
    grid[chap_on_fire] = 6
    grid[chap_burnt_out] = 7
    
    #dense forest
    dense_forest_fire = dense_forest & fire_neighbour
    fire_chance_df[dense_forest_fire] += 1
    df_on_fire = (fire_chance_df > 30)
    burnt_up_df[df_on_fire] -= 1
    df_burnt_out = (burnt_up_df < 10)
    grid[df_on_fire] = 6
    grid[df_burnt_out] = 7
    
    #canyon
    canyon_fire = canyon & fire_neighbour
    fire_chance_canyon[canyon_fire] += 1
    canyon_on_fire = (fire_chance_canyon > 1)
    burnt_up_canyon[canyon_on_fire] -= 1
    canyon_burnt_out = (burnt_up_canyon < 97)
    grid[canyon_on_fire] = 6
    grid[canyon_burnt_out] = 7
    
    #need to vary the interaction between fire and environment now to
    #suit how quickly everything burns.
    
    #wind direction
    #value stored in 'wind' giving the direction based on number like keypad
    #       NW , N , NE     7,  8,  9
    #       W ,    ,  E     4,   ,  6
    #       SW,  S , SE     1,  2,  3
    #
    
    wind_direction = 4
    if (wind_direction == 8):
        s_fire = (S==6) & chaparral_fire
        fire_chance_chap[s_fire] += 2
        se_fire = (SE==6) & chaparral_fire
        fire_chance_chap[se_fire] += 2*math.sin(math.pi/4)
        sw_fire = (SW==6) & chaparral_fire
        fire_chance_chap[sw_fire] += 2*math.sin(math.pi/4)
        
        s_fire_df = (S==6) & dense_forest_fire
        fire_chance_df[s_fire_df] +=2
        se_fire_df = (SE==6) & dense_forest_fire
        fire_chance_df[se_fire_df] += 2*math.sin(math.pi/4)
        sw_fire_df = (SW==6) & dense_forest_fire
        fire_chance_df[sw_fire_df] += 2*math.sin(math.pi/4)
        
        s_fire_c = (S==6) & canyon_fire
        fire_chance_canyon[s_fire_c] +=2
        se_fire_c = (SE==6) & canyon_fire
        fire_chance_canyon[se_fire_c] += 2*math.sin(math.pi/4)
        sw_fire_c = (SW==6) & canyon_fire
        fire_chance_canyon[sw_fire_c] += 2*math.sin(math.pi/4)
        
    if (wind_direction == 9):
        sw_fire = (SW==6) & chaparral_fire
        fire_chance_chap[sw_fire] += 2
        w_fire = (W==6) & chaparral_fire
        fire_chance_chap[w_fire] += 2*math.sin(math.pi/4)
        s_fire = (S==6) & chaparral_fire
        fire_chance_chap[s_fire] += 2*math.sin(math.pi/4)
        
        sw_fire_df = (SW==6) & dense_forest_fire
        fire_chance_df[sw_fire_df] += 2
        w_fire_df = (W==6) & dense_forest_fire
        fire_chance_df[w_fire_df] += 2*math.sin(math.pi/4)
        s_fire_df = (S==6) & dense_forest_fire
        fire_chance_df[s_fire_df] += 2*math.sin(math.pi/4)
        
        sw_fire_c = (SW==6) & canyon_fire
        fire_chance_canyon[sw_fire_c] += 2
        w_fire_c = (W==6) & canyon_fire
        fire_chance_canyon[w_fire_c] += 2*math.sin(math.pi/4)
        s_fire_c = (S==6) & canyon_fire
        fire_chance_canyon[s_fire_c] += 2*math.sin(math.pi/4)
        
    if (wind_direction == 7):
        se_fire = (SE==6) & chaparral_fire
        fire_chance_chap[se_fire] += 2
        e_fire = (E==6) & chaparral_fire
        fire_chance_chap[e_fire] += 2*math.sin(math.pi/4)
        s_fire = (S==6) & chaparral_fire
        fire_chance_chap[s_fire] += 2*math.sin(math.pi/4)
        
        se_fire_df = (SE==6) & dense_forest_fire
        fire_chance_df[se_fire_df] += 2
        e_fire_df = (E==6) & dense_forest_fire
        fire_chance_df[e_fire_df] += 2*math.sin(math.pi/4)
        s_fire_df = (S==6) & dense_forest_fire
        fire_chance_df[s_fire_df] += 2*math.sin(math.pi/4)
        
        se_fire_c = (SE==6) & canyon_fire
        fire_chance_canyon[se_fire_c] += 2
        e_fire_c = (E==6) & canyon_fire
        fire_chance_canyon[e_fire_c] += 2*math.sin(math.pi/4)
        s_fire_c = (S==6) & canyon_fire
        fire_chance_canyon[s_fire_c] += 2*math.sin(math.pi/4)
        
    if (wind_direction == 6):
        w_fire = (W==6) & chaparral_fire
        fire_chance_chap[w_fire] += 2
        nw_fire = (NW==6) & chaparral_fire
        fire_chance_chap[nw_fire] += 2*math.sin(math.pi/4)
        sw_fire = (SW==6) & chaparral_fire
        fire_chance_chap[sw_fire] += 2*math.sin(math.pi/4)
        
        w_fire_df = (W==6) & dense_forest_fire
        fire_chance_df[w_fire_df] += 2
        nw_fire_df = (NW==6) & dense_forest_fire
        fire_chance_df[nw_fire_df] += 2*math.sin(math.pi/4)
        sw_fire_df = (SW==6) & dense_forest_fire
        fire_chance_df[sw_fire_df] += 2*math.sin(math.pi/4)
        
        w_fire_c = (W==6) & canyon_fire
        fire_chance_canyon[w_fire_c] += 2
        nw_fire_c = (NW==6) & canyon_fire
        fire_chance_canyon[nw_fire_c] += 2*math.sin(math.pi/4)
        sw_fire_c = (SW==6) & canyon_fire
        fire_chance_canyon[sw_fire_c] += 2*math.sin(math.pi/4)
        
    if (wind_direction == 4):
        e_fire = (E==6) & chaparral_fire
        fire_chance_chap[e_fire] += 2
        ne_fire = (NE==6) & chaparral_fire
        fire_chance_chap[ne_fire] += 2*math.sin(math.pi/4)
        se_fire = (SE==6) & chaparral_fire
        fire_chance_chap[se_fire] += 2*math.sin(math.pi/4)
        
        e_fire_df = (E==6) & dense_forest_fire
        fire_chance_df[e_fire_df] += 2
        ne_fire_df = (NE==6) & dense_forest_fire
        fire_chance_df[ne_fire_df] += 2*math.sin(math.pi/4)
        se_fire_df = (SE==6) & dense_forest_fire
        fire_chance_df[se_fire_df] += 2*math.sin(math.pi/4)
        
        e_fire_c = (E==6) & canyon_fire
        fire_chance_canyon[e_fire_c] += 2
        ne_fire_c = (NE==6) & canyon_fire
        fire_chance_canyon[ne_fire_c] += 2*math.sin(math.pi/4)
        se_fire_c = (SE==6) & canyon_fire
        fire_chance_canyon[se_fire_c] += 2*math.sin(math.pi/4)
        
    if (wind_direction == 2):
        n_fire = (N==6) & chaparral_fire
        fire_chance_chap[n_fire] += 2
        ne_fire = (NE==6) & chaparral_fire
        fire_chance_chap[ne_fire] += 2*math.sin(math.pi/4)
        nw_fire = (NW==6) & chaparral_fire
        fire_chance_chap[nw_fire] += 2*math.sin(math.pi/4)
        
        n_fire_df = (N==6) & dense_forest_fire
        fire_chance_df[n_fire_df] += 2
        ne_fire_df = (NE==6) & dense_forest_fire
        fire_chance_df[ne_fire_df] += 2*math.sin(math.pi/4)
        nw_fire_df = (NW==6) & dense_forest_fire
        fire_chance_df[nw_fire_df] += 2*math.sin(math.pi/4)
        
        n_fire_c = (N==6) & canyon_fire
        fire_chance_canyon[n_fire_c] += 2
        ne_fire_c = (NE==6) & canyon_fire
        fire_chance_canyon[ne_fire_c] += 2*math.sin(math.pi/4)
        nw_fire_c = (NW==6) & canyon_fire
        fire_chance_canyon[nw_fire_c] += 2*math.sin(math.pi/4)
        
    if (wind_direction == 3):
        nw_fire = (NW==6) & chaparral_fire
        fire_chance_chap[nw_fire] += 2
        w_fire = (W==6) & chaparral_fire
        fire_chance_chap[w_fire] += 2*math.sin(math.pi/4)
        n_fire = (N==6) & chaparral_fire
        fire_chance_chap[n_fire] += 2*math.sin(math.pi/4)
        
        nw_fire_df = (NW==6) & dense_forest_fire
        fire_chance_df[nw_fire_df] += 2
        w_fire_df = (W==6) & dense_forest_fire
        fire_chance_df[w_fire_df] += 2*math.sin(math.pi/4)
        n_fire_df = (N==6) & dense_forest_fire
        fire_chance_df[n_fire_df] += 2*math.sin(math.pi/4)
        
        nw_fire_c = (NW==6) & canyon_fire
        fire_chance_canyon[nw_fire_c] += 2
        w_fire_c = (W==6) & canyon_fire
        fire_chance_canyon[w_fire_c] += 2*math.sin(math.pi/4)
        n_fire_c = (N==6) & canyon_fire
        fire_chance_canyon[n_fire_c] += 2*math.sin(math.pi/4)
        
    if (wind_direction == 1):
        ne_fire = (NE==6) & chaparral_fire
        fire_chance_chap[ne_fire] += 2
        n_fire = (N==6) & chaparral_fire
        fire_chance_chap[n_fire] += 2*math.sin(math.pi/4)
        e_fire = (E==6) & chaparral_fire
        fire_chance_chap[e_fire] += 2*math.sin(math.pi/4)
        
        ne_fire_df = (NE==6) & dense_forest_fire
        fire_chance_df[ne_fire_df] += 2
        n_fire_df = (N==6) & dense_forest_fire
        fire_chance_df[n_fire_df] += 2*math.sin(math.pi/4)
        e_fire_df = (E==6) & dense_forest_fire
        fire_chance_df[e_fire_df] += 2*math.sin(math.pi/4)
        
        ne_fire_c = (NE==6) & canyon_fire
        fire_chance_canyon[ne_fire_c] += 2
        n_fire_c = (N==6) & canyon_fire
        fire_chance_canyon[n_fire_c] += 2*math.sin(math.pi/4)
        e_fire_c = (E==6) & canyon_fire
        fire_chance_canyon[e_fire_c] += 2*math.sin(math.pi/4)
    
    return grid


def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])

    # Create grid object using parameters from config + transition function
    fire_chance_chap = np.zeros(config.grid_dims)
    fire_chance_df = np.zeros(config.grid_dims)
    fire_chance_canyon = np.zeros(config.grid_dims)
    burnt_up_chap = np.zeros(config.grid_dims)
    burnt_up_chap.fill(100)
    burnt_up_df = np.zeros(config.grid_dims)
    burnt_up_df.fill(100)
    burnt_up_canyon = np.zeros(config.grid_dims)
    burnt_up_canyon.fill(100)
    wind = np.zeros(config.grid_dims)
    grid = Grid2D(config, (transition_function, fire_chance_chap,
                           fire_chance_df, fire_chance_canyon, burnt_up_chap,
                           burnt_up_df, burnt_up_canyon, wind))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
