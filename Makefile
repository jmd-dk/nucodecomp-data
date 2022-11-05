# Python interpreter
python ?= python3

# Use the Bash shell
SHELL = /usr/bin/env bash

# Figures to produce
figs = 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17


# Get DOIs
include .doi


# Function for downloading data sets from Zenodo based on DOIs
define download
$(shell
    [ ! -f $2 ] || exit 0;
    extract() { (echo "Extracting $$1:" && tar -xvf $$1) >/dev/tty && rm -f $$1; };
    if [ -d $1 ]; then
        for f in $1/*; do
            if [ -n "$3" ] && [ "$$(basename $$f)" != "$3" ]; then
                continue;
            fi;
            ln -s -f $$f .;
            extract $$(basename $$f);
        done;
    else
        for url in $$($(python) -c "pass;
            import json, urllib.request;
            response = urllib.request.urlopen('https://doi.org/' + '$1'.strip());
            record = response.url.split('/')[-1];
            response = urllib.request.urlopen('https://zenodo.org/api/records/' + record);
            [
                print(f['links']['self'])
                for f in json.loads(response.read())['files']
                if f['links']['self'].endswith("$3")
            ];
        "); do
            wget --continue --no-check-certificate $$url;
            extract $$(basename $$url);
        done
    fi
)
endef


# Default target
all: figure


# Figures
figure: $(addprefix figure/figure, $(addsuffix .pdf, $(figs)))
figure/figure%.pdf: script/figure%.py data-figure
	$(python) -B $<


# Power spectra
powerspec: script/compute_powerspec.py
	$(python) -B $<
.PHONY: powerspec


# Demonstrations
demo-cosmology: demo/cosmology.py
	$(python) -B $<
.PHONY: demo-cosmology

demo-ic: demo/ic.py data-ic-phase
	$(python) -B $<
.PHONY: demo-ic

demo: demo-cosmology demo-ic


# Data
data-figure:
	@$(call download,$(doi_data_figure),data/0.0eV/gadget3/z0/halo_cdm)
.PHONY: data-figure

data-snapshot-0.0eV-fiducial-z0:
	@$(call download,$(doi_data_snapshot_fiducial),data/0.0eV/gadget3/z0/snapshot/snapshot.0,data-snapshot-0.0eV-z0.tar.xz)
data-snapshot-0.0eV-fiducial-z1:
	@$(call download,$(doi_data_snapshot_fiducial),data/0.0eV/gadget3/z1/snapshot/snapshot.0,data-snapshot-0.0eV-z1.tar.xz)
.PHONY: data-snapshot-0.0eV-fiducial-z0 data-snapshot-0.0eV-fiducial-z1
data-snapshot-0.0eV-fiducial: data-snapshot-0.0eV-fiducial-z0 data-snapshot-0.0eV-fiducial-z1

data-snapshot-0.15eV-fiducial-z0:
	@$(call download,$(doi_data_snapshot_fiducial),data/0.15eV/gadget3/z0/snapshot/snapshot.0,data-snapshot-0.15eV-z0.tar.xz)
data-snapshot-0.15eV-fiducial-z1:
	@$(call download,$(doi_data_snapshot_fiducial),data/0.15eV/gadget3/z1/snapshot/snapshot.0,data-snapshot-0.15eV-z1.tar.xz)
.PHONY: data-snapshot-0.15eV-fiducial-z0 data-snapshot-0.15eV-fiducial-z1
data-snapshot-0.15eV-fiducial: data-snapshot-0.15eV-fiducial-z0 data-snapshot-0.15eV-fiducial-z1

data-snapshot-0.3eV-fiducial-z0:
	@$(call download,$(doi_data_snapshot_fiducial),data/0.3eV/gadget3/z0/snapshot/snapshot.0,data-snapshot-0.3eV-z0.tar.xz)
data-snapshot-0.3eV-fiducial-z1:
	@$(call download,$(doi_data_snapshot_fiducial),data/0.3eV/gadget3/z1/snapshot/snapshot.0,data-snapshot-0.3eV-z1.tar.xz)
.PHONY: data-snapshot-0.3eV-fiducial-z0 data-snapshot-0.3eV-fiducial-z1
data-snapshot-0.3eV: data-snapshot-0.3eV-fiducial-z0 data-snapshot-0.3eV-fiducial-z1

data-snapshot-0.6eV-fiducial-z0:
	@$(call download,$(doi_data_snapshot_fiducial),data/0.6eV/gadget3/z0/snapshot/snapshot.0,data-snapshot-0.6eV-z0.tar.xz)
data-snapshot-0.6eV-fiducial-z1:
	@$(call download,$(doi_data_snapshot_fiducial),data/0.6eV/gadget3/z1/snapshot/snapshot.0,data-snapshot-0.6eV-z1.tar.xz)
.PHONY: data-snapshot-0.6eV-fiducial-z0 data-snapshot-0.6eV-fiducial-z1
data-snapshot-0.6eV-fiducial: data-snapshot-0.6eV-fiducial-z0 data-snapshot-0.6eV-fiducial-z1

data-snapshot-fiducial-z0: data-snapshot-0.0eV-fiducial-z0 data-snapshot-0.15eV-fiducial-z0 data-snapshot-0.3eV-fiducial-z0 data-snapshot-0.6eV-fiducial-z0
data-snapshot-fiducial-z1: data-snapshot-0.0eV-fiducial-z1 data-snapshot-0.15eV-fiducial-z1 data-snapshot-0.3eV-fiducial-z1 data-snapshot-0.6eV-fiducial-z1
data-snapshot-fiducial: data-snapshot-fiducial-z0 data-snapshot-fiducial-z1

data-snapshot-0.0eV-1024Mpc-z0:
	@$(call download,$(doi_data_snapshot_0.0eV_1024Mpc),data/0.0eV_1024Mpc/gadget3/z0/snapshot/snapshot.0,data-snapshot-0.0eV_1024Mpc-z0.tar.xz)
data-snapshot-0.0eV-1024Mpc-z1:
	@$(call download,$(doi_data_snapshot_0.0eV_1024Mpc),data/0.0eV_1024Mpc/gadget3/z1/snapshot/snapshot.0,data-snapshot-0.0eV_1024Mpc-z1.tar.xz)
.PHONY: data-snapshot-0.0eV-1024Mpc-z0 data-snapshot-0.0eV-1024Mpc-z1
data-snapshot-0.0eV-1024Mpc: data-snapshot-0.0eV-1024Mpc-z0 data-snapshot-0.0eV-1024Mpc-z1

data-snapshot-0.15eV-1024Mpc-z0:
	@$(call download,$(doi_data_snapshot_0.15eV_1024Mpc_z0),data/0.15eV_1024Mpc/gadget3/z0/snapshot/snapshot.0)
data-snapshot-0.15eV-1024Mpc-z1:
	@$(call download,$(doi_data_snapshot_0.15eV_1024Mpc_z1),data/0.15eV_1024Mpc/gadget3/z1/snapshot/snapshot.0)
data-snapshot-0.15eV-1024Mpc: data-snapshot-0.15eV-1024Mpc-z0 data-snapshot-0.15eV-1024Mpc-z1

data-snapshot-1024Mpc-z0: data-snapshot-0.0eV-1024Mpc-z0 data-snapshot-0.15eV-1024Mpc-z0
data-snapshot-1024Mpc-z1: data-snapshot-0.0eV-1024Mpc-z1 data-snapshot-0.15eV-1024Mpc-z1
data-snapshot-1024Mpc: data-snapshot-1024Mpc-z0 data-snapshot-1024Mpc-z1

data-snapshot-0.0eV-HR-z0:
	@$(call download,$(doi_data_snapshot_0.0eV_HR),data/0.0eV_HR/gadget3/z0/snapshot/snapshot.0,data-snapshot-0.0eV_HR-z0.tar.xz)
data-snapshot-0.0eV-HR-z1:
	@$(call download,$(doi_data_snapshot_0.0eV_HR),data/0.0eV_HR/gadget3/z1/snapshot/snapshot.0,data-snapshot-0.0eV_HR-z1.tar.xz)
.PHONY: data-snapshot-0.0eV-HR-z0 data-snapshot-0.0eV-HR-z1
data-snapshot-0.0eV-HR: data-snapshot-0.0eV-HR-z0 data-snapshot-0.0eV-HR-z1

data-snapshot-0.15eV-HR-z0:
	@$(call download,$(doi_data_snapshot_0.15eV_HR_z0),data/0.15eV_HR/gadget3/z0/snapshot/snapshot.0)
data-snapshot-0.15eV-HR-z1:
	@$(call download,$(doi_data_snapshot_0.15eV_HR_z1),data/0.15eV_HR/gadget3/z1/snapshot/snapshot.0)
data-snapshot-0.15eV-HR: data-snapshot-0.15eV-HR-z0 data-snapshot-0.15eV-HR-z1

data-snapshot-HR-z0: data-snapshot-0.0eV-HR-z0 data-snapshot-0.15eV-HR-z0
data-snapshot-HR-z1: data-snapshot-0.0eV-HR-z1 data-snapshot-0.15eV-HR-z1
data-snapshot-HR: data-snapshot-HR-z0 data-snapshot-HR-z1

data-snapshot: data-snapshot-fiducial data-snapshot-1024Mpc data-snapshot-HR

data-ic-phase:
	@$(call download,$(doi_data_ic_fiducial),data/0.0eV/ic/phase,data-ic-phase.tar.xz)
.PHONY: data-ic-phase

data-ic-0.0eV-fiducial:
	@$(call download,$(doi_data_ic_fiducial),data/0.0eV/ic/snapshot.0,data-ic-0.0eV.tar.xz)
data-ic-0.15eV-fiducial:
	@$(call download,$(doi_data_ic_fiducial),data/0.15eV/ic/snapshot.0,data-ic-0.15eV.tar.xz)
data-ic-0.3eV-fiducial:
	@$(call download,$(doi_data_ic_fiducial),data/0.3eV/ic/snapshot.0,data-ic-0.3eV.tar.xz)
data-ic-0.6eV-fiducial:
	@$(call download,$(doi_data_ic_fiducial),data/0.6eV/ic/snapshot.0,data-ic-0.6eV.tar.xz)
.PHONY: data-ic-0.0eV-fiducial data-ic-0.15eV-fiducial data-ic-0.3eV-fiducial data-ic-0.6eV-fiducial
data-ic-fiducial: data-ic-0.0eV-fiducial data-ic-0.15eV-fiducial data-ic-0.3eV-fiducial data-ic-0.6eV-fiducial

data-ic-0.0eV-1024Mpc:
	@$(call download,$(doi_data_ic_1024Mpc),data/0.0eV_1024Mpc/ic/snapshot.0,data-ic-0.0eV_1024Mpc.tar.xz)
data-ic-0.15eV-1024Mpc:
	@$(call download,$(doi_data_ic_1024Mpc),data/0.15eV_1024Mpc/ic/snapshot.0,data-ic-0.15eV_1024Mpc.tar.xz)
.PHONY: data-ic-0.0eV-1024Mpc data-ic-0.15eV-1024Mpc
data-ic-1024Mpc: data-ic-0.0eV-1024Mpc data-ic-0.15eV-1024Mpc

data-ic-0.0eV-HR:
	@$(call download,$(doi_data_ic_HR),data/0.0eV_HR/ic/snapshot.0,data-ic-0.0eV_HR.tar.xz)
data-ic-0.15eV-HR:
	@$(call download,$(doi_data_ic_HR),data/0.15eV_HR/ic/snapshot.0,data-ic-0.15eV_HR.tar.xz)
.PHONY: data-ic-0.0eV-HR data-ic-0.15eV-HR
data-ic-HR: data-ic-0.0eV-HR data-ic-0.15eV-HR

data-ic: data-ic-phase data-ic-fiducial data-ic-1024Mpc data-ic-HR


# Clean
clean-figure:
	$(RM) $(addprefix figure/figure, $(addsuffix .pdf, $(figs)))
.PHONY: clean-figure

clean-powerspec:
	$(RM) data/*/gadget3/*/powerspec_*
.PHONY: clean-powerspec

clean-demo-cosmology:
	$(RM) demo/cosmology.pdf
.PHONY: clean-demo-cosmology

clean-demo-ic:
	$(RM) demo/ic.pdf
.PHONY: clean-demo-ic

clean-demo: clean-demo-cosmology clean-demo-ic

clean-tar.xz:
	$(RM) *.tar.xz
.PHONY: clean-tar.xz

clean: clean-tar.xz clean-figure clean-powerspec clean-demo

clean-data-figure:
	@for d in data/*/*; do                       \
	    if [[ $$d == */ic ]]; then               \
	         continue;                           \
	    elif [[ $$d == */gadget3 ]]; then        \
	        for f in $$d/*/*; do                 \
	            if [[ $$f != */snapshot ]]; then \
	                rm -rf $$f;                  \
	            fi;                              \
	        done;                                \
	    else                                     \
	        rm -rf $$d;                          \
	    fi;                                      \
	done
