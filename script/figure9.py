from helper import *

# Specifications
mass = 0.15
sim = 'fiducial'
codes = [
    'gadget3',
    'lgadget3',
    'opengadget3',
    'gadget4',
    'nmgadget4',
    'arepo',
    'concept',
    'pkdgrav3',
    'swift',
    'anubis',
    'gevolution',
    'cola',
]
redshifts = [0, 1]
spectrum = 'cdm'
reference = 'gadget3'
filename_figure = f'{this_dir}/../figure/figure9.pdf'

# Main function
def plot(mass, sim, codes, redshifts, spectrum, reference, filename_figure):
    # Load and plot
    fig, axes = plt.subplots(1, len(redshifts))
    k_desired = np.logspace(np.log10(1e-2), np.log10(1e+1), 30)
    k_fixed = 1
    configuration_expr = lambda k1, k2, k3: (k1 == k2) & (k3 == k_fixed)
    k_plot = 1
    for z, ax in zip(redshifts, axes):
        k1, k2, k3, bpower_ref, _ = load_bispec(
            mass, sim, reference, z, spectrum, configuration_expr, k_desired,
        )
        for code in codes:
            _, _, _, bpower, _ = load_bispec(
                mass, sim, code, z, spectrum, configuration_expr, k_desired,
            )
            ax.semilogx(
                (k1, k2, k3)[k_plot - 1],
                bpower/bpower_ref - 1,
                **get_plot_kwargs(code),
            )
    # Finishing touches
    for z, ax in zip(redshifts, axes):
        ax.set_title(
            rf'$z = {z}$',
            x=0.2, y=0.9,
            bbox={'fc': 'white', 'ec': 'white'},
        )
        ax.grid()
        ax.set_xlabel(r'$k$ $[h\, \mathrm{Mpc}^{-1}]$', fontsize=13)
        ax.set_xlim(0.01, 1)
        ax.set_ylim(-0.08, 0.08)
        ax.tick_params(
            direction='in', which='both',
            top=True, right=True, labelsize=10,
        )
        for tick in ax.get_yticklabels():
            tick.set_rotation(90)
            tick.set_va('center')
        ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        for attr in ['set_xticks', 'set_xticklabels']:
            getattr(ax, attr)([0.01, 0.1, 1])
        ax.set_yticks([-0.05, 0, 0.05])
        ax.fill_between([1e-3, 1e+3], -0.01, +0.01, color='grey', alpha=0.2)
    axes[0].set_ylabel(
        (
            rf'$B_\mathrm{{ccc}}/B_\mathrm{{ccc}}^'
            rf'{{({codespecs[reference].label})}} - 1$'
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
    plot(mass, sim, codes, redshifts, spectrum, reference, filename_figure)

