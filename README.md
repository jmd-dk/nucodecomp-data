# Euclid massive neutrino code comparison data
This repository contains the main data processing pipeline used to make all
figures included in the paper
‘Euclid: Modelling massive neutrinos in cosmology — a code comparison’.

- [Euclid massive neutrino code comparison data](#euclid-massive-neutrino-code-comparison-data)
  * [Introduction](#introduction)
  * [Data](#data)
    + [Data directory structure](#data-directory-structure)
    + [Figure data](#figure-data)
      - [Power spectra](#power-spectra)
    + [Simulation snapshots](#simulation-snapshots)
    + [Initial conditions](#initial-conditions)
  * [Figures](#figures)
  * [Demonstrations](#demonstrations)
    + [Cosmology](#cosmology)
    + [Initial conditions](#initial-conditions-1)
  * [Cleanup](#cleanup)
  * [Required libraries and tools](#required-libraries-and-tools)
  * [Docker](#docker)



## Introduction
All figures can be found pre-generated in the `figure` directory. To
regenerate them from data, do
```bash
make clean-figure && python=/path/to/python make
```
with `/path/to/python` the path to the Python interpreter to use (see
[Required libraries and tools](#required-libraries-and-tools) for required
Python packages). The necessary data will be downloaded from
[Zenodo](https://zenodo.org/), amounting to a 6 GB download that takes up
18 GB of disk space once extracted. See the [Figures](#figures) section for
further details.

Further data (simulation snapshots, initial conditions) are made available,
see the [Data](#data) section.

For computing power spectra from snapshots,
see [Power spectra](#power-spectra).

Demonstrations of how the cosmology is specified and how initial conditions
are set up can be found in the [Demonstrations](#demonstrations) section.



## Data

### Data directory structure
All data files will appear in the `data` directory, which have the following
directory structure:
- `data/`
  - `0.0eV/`
    - `ic/`
      - `phase`
      - `snapshot.*`
    - `gadget3/`
      - `z0/`
        - `snapshot/`
          - `snapshot.*`
        - `powerspec_cdm`
        - ⋯  (other data files)
      - `z1/`
        - `snapshot/`
          - `snapshot.*`
        - `powerspec_cdm`
        - ⋯  (other data files)
    - ⋯  (other codes)
  - `0.0eV_HR/`
    - ⋯  (similar to `0.0eV/`)
  - `0.0eV_1024Mpc/`
    - ⋯  (similar to `0.0eV/`)
  - `0.15eV/`
    - ⋯  (similar to `0.0eV/`)
  - `0.15eV_HR/`
    - ⋯  (similar to `0.0eV/`)
  - `0.15eV_1024Mpc/`
    - ⋯  (similar to `0.0eV/`)
  - `0.3eV/`
    - ⋯  (similar to `0.0eV/`)
  - `0.6eV/`
    - ⋯  (similar to `0.0eV/`)

with the first-level directory labelling the simulation by the neutrino mass
and one of ‘fiducial’ (512 Mpc/h box, 512³ particles), ‘HR’ (512 Mpc/h box,
1024³ particles) or ‘1024Mpc’ (1024 Mpc/h box, 1024³ particles). The `ic`
directories contain initial conditions in the form of a snapshot. The special
`phase` file, providing the primordial random phases, is exclusive to the
`0.0eV/ic` directory (all simulations share the same phases). Each snapshot
(be it initial conditions or final results) is distributed across several
files, as indicated by the asterisk in `snapshot.*`. Snapshots are only made
available for GADGET-3, the reference simulation code employed for this
project.



### Figure data
The data necessary to generate the figures can be downloaded via
```bash
make data-figure
```



#### Power spectra
As snapshots are available in the case of GADGET-3, rather than using the
downloaded GADGET-3 power spectrum data files for the figures, these power
spectrum data files can alternatively be computed from the snapshots. That is,
once the snapshots have been downloaded using
```bash
make data-snapshot
```
all GADGET-3 power spectra can be computed via
```bash
make powerspec
```
Already existing power spectra will not be recomputed and missing snapshots
are allowed. All such GADGET-3 power spectra can be removed using
```bash
make clean-powerspec
```
Recomputing all GADGET-3 power spectra from snapshots takes about 3 hours on
modern hardware and requires roughly 25 GB of RAM. This computation can be
sped up through parallelization by setting e.g.
```bash
export OMP_NUM_THREADS=8
```
The script employed for computing the power spectra is found within the
`script` directory and is called `compute_powerspec.py`.



### Simulation snapshots
Simulation snapshots are available for GADGET-3 at redshifts 1 and 0, for the
entire simulation suite. These can be downloaded via
```bash
make data-snapshot
```



### Initial conditions
Initial conditions are available for all simulations. These are given as
GADGET snapshots at redshift 127. For the cosmologies with massive neutrinos,
the snapshots contain both matter and neutrino particles. These initial
condition snapshots can be downloaded via
```bash
make data-ic
```
While the initial condition snapshots are code agnostic in principle, many
cosmological simulation codes require initial conditions in a special format,
e.g. due to the way neutrinos are handled. Besides the specification of the
cosmology and simulation parameters, a set of primordial amplitudes and phases
are further needed to specify the initial conditions. We use
"[fixed](https://arxiv.org/abs/1603.05253)" amplitudes, leaving only the
phases. These phases are available for download using
```bash
make data-phase
```
All simulations employ the same phases. For how to use these phases to
generate matching initial conditions of your own, see the
[initial conditions demo](#initial-conditions-1).



## Figures
The figures (already present in the `figure` directory) can be regenerated by
running
```bash
python=/path/to/python make
```
Missing data will be computed or downloaded as needed.
Already existing figures will be skipped. You can remove all figures via
```bash
make clean-figure
```
The Python scripts used for generating the figures are found in the `script`
directory, one script per figure.



## Demonstrations
...



### Cosmology
... `demo/cosmology.py`
```bash
make demo-cosmology
```

### Initial conditions
... `demo/ic.py`
```bash
make demo-ic
```



## Cleanup
Each `make` target has an associated ‘clean’ target which undoes the action:
- Figures are removed with
  ```bash
  make clean-figure
  ```
- GADGET-3 power spectrum data files are removed with
  ```bash
  make clean-powerspec
  ```
- Figure data files are removed with
  ```bash
  make clean-data-figure
  ```
- GADGET-3 snapshots are removed with
  ```bash
  make clean-data-snapshot
  ```
- Initial condition files are removed with
  ```bash
  make clean-data-ic
  ```
- The figures as well as the GADGET-3 power spectrum data are removed with
  ```bash
  make clean
  ```
- All clean targets can be run together using
  ```bash
  make distclean
  ```



## Required libraries and tools
The generation of figures from the various data, as well as the power spectrum
computations from the snapshots, requires the following libraries and tools to
be installed on the system. All should be to be on the `PATH`.
- Python 3.9.12
  - NumPy 1.21.5
  - SciPy 1.7.3
  - Matplotlib 3.3.4
  - [CLASS 2.7.2](https://github.com/lesgourg/class_public/tree/v2.7.2)
  - [Pylians3 729d74c8af324a77a02926c82b89f678856bfdfe](https://github.com/franciscovillaescusa/Pylians3/tree/729d74c8af324a77a02926c82b89f678856bfdfe)
- LaTeX, e.g. TeX Live 2020.20210202-3
- (GNU) Make 4.2.1
- (GNU) wget 1.21.3
- (GNU) tar 1.30
- XZ Utils 5.2.4

The listed version numbers are known to work and coincide with those shipping
with the [published Docker image](#docker), though many other version
combinations will work as well.



## Docker
All of the [above dependencies](#required-libraries-and-tools) has been
bundled into a custom Docker image, available at
[jmddk/nucodecomp](https://hub.docker.com/r/jmddk/nucodecomp). To run the data
analysis pipeline through Docker, you can e.g. run Docker interactively,
```bash
docker run --rm -it -v ${PWD}:/mnt jmddk/nucodecomp
```
after which all of the above `make` commands are available. You can copy
results produced within the running Docker container (say the `figure`
directory) to your host filesystem using
```bash
cp -r figure /mnt/
```
The `Dockerfile` used to build the Docker image is provided as part of
this repository.

