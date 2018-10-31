#!/bin/bash

# create rmsd plots comparing set of tarjectory structs to set of (median cluster) structs

declare RUNS
RUNS=(b0 b1 b2 b3 b4 c1 c2 c3)

RUNSDIR="/home/gerr/hdd/sci/dat/comp/mdsim/runs_hpc/cmp_rmsd/"

#pushd ${RUNSDIR}
for st in ${RUNS[@]}; do
    for rn in ${RUNS[@]}; do
        echo "bh4 bh4" | gmx rms -s str_${st}.gro -f ../${rn}/md01_ctr.xtc -o pr_bh4-${st}_${rn}.xvg -tu ns -dt 0.02 -n ../${rn}/idx_bh4.ndx
        echo "bh4top bh4top" | gmx rms -s str_${st}.gro -f ../${rn}/md01_ctr.xtc -o pr_bh4top-${st}_${rn}.xvg -tu ns -dt 0.02 -n ../${rn}/idx_bh4.ndx
        echo "bh4top loop" | gmx rms -s str_${st}.gro -f ../${rn}/md01_ctr.xtc -o pr_loop-${st}_${rn}.xvg -tu ns -dt 0.02 -n ../${rn}/idx_bh4.ndx
        echo "bh4top lS1"  | gmx rms -s str_${st}.gro -f ../${rn}/md01_ctr.xtc -o pr_lS1-${st}_${rn}.xvg  -tu ns -dt 0.02 -n ../${rn}/idx_bh4.ndx
        echo "bh4top lS2"  | gmx rms -s str_${st}.gro -f ../${rn}/md01_ctr.xtc -o pr_lS2-${st}_${rn}.xvg  -tu ns -dt 0.02 -n ../${rn}/idx_bh4.ndx
    done
done
#popd