.PHONY: clean-data-figure

clean-data-snapshot-0.0eV-fiducial-z0:
	$(RM) -r data/0.0eV/*/z0/snapshot
clean-data-snapshot-0.0eV-fiducial-z1:
	$(RM) -r data/0.0eV/*/z1/snapshot
.PHONY: clean-data-snapshot-0.0eV-fiducial-z0 clean-data-snapshot-0.0eV-fiducial-z1
clean-data-snapshot-0.0eV-fiducial: clean-data-snapshot-0.0eV-fiducial-z0 clean-data-snapshot-0.0eV-fiducial-z1

clean-data-snapshot-0.15eV-fiducial-z0:
	$(RM) -r data/0.15eV/*/z0/snapshot
clean-data-snapshot-0.15eV-fiducial-z1:
	$(RM) -r data/0.15eV/*/z1/snapshot
.PHONY: clean-data-snapshot-0.15eV-fiducial-z0 clean-data-snapshot-0.15eV-fiducial-z1
clean-data-snapshot-0.15eV-fiducial: clean-data-snapshot-0.15eV-fiducial-z0 clean-data-snapshot-0.15eV-fiducial-z1

clean-data-snapshot-0.3eV-fiducial-z0:
	$(RM) -r data/0.3eV/*/z0/snapshot
clean-data-snapshot-0.3eV-fiducial-z1:
	$(RM) -r data/0.3eV/*/z1/snapshot
