from helper import *

# Specifications
mass = 0.15
sim = '1024Mpc'
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
]
z = 0
spectra = ('cdm x halo1e+13ref', 'cdm')
reference = 'gadget3'
filename_figure = f'{this_dir}/../figure/figure15.pdf'

# Main function
def plot(mass, sim, codes, z, spectra, reference, filename_figure):
    # Load and plot
    boxsize, gridsize = get_boxgrid(sim)
    fig, axes = plt.subplots(2, 2, figsize=(9, 6))
    k_desired = np.logspace(np.log10(1e-2), np.log10(1e+1), 50)
    def load_biases(code, modes=None):
        def load_bias(mass, modes):
            k, power_cdmxhalo, modes = load_powerspec(
                mass, sim, code, z, spectra[0], k_desired, modes,
            )
            _, power, _ = load_powerspec(
                mass, sim, code, z, spectra[1], k_desired, modes,
            )
            bias = power_cdmxhalo/power
            return k, bias, modes
        k, bias_0, modes = load_bias(0, modes)
        _, bias, _ = load_bias(mass, modes)
        return k, bias_0, bias, modes
    k, bias_0_ref, bias_ref, modes = load_biases(reference)
    ratio_ref = bias_ref/bias_0_ref
    for code in codes:
        _, bias_0, bias, _ = load_biases(code, modes)
        ratio = bias/bias_0
        axes[0, 0].semilogx(k, bias, **get_plot_kwargs(code))
        axes[0, 1].semilogx(k, ratio, **get_plot_kwargs(code))
        axes[1, 0].semilogx(k, bias/bias_ref - 1, **get_plot_kwargs(code))
        axes[1, 1].semilogx(k, ratio/ratio_ref - 1, **get_plot_kwargs(code))
    # Finishing touches
    for i, ax in enumerate(axes.flatten()):
        ax.grid()
        ax.set_xlabel(r'$k$ $[h\, \mathrm{Mpc}^{-1}]$', fontsize=13)
        ax.set_xlim(1e-2, 5)
        ax.set_ylim(*[(1, 1.8), (1, 1.1), (-0.04, 0.1), (-0.02, 0.02)][i])
        ax.tick_params(
            direction='in', which='both',
            top=True, right=True, labelsize=10,
        )
        for tick in ax.get_yticklabels():
            tick.set_rotation(90)
            tick.set_va('center')
        ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        ax.set_yticks([
            [1.2, 1.4, 1.6, 1.8],
            [1.025, 1.05, 1.075, 1.1],
            [0, 0.04, 0.08],
            [-0.01, 0, .01],
        ][i])
        k_nyq = 2*np.pi/boxsize*(gridsize//2)
        ax.axvline(x=k_nyq, color='grey', linestyle='dashdot', lw=2)
        if i in {2, 3}:
            ax.fill_between([1e-3, 1e+3], -0.01, +0.01, color='grey', alpha=0.2)
        ax.set_ylabel(
            [
                r'$b = P_\mathrm{h,cb}/P_\mathrm{cb}$',
                r'$Q \equiv b^\mathrm{(massive)}/b^\mathrm{(massless)}$',
                rf'$b/b^{{({codespecs[reference].label})}} - 1$',
                rf'$Q/Q^{{({codespecs[reference].label})}} - 1$',
            ][i],
            fontsize=13,
        )
    for ax in axes[0, :]:
        ax.set_xticklabels([])
    plt.subplots_adjust(
        left=0.06, right=0.99,
        bottom=0.08, top=0.85,
        wspace=0.15, hspace=0,
    )
    fig.legend(
        *axes[0, 0].get_legend_handles_labels(),
        loc='lower center',
        bbox_to_anchor=(0.02, 0.87, 1, 1),
        ncol=6,
    )
    os.makedirs(os.path.dirname(filename_figure), exist_ok=True)
    fig.savefig(filename_figure)

if __name__ == '__main__':
    if not os.path.isfile(filename_figure):
        plot(mass, sim, codes, z, spectra, reference, filename_figure)

