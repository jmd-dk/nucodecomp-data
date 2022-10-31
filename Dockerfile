# Basics
FROM continuumio/anaconda3:2022.05
SHELL ["/usr/bin/env", "bash", "-c"]
CMD ["bash"]

# Build options
ARG workdir="/nucodecomp"
ARG matplotlib_version=3.3.4
ARG pylians_version=729d74c8af324a77a02926c82b89f678856bfdfe
ARG class_version=2.7.2

# Build environment as root
RUN : \
    # Add Python binary directory to PATH
    && echo "export PATH=\"\${PATH}:/opt/conda/bin\"" >> ~/.bashrc \
    # Update APT cache and install apt-utils
    && apt-get update \
    && apt-get install -y apt-utils \
    # Install and set up Bash auto-completion
    && apt-get install -y --no-install-recommends bash-completion \
    && echo "[ ! -t 0 ] || source /etc/bash_completion" >> ~/.bashrc \
    # Set up Bash history search with ↑↓
    && echo "[ ! -t 0 ] || bind '\"\e[A\": history-search-backward' 2>/dev/null" >> ~/.bashrc \
    && echo "[ ! -t 0 ] || bind '\"\e[B\": history-search-forward' 2>/dev/null" >> ~/.bashrc \
    # Set up colour prompt
    && echo "[ ! -t 0 ] || PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\\$ '" >> ~/.bashrc \
    && echo "[ ! -t 0 ] || alias ls='ls --color=auto'" >> ~/.bashrc \
    && echo "[ ! -t 0 ] || alias grep='grep --color=auto'" >> ~/.bashrc \
    # Install build tools
    && apt-get install -y gcc make \
    # Install xz-utils
    && apt-get install -y xz-utils \
    # Install TexLive
    && apt-get install -y \
        texlive-latex-recommended \
        texlive-latex-extra \
        texlive-fonts-recommended \
        dvipng cm-super \
    # Disable conda auto-update
    && conda config --set auto_update_conda false \
    # Install Matplotlib (conda is slow)
    && pip install matplotlib==${matplotlib_version} \
    # Install pyFFTW
    && conda install -y -c conda-forge pyfftw \
    # Install Pylians
    && ( : \
        && cd /opt/conda/lib/python*/site-packages \
        && wget --no-ch https://github.com/franciscovillaescusa/Pylians3/archive/${pylians_version}.tar.gz \
        && tar xfz ${pylians_version}.tar.gz \
        && rm -f ${pylians_version}.tar.gz \
        && mv Pylians* pylians \
        && cd pylians \
        && python setup.py build \
        && cd build/lib.* \
        && echo "export PYTHONPATH=\"\${PYTHONPATH}:$(pwd)\"" >> ~/.bashrc \
    ) \
    # Install CLASS
    && ( : \
        && cd /opt/conda/lib/python*/site-packages \
        && wget --no-ch https://github.com/lesgourg/class_public/archive/v${class_version}.tar.gz \
        && tar xfz v${class_version}.tar.gz \
        && rm -f v${class_version}.tar.gz \
        && cd class_public* \
        && PYTHON=$(which python) make \
    ) \
    # Add euclid user
    && apt-get install -y --no-install-recommends sudo \
    && echo "Defaults lecture = never" > "/etc/sudoers.d/privacy" \
    && groupadd -r euclid \
    && useradd -m -g euclid euclid \
    && echo   "root:euclid" | chpasswd \
    && echo "euclid:euclid" | chpasswd \
    && adduser euclid sudo \
    && echo "euclid ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers \
    && cp ~/.bashrc /home/euclid/ \
    && chown -R "euclid:euclid" /home/euclid \
    # Remove unnecessary packages and clean APT cache
    && apt-get autoremove -y gcc \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && apt-get autoclean -y \
    && rm -rf /var/lib/{apt/lists,cache,log}/* \
    && rm -rf $(ls /var/lib/dpkg/info/* | grep -v "\.list") \
    # Remove other caches
    && sudo rm -rf /tmp/* ~/.cache/* \
    # Allow for APT auto-completion
    && rm -f /etc/apt/apt.conf.d/docker-clean \
    && :

# Set up environment
COPY . ${workdir}/
RUN chown -R "euclid:euclid" "${workdir}"
USER euclid
ENV TERM=linux
WORKDIR ${workdir}