.PHONY: clean-data-snapshot-0.3eV-fiducial-z0 clean-data-snapshot-0.3eV-fiducial-z1
clean-data-snapshot-0.3eV-fiducial: clean-data-snapshot-0.3eV-fiducial-z0 clean-data-snapshot-0.3eV-fiducial-z1

clean-data-snapshot-0.6eV-fiducial-z0:
	$(RM) -r data/0.6eV/*/z0/snapshot
clean-data-snapshot-0.6eV-fiducial-z1:
	$(RM) -r data/0.6eV/*/z1/snapshot
.PHONY: clean-data-snapshot-0.6eV-fiducial-z0 clean-data-snapshot-0.6eV-fiducial-z1
clean-data-snapshot-0.6eV-fiducial: clean-data-snapshot-0.6eV-fiducial-z0 clean-data-snapshot-0.6eV-fiducial-z1

clean-data-snapshot-fiducial-z0: clean-data-snapshot-0.0eV-fiducial-z0 clean-data-snapshot-0.15eV-fiducial-z0 clean-data-snapshot-0.3eV-fiducial-z0 clean-data-snapshot-0.6eV-fiducial-z0
clean-data-snapshot-fiducial-z1: clean-data-snapshot-0.0eV-fiducial-z1 clean-data-snapshot-0.15eV-fiducial-z1 clean-data-snapshot-0.3eV-fiducial-z1 clean-data-snapshot-0.6eV-fiducial-z1
clean-data-snapshot-fiducial: clean-data-snapshot-fiducial-z0 clean-data-snapshot-fiducial-z1

