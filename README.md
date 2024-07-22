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
pip install git+ssh://git@github.com:DLR-HR/fsar_applyluts.git
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

Now you can execute the tool. The tool needs the path to the gtc-lut directory, where the lookup 
tables are contained, as well as the path to the input file and the path where the output 
file should be placed at, including a filename:
```shell
apply_LUT --gtc_lut /merz/Geocoding/GTC/GTC-LUT --input_file /merz/Geocoding/GTC/GTC-IMG/ampgeo_phh.tif --output_file /merz/output/gtc2sr.tif
```
Furthermore, there are optional arguments, you can give to the tool:
* --order: order of the spline interpolation, has to be between 0-5. The default is 3 for floating point data and 0 for integer data.
* --blocksize: the size per processed chunk of data. The default is 512
* --geometry: type geo if you want to go from geocoded to slant range or sr if you want to go from slant range to geocoded.
* --band: the frequency band of the input file The program will try to decide this itself based on your input file, if you type nothing

If you want to receive this information about the arguments in the script you can use
```shell
apply_LUT -h
```

### Deactivating the virtual environment
If you want to deactivate the virtual environment either close the command line or use:
```shell
deactivate
```
