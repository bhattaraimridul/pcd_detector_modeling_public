import re
import sys
import os
import subprocess
import shutil
import scipy.io
import time

from scripts.create_run_mac import create_run_mac_faceon, create_run_mac_edgeon
from scripts.create_run_energy_mac import create_run_energy_mac
from scripts.create_detector_construction import create_faceon_detector, create_edgeon_detector
from scripts.create_physics_list import create_physics_list
from scripts.run_geant4_simulation import run_geant4_simulation

def parse_parameters(param_file):
    params = {}
    with open(param_file, 'r') as file:
        for line in file:
            if ':' in line and not line.strip().startswith('#'):
                key, value = line.split(':', 1)
                value = re.split(r'\s+#', value.strip())[0]  # remove inline comments
                try:
                    params[key.strip()] = float(value) if "." in value else int(value)
                except ValueError:
                    params[key.strip()] = value.strip()
    return params

def save_parameters_to_mat(params, output_file):
    scipy.io.savemat(output_file, params)
    print(f"Parameters saved to {output_file}.", flush=True)

def create_run_charge_sharing_matlab(source_dir, output_dir, mat_file_path, detector_material, apply_charge_sharing):
    try:
        # Create .m file that includes paths to .mat parameter file and .mat constant file
        constant_file_path = os.path.join(source_dir, "source", "constants_charge_sharing", f"constants_{detector_material}.mat")
        
        matlab_code = f"""%% Author: Mridul Bhattarai
    parameterFile = '{mat_file_path}';  % path to parameters .mat file
    constantsFile = '{constant_file_path}'; % path to constants .mat file
    """
        # paths for the two files
        file1_path = os.path.join(output_dir, "generate_detector_response.m")
        if apply_charge_sharing.lower() == "yes":
            print("Applying charge sharing effect...", flush=True)
            file2_path = os.path.join(source_dir, "source", "constants_charge_sharing", "generate_detector_response.m")
        elif apply_charge_sharing.lower() == "no":
            print("Not applying charge sharing effect...", flush=True)
            file2_path = os.path.join(source_dir, "source", "constants_charge_sharing", "generate_detector_response_no_charge_sharing.m")
        else:
            raise ValueError("Set apply_charge_sharing: yes/no")

        with open(file1_path, 'w') as m_file:
            m_file.write(matlab_code)

        with open(file2_path, 'r') as file2:
            file2_content = file2.read()

        with open(file1_path, 'a') as m_file:
            m_file.write("\n")
            m_file.write(file2_content)

        # run MATLAB
        process = subprocess.Popen(
            ['matlab', '-batch', f"run('{file1_path}')"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in process.stdout:
            print(line, end='')  # stream MATLAB output to Python's stdout in real time

        process.wait(timeout=300)  # 5 min timeout, code exits if MATLAB doesn't print any output for 5 mins

        if process.returncode != 0:
            raise RuntimeError("MATLAB execution failed during Module 2.")
        
    except subprocess.TimeoutExpired:
        process.kill()
        raise RuntimeError("MATLAB execution timed out during Module 2.")
    except Exception as e:
        raise RuntimeError(f"Module 2 run failed: {e}")

def create_run_sum_interaction(source_dir, output_dir, mat_file_path): # for edge-on designs
    # Create .m file that includes paths to .mat parameter file
    
    matlab_code = f"""%% Author: Mridul Bhattarai
parameterFile = '{mat_file_path}';  % path to parameters .mat file

"""
    # paths for the two files
    file1_path = os.path.join(output_dir, "sum_interaction_edgeon.m")

    print("Summing interactions for edge-on PCD...", flush=True)
    file2_path = os.path.join(source_dir, "source", "constants_charge_sharing", "sum_interaction_edgeon.m")

    with open(file1_path, 'w') as m_file:
        m_file.write(matlab_code)

    with open(file2_path, 'r') as file2:
        file2_content = file2.read()

    with open(file1_path, 'a') as m_file:
        m_file.write("\n")
        m_file.write(file2_content)

    # run MATLAB
    subprocess.run(['matlab', '-nodisplay', '-nosplash', '-r', f"run('{file1_path}');exit;"])

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 DukeCounter.py parameter.txt")
        sys.exit(1)

    start_time = time.time() # start time of the simulation 
    
    param_file = sys.argv[1]
    params = parse_parameters(param_file)

    source_dir = os.path.dirname(os.path.abspath(__file__))
    geant4_installation_dir = params.get("geant4_installation_dir", os.path.join(source_dir, "geant4"))
    
    # Default values: module 1
    run_module_1 = params.get("run_module_1", "yes")
    num_events = params.get("num_events", 100000)
    energy_max = params.get("energy_max", 120)
    physics_list = params.get("physics_list", "livermore").lower()
    detector_material = params.get("detector_material", "cdte").lower()
    detector_thickness_z = params.get("detector_thickness_z", 1.6)

    # edge-on design
    detector_design = params.get("detector_design", "face-on").lower()
    foil_material = params.get("foil_material", "W").lower()
    foil_thickness = params.get("foil_thickness_y", 0.02)

    output_dir = params.get("output_dir", "./output")

    # Default vals: charge sharing params
    run_module_2 = params.get("run_module_2", "yes")
    num_workers_parallel_computing = params.get("num_workers_parallel_computing", 32)
    detector_pixel_size_x = params.get("detector_pixel_size_x", 0.50)
    detector_pixel_size_y = params.get("detector_pixel_size_y", 0.60)
    apply_charge_sharing = params.get("apply_charge_sharing", "yes")
    bias_voltage = params.get("bias_voltage", 1000)
    sigma_electronic_noise = params.get("sigma_electronic_noise", 1.5)
    detector_response_matrix_size_xy = params.get("detector_response_matrix_size_xy", 3);
    generate_dukesim_detector_response = params.get("generate_dukesim_detector_response", "yes")
    LT = params.get("LT", 20)
    HT = params.get("HT", 65)

    if run_module_1.lower() == "yes":
        print("Running Module 1.", flush=True)
        
        create_run_energy_mac("./source/run_energy.mac", num_events)
        create_physics_list("./source/src/PhysicsList.cc", physics_list)

        if detector_design == "face-on":
            # create_run_mac_faceon("./source/run.mac", num_events, energy_max)
            # April 23, 2025 - using rectangular source for both face-on and edge-on designs, avoiding the borders in both x- and y-axes using x- and y-limits determined using subsampling technique
            create_run_mac_faceon("./source/run.mac", num_events, energy_max, detector_pixel_size_x, detector_pixel_size_y)
            
            create_faceon_detector("./source/src/PCD_DetectorConstruction.cc", detector_material, detector_thickness_z)
        elif detector_design == "edge-on":
            # create_run_mac_edgeon("./source/run.mac", num_events, energy_max)
            # April 23, 2025 - using rectangular source for both face-on and edge-on designs, avoiding the borders in both x- and y-axes using x- and y-limits determined using subsampling technique
            create_run_mac_edgeon("./source/run.mac", num_events, energy_max, detector_pixel_size_x, detector_pixel_size_y)
            
            create_edgeon_detector("./source/src/PCD_DetectorConstruction.cc", detector_material, detector_pixel_size_y, detector_thickness_z, foil_material, foil_thickness)
        else:
            raise ValueError("Set detector_design: face-on/edge-on")

        print("run.mac, run_energy.mac, PhysicsList.cc, and PCD_DetectorConstruction.cc files created successfully.", flush=True)

        run_geant4_simulation(os.path.join(source_dir, "source"), output_dir, geant4_installation_dir)

        print("Geant4 simulation done successfully. Module 1 run complete.", flush=True)
    elif run_module_1.lower() == "no":
        print(f"\033[33m\033[1mrun_module_1\033[0m\033[33m is set to \033[1mno\033[0m\033[33m, so Monte Carlo simulation results are expected in the output directory: {output_dir}.\033[0m")

    if run_module_2.lower() == "yes":
        print("Running Module 2.", flush=True)
        
        # Save parameters to .mat file
        mat_file_path = os.path.join(output_dir, "simulation_parameters.mat")
        save_parameters_to_mat(params, mat_file_path)
        
        if detector_design == "edge-on":
            create_run_sum_interaction(source_dir, output_dir, mat_file_path)
            
        create_run_charge_sharing_matlab(source_dir, output_dir, mat_file_path, detector_material, apply_charge_sharing) # mat_file_path includes edge-on or face-on design 
        print("Module 2 run complete.", flush=True)

    end_time = time.time()
    total_time = end_time - start_time

    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    seconds = int(total_time % 60)

    print(f"Total time for the simulation = {hours} hr, {minutes} min, {seconds} sec.")
    
    print("\033[1m\033[3m\033[34m SIMULATION COMPLETE. CONGRATS! \033[0m")

if __name__ == "__main__":
    main()
