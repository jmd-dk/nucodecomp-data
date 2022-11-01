# Python interpreter
python ?= python3
# Use the Bash shell
SHELL = /usr/bin/env bash
# Figures to produce
figs = 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17


# Get DOIs
include .doi


# Function for downloading data sets based on DOIs
define download
$(shell
    [ ! -f $2 ] || exit 0;
    for url in $$($(python) -c "pass;
        import json, urllib.request;
        response = urllib.request.urlopen('https://doi.org/' + '$1'.strip());
        record = response.url.split('/')[-1];
        response = urllib.request.urlopen('https://zenodo.org/api/records/' + record);
        [print(f['links']['self']) for f in json.loads(response.read())['files']];
    "); do
        wget --no-ch $${url};
        fname=$$(basename $${url});
        tar -xvf $${fname};
        rm -f $${fname};
    done;
)
endef


# Default target
all: figure

# Figures
figure: $(addprefix figure/figure, $(addsuffix .pdf, $(figs)))
figure/figure%.pdf: script/figure%.py data-figure $(MAKEFILE_LIST)
	$(python) -B $<

# Power spectra
powerspec: script/compute_powerspec.py data-snapshot $(MAKEFILE_LIST)
	$(python) -B $<
.PHONY: powerspec


# Data
data-figure:
	@printf "$(call download, $(doi_data_figure), data/0.0eV/gadget3/z0/halo_cdm)"
.PHONY: data-figure

data-snapshot:
	@printf "$(call download, $(doi_data_snapshot), data/0.0eV/gadget3/z0/snapshot/snapshot.0)"
.PHONY: data-snapshot


# Clean
clean-powerspec:
	$(RM) data/*/gadget3/*/powerspec_*
.PHONY: clean-powerspec

clean-figure:
	$(RM) $(addprefix figure/figure, $(addsuffix .pdf, $(figs)))
.PHONY: clean-figure

clean: clean-powerspec clean-figure

