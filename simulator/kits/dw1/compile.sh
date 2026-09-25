#!/bin/bash
# dw1: the WF process at an arbitrary list of games.  Same compiler and flags
# as DonationWF/Code/Sim/wf3, so the binary is the same build of the same
# generation loop.
set -e
module load intel/25.2.1-fasrc01
ifx -O3 -xHost -fp-model precise -o sf.x sf.f payf3.f payf2.f mtb.f mt.f
ls -la sf.x
