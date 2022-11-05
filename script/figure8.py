from helper import *

# Specifications
masses = [0, 0.15, 0.3, 0.6]
sim = 'fiducial'
codes = [
    'lgadget3',
    'nmgadget4',
    'arepo',
    'concept',
    'pkdgrav3',
    'cola',
    'opengadget3',
    'swift',
    'anubis',
    'gevolution',
    'gadget4',
]
z = 1
spectrum = 'cdm'
reference = 'gadget3'
filename_figure = f'{this_dir}/../figure/figure8.pdf'

# Main function
def plot(masses, sim, codes, z, spectrum, reference, filename_figure):
    def first_duplicate(a):
        a = (a/k_fundamental).round().astype(int)
        b = np.zeros(a.size, dtype=int)
        seen = set()
        for i, el in enumerate(a, 1):
            if el not in seen:
                b[el] = i
            seen.add(el)
        return b[b != 0]
    def get_subpanel(panel, code):
        for subpanel, ax in zip(codes_subpanels, panel):
            if code in subpanel:
                return ax
    boxsize, _ = get_boxgrid(sim)
    k_fundamental = 2*np.pi/boxsize
    codes_subpanels = [
        ['lgadget3', 'nmgadget4', 'arepo'                    ],
        ['concept',  'pkdgrav3',  'cola',       'opengadget3'],
        ['swift',    'anubis',    'gevolution', 'gadget4'    ],
    ]
    # Load and plot
    k_fundamental = 2*np.pi/boxsize
    fig, axes = plt.subplots(7, 2, figsize=(9, 11),
        gridspec_kw={
            'left': 0.06, 'right': 0.99, 'bottom': 0.04, 'top': 0.97,
            'wspace': 0.15, 'hspace': 0, 'height_ratios': [1, 1, 1, 0.45, 1, 1, 1],
        },
    )
    for ax in axes[3, :]:
        ax.set_visible(False)
    panels = {
        0   : axes[ :3, 0],
        0.15: axes[ :3, 1],
        0.3 : axes[4:7, 0],
        0.6 : axes[4:7, 1],
    }
    for mass in masses:
        panel = panels[mass]
        k1, _, _, bpower_reference, _ = load_bispec(mass, sim, reference, z, spectrum)
        kver = first_duplicate(k1)
        minplot = np.empty(kver.size - 1)
        maxplot = np.empty(kver.size - 1)
        for code in codes:
            ax = get_subpanel(panel, code)
            _, _, _, bpower, _ = load_bispec(mass, sim, code, z, spectrum)
            relative = bpower/bpower_reference - 1
            for i, (j1, j2) in enumerate(zip(kver, kver[1:])):
                minplot[i] = np.min(relative[j1:j2])
                maxplot[i] = np.max(relative[j1:j2])
            ax.fill_between(
                k1[kver[:-1]], minplot, maxplot,
                alpha=0.5, **get_plot_kwargs(code, pop='linestyle'),
            )
    # Finishing touches
    for mass in masses:
        panel = panels[mass]
        panel[0].set_title(rf'${mass}\, \mathrm{{eV}}$')
        panel[1].set_ylabel(
            (
                rf'$B_\mathrm{{ccc}} / B_\mathrm{{ccc}}^'
                rf'{{({codespecs[reference].label})}} - 1$'
            ),
            fontsize=13,
        )
        panel[2].set_xlabel(r'$k_\mathrm{max}$ $[h\, \mathrm{Mpc}^{-1}]$', fontsize=13)
    for ax in axes.flatten():
        ax.grid()
        ax.set_ylim(-0.2, 0.2)
        ax.tick_params(
            direction='in', which='both',
            top=True, right=True, labelsize=10,
        )
        for tick in ax.get_yticklabels():
            tick.set_rotation(90)
            tick.set_va('center')
        for attr in ('xaxis', 'yaxis'):
            getattr(ax, attr).set_major_formatter(
                matplotlib.ticker.FormatStrFormatter('%g')
            )
        ax.set_xticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticks([-0.1, 0, 0.1])
        if ax.get_visible():
            ax.legend(
                loc='upper right',
                ncol=4,
                fontsize='small',
                handletextpad=0.5,
                columnspacing=0.5,
            )
    os.makedirs(os.path.dirname(filename_figure), exist_ok=True)
    fig.savefig(filename_figure)

if __name__ == '__main__':
    if not os.path.isfile(filename_figure):
        plot(masses, sim, codes, z, spectrum, reference, filename_figure)

