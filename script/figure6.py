from helper import *

# Specifications
mass = 0.15
sim = 'HR'
codes = [
    'gadget3',
    'opengadget3',
    'gadget4',
    'concept',
    'swift',
    'anubis',
    'gevolution',
    'class',
]
z = 0
spectra = ['cdm x ncdm', 'ncdm']
reference = 'swift'
filename_figure = f'{this_dir}/../figure/figure6.pdf'

# Main function
def plot(mass, sim, codes, z, spectra, reference, filename_figure):
    # Load and plot
    boxsize, gridsize = get_boxgrid(sim)
    fig, axes = plt.subplots(1, len(spectra))
    k_desired = np.logspace(np.log10(1e-2), np.log10(1e+1), 30)
    for spectrum, ax in zip(spectra, axes):
        k, power_ref, modes = load_powerspec(
            mass, sim, reference, z, spectrum, k_desired,
        )
        for code in codes:
            _, power, _ = load_powerspec(
                mass, sim, code, z, spectrum, k_desired, modes,
            )
            ax.semilogx(k, power/power_ref - 1, **get_plot_kwargs(code))
    # Finishing touches
    for spectrum, ax in zip(spectra, axes):
        ax.grid()
        ax.set_xlabel(r'$k$ $[h\, \mathrm{Mpc}^{-1}]$', fontsize=13)
        ax.set_xlim(0.01, 10)
        ax.set_ylim(-0.1, 0.1)
        ax.tick_params(
            direction='in', which='both',
            top=True, right=True, labelsize=10,
        )
        for tick in ax.get_yticklabels():
            tick.set_rotation(90)
            tick.set_va('center')
        ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        for attr in ['set_xticks', 'set_xticklabels']:
            getattr(ax, attr)([0.01, 0.1, 1, 10])
        ax.set_yticks([-0.05, 0, 0.05, 0.1])
        k_nyq = 2*np.pi/boxsize*(gridsize//2)
        ax.axvline(x=k_nyq, color='grey', linestyle='dashdot', lw=2)
        ax.fill_between([1e-3, 1e+3], -0.01, +0.01, color='grey', alpha=0.2)
        subscript = {'cdm x ncdm': r'{\nu,\mathrm{cb}}', 'ncdm': r'{\nu}'}[spectrum]
        ax.set_ylabel(
            (
                rf'$P_{subscript}/P_{subscript}^'
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
        plot(mass, sim, codes, z, spectra, reference, filename_figure)

