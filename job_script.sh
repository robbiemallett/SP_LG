#!/bin/bash -l

# Request ten minutes of wallclock time (format hours:minutes:seconds).
#$ -l h_rt=0:05:0

# Request 1 gigabyte of RAM for each core/thread (must be an integer followed by M, G, or T)
#$ -l mem=1G

# Request 15 gigabyte of TMPDIR space (default is 10 GB)
#$ -l tmpfs=15G

# Set the name of the job.
#$ -N testing

# Request 16 cores.
#$ -pe smp 2

# Set the working directory to somewhere in your scratch space.
#$ -wd /home/ucfarm0/Scratch

# 8. Run the application.
python3 /home/ucfarm0/SP_LG/SP_LG/master_script.py
