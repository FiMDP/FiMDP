#!/usr/bin/env python3
import sys
import ast
from statistics import stdev


def main(argv):
    if len(argv) != 1:
        raise IOError(f"Incorrect number of arguments for script: {len(argv)}, expected 1.")
    name = argv[0]

    main_log_file = open(f"{name}.log", 'r')
    main_lines = main_log_file.readlines()

    results_str = main_lines[-1].split("INFO")[1].split("RESULTS ():")[1].strip()

    results_list = ast.literal_eval(results_str)

    target_hits = []
    all_decision_times = []
    rewards = []

    for _, target_hit, _, decision_times, _, reward in results_list:
        target_hits.append(target_hit)
        all_decision_times.extend(decision_times)
        rewards.append(reward)

    stats = []

    stats.append(f"Target hits: {target_hits.count(True)}/{len(target_hits)}")
    stats.append(f"Decision count: {len(all_decision_times)}, Average: {sum(all_decision_times)/len(all_decision_times)}")
    stats.append(f"Decision standard deviation: {stdev(all_decision_times)}")
    stats.append(f"Average reward: {sum(rewards)/len(rewards)}")
    stats.append(f"Reward standard deviation: {stdev(rewards)}")

    for stat in stats:
        print(f"{stat}")

    stat_file = open(f"{name}_STATS.txt", 'w')
    stat_file.write('\n'.join(stats) + '\n')

    stat_file.close()
    main_log_file.close()

if __name__ == "__main__":
    main(sys.argv[1:])