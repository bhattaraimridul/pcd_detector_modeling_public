## FULL IMPLEMENTATION UPON REQUEST: 
**bhattaraimridul@gmail.com** OR **mridul.bhattarai@duke.edu** OR **https://mridulbhattarai.com/contact/**. 

## DukeCounter Detector Response Generator

Author: Mridul Bhattarai, PhD (Center for Virtual Imaging Trials at Duke University)

## Purpose
It can be used to generate detector responses for any photon-counting detector design (face-on and edge-on) and material (CdTe, CZT, GaAs, and Si). 

Detector response refers to the spatio-energetic mean and covariance matrices used to model detector efficiency, crosstalk, and noise characteristics. 

For more information:
  Paper - https://doi.org/10.1002/mp.70195
  Author's Website - https://mridulbhattarai.com/research-projects/photon-counting-ct-data-engine/
  Lab's Website - https://cvit.duke.edu/ 

## How does it work

The software takes a parameter file (.txt) as an input, runs Monte Carlo in Geant4 and charge sharing in MATLAB, and produces mean and covariance matrices as output (.mat and .bin).

## Setup Steps 

# Installing a Virtual Environment using dukecounter_venv_requirements.txt:

1. $ cd dukecounter_detector_response
2. $ python3 -m venv DukeCounterEnv
3. $ source DukeCounterEnv/bin/activate
4. (DukeCounterEnv) $ python3 -m pip install --upgrade pip
5. (DukeCounterEnv) $ python3 -m pip install -r dukecounter_venv_requirements.txt

# Installing Geant4 using Docker (if Geant4 is not already installed)
This workflow installs Geant4 on the host system using Docker, without requiring root/admin privileges. 
Docker is used only as an installer. After installation, Geant4 runs natively on the host. 

1. $ cd install_geant4_docker
2. $ chmod +x run_installation.sh
3. $ run_installation.sh /absolute/host/path/to/install/geant4
4. Check installation: $ ls /absolute/host/path/to/install/geant4 => bin, lib, include, share (directories)

## Running DukeCounter:

1. Activate the installed virtual environment: 
	$ source DukeCounterEnv/bin/activate
2. Modify parameter.txt as needed
3. Run the script:
	$ nohup python3 DukeCounter.py parameter.txt &

## Modules: 

DukeCounter executes two modules: 
1. Geant4 for Monte Carlo simulation 
2. MATLAB for charge sharing simulation 

Both modules can also be run individually.

## License: 

Contact - bhattaraimridul@gmail.com or https://mridulbhattarai.com/contact/ 

## How to cite

Bhattarai M, Panta RK, Segars WP, Abadi E, Samei E. Development of a customizable model for spectral photon-counting detector CT. Med Phys. 2025; 52:e70195. https://doi.org/10.1002/mp.70195

