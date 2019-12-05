#!/usr/bin/python3

"""
Copyright © 5/12/2019, Alexis GROS MAURICE ANDRÉ
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders X be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.

Except as contained in this notice, the name of the Alexis GROS MAURICE ANDRÉ shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from Alexis GROS MAURICE ANDRÉ.
"""

import os
import subprocess
import matplotlib.pyplot as plt
import sys
import json
from calendar import monthrange


def get_efficiency_datas(
    date, repo_path, branch_name, verbose, dir, file_extension
    ):
    core_command_total = 'git -C '+repo_path+' log '+branch_name+\
        ' --before="'+date+'" --stat'
    command_nb_changes_total = core_command_total +\
        ' | grep "\.'+file_extension+' *|" |'+\
        ' grep "'+dir+'" | cut -d"|" -f 2 | cut -d"-" -f 1 | cut -d"+" -f 1 |'+\
        ' paste -s -d+ | bc'

    core_command_actual = 'git -C '+repo_path+' diff --stat `git -C '+\
        repo_path+' rev-list -1 --before="'+date+'" '+\
        branch_name+'`  `git -C '+\
        repo_path+' rev-list '+branch_name+' | tail -n 1` '+branch_name
    command_nb_changes_actual = core_command_actual+\
        ' | grep "\.'+file_extension+' *|" |'+\
        ' grep "'+dir+'" | cut -d"|" -f 2 | cut -d"-" -f 1 | cut -d"+" -f 1 |'+\
        ' paste -s -d+ | bc'

    result = os.popen(command_nb_changes_total).read()
    result2 = os.popen(command_nb_changes_actual).read()
    nb_changes_total = -1
    if result != '':
        nb_changes_total = int(result)
    nb_changes_actual = -1
    if result != '':
        nb_changes_actual = int(result2)
    if nb_changes_actual == -1 or nb_changes_total == -1:
        return [-1, float(nb_changes_actual), float(nb_changes_total)]
    if verbose:
        print("-nb_change_actual---"+str(nb_changes_actual))
        print("-nb_change_total---"+str(nb_changes_total))
    efficiency = float(nb_changes_actual) / float(nb_changes_total)
    return [efficiency, float(nb_changes_actual), float(nb_changes_total)]


def print_help():
    print('Usage:')
    print('\tplot.py GIT_REPOSITORY_PATH BRANCH_NAME [--show] [--recover] [-v] [--step] [--file EXTENSION] [--dir DIR]')
    print('\nOptions')
    print(
        '\t--recover: Will attempt to load data.txt to fetch previous datas'+\
        'instead of generating new ones'
        )
    print('\t--show: Show the graph')
    print('\t-v: Verbose')
    print('\t--step NUM_STEP: How many days between each date? (default=16)')
    print('\t--file EXTENSION: Only count for files with a certain EXTENSION')
    print('\t--dir DIR: Only count for files with DIR as a parent directory')
    print('\nExample:')
    print(
        '\t./gitstatplot.py ~/Documents/Projects/lapentrycoach_simulator'+\
        'development-version2 --step 16 --show --dir game --file gd'
        )
    quit()


def show_graph(dates, efficiencies, changes_actuals, changes_totals):
    start_index = next(x for x, val in enumerate(efficiencies) if val > -1)
    changes_actuals_ratio = changes_actuals.copy()
    for i in range(len(changes_actuals)):
        changes_actuals_ratio[i] /= changes_actuals_ratio[-1]
        changes_actuals_ratio[i] *= 100
    changes_totals_ratio = changes_totals.copy()
    for i in range(len(changes_totals_ratio)):
        changes_totals_ratio[i] /= changes_totals_ratio[-1]
        changes_totals_ratio[i] *= 100

    plt.plot(dates[start_index:], efficiencies[start_index:], 'r',
        label='efficiency')
    plt.plot(
        dates[start_index:], changes_actuals_ratio[start_index:], 'g',
        label='code lines ('+str(round(changes_actuals[-1], 0))+')'
        )
    plt.plot(
        dates[start_index:], changes_totals_ratio[start_index:], 'b',
        label='code changes ('+str(round(changes_totals[-1], 0))+')'
        )
    plt.legend()
    plt.grid
    plt.axes().xaxis.set_major_locator(plt.MaxNLocator(10))
    plt.xlabel('time')
    plt.ylabel('percentage')
    plt.show()


def parse_arguments():
    recover_from_file = False
    verbose = False
    show_plot = False
    repo_path = ''
    branch_name = ''
    step = 16
    file_extension = ''
    dir = ''
    if len(sys.argv) < 3:
        if len(sys.argv) == 2 and sys.argv[1] == '--help':
            print_help()
        else:
            print('Badly formulated request')
            print_help()
    else:
        repo_path = sys.argv[1]
        branch_name = sys.argv[2]
        for i, arg in enumerate(sys.argv):
            if arg == "-v":
                verbose = True
            elif arg == "--recover":
                recover_from_file = True
            elif arg == '--show':
                show_plot = True
            elif arg == '--step':
                step = int(sys.argv[i+1])
            elif arg == '--dir':
                dir = sys.argv[i+1]
            elif arg == '--file':
                file_extension = sys.argv[i+1]

    return recover_from_file, verbose, show_plot, repo_path, branch_name, step,\
        dir, file_extension


def main():
    recover_from_file, verbose, show_plot,\
        repo_path, branch_name, step, dir, file_extension = parse_arguments()

    dates = []
    efficiencies = []
    changes_actuals = []
    changes_totals = []
    if recover_from_file:
        with open('data.txt') as json_file:
            data = json.load(json_file)
            dates = data['dates']
            efficiencies = data['efficiencies']
            changes_actuals = data['changes_actuals']
            changes_totals = data['changes_totals']
    else:
        for year in range(2018, 2019+1):
            for month in range(1, 12+1):
                for day in range(1, monthrange(year, month)[1]+1, step):
                    date = str(year)+"-"+str(month)+"-"+str(day)
                    dates.append(date)
        print("num_dates: "+str(len(dates)))
        for date in dates:
            efficiency, nb_changes_actual, nb_changes_total =\
                get_efficiency_datas(
                    date, repo_path, branch_name, verbose, dir, file_extension
                    )
            efficiencies.append(efficiency*100)
            changes_actuals.append(nb_changes_actual)
            changes_totals.append(nb_changes_total)
            if efficiency != -1:
                print(date+": "+str(round(efficiency*100, 1))+"%")
        with open('data.txt', 'w') as outfile:
            json.dump(
                {
                    'dates': dates,
                    'efficiencies': efficiencies,
                    'changes_actuals': changes_actuals,
                    'changes_totals': changes_totals
                }, outfile
            )

    if show_plot:
        show_graph(dates, efficiencies, changes_actuals, changes_totals)


main()
