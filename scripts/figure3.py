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
    'pinocchio',
    'class',
    'baccoemulator',
    'react',
]
redshifts = [0, 1]
spectrum = 'cdm'
reference = 'gadget3'
filename_figure = f'{this_dir}/../figures/figure3.pdf'

# Main function
def plot(mass, sim, codes, redshifts, spectrum, reference, filename_figure):
    # Load and plot
    boxsize, gridsize = get_boxgrid(sim)
    fig, axes = plt.subplots(1, len(redshifts))
    k_desired = np.logspace(np.log10(1e-2), np.log10(1e+1), 50)
    for z, ax in zip(redshifts, axes):
        k, power_0_ref, modes = load_powerspec(
            0, sim, reference, z, spectrum, k_desired,
        )
        _, power_ref, _ = load_powerspec(
            mass, sim, reference, z, spectrum, k_desired,
        )
        ratio_ref = power_ref/power_0_ref
        for code in codes:
            _, power_0, _ = load_powerspec(
                0, sim, code, z, spectrum, k_desired, modes,
            )
            _, power, _ = load_powerspec(
                mass, sim, code, z, spectrum, k_desired, modes,
            )
            ratio = power/power_0
            ax.semilogx(k, ratio/ratio_ref - 1, **get_plot_kwargs(code))
    # Finishing touches
    for z, ax in zip(redshifts, axes):
        ax.set_title(
            rf'$z = {z}$',
            x=0.1, y=0.9,
            bbox={'fc': 'white', 'ec': 'white'},
        )
        ax.grid()
        ax.set_xlabel(r'$k$ $[h\, \mathrm{Mpc}^{-1}]$', fontsize=13)
        ax.set_xlim(0.01, 5)
        ax.set_ylim(-0.02, 0.02)
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
        ax.set_yticks([-0.01, 0, 0.01, 0.02])
        k_nyq = 2*np.pi/boxsize*(gridsize//2)
        ax.axvline(x=k_nyq, color='grey', linestyle='dashdot', lw=2)
        ax.fill_between([1e-3, 1e+3], -0.01, +0.01, color='grey', alpha=0.2)
    axes[0].set_ylabel(
        (
            rf'$S_\mathrm{{cb}}/S_\mathrm{{cb}}^'
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

