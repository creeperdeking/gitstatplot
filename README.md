# gitstatplot
A simple script for extracting intresting datas out of the git history.

Usage:  
	plot.py GIT_REPOSITORY_PATH BRANCH_NAME [--show] [--recover] [-v] [--step] [--file EXTENSION] [--dir DIR]

Options:  
	--recover: Will attempt to load data.txt to fetch previous datas instead of generating new ones  
	--show: Show the graph  
	-v: Verbose  
	--step NUM_STEP: How many days between each date? (default=16)  
	--file EXTENSION: Only count for files with a certain EXTENSION  
	--dir DIR: Only count for files with DIR as a parent directory

Example:  
	./gitstatplot.py ~/Documents/Projects/lapentrycoach_simulator development-version2 --step 16 --show --dir game --file gd

