import collections, contextlib, functools, itertools, io, os, re, sys
from glob import glob
import numpy as np
import matplotlib; matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.ticker
import scipy.interpolate
import classy                               # CLASS
import readgadget, MAS_library, Pk_library  # Pylians


# Absolute path to the script directory
this_dir = os.path.dirname(os.path.abspath(__file__))

# Set up Matplotlib
plt.rcParams.update({
    'figure.figsize': (9, 4.5),  # default, changed by some figures
    'text.usetex': True,
    'text.latex.preamble': r'\usepackage{amsmath}',
    'font.family': 'serif',
    'legend.edgecolor': 'black',
    'lines.linewidth': 2,
})

# Code specification
CodeSpec = collections.namedtuple(
    'CodeSpec',
    ('name', 'label', 'color', 'linestyle', 'is_simulation'),
    defaults=[True],
)
codespecs = {
    # Simulation codes
    'gadget3':         CodeSpec('gadget3',         r'\texttt{GADGET-3}',                         '#CC6677', 'solid'),
    'lgadget3':        CodeSpec('lgadget3',        r'\texttt{L-GADGET3}',                        '#4477AA', 'dashed'),
    'opengadget3':     CodeSpec('opengadget3',     r'\texttt{openGADGET3}',                      '#332288', 'solid'),
    'gadget4':         CodeSpec('gadget4',         r'\texttt{GADGET-4}',                         '#DDCC77', 'solid'),
    'nmgadget4':       CodeSpec('nmgadget4',       r'\texttt{NM-GADGET4}',                       '#EE6677', 'dashed'),
    'arepo':           CodeSpec('arepo',           r'\texttt{AREPO}',                            '#117733', 'solid'),
    'concept':         CodeSpec('concept',         r'\texttt{CO\textit{N}\hspace{-0.04em}CEPT}', '#228833', 'dashed'),
    'pkdgrav3':        CodeSpec('pkdgrav3',        r'\texttt{PKDGRAV3}',                         '#CCBB44', 'dashed'),
    'swift':           CodeSpec('swift',           r'\texttt{SWIFT}',                            '#88CCEE', 'solid'),
    'anubis':          CodeSpec('anubis',          r'\texttt{ANUBIS}',                           '#882255', 'solid'),
    'gevolution':      CodeSpec('gevolution',      r'\texttt{gevolution}',                       '#44AA99', 'solid'),
    'cola':            CodeSpec('cola',            r'\texttt{COLA}',                             '#66CCEE', 'dashed'),
    'pinocchio':       CodeSpec('pinocchio',       r'{\texttt{PINOCCHIO}',                       '#AA3377', 'dashed'),
    # Boltzmann solvers, emulators and fitting methods
    'class':           CodeSpec('class',           r'\texttt{CLASS}',                            '#CC6677', 'dotted', is_simulation=False),
    'baccoemulator':   CodeSpec('baccoemulator',   r'\texttt{BACCOemulator}',                    '#332288', 'dotted', is_simulation=False),
    'react':           CodeSpec('react',           r'\texttt{ReACT}',                            '#DDCC77', 'dotted', is_simulation=False),
    'hmcode':          CodeSpec('hmcode',          r'\texttt{HMcode}',                           '#117733', 'dotted', is_simulation=False),
    'halofit':         CodeSpec('halofit',         r'\texttt{halofit}',                          '#88CCEE', 'dotted', is_simulation=False),
    'cosmicemu':       CodeSpec('cosmicemu',       r'\texttt{CosmicEmu}',                        '#882255', 'dotted', is_simulation=False),
    'euclidemulator2': CodeSpec('euclidemulator2', r'\texttt{EuclidEmulator2}',                  '#44AA99', 'dotted', is_simulation=False),
    'treelevel':       CodeSpec('treelevel',       r'\texttt{tree-level}',                       '#CC6677', 'dotted', is_simulation=False),
    'tinker10':        CodeSpec('tinker10',        r'\texttt{Tinker10}',                         '#ABABAB', 'dotted', is_simulation=False),
    'despali16':       CodeSpec('despali16',       r'\texttt{Despali16}',                        '#595959', 'dotted', is_simulation=False),
}

# Patch part of Pylians to suppress unwanted output to screen
def patch_pylians(lib, funcname, silence=()):
    def _func(*args, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()) as f:
            results = func_ori(*args, **kwargs)
        lines = f.getvalue().strip().split('\n')
        for line in lines:
            if not line:
                continue
            if any(line.startswith(s) for s in silence):
                continue
            print(line)
        return results
    func_ori = getattr(lib, funcname)
    setattr(lib, funcname, _func)
