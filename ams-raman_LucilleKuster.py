# PROGRAM HEADER,  Generate and export Raman spectrum from an AMS output
# Works for several AMS file
# The spectrum need to have more than one peak
"""
Filename: ams-raman.py
Author: Lucille Kuster
Date created: 2024-06-28
"""

import os
import numpy as np
from scipy import special

# Define your input and output file paths ---- automat. detect all .out file in your path
path = '/Users/lucille/Desktop' # Path where the AMS output file is located
input_dir = path + '/'
output_dir = path + '/'

print("-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_- \n"
      "|     AMS Raman in progress...    | \n"
      "-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_- \n"
      "\n")

# Function to process the .out file
def process_out_file(input_file, output_file):
    raman_intensities_found = False
    resonance_raman_found = False
    extract_data = False

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            if 'Raman Intensities' in line:
                raman_intensities_found = True
                print('-----Raman calculation found----- \n')
            if 'Raman incident light frequency' in line:
                resonance_raman_found = True
                print('-----Resonance Raman found----- \n')
            if 'Index   Frequency (cm-1)  Raman Int (A^4/amu)    Depol ratio (lin)    Depol ratio (nat)   Irrep' in line:
                extract_data = True
                continue
            if extract_data:
                if '------------' in line:
                    break
                columns = line.split()
                if len(columns) >= 3:
                    frequency = columns[1]
                    raman_intensity = columns[2]
                    outfile.write(f'{frequency} {raman_intensity}\n')

    if not raman_intensities_found:
        print('NO Raman calculation found ---- k bye')
        os.remove(output_file)
        return

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Process each .out file in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".out"):
        input_file_path = os.path.join(input_dir, filename)
        output_file_path = os.path.join(output_dir, filename.replace('.out', '_Raman.txt'))
        process_out_file(input_file_path, output_file_path)

print('------ Processing completed... Ready to voigtify! ')

# voigtify:
def normalize(intensities):
    minimum, maximum = intensities.min(), intensities.max()
    intensities = (intensities - minimum) / (maximum - minimum)
    return intensities


def interpolate_spec(spectrum, resolution=1):
    inputWavenumbers = spectrum[:, 0]
    rangeMin = int(np.rint(inputWavenumbers.min()))
    rangeMax = int(np.rint(inputWavenumbers.max()))
    outputWavenumbers = range(rangeMin, rangeMax + 1, resolution)

    outputIntensities = np.interp(outputWavenumbers, inputWavenumbers, spectrum[:, 1])
    interpolated = np.empty((len(outputWavenumbers), 2))
    interpolated[:, 0], interpolated[:, 1] = outputWavenumbers, outputIntensities

    return interpolated


def gen_from_peaks(data, half_width=60):
    wave_max = int(round(data[:, 0].max() + 200))
    wave_min = max(0, int(round(data[:, 0].min() - 200)))
    nbPoints = wave_max - wave_min + 1

    spectrum = np.empty((nbPoints, 2))
    spectrum[:, 0] = np.linspace(wave_min, wave_max, nbPoints)
    spectrum[:, 1] = np.zeros(nbPoints)

    for peak in data:
        mu, inputIntensity = int(round(peak[0])), peak[1]
        beginWave, endWave = max(0, mu - half_width), max(0, mu + half_width)

        nbTicks = len(range(beginWave, endWave + 1, 1))
        curvePoints = np.linspace(beginWave - mu, endWave - mu, nbTicks)

        voigtFactors = special.voigt_profile(curvePoints, 1, 4)

        outputIntensities = inputIntensity * normalize(voigtFactors)

        padStart, padEnd = beginWave - wave_min, wave_max - endWave
        intensitiesPadded = np.pad(outputIntensities, (padStart, padEnd), 'constant', constant_values=(0, 0))
        signalMatrix = np.zeros((nbPoints, 2))
        signalMatrix[:, 1] = intensitiesPadded

        spectrum += signalMatrix

    return spectrum


def fetch_theoretical_spectrum(file_path):
    peakInformation = np.genfromtxt(file_path, dtype='float32')
    readArray = gen_from_peaks(peakInformation)
    if len(readArray.shape) != 2:
        raise ValueError("Parsed data does not have the expected two axes.")
    return readArray


def pre_process_single_spec(spectrum):
    sorted_spec = spectrum[np.argsort(spectrum[:, 0])]
    scaled_spec = interpolate_spec(sorted_spec, 1)
    norm_spec = scaled_spec.copy()
    norm_spec[:, 1] = normalize(scaled_spec[:, 1])

    return norm_spec


# Process each _processed.txt file in the output directory
for filename in os.listdir(output_dir):
    if filename.endswith("_Raman.txt"):
        input_file_path = os.path.join(output_dir, filename)
        output_file_path = os.path.join(output_dir, filename.replace('_Raman.txt', '_Wide-Raman.txt'))

        print("Ready to read and convert file at: " + str(input_file_path))
        rawSpectrum = fetch_theoretical_spectrum(input_file_path)
        processedSpectrum = pre_process_single_spec(rawSpectrum)

        print("Exporting to: " + str(output_file_path))
        try:
            np.savetxt(output_file_path, processedSpectrum, delimiter=",", header="wavenumber,intensity")
        except OSError:
            print("Unable to write file!")
            exit(1)

print('\n     ~ Processing of spectra completed ~       ')