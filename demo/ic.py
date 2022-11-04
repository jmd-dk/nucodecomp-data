from glob import glob
import os, sys
import numpy as np
import scipy.fft, scipy.interpolate
import matplotlib.pyplot as plt
import MAS_library, Pk_library  # Pylians
import cosmology                # other demo script

# Absolute path to the demo directory
this_dir = os.path.dirname(os.path.abspath(__file__))

# Iterator over Fourier grid
def fourier_loop(gridsize):
    """The iteration is over a complex 3D grid resulting from
    a real Fourier transform. The conventions employed for the
    data layout — i.e. the mapping between grid indices (i, j, k)
    and wave vector components (ki, kj, kk) — are those used
    by e.g. NumPy, SciPy, FFTW.
    """
    nyquist = gridsize//2
    for i in range(gridsize):
        ki = i - gridsize*(i >= nyquist)
        for j in range(gridsize):
            kj = j - gridsize*(j >= nyquist)
            for k in range(nyquist + 1):
                kk = k
                yield i, j, k, ki, kj, kk

# Function implementing Fourier deconvolution
def deconvolve(grid, interpolation):
    """The passed grid should be in real space,
    and the returned grid will similarly be in real space.
    """
    order = [None, 'NGP', 'CIC', 'TSC', 'PCS'].index(interpolation)
    gridsize = grid.shape[0]
    grid = scipy.fft.rfftn(grid)
    for i, j, k, ki, kj, kk in fourier_loop(gridsize):
        grid[i, j, k] /= (
             np.sinc(ki/gridsize)
            *np.sinc(kj/gridsize)
            *np.sinc(kk/gridsize)
        )**order
    grid = scipy.fft.irfftn(grid)
    return grid

# Function converting wave vector components (ki, kj, kk)
# into linear index, used to index into the array of phases.
def get_curve_key(ki, kj, kk):
    """The same phases may be utilized across simulations of
    different grid sizes. With the shared phases stored in a 1D array,
    some mapping from 1D to 3D is needed. Enlarging the grid should
    only add new modes (phases), leaving the inner modes intact.
    The mapping should then be independent of the grid size.
    Below we implement such a mapping as a space-filling curve which fills
    all (meaning ~half, due to the exploitation of the Hermitian symmetry)
    of Fourier space, starting from the origin and expanding outwards in
    cuboidal shells. The details are unimportant, what matters is that the
    output domain (image) of this function is exactly all of the integers
      0 ≤ i < gridsize*gridsize*(gridsize/2 + 1)
    when called with all integer triplets (ki, kj, kk) from the input domain
      -gridsize/2 ≤ ki < gridsize/2
      -gridsize/2 ≤ kj < gridsize/2
                0 ≤ kk ≤ gridsize/2
    for any value of gridsize.
    """
    kl = ki*(abs(ki) > abs(kj)) + kj*(abs(ki) < abs(kj))
    kl += (kl == 0)*max(ki, kj)
    s = (abs(kl) + (kl > 0))*(abs(kl) >= kk) + kk*(kk > abs(kl))
    f = 2*(kk == s)
    f += (f == 0) & (ki != -s) & (ki != s - 1)
    key = (
        + s   *((         (3 - kj))*(f == 0) + (-2*ki + (s == -kj))*(f == 1) + (1 + 2*ki)*(f == 2))
        + s**2*((-7 + 2*(s == -ki))*(f == 0) + (                -2)*(f == 1) + (       2)*(f == 2))
        + s**3*4
        + kj*(f == 2) + kk*(f != 2)
    )
    return key