patch_pylians(Pk_library, 'expected_Pk', ['Time'])
patch_pylians(Pk_library, 'XPk', ['Time', 'Computing'])

# Helper functions used by the figure scripts
def load_halo(
    mass, sim, code, z, spectrum, *,
    threshold=None, bins=None,
):
    # For a few codes we have the precomputed halo mass function stored
    filename = get_filename(mass, sim, code, z, f'hmf_{spectrum}')
    if bins is not None and os.path.isfile(filename):
        counts, bin_edges = np.histogram(1, bins=bins)
        bin_centers = np.sqrt(bin_edges[1:]*bin_edges[:-1])
        bin_centers_file, hmf = loadtxt(
            mass, sim, code, z, f'hmf_{spectrum}', unpack=True,
        )
        hmf = np.exp(
            scipy.interpolate.interp1d(
                np.log(bin_centers_file), np.log(hmf),
                kind='linear', fill_value='extrapolate',
            )(np.log(bin_centers))
        )
        boxsize, _ = get_boxgrid(sim)
        counts = hmf*boxsize**3*np.diff(bins)/bin_centers
        return bin_centers, counts
    # For most codes we have the halo catalogs stored
    halomasses, x, y, z = loadtxt(
        mass, sim, code, z, f'halo_{spectrum}', dtype=np.float32, unpack=True,
    )
    pos = np.array((x, y, z)).T
    if threshold is not None:
        if isinstance(threshold, int):
            # Select the `threshold` most massive halos
            selection = halomasses.argsort()[-threshold:]
        else:
            # Select halos with masses above `threshold`
            selection = (halomasses > float(threshold))
        halomasses = halomasses[selection]
        pos = pos[selection]
    if bins is None:
        return halomasses, pos
    # Return halo mass function
    counts, bin_edges = np.histogram(halomasses, bins=bins)
    bin_centers = np.sqrt(bin_edges[1:]*bin_edges[:-1])
    return bin_centers, counts
def get_bispec_treelevel(mass, z, spectrum, k_vec, k_plot):
    # Transform k_vec[:] to scalars or the k to be plotted
    collapse = lambda k: k_vec[k_plot - 1] if len(set(k)) > 1 else k[0]
    k_vec = [collapse(k) for k in k_vec]
    # Construct tree-level bispectrum from CLASS power spectrum
    sim, code = 'fiducial', 'class'
    k, power, _ = load_powerspec(mass, sim, code, z, spectrum)
    power /= (2*np.pi)**3  # use a different Fourier convention
    spline = scipy.interpolate.interp1d(
        np.log(k),
        np.log(power),
        kind='cubic',
    )
    interp = lambda k: np.exp(spline(np.log(k)))
    power_vec = [interp(k) for k in k_vec]
    def kernel(k1, k2, k3):
        x = (k3**2 - k2**2 - k1**2)/(2*k1*k2)
        return 5/7 + 1/2*x*(k1/k2 + k2/k1) + 2/7*x**2
    bpower = sum(
        kernel(*[k_vec[p] for p in perm])*power_vec[perm[0]]*power_vec[perm[1]]
        for perm in itertools.permutations(range(3))
    )
    return bpower
def load_bispec(
    mass, sim, code, z, spectrum, configuration_expr=None, k_desired=None, modes=None, *,
    correct_z=True,
):
    # Load the bispectrum with shot noise already subtracted
    k1, k2, k3, bpower, modes_read = loadtxt(
        mass, sim, code, z, f'bispec_{spectrum}',
        usecols=(0, 1, 2, 6, 8), unpack=True,
    )
    if modes is None:
        modes = modes_read
    # Keep only closed triangles
    closed = (k1 < k2 + k3)
    k1     = k1    [closed]
    k2     = k2    [closed]
    k3     = k3    [closed]
    bpower = bpower[closed]
    modes  = modes [closed]
    if configuration_expr is not None:
        mask = configuration_expr(k1, k2, k3)
        k1     = k1    [mask]
        k2     = k2    [mask]
        k3     = k3    [mask]
        bpower = bpower[mask]
        modes  = modes [mask]
    # Convert to proper units
    boxsize, _ = get_boxgrid(sim)
    k_fundamental = 2*np.pi/boxsize
    k1 *= k_fundamental
    k2 *= k_fundamental
    k3 *= k_fundamental
    # Correct if not exactly at the specified redshift
    if correct_z and spectrum == 'cdm':
        bpower *= get_zcorrection_factor(mass, sim, code, z, f'bispec_{spectrum}')
    # Rebin as requested
    if k_desired is not None:
        # Note that k2 and k3 should not be used after rebinning
        k_lower = max(np.min(k1), np.min(k1))
        k_upper = min(np.max(k1), np.max(k1))
        k1, bpower, _ = rebin(k_desired, k1, bpower, modes)
        mask = (k_lower*(1 - 1e-4) <= k1) & (k1 <= k_upper*(1 + 1e-4))
        bpower[~mask] = np.nan
    return k1, k2, k3, bpower, modes
