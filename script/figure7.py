from helper import *

# Specifications
mass = 0.15
sim = 'HR'
codes = [
    'class',
    'baccoemulator',
    'react',
    'hmcode',
    'halofit',
    'cosmicemu',
    'euclidemulator2',
]
z = 0
spectrum = 'cdm + ncdm'
reference = 'gadget3'
filename_figure = f'{this_dir}/../figure/figure7.pdf'

# Main function
def plot(mass, sim, codes, z, spectrum, reference, filename_figure):
    # Load and plot
    def get_spectrum_0(code):
        spectrum_0 = 'cdm'
        if code == 'baccoemulator':
            # BACCOemulator is special
            spectrum_0 = 'cdm + ncdm'
        return spectrum_0
    boxsize, gridsize = get_boxgrid(sim)
    fig, axes = plt.subplots(1, 2)
    k_desired = np.logspace(np.log10(1e-2), np.log10(1e+1), 50)
    k, power_0_ref, modes = load_powerspec(
        0, sim, reference, z, get_spectrum_0(reference), k_desired,
    )
    _, power_ref, _ = load_powerspec(
        mass, sim, reference, z, spectrum, k_desired,
    )
    ratio_ref = power_ref/power_0_ref
    for code in codes:
        _, power_0, _ = load_powerspec(
            0, sim, code, z, get_spectrum_0(code), k_desired, modes,
        )
        _, power, _ = load_powerspec(
            mass, sim, code, z, spectrum, k_desired, modes,
        )
        ratio = power/power_0
        axes[0].semilogx(k, power/power_ref - 1, **get_plot_kwargs(code))
        axes[1].semilogx(k, ratio/ratio_ref - 1, **get_plot_kwargs(code))
    # Finishing touches
    for i, ax in enumerate(axes):
        ax.grid()
        ax.set_xlabel(r'$k$ $[h\, \mathrm{Mpc}^{-1}]$', fontsize=13)
        ax.set_xlim(0.01, 10)
        ax.set_ylim([(-0.1, 0.1), (-0.02, 0.02)][i])
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
        ax.set_yticks([[-0.05, 0, 0.05, 0.1], [-0.01, 0, 0.01, 0.02]][i])
        k_nyq = 2*np.pi/boxsize*(gridsize//2)
        ax.axvline(x=k_nyq, color='grey', linestyle='dashdot', lw=2)
        ax.fill_between([1e-3, 1e+3], -0.01, +0.01, color='grey', alpha=0.2)
        variable = ['P', 'S'][i]
        ax.set_ylabel(
            (
                rf'${variable}_\mathrm{{m}}/{variable}_\mathrm{{m}}^'
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
    plot(mass, sim, codes, z, spectrum, reference, filename_figure)

