from helper import *

# Specifications
masses = [0.15, 0.3, 0.6]
sim = 'fiducial'
codes = [
    'gadget3',
    'lgadget3',
    'opengadget3',
    'gadget4',
    'nmgadget4',
    'concept',
    'pkdgrav3',
    'swift',
    'anubis',
    'gevolution',
    'cola',
    'pinocchio',
    'tinker10',
    'despali16',
]
redshifts = [0, 1]
spectrum = 'cdm'
filename_figure = f'{this_dir}/../figures/figure13.pdf'

# Main function
def plot(masses, sim, codes, redshifts, spectrum, filename_figure):
    # Load and plot
    fig, axes = plt.subplots(1, len(redshifts))
    bins = np.logspace(11.7, 15, 10)
    for z, ax in zip(redshifts, axes):
        for code in codes:
            bin_centers, counts_0 = load_halo(
                0, sim, code, z, spectrum, bins=bins,
            )
            for i, mass in enumerate(masses):
                bin_centers, counts = load_halo(
                    mass, sim, code, z, spectrum, bins=bins,
                )
                ax.semilogx(
                    bin_centers, counts/counts_0,
                    **get_plot_kwargs(code, pop='label'*(i != 0)),
                )
    # Finishing touches
    for z, ax in zip(redshifts, axes):
        ax.set_title(
            f'$z = {z}$',
            x=0.48, y=0.88,
            bbox={'fc': 'white', 'ec': 'white'},
        )
        ax.grid()
        ax.set_xlabel(r'$M_\mathrm{200b}$ $[h^{-1} M_{\odot}]$', fontsize=13)
        ax.set_xlim(7e11, 8e14)
        ax.set_ylim(0, 1.2)
        ax.tick_params(
            direction='in', which='both',
            top=True, right=True, labelsize=10,
        )
        for tick in ax.get_yticklabels():
            tick.set_rotation(90)
            tick.set_va('center')
        ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1, 1.2])
        for mass in masses:
            pos, rot = {
                0: {
                    0.15: ((1e14, 0.97),  -5),
                    0.3:  ((1e14, 0.70), -25),
                    0.6:  ((1e14, 0.50), -35),
                },
                1: {
                    0.15: ((2e13, 0.94),  -5),
                    0.3:  ((2e13, 0.63), -30),
                    0.6:  ((2e13, 0.40), -40),
                },
            }[z][mass]
            ax.text(*pos, rf'${mass}\, \mathrm{{eV}}$', rotation=rot, fontsize='small')
    axes[0].set_ylabel(
        (
            r'$R \equiv {\frac{\mathrm{d}n}{\mathrm{d}\ln M}}^\mathrm{(massive)}/'
            r'{\frac{\mathrm{d}n}{\mathrm{d}\ln M}}^\mathrm{(massless)}$'
        ),
        fontsize=13,
    )
    plt.subplots_adjust(
        left=0.06, right=0.99,
        bottom=0.1, top=0.8,
        wspace=0.15, hspace=0.17,
    )
    fig.legend(
        *axes[0].get_legend_handles_labels(),
        loc='lower center',
        bbox_to_anchor=(0.02, 0.82, 1, 1),
        ncol=6,
    )
    os.makedirs(os.path.dirname(filename_figure), exist_ok=True)
    fig.savefig(filename_figure)

if __name__ == '__main__':
    plot(masses, sim, codes, redshifts, spectrum, filename_figure)