def load_powerspec(
    mass, sim, code, z, spectrum, k_desired=None, modes=None, *,
    correct_z=True, subtract_neutrino_shotnoise=True,
):
    # Read in data
    if codespecs[code].is_simulation:
        k, power, modes_read = loadtxt(
            mass, sim, code, z, f'powerspec_{spectrum}', unpack=True,
        )
    else:
        k, power = loadtxt(
            mass, sim, code, z, f'powerspec_{spectrum}', unpack=True,
        )
        modes_read = None
    if modes is None:
        modes = modes_read
    # If no power spectrum data is actually present within the file,
    # return arrays of size 1.
    if all(np.isnan(power)):
        return k[:1], power[:1], (None if modes is None else modes[:1])
    # Correct if not exactly at the specified redshift
    if correct_z and spectrum == 'cdm':
        power *= get_zcorrection_factor(mass, sim, code, z, f'powerspec_{spectrum}')
    # Subtract shotnoise from neutrinos
    boxsize, gridsize = get_boxgrid(sim)
    if subtract_neutrino_shotnoise and codespecs[code].is_simulation and spectrum == 'ncdm':
        if code == 'concept':
            # Neutrinos in CONCEPT have no shot noise
            noise = 0
        elif code == 'swift':
            # The delta-f method of SWIFT has special shot noise
            sim_name = get_sim_name(mass, sim)
            noise = {
                (0, '0.15eV'        ): 0.0211911,
                (0, '0.15eV_HR'     ): 0.002660295,
                (0, '0.15eV_1024Mpc'): 0.02391492,
                (0, '0.3eV'         ): 0.12407663,
                (0, '0.6eV'         ): 0.6814035,
                (1, '0.15eV'        ): 0.003407,
                (1, '0.15eV_HR'     ): 0.00043113125,
                (1, '0.15eV_1024Mpc'): 0.00391519,
                (1, '0.3eV'         ): 0.02111753,
                (1, '0.6eV'         ): 0.11054256,
            }.get((z, sim_name), 0)
            if noise == 0:
                print(f'Unknown neutrino snot noise for {sim_name} {code} z={z}')
        else:
            # Particle shot noise in the Gaussian limit
            num_nu = gridsize**3
            noise = boxsize**3/num_nu
        power -= noise
    # Rebin as requested
    if k_desired is not None:
        k_lower = max(np.min(k), np.min(k))
        k_upper = min(np.max(k), np.max(k))
        if not codespecs[code].is_simulation:
            k_min = 2*np.pi/boxsize
            k_max = np.sqrt(3)*k_min*(gridsize//2)
            k_min *= 1 - 1e-3
            k_max *= 1 + 1e-3
            if k[0] > k_min:
                k = np.concatenate(([k_min], k))
                power = np.concatenate(([power[0]], power))
            if k[-1] < k_max:
                k = np.concatenate((k, [k_max]))
                power = np.concatenate((power, [power[-1]]))
            k, power, _ = Pk_library.expected_Pk(
                k.astype(np.float32), power.astype(np.float32), boxsize, gridsize,
            )
        k, power, _ = rebin(k_desired, k, power, modes)
        mask = (k_lower <= k) & (k <= k_upper)
        power[~mask] = np.nan
    return k, power, modes
def get_filename(mass, sim, code, z, basename, try_fiducial=True):
    sim_name = get_sim_name(mass, sim)
    basename = basename.replace(' ', '')
    filename = f'{this_dir}/../data/{sim_name}/{code}/z{z}/{basename}'
    if not os.path.isfile(filename) and not codespecs[code].is_simulation:
        return get_filename(mass, 'fiducial', code, z, basename, try_fiducial=False)
    return filename
def get_boxgrid(sim):
    boxsize, gridsize = 512, 512
    if sim == 'HR':
        gridsize *= 2
    elif sim == '1024Mpc':
        boxsize  *= 2
        gridsize *= 2
    return boxsize, gridsize
def get_sim_name(mass, sim):
    return f'{float(mass)}eV' + f'_{sim}'*(sim != 'fiducial')
def get_zcorrection_factor(mass, sim, code, z, basename):
    filename = get_filename(mass, sim, code, z, basename)
    header = get_header(filename)
    match = re.search(r' z *= *(.+?) ', '\n'.join(header))
    fac = 1
    if match:
        z_dump = float(match.group(1))
        if z_dump != z:
            fac = get_growthfac(mass, z)/get_growthfac(mass, z_dump)
    spectrum = basename.partition('_')[0]
    fac **= {'powerspec': 2, 'bispec': 3}.get(spectrum, 1)
    return fac
def get_plot_kwargs(code, pop=None):
    attrs = {'label', 'color', 'linestyle'}
    if pop is not None:
        for attr in any2list(pop):
            attrs.discard(attr)
    codespec = codespecs[code]
    return {
        attr: getattr(codespec, attr)
        for attr in attrs
    }
def any2list(val):
    if isinstance(val, (str, bytes)):
        val = [val]
    try:
        iter(val)
    except TypeError:
        val = [val]
    return list(val)
def rebin(k_desired, k_in, power_in, modes_in):
    def get_weights(weights):
        weights = np.asarray(weights).copy()
        weights[np.isnan(weights)] = 0
        return weights
    k, _     = np.histogram(k_in, k_desired, weights=get_weights(    k_in*modes_in))
    power, _ = np.histogram(k_in, k_desired, weights=get_weights(power_in*modes_in))
    modes, _ = np.histogram(k_in, k_desired, weights=get_weights(         modes_in))
    mask = (modes > 0)
    k, power, modes = k[mask], power[mask], modes[mask]
    k /= modes
    power /= modes
    power[power == 0] = np.nan
    return k, power, modes
def get_class_background(mass, extra_params=None):
    if extra_params is None:
        extra_params = {}
    params = {
        # General cosmological parameters
        'H0': 67,
        'Omega_cdm': {
            0   : 0.269984542,
            0.15: 0.266396931,
            0.3 : 0.262809319,
            0.6 : 0.255634096,
        }[mass],
        'Omega_b': 0.049,
        'T_cmb': 2.7255,
    }
    params.update(
        {
            # Neutrino parameters
            'N_ur'  : 3.046,
            'N_ncdm': 0,
        } if mass == 0 else
        {
            # Neutrino parameters
            'N_ur'    : 0,
            'N_ncdm'  : 1,
            'm_ncdm'  : mass/3,
            'deg_ncdm': 3,
            'T_ncdm'  : (4/11)**(1/3)*(3.046/3)**(1/4),
            # Neutrino precision settings
            'Quadrature strategy'    : 2,
            'Number of momentum bins': 100,
        }
    )
    params.update(extra_params)
    cosmo = classy.Class()
    cosmo.set(params)
    cosmo.compute()
    background = cosmo.get_background()
    return background
def get_growthfac(mass, z):
    background = get_class_background(mass)
    growthfac = np.exp(
        scipy.interpolate.interp1d(
            np.log(1/(1 + background['z'])),
            np.log(background['gr.fac. D']),
            kind='cubic',
            fill_value='extrapolate',
        )(np.log(1/(1 + z)))
    )
    return growthfac
def loadtxt(mass, sim, code, z, basename, **kwargs):
    filename = get_filename(mass, sim, code, z, basename)
    # Check whether header is consistent
    header = get_header(filename)
    if len(header) == 0:
        print(f'No header present in {filename}', file=sys.stderr)
    else:
        match = re.search(
            r'(.+) for (.+eV.*) (.+) z=(.+?) (.+?) ',
            header[0].strip() + ' ',
        )
        if match:
            try:
                consistent = (
                    match.group(2) == get_sim_name(
                        mass,
                        sim if codespecs[code].is_simulation else 'fiducial',
                    )
                    and match.group(3) == code
                    and np.isclose(float(match.group(4)), z, atol=0.02)
                    and match.group(5) in basename.replace(' ', '')
                )
            except Exception:
                consistent = False
            if not consistent:
                print(f'Inconsistent header of {filename}', file=sys.stderr)
        else:
            print(f'Could not parse header of {filename}', file=sys.stderr)
    if len(header) < 2:
        print(f'Incomplete header of {filename}', file=sys.stderr)
    # Load data
    return np.loadtxt(filename, **kwargs)
def get_header(filename):
    header = []
    with open(filename, 'r') as f:
        for line in f:
            if not line.startswith('#'):
                break
            header.append(line.strip(' #\r\n\t'))
    return header