# Demonstration function
def demo(mass=0.0, gridsize=128):
    """Function demonstrating the initial condition generation,
    in particular the use of the primordial phases from the external file.
    A matter δ field will be realized, after which its power spectrum
    and projected 2D (slice) render will be constructed and plotted.
    If the initial condition snapshot is available among the data,
    its power spectrum and 2D render will be plotted as well.
    For simplicity, we perform the realization as naïvely as possible,
    without the use of back-scaling, gauge considerations or other
    more sophisticated strategies.
    """
    # Specifications
    z_ini = 127
    boxsize = 512  # Mpc/h
    interpolation = 'CIC'
    k_min, k_max = 5e-3, 10  # h/Mpc
    k_lin = np.logspace(np.log10(k_min), np.log10(k_max), 100)
    # Get initial power spectrum
    params = cosmology.get_cosmo_params(mass)
    power_lin = cosmology.get_lin_power(params, z_ini, k_lin)
    # Construct spline from k2 [grid units] to sqrt(power) [(Mpc/h)^(3/2)]
    k_fundamental = 2*np.pi/boxsize
    get_sqrt_power_lin = (
        lambda k2, spline=scipy.interpolate.interp1d(
            np.log(k_lin), np.log(np.sqrt(power_lin)), kind='cubic',
        ): 0 if k2 == 0 else np.exp(spline(np.log(k_fundamental*np.sqrt(k2))))
    )
    # Read in phases
    filename = os.path.realpath(f'{this_dir}/../data/0.0eV/ic/phase')
    if not os.path.isfile(filename):
        print(
            (
                f'Missing phase file {filename}\n'
                f'You may download this via\n'
                f'  make data-ic-phase'
            ),
            file=sys.stderr,
        )
        sys.exit(1)
    nyquist = gridsize//2
    size = gridsize**2*(nyquist + 1)
    phase = np.fromfile(filename, dtype=np.float32, count=size)
    if phase.size < size:
        print(f'Too few phases available for grid size {gridsize}', file=sys.stderr)
        sys.exit(1)
    # Construct grid in Fourier space
    grid = np.empty((gridsize, gridsize, nyquist + 1), dtype=np.complex64)
    for i, j, k, ki, kj, kk in fourier_loop(gridsize):
        # Get "fixed" amplitude as sqrt(power)
        k2 = ki**2 + kj**2 + kk**2
        r = get_sqrt_power_lin(k2)
        # Look up phase
        key = get_curve_key(ki, kj, kk)
        θ = phase[key]
        # Assign Fourier mode to grid
        grid[i, j, k] = r*np.exp(1j*θ)
        # Note that the symmetry requirements for the DC plane
        # is already baked-in to the provided phases.
        # For simplicity, we leave out the symmetry conditions
        # for the Nyquist planes.
    # Transform to real space and normalize
    grid = scipy.fft.irfftn(grid)
    grid *= gridsize**3/boxsize**1.5
    # Compute power spectrum using Pylians
    tmp = Pk_library.Pk(grid, boxsize, MAS=0)
    k_grid, power_grid = tmp.k3D, tmp.Pk[:, 0]
    # Plot power spectra
    fig, axes = plt.subplot_mosaic('tt\nlr')
    axes['t'].loglog(k_lin, power_lin, label='linear')
    axes['t'].loglog(k_grid, power_grid, label='realized grid')
    # Also compute power spectrum for initial condition snapshot, if available
    grid_ic = None
    for sim in ('', '_HR'):
        filename = f'{this_dir}/../data/{mass}eV{sim}/ic/snapshot'
        if glob(f'{filename}*'):
            grid_ic = MAS_library.density_field_gadget(
                filename, [1], gridsize, interpolation,
            )
            grid_ic /= np.mean(grid_ic)
            grid_ic -= 1
            tmp = Pk_library.Pk(grid_ic, boxsize, MAS=interpolation)
            k_ic, power_ic = tmp.k3D, tmp.Pk[:, 0]
            axes['t'].loglog(k_ic, power_ic, '--', label='initial condition snapshot')
            break
    # Plot 2D slices
    def render2d(grid, ax):
        slice = np.sum(grid[:, :, :grid.shape[2]//8], 2)  # project along z
        ax.imshow(
            slice,
            interpolation='none',
            origin='lower',
            vmin=(slice.min() + 0.15*(slice.max() - slice.min())),
            vmax=(slice.min() + 0.85*(slice.max() - slice.min())),
        )
    render2d(grid, axes['l'])
    if grid_ic is not None:
        # Due to the particle interpolation (mass assignment) carried out
        # by Pylians, the grid should be deconvolved.
        grid_ic = deconvolve(grid_ic, interpolation)
        render2d(grid_ic, axes['r'])
    # Finalize plots
    axes['t'].set_title(rf'$\sum m_\nu = {mass}\, \mathrm{{eV}}$, $z = {z_ini}$')
    axes['t'].set_xlabel(r'$k$ $[h\, \mathrm{Mpc}^{-1}]$')
    axes['t'].set_ylabel(r'$P$ $[(\mathrm{Mpc}/h)^{3}]$')
    axes['t'].legend()
    axes['l'].set_title('realized grid')
    axes['r'].set_title('initial condition snapshot')
    axes['l'].set_axis_off()
    axes['r'].set_axis_off()
    plt.tight_layout()
    fig.savefig(f'{this_dir}/ic.pdf')

if __name__ == '__main__':
    demo()

