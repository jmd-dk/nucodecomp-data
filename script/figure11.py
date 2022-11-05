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
    'treelevel',
]
z = 1
spectrum = 'cdm'
reference = 'gadget3'
filename_figure = f'{this_dir}/../figure/figure11.pdf'

# Main function
def plot(mass, simulations, codes, z, spectrum, reference, filename_figure):
    def get_bispec(mass, sim, code, z, spectrum, configuration_expr, k_desired):
        if code == 'treelevel':
            bpower = get_bispec_treelevel(mass, z, spectrum, [k1, k2, k3], k_plot)
            return k1, k2, k3, bpower
        k1_read, k2_read, k3_read, bpower, _ = load_bispec(
            mass, sim, code, z, spectrum, configuration_expr, k_desired,
        )
        return k1_read, k2_read, k3_read, bpower
    # Load and plot
    fig, axes = plt.subplots(1, len(simulations))
    k_desired = np.logspace(np.log10(1e-2), np.log10(1e+1), 30)
    k_plot = 1
    for sim, ax in zip(simulations, axes):
        boxsize, _ = get_boxgrid(sim)
        k_fixed = 1*(boxsize//512)
        configuration_expr = lambda k1, k2, k3: (k1 == k2) & (k3 == k_fixed)
        k1, k2, k3, bpower_0_ref = get_bispec(
            0, sim, reference, z, spectrum, configuration_expr, k_desired,
        )
        _, _, _, bpower_ref = get_bispec(
            mass, sim, reference, z, spectrum, configuration_expr, k_desired,
        )
        ratio_ref = bpower_ref/bpower_0_ref
        for code in codes:
            _, _, _, bpower_0 = get_bispec(
                0, sim, code, z, spectrum, configuration_expr, k_desired,
            )
            _, _, _, bpower = get_bispec(
                mass, sim, code, z, spectrum, configuration_expr, k_desired,
            )
            ratio = bpower/bpower_0
            ax.semilogx((k1, k2, k3)[k_plot - 1], ratio/ratio_ref - 1, **get_plot_kwargs(code))
    # Finishing touches
    for sim, ax in zip(simulations, axes):
        ax.set_title(
            {'1024Mpc': 'larger volume', 'HR': 'higher resolution'}[sim],
            x=0.2, y=0.9,
            bbox={'fc': 'white', 'ec': 'white'},
        )
        ax.grid()
        ax.set_xlabel(r'$k$ $[h\, \mathrm{Mpc}^{-1}]$', fontsize=13)
        ax.set_xlim(0.01, 1)
        ax.set_ylim(-0.04, 0.04)
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
        ax.set_yticks([-0.02, 0, 0.02, 0.04])
        ax.fill_between([1e-3, 1e+3], -0.01, +0.01, color='grey', alpha=0.2)
    axes[0].set_ylabel(
        (
            rf'$T_\mathrm{{ccc}}/T_\mathrm{{ccc}}^'
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
    if not os.path.isfile(filename_figure):
        plot(mass, simulations, codes, z, spectrum, reference, filename_figure)

