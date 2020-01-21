import sys
from src.memetic import memetic_heuristic
from src.flowshop import Flowshop
from src.visualisation import save_solution_as_html
from src.utils import read_global_memetic_results, update_global_memetic_results, get_best_known_and_found_solutions, \
    load_parameters, write_global_memetic_results
import matplotlib.pyplot as plt

time_limit = float(sys.argv[1])
flow_shop_file_path = sys.argv[2]
parameters_file_path = sys.argv[3]
global_memetic_results_path = sys.argv[4]
visualise_results = bool(int(sys.argv[5]))  # Warning bool("0") return True (like bool("1"))

parameters = load_parameters(parameters_file_path)
parameters['time_limit'] = time_limit

# Loading an instance of the FlowShop Problem
flow_shop_instance = Flowshop()
flow_shop_instance.definir_par(flow_shop_file_path)
file_name = flow_shop_file_path.split('/')[-1].split('.txt')[0]

# Loading the best known and found results for this instance
global_memetic_results = read_global_memetic_results(global_memetic_results_path)
best_known_solution, best_solution_found = get_best_known_and_found_solutions(global_memetic_results, file_name)

# Executing the memetic algorithm
list_statistics, best_scheduling, iterations_where_restart = memetic_heuristic(flow_shop_instance, parameters)
best_c_max = best_scheduling.duree()
initial_statistics = list_statistics[0]
max_printed_solution = max([statistics[0] for statistics in list_statistics])

# Save results (in the csv files, in the plt figure and in the html visualisation file) IF a best solution is obtained
# And show/print the results no matter the quality of the solution IF the boolean 'visualise_results' is true
relative_gap = round(((best_c_max - best_known_solution) / best_known_solution) * 100, 2)  # round to 2 decimals
global_memetic_results, is_updated = update_global_memetic_results(global_memetic_results, file_name, best_c_max,
                                                                   relative_gap, initial_statistics[0],
                                                                   initial_statistics[1], initial_statistics[2],
                                                                   parameters)
if visualise_results or is_updated:
    # plt figure
    plt.figure("Memetic heuristic results with instance " + file_name)
    plt.title("Memetic heuristic applied to the instance: " + file_name)
    generations = range(len(list_statistics))
    # Plot restart
    for index in iterations_where_restart:
        plt.plot([index, index], [best_known_solution, max_printed_solution], '-y')
    # Mean curve
    plt.plot(generations, [statistics[0] for statistics in list_statistics],
             '-b', label="mean memetic")
    # Min curve
    plt.plot(generations, [statistics[1] for statistics in list_statistics],
             '-g', label="min memetic, Cmax=" + str(best_c_max))
    # Max curve
    # plt.plot(generations, [statistics[2] for statistics in list_statistics],
    #         '-r', label="max memetic")
    # Opt/Best known curve
    plt.plot([0, len(list_statistics) - 1], [best_known_solution, best_known_solution],
             '--k', label="best known, Cmax=" + str(best_known_solution))

    plt.xlabel("Generation/Iteration of the population")
    plt.ylabel("Cmax (duration of the best scheduling in the population)")
    plt.legend(bbox_to_anchor=(0.5, 1), ncol=2, loc='upper center', mode='expand', borderaxespad=0.)

    if is_updated:
        plt.savefig("res/figures/memetic_" + file_name)
        save_solution_as_html(best_scheduling, file_name=("memetic_" + file_name), file_path="res/visualisation_html/",
                              show_durations=False)
        write_global_memetic_results(global_memetic_results_path, global_memetic_results)
        print("A better scheduling is found for the instance " + file_name + ":")
    if visualise_results:
        plt.show()
        # show_solution_figure(best_scheduling, show_durations=True)

if not is_updated:
    print("Scheduling found (not the best) for the instance " + file_name + ":")
print("    Cmax -> Obtained: " + str(best_c_max) + " (" + str(relative_gap) + "%), Best known: " +
      str(best_known_solution) + ", (ex-)Best found: " + str(best_solution_found))
