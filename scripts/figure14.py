from helper import *

# Specifications
mass = 0.15
simulations = ['1024Mpc', 'HR']
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
z = 0
spectrum = 'cdm'
reference = 'gadget3'
filename_figure = f'{this_dir}/../figures/figure14.pdf'

# Main function
def plot(mass, simulations, codes, z, spectrum, reference, filename_figure):
    # Load and plot
    fig, axes = plt.subplots(1, len(simulations))
    bins = np.logspace(11.7, 15, 10)
    for sim, ax in zip(simulations, axes):
        bin_centers, counts_0_ref = load_halo(
            0, sim, reference, z, spectrum, bins=bins,
        )
        _, counts_ref = load_halo(
            mass, sim, reference, z, spectrum, bins=bins,
        )
        ratio_ref = counts_ref/counts_0_ref
        for code in codes:
            _, counts_0 = load_halo(
                0, sim, code, z, spectrum, bins=bins,
            )
            _, counts = load_halo(
                mass, sim, code, z, spectrum, bins=bins,
            )
            ratio = counts/counts_0
            ax.semilogx(
                bin_centers, ratio/ratio_ref - 1,
                **get_plot_kwargs(code),
            )
    # Finishing touches
    for sim, ax in zip(simulations, axes):
        ax.set_title(
            {'1024Mpc': 'larger volume', 'HR': 'higher resolution'}[sim],
            x=0.8, y=0.9,
            bbox={'fc': 'white', 'ec': 'white'},
        )
        ax.grid()
        ax.set_xlabel(r'$M_\mathrm{200b}$ $[h^{-1} M_{\odot}]$', fontsize=13)
        ax.set_xlim(7e11, 8e14)
        ax.set_ylim(-0.04, 0.04)
        ax.tick_params(
            direction='in', which='both',
            top=True, right=True, labelsize=10,
        )
        for tick in ax.get_yticklabels():
            tick.set_rotation(90)
            tick.set_va('center')
        ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        ax.set_yticks([-0.02, 0, 0.02, 0.04])
        ax.fill_between([1e+0, 1e+20], -0.01, +0.01, color='grey', alpha=0.2)
    axes[0].set_ylabel(
        rf'$R/R^{{({codespecs[reference].label})}} - 1$',
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
    plot(mass, simulations, codes, z, spectrum, reference, filename_figure)

