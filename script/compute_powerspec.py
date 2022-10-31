from helper import *

# Specifications
recompute = False                            # recompute existing results?
masses = [0, 0.15, 0.3, 0.6]                 # neutrino mass in eV;  from [0, 0.15, 0.3, 0.6]
simulations = ['fiducial', 'HR', '1024Mpc']  # simulation type;      from ['fiducial', 'HR', '1024Mpc']
codes = ['gadget3']                          # simulation code;      from ['gadget3']
redshifts = [0, 1]                           # redshift z;           from [0, 1]
spectra = [                                  # species for spectra;  from ['cdm', 'ncdm', 'halo<minhalomass>ref<refnumass>']
    'cdm',
    'ncdm',
    'cdm + ncdm',  # combined auto power spectrum
    'cdm x ncdm',  # cross power spectrum
    'cdm x halo1e+13ref',
    'cdm x halo1e+13ref0',
]

# Global constants
mas = 'CIC'
axis = 0
verbose = False
halo_density_criterion = '200b'
threads = int(os.environ.get('OMP_NUM_THREADS', 1))

# Main function
def compute(masses, simulations, codes, redshifts, spectra, recompute=False):
    masses      = any2list(masses)
    simulations = any2list(simulations)
    codes       = any2list(codes)
    redshifts   = any2list(redshifts)
    spectra     = any2list(spectra)
    # Helper functions
    def get_delta(filename_or_pos, ptypes=None):
        if ptypes is None:
            # Construct delta from positions
            delta = np.zeros([gridsize]*3, dtype=np.float32)
            MAS_library.MA(filename_or_pos, delta, boxsize, mas, verbose=verbose)
        else:
            # Construct delta from snapshot
            delta = MAS_library.density_field_gadget(
                filename_or_pos, ptypes, gridsize, mas, axis=axis, verbose=verbose,
            )
        delta /= np.mean(delta, dtype=np.float64)
        delta -= 1
        return delta
    @functools.lru_cache
    def get_nhalo(mass, sim, code, z, threshold):
        halomasses, _ = load_halo(mass, sim, code, z, 'cdm', threshold=threshold)
        return len(halomasses)
    # Carry out computations
    species2ptype = {'cdm': 1, 'ncdm': 2}
    for mass, sim, code, z, spectrum in itertools.product(
        masses, simulations, codes, redshifts, spectra,
    ):
        # Define needed information
        boxsize, gridsize = get_boxgrid(sim)
        filename_output = get_filename(mass, sim, code, z, f'powerspec_{spectrum}')
        if not recompute and os.path.isfile(filename_output):
            continue
        filename_snapshot = get_filename(mass, sim, code, z, 'snapshot/snapshot')
        if not glob(f'{filename_snapshot}*'):
            continue
        spectrum_type = ('cross' if 'x' in spectrum else 'auto')
        ptypes = [
            species2ptype[species]
            for species in (
                spectrum
                .replace(' ', '')
                .split({'auto': '+', 'cross': 'x'}[spectrum_type])
            )
            if not species.startswith('halo')
        ]
        header = readgadget.header(filename_snapshot)
        if not all(header.nall[ptype] > 0 for ptype in ptypes):
            continue
        sim_name = get_sim_name(mass, sim)
        data_name = f'{sim_name} {code} z={z} {spectrum}'
        # Compute density field and power spectrum
        if spectrum_type == 'auto':
            print(f'Computing density field for {data_name}')
            delta = get_delta(filename_snapshot, ptypes)
            print(f'Computing auto power spectrum for {data_name}')
            pk = Pk_library.Pk(delta, boxsize, axis, mas, threads, verbose)
            power = pk.Pk[:, 0]
        elif spectrum_type == 'cross':
            print(f'Computing density fields for {data_name}')
            deltas = [get_delta(filename_snapshot, [ptype]) for ptype in ptypes]
            if len(deltas) == 1:
                # Halos
                threshold, ref = re.search(r'halo(.*)ref(.*)', spectrum).groups()
                nhalo = get_nhalo(float(ref) if ref else mass, sim, code, z, threshold)
                _, pos = load_halo(mass, sim, code, z, 'cdm', threshold=nhalo)
                deltas.append(get_delta(pos))
            print(f'Computing cross power spectrum for {data_name}')
            pk = Pk_library.XPk(deltas, boxsize, axis, [mas]*2, threads)
            power = pk.XPk[:, 0, 0]
        k = pk.k3D
        modes = pk.Nmodes3D
        # Save power spectrum
        z_actual = header.redshift
        data_name = f'{sim_name} {code} z={z_actual} {spectrum}'
        os.makedirs(os.path.dirname(filename_output), exist_ok=True)
        np.savetxt(
            filename_output, np.array((k, power, modes)).T,
            header='\n'.join([
                f'{spectrum_type.capitalize()} power spectrum for {data_name}',
                f'{"k [h/Mpc]": <22} {"P [(Mpc/h)^3]": <24} modes',
            ]),
        )

if __name__ == '__main__':
    compute(masses, simulations, codes, redshifts, spectra, recompute)