clean-data-snapshot-0.0eV-1024Mpc-z0:
	$(RM) -r data/0.0eV_1024Mpc/*/z0/snapshot
clean-data-snapshot-0.0eV-1024Mpc-z1:
	$(RM) -r data/0.0eV_1024Mpc/*/z1/snapshot
.PHONY: clean-data-snapshot-0.0eV-1024Mpc-z0 clean-data-snapshot-0.0eV-1024Mpc-z1
clean-data-snapshot-0.0eV-1024Mpc: clean-data-snapshot-0.0eV-1024Mpc-z0 clean-data-snapshot-0.0eV-1024Mpc-z1

clean-data-snapshot-0.15eV-1024Mpc-z0:
	$(RM) -r data/0.15eV_1024Mpc/*/z0/snapshot
clean-data-snapshot-0.15eV-1024Mpc-z1:
	$(RM) -r data/0.15eV_1024Mpc/*/z1/snapshot
.PHONY: clean-data-snapshot-0.15eV-1024Mpc-z0 clean-data-snapshot-0.15eV-1024Mpc-z1
clean-data-snapshot-0.15eV-1024Mpc: clean-data-snapshot-0.15eV-1024Mpc-z0 clean-data-snapshot-0.15eV-1024Mpc-z1

clean-data-snapshot-1024Mpc-z0: clean-data-snapshot-0.0eV-1024Mpc-z0 clean-data-snapshot-0.15eV-1024Mpc-z0
clean-data-snapshot-1024Mpc-z1: clean-data-snapshot-0.0eV-1024Mpc-z1 clean-data-snapshot-0.15eV-1024Mpc-z1
clean-data-snapshot-1024Mpc: clean-data-snapshot-1024Mpc-z0 clean-data-snapshot-1024Mpc-z1

