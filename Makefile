# Python interpreter
python ?= python3
# Figures to produce
figs = 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17


# Default target
all: powerspec
	@$(MAKE) --no-print-directory figure


# Power spectra
powerspec: script/compute_powerspec.py
	$(python) -B $<
.PHONY: powerspec


# Figures
figure: $(addprefix figure/figure, $(addsuffix .pdf, $(figs)))
figure/figure%.pdf: script/figure%.py $(MAKEFILE_LIST)
	$(python) -B $<


# Clean targets
clean-powerspec:
	$(RM) data/*/gadget3/*/powerspec_*
.PHONY: clean-powerspec

clean-figure:
	$(RM) $(addprefix figure/figure, $(addsuffix .pdf, $(figs)))
.PHONY: clean-figure

clean: clean-powerspec clean-figure

