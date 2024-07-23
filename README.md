# fsar_applyLUTs
Command line tool for rerastering F-SAR data from slant range to geocoded or the other way around.

## Installation and setup
To install the tool, we first have to create and activate a virtual python environment.
To do this, open the command line and go into the folder, you want to create this environment at:
```shell
cd /home/apply_LUTs_venv
```

### creating the virtual environment

You will need to have virtualenv installed, if it is not installed, you can do so with pip:
```shell
pip install virtualenv
```
After that, you can use
```shell
virtualenv .venv
```
to create an virtual environment

<br>

Now, you have to activate the virtual environment. On Windows, you do this by using the command:
```shell
.venv\Scripts\activate
```
and on Unix/macOS by using:
```shell
source .venv/bin/activate
```

<br>

after the virtual environment is activated, install the tool either using HTTPS where you'll
be asked to log in to your gitlab account:
```shell
pip install git+https://github.com/DLR-HR/fsar_applyluts.git
```
or by using SSH, if you have linked an SSH key to your gitlab account:
```shell
pip install git+ssh://git@github.com/DLR-HR/fsar_applyluts.git
```

### cloning the tool (for developers)
If you want to clone the tool to be able to change the code, first clone the git repository
using HTTPS:
```shell
git clone https://github.com/DLR-HR/fsar_applyluts.git
```
or with an SSH key:
```shell
git clone git@github.com:DLR-HR/fsar_applyluts.git
```

<br>

to install the required dependencies, first you'll have to go into the newly created fsar_applyLUTs
folder:
```shell
cd fsar_applyluts
```
and then you can use pip install to install the dependencies:
```shell
pip install -r requirements.txt
```
This also works in a virtual environment.

## Usage
The tool is easily usable from the command line, however, you have to be in the activated
virtual environment to use it. If you've just installed the tool and have not closed the command
line you can skip Reactivating the virtual environment, since it's still activated.

### Reactivating the virtual environment 
First change into the directory
the virtual environment has been set up at:
```shell
cd /home/apply_LUTs_venv
```
Now activate it by using the same command as before, so for windows this would be:
```shell
.venv\Scripts\activate
```
and for Unix/macOS it would be:
```shell
source .venv/bin/activate
```

### Running the tool

The mapping between slantrange and geographic UTM grids is accomplished with the `apply_LUT` script. The command line flag `--help` gives an overview of the interface:

```shell
apply_LUT --help
usage: apply_LUT [-h] [--dir {sr2geo,geo2sr}] --luts LUTS [--band {X,C,S,L,P,}] --in INPUT_FILE --out OUTPUT_FILE [--order ORDER] [--blocksize BLOCKSIZE]

options:
  -h, --help            show this help message and exit
  --dir {sr2geo,geo2sr}
                        sr2geo: map from slantrange to UTM grid (default); geo2sr: map from UTM grid to slantrange
  --luts LUTS           path to the GTC-LUT directory
  --band {X,C,S,L,P,}   The frequency band of the input file (defaults to '', which works when the geocoded product only contains one band)
  --in INPUT_FILE       absolute path to the input file
  --out OUTPUT_FILE     absolute path to the output file
  --order ORDER         order of the spline interpolation, has to be between 0-5. The default is 3 for floating point data and 0 for integer data
  --blocksize BLOCKSIZE
                        the size per processed chunk of data. Defaults to 512
```

As an example taken from the `23GABONX` (aka AfriSAR-2) campaign, the following command will map in interferometric coherence in a secondary acquisition `23gabonx0906` 
to the UTM grid of the primary acquisition `23gabonx0903`:

```shell
apply_LUT --luts=/data/23GABONX/FL09/PS03/TL01/GTC/GTC-LUT --in=/data/23GABONX/FL09/PS06/TL01/INF/INF-SR/coh_23gabonx0903_23gabonx0906_Lhh_tL01.tif --out=/data/23GABONX/FL09/PS03/TL01/GTC/GTC-IMG/cohgeo_23gabonx0903_23gabonx0906_Lhh_tL01.tif
```

### Deactivating the virtual environment
If you want to deactivate the virtual environment either close the command line or use:
```shell
deactivate
```