clean-data-snapshot-0.0eV-HR-z0:
	$(RM) -r data/0.0eV_HR/*/z0/snapshot
clean-data-snapshot-0.0eV-HR-z1:
	$(RM) -r data/0.0eV_HR/*/z1/snapshot
.PHONY: clean-data-snapshot-0.0eV-HR-z0 clean-data-snapshot-0.0eV-HR-z1
clean-data-snapshot-0.0eV-HR: clean-data-snapshot-0.0eV-HR-z0 clean-data-snapshot-0.0eV-HR-z1

clean-data-snapshot-0.15eV-HR-z0:
	$(RM) -r data/0.15eV_HR/*/z0/snapshot
clean-data-snapshot-0.15eV-HR-z1:
	$(RM) -r data/0.15eV_HR/*/z1/snapshot
.PHONY: clean-data-snapshot-0.15eV-HR-z0 clean-data-snapshot-0.15eV-HR-z1
clean-data-snapshot-0.15eV-HR: clean-data-snapshot-0.15eV-HR-z0 clean-data-snapshot-0.15eV-HR-z1

clean-data-snapshot-HR-z0: clean-data-snapshot-0.0eV-HR-z0 clean-data-snapshot-0.15eV-HR-z0
clean-data-snapshot-HR-z1: clean-data-snapshot-0.0eV-HR-z1 clean-data-snapshot-0.15eV-HR-z1
clean-data-snapshot-HR: clean-data-snapshot-HR-z0 clean-data-snapshot-HR-z1

clean-data-snapshot: clean-data-snapshot-fiducial clean-data-snapshot-1024Mpc clean-data-snapshot-HR

clean-data-ic-phase:
	$(RM) data/*eV/ic/phase
.PHONY: clean-data-ic-phase

clean-data-ic-0.0eV-fiducial:
	$(RM) -r data/0.0eV/ic
clean-data-ic-0.15eV-fiducial:
	$(RM) -r data/0.15eV/ic
clean-data-ic-0.3eV-fiducial:
	$(RM) -r data/0.3eV/ic
clean-data-ic-0.6eV-fiducial:
	$(RM) -r data/0.6eV/ic
.PHONY: clean-data-ic-0.0eV-fiducial clean-data-ic-0.15eV-fiducial clean-data-ic-0.3eV-fiducial clean-data-ic-0.6eV-fiducial
clean-data-ic-fiducial: clean-data-ic-0.0eV-fiducial clean-data-ic-0.15eV-fiducial clean-data-ic-0.3eV-fiducial clean-data-ic-0.6eV-fiducial

clean-data-ic-0.0eV-1024Mpc:
	$(RM) -r data/0.0eV_1024Mpc/ic
clean-data-ic-0.15eV-1024Mpc:
	$(RM) -r data/0.15eV_1024Mpc/ic
.PHONY: clean-data-ic-0.0eV-1024Mpc clean-data-ic-0.15eV-1024Mpc
clean-data-ic-1024Mpc: clean-data-ic-0.0eV-1024Mpc clean-data-ic-0.15eV-1024Mpc

clean-data-ic-0.0eV-HR:
	$(RM) -r data/0.0eV_HR/ic
clean-data-ic-0.15eV-HR:
	$(RM) -r data/0.15eV_HR/ic
.PHONY: clean-data-ic-0.0eV-HR clean-data-ic-0.15eV-HR
clean-data-ic-HR: clean-data-ic-0.0eV-HR clean-data-ic-0.15eV-HR

clean-data-ic: clean-data-ic-phase clean-data-ic-fiducial clean-data-ic-1024Mpc clean-data-ic-HR

clean-data: clean-tar.xz clean-data-figure clean-data-snapshot clean-data-ic

distclean: clean clean-data

