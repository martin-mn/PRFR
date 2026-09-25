# gfortran 14.1.0 -O2, macOS 26.6 arm64 (Apple M2 Pro), 2026-09-24

Reference outputs of `../smoke.sh`: for each (kit, itend, task) the sha256 of the files the run writes into its run
directory (the summary `<task>`, `w<task>`, `h<task>` and, where the kit writes one, `r<task>`), checked with
`shasum -a 256 -c`. `f1_20000_1902.summary` is the summary file of the default run, one line per replicate:
`gid ie u v Emax pay ef ps1..ps16` (see `../../README.md`). The first line of this file is what `smoke.sh` prints.
