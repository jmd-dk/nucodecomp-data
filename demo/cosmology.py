import os
import numpy as np
import matplotlib.pyplot as plt
import classy

# Absolute path to the demo directory
this_dir = os.path.dirname(os.path.abspath(__file__))

# Function specifying the cosmologies
def get_cosmo_params(mass):
    """This function specifies the cosmology in case of all four
    neutrino masses (0 eV, 0.15 eV, 0.3 eV, 0.6 eV)
    in terms of CLASS parameters.
    """
    # General parameters
    params = {
        'h': 0.67,
        'Omega_b': 0.049,
        'Omega_cdm': {
            0   : 0.269984542,
            0.15: 0.266396931,
            0.3 : 0.262809319,
            0.6 : 0.255634096,
        }[mass],
        'T_cmb': 2.7255,
        'A_s': 2.215e-09,
        'n_s': 0.9619,
    }
    # Neutrino parameters
    N_eff = 3.046
    if mass == 0:
        params.update({
            'N_ur': N_eff,
            'N_ncdm': 0,
        })
    else:
        params.update({
            'N_ur': 0,
            'N_ncdm': 1,
            'm_ncdm': mass/3,
            'deg_ncdm': 3,
            'T_ncdm': (4/11)**(1/3)*(N_eff/3)**(1/4),
            # Precision settings
            'evolver': 0,
            'Quadrature strategy': 2,
            'Number of momentum bins': 100,
        })
    return params

# Demonstration function
def demo(z=0):
    """Function demonstrating the cosmologies by plotting
    the linear matter power spectra at some redshift z.
    If available among the data, the corresponding (non-linear)
    GADGET-3 power spectra are plotted as well.
    """
    # Specifications
    k_min, k_max = 5e-3, 10  # h/Mpc
    n = 100
    masses = [0.0, 0.15, 0.3, 0.6]  # eV
    # Handle each neutrino mass in turn
    for mass in masses:
        # Compute
        params = get_cosmo_params(mass)
        h = params['h']
        params.update({
            'output': 'mPk',
            'P_k_max_h/Mpc': k_max,
            'z_max_pk': z,
        })
        cosmo = classy.Class()
        cosmo.set(params)
        cosmo.compute()
        k = np.logspace(np.log10(k_min), np.log10(k_max), n)
        power = h**3*np.array([cosmo.pk_lin(h*ki, z) for ki in k])
        # Plot
        plt.loglog(k, power, label=rf'$\sum m_\nu = {mass}\, \mathrm{{eV}}$')
        # Also plot GADGET-3 spectrum, if available
        for sim in ('_1024Mpc', '_HR', ''):
            filename = f'{this_dir}/../data/{mass}eV{sim}/gadget3/z{z}/powerspec_cdm'
            if os.path.isfile(filename):
                break
        else:
            continue
        k_gadget, power_gadget = np.loadtxt(filename, usecols=(0, 1), unpack=True)
        plt.loglog(k_gadget, power_gadget, 'k--', lw=1, zorder=100)
    # Finish plot
    plt.title(rf'$z = {z}$')
    plt.xlabel(r'$k$ $[h\, \mathrm{Mpc}^{-1}]$')
    plt.ylabel(r'$P$ $[(\mathrm{Mpc}/h)^{3}]$')
    plt.legend()
    plt.savefig(f'{this_dir}/cosmology.pdf')

if __name__ == '__main__':
    demo()

