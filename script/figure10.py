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
    'treelevel',
]
z = 1
spectrum = 'cdm'
reference = 'gadget3'
filename_figure = f'{this_dir}/../figure/figure10.pdf'

# Main function
def plot(masses, sim, codes, z, spectrum, reference, filename_figure):
    def get_bispec(mass, sim, code, z, spectrum, configuration_expr, k_desired):
        if code == 'treelevel':
            bpower = get_bispec_treelevel(mass, z, spectrum, [k1, k2, k3], configuration.k_plot)
            return k1, k2, k3, bpower
        k1_read, k2_read, k3_read, bpower, _ = load_bispec(
            mass, sim, code, z, spectrum, configuration_expr, k_desired,
        )
        return k1_read, k2_read, k3_read, bpower
    # Load and plot
    fig, axes = plt.subplots(9, 2, figsize=(9, 11),
        gridspec_kw={
            'left': 0.06, 'right': 0.99, 'bottom': 0.04, 'top': 0.91,
            'wspace': 0.15, 'hspace': 0, 'height_ratios': [2.5, 1, 1, 1, 0.9, 2.5, 1, 1, 1],
        },
    )
    for ax in axes[4, :]:
        ax.set_visible(False)
    boxsize, _ = get_boxgrid(sim)
    k_fundamental = 2*np.pi/boxsize
    k_desired = np.logspace(np.log10(1e-2), np.log10(1e+1), 30)
    k_fixed = {
        'squeezed':    [None, None,    1],
        'equilateral': [None, None, None],
        'scaleneA':    [  64,   46, None],
        'scaleneB':    [  32, None,   16],
    }
    Configuration = collections.namedtuple(
        'Configuration',
        ['panel', 'expr', 'k_plot', 'title', 'k_desired'],
        defaults=[None],
    )
    configurations = {
        'squeezed': Configuration(
            axes[:4, 0], lambda k1, k2, k3: (k1 == k2) & (k3 == k_fixed['squeezed'][2]), 1,
            (
                rf'Squeezed triangles: $k_1=k_2\equiv k$, '
                rf'$k_3 = {k_fixed["squeezed"][2]*k_fundamental:.2g}\, h\, \mathrm{{Mpc}}^{{-1}}$'
            ),
            k_desired,
        ),
        'equilateral': Configuration(
            axes[ :4, 1], lambda k1, k2, k3: (k1 == k2) & (k2 == k3), 1,
            r'Equilateral triangles: $k_1=k_2=k_3 \equiv k$',
            k_desired,
        ),
        'scaleneA': Configuration(
            axes[5:9, 0], lambda k1, k2, k3: (k1 == k_fixed['scaleneA'][0]) & (k2 == k_fixed['scaleneA'][1]), 3,
            (
                rf'Scalene triangles: $k_1={k_fixed["scaleneA"][0]*k_fundamental:.2g}\, h\, \mathrm{{Mpc}}^{{-1}}$, '
                rf'$k_2={k_fixed["scaleneA"][1]*k_fundamental:.2g}\, h\, \mathrm{{Mpc}}^{{-1}}$'
            ),
        ),
        'scaleneB': Configuration(
            axes[5:9, 1], lambda k1, k2, k3: (k1 == k_fixed['scaleneB'][0]) & (k3 == k_fixed['scaleneB'][2]), 2,
            (
                rf'Scalene triangles: $k_1={k_fixed["scaleneB"][0]*k_fundamental:.2g}\, h\, \mathrm{{Mpc}}^{{-1}}$, '
                rf'$k_3={k_fixed["scaleneB"][2]*k_fundamental:.2g}\, h\, \mathrm{{Mpc}}^{{-1}}$'
            ),
        ),
    }
    for configuration in configurations.values():
        k1, k2, k3, bpower_0_ref = get_bispec(
            0, sim, reference, z, spectrum, configuration.expr, configuration.k_desired,
        )
        ratios_ref = {}
        for mass in masses:
            _, _, _, bpower_ref = get_bispec(
                mass, sim, reference, z, spectrum, configuration.expr, configuration.k_desired,
            )
            ratios_ref[mass] = bpower_ref/bpower_0_ref
        for code in codes:
            _, _, _, bpower_0 = get_bispec(
                0, sim, code, z, spectrum, configuration.expr, configuration.k_desired,
            )
            for i, mass in enumerate(masses):
                _, _, _, bpower = get_bispec(
                    mass, sim, code, z, spectrum, configuration.expr, configuration.k_desired,
                )
                # Upper subpanel
                ratio = bpower/bpower_0
                configuration.panel[0].semilogx(
                    (k1, k2, k3)[configuration.k_plot - 1], ratio,
                    **get_plot_kwargs(code, pop='label'*(i != 0)),
                )
                # Lower subpanels
                configuration.panel[1 + i].semilogx(
                    (k1, k2, k3)[configuration.k_plot - 1], ratio/ratios_ref[mass] - 1,
                    **get_plot_kwargs(code),
                )
    # Finishing touches
    fig.legend(
        *axes[0, 0].get_legend_handles_labels(),
        loc='lower center',
        bbox_to_anchor=(0.02, 0.93, 1, 1),
        ncol=6,
    )
    for ax in axes.flatten():
        ax.grid()
        ax.tick_params(
            direction='in', which='both',
            top=True, right=True, labelsize=10,
        )
        for tick in ax.get_yticklabels():
            tick.set_rotation(90)
            tick.set_va('center')
        ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
    for configuration_name, configuration in configurations.items():
        configuration.panel[0].set_title(configuration.title, fontsize=12.4)
        configuration.panel[0].set_ylabel(
            (
                r'$T_\mathrm{ccc} \equiv B_\mathrm{ccc}^\mathrm{(massive)}/'
                r'B_\mathrm{ccc}^\mathrm{(massless)}$'
            ),
            fontsize=13,
        )
        configuration.panel[2].set_ylabel(
            (
                rf'$T_\mathrm{{ccc}}/T_\mathrm{{ccc}}^'
                rf'{{({codespecs[reference].label})}}-1$'
            ),
            fontsize=13,
        )
        configuration.panel[3].set_xlabel(
            rf'$k_{configuration.k_plot}$ $[h\, \mathrm{{Mpc}}^{{-1}}]$'.replace('k_1', 'k'),
            fontsize=13,
        )
        configuration.panel[0].set_ylim(*
            ((0.5, 1) if configuration_name == 'squeezed' else (0.3, 1))
        )
        configuration.panel[0].set_yticks(            
            [0.6, 0.7, 0.8, 0.9, 1]
            if configuration_name == 'squeezed' else
            [0.4, 0.6, 0.8, 1]
        )
        for mass, ax in zip(masses, configuration.panel[1:]):
            ax.fill_between([1e-3, 1e+3], -0.01, +0.01, color='grey', alpha=0.2)
            ax.set_title(
                rf'${mass}\, \mathrm{{eV}}$',
                x=0.065, y=0.05,
                bbox={'fc': 'white', 'ec': 'white', 'boxstyle': 'round'},
                fontsize='small',
            )
            configuration.panel[0].text(
                *{
                    'squeezed':    {0.15: (0.50, 0.93), 0.3: (0.40, 0.710), 0.6: (0.30, 0.55)},
                    'equilateral': {0.15: (0.40, 0.90), 0.3: (0.50, 0.695), 0.6: (0.50, 0.45)},
                    'scaleneA':    {0.15: (0.40, 0.90), 0.3: (0.40, 0.700), 0.6: (0.40, 0.45)},
                    'scaleneB':    {0.15: (0.32, 0.90), 0.3: (0.32, 0.770), 0.6: (0.32, 0.55)},
                }[configuration_name][mass],
                rf'${mass}\, \mathrm{{eV}}$',
                fontsize='small',
            )
            ax.set_ylim(-0.08, 0.08)
            ax.set_yticks([-0.05, 0, 0.05])
        for ax in configuration.panel:
            ax.set_xlim(*
                {
                    'scaleneA': (0.2, 0.6),
                    'scaleneB': (0.2, 0.4),
                }.get(configuration_name, (1e-2, 1)),
            )
            ax.set_xscale('linear' if configuration_name.startswith('scalene') else 'log')
            ax.set_xticks(
                {
                    'scaleneA': [0.2, 0.3, 0.4, 0.5, 0.6],
                    'scaleneB': [0.2, 0.25, 0.3, 0.35, 0.4],
                }.get(configuration_name, [0.01, 0.1, 1]),
            )
            ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
        for ax in configuration.panel[:-1]:
            ax.set_xticklabels([])
    os.makedirs(os.path.dirname(filename_figure), exist_ok=True)
    fig.savefig(filename_figure)

if __name__ == '__main__':
    plot(masses, sim, codes, z, spectrum, reference, filename_figure)

