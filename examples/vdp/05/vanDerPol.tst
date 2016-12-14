
inf = float('inf')
plant_pvt_init_data = None

initial_set = [[-0.4, -0.4], [0.4, 0.4]]
error_set = [[-1, -6.5], [-0.7, -5.6]]

grid_eps = [1.0, 1.0]
num_samples = -10
delta_t = 0.5

initial_discrete_state = []
initial_private_state = []

T = 1.0


MAX_ITER = inf


plant_description = 'python'
plant_path = 'vanDerPol.py'

#############################################
initial_controller_integer_state = []
initial_controller_float_state = []
num_control_inputs = 0
min_smt_sample_dist = 0

ci = [[], []]
pi = [[],[]]
controller_path = None
controller_path_dir_path = None
