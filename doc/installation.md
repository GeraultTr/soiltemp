# Installation

You must use conda environment : <https://docs.conda.io/en/latest/index.html>

## Users

### Create a new environment with SoilTemp installed in there

```bash

mamba create -n SoilTemp -c openalea3 -c conda-forge  openalea.soiltemp
mamba activate SoilTemp
```

Install SoilTemp in a existing environment

```bash
mamba install -c openalea3 -c conda-forge openalea.soiltemp
```

### (Optional) Test your installation

```bash
mamba install -c conda-forge pytest
git clone https://github.com/openalea/soiltemp.git
cd soiltemp/test; pytest
```

## Developers

### Install From source

```bash
# Install dependency with conda
mamba env create -n phm -f conda/environment.yml
mamba activate SoilTemp

# Clone SoilTemp and install
git clone https://github.com/openalea/soiltemp.git
cd soiltemp
pip install .

# (Optional) Test your installation
cd test; pytest
```
