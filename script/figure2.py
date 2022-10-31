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
filename_figure = f'{this_dir}/../figure/figure2.pdf'

# Main function
def plot(masses, sim, codes, redshifts, spectrum, filename_figure):
    # Load and plot
    boxsize, gridsize = get_boxgrid(sim)
    fig, axes = plt.subplots(1, len(redshifts))
    k_desired = np.logspace(np.log10(1e-2), np.log10(1e+1), 50)
    modes = None
    for z, ax in zip(redshifts, axes):
        for code in codes:
            k, power_0, modes = load_powerspec(
                0, sim, code, z, spectrum, k_desired, modes,
            )
            for i, mass in enumerate(masses):
                _, power, _ = load_powerspec(
                    mass, sim, code, z, spectrum, k_desired, modes,
                )
                ax.semilogx(
                    k, power/power_0,
                    **get_plot_kwargs(code, pop='label'*(i != 0)),
                )
    # Finishing touches
    for z, ax in zip(redshifts, axes):
        ax.set_title(
            rf'$z = {z}$',
            x=0.1, y=0.1,
            bbox={'fc': 'white', 'ec': 'white'},
        )
        ax.grid()
        ax.set_xlabel(r'$k$ $[h\, \mathrm{Mpc}^{-1}]$', fontsize=13)
        ax.set_xlim(0.01, 5)
        ax.set_ylim(0.5, 1)
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
        ax.set_yticks([0.6, 0.7, 0.8, 0.9, 1.0])
        k_nyq = 2*np.pi/boxsize*(gridsize//2)
        ax.axvline(x=k_nyq, color='grey', linestyle='dashdot', lw=2)
        ax.text(
            0.1, 0.96, r'$0.15\, \mathrm{eV}$',
            fontsize='small', rotation=-4,
        )
        ax.text(
            0.1, 0.89, r'$0.3\, \mathrm{eV}$',
            fontsize='small', rotation=(-9 - (z - 1)*5),
        )
        ax.text(
            0.1, 0.76 - (z - 1)*0.01, r'$0.6\, \mathrm{eV}$',
            fontsize='small', rotation=(-22 - (z - 1)*13),
        )
    axes[0].set_ylabel(
        (
            r'$S_\mathrm{cb} \equiv P_{\mathrm{cb}}^{\mathrm{(massive)}}'
            r'/P_{\mathrm{cb}}^\mathrm{(massless)}$'
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

