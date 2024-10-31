# PROGRAM HEADER,  Create an output CSV with different rR spectra - ORCA
# and generated a PNG picture of all the files
"""
Filename: orca-excelrizer.py
Author: Lucille Kuster
Date created: 2023-10-17
"""
import pandas as pd
import os
import matplotlib.pyplot as plt

# Path -- Can be changed
name = "Name" # Name of the output file (.ott or .out file)
path = "/Users/lucille/Desktop/" # Path of all your .spectrum. files and output file

# List of wavenumbers -- Can be changed
wavenumbers = [20000, 19048, 18182, 17391, 16667]

# Anharmonic correction factor -- Can be changed
factor = 0.96

input_path = path + name + ".inp"
output_name = name + '-RR-allData.csv'
output_path = path + output_name
plot_output_path = path + name + 'combined_rr_spectra.png'


print("-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_- \n"
      "|    rR spectra in progress...    | \n"
      "-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_- \n")
print(" ~ Script made by Lucille Kuster ~ \n")

# Initialize an empty DataFrame to store the data
result_df = pd.DataFrame()

# List of input files
input_files = []

# Loop through each input file
for wave in wavenumbers:
    current_file = path + str(name) + ".spectrum." + str(wave)
    input_files.append(current_file)
    if not os.path.exists(current_file):
        print(f"File {current_file} does not exist. Skipping.")
        continue

    # Read the data from the input file, assuming columns are separated by tabs
    df = pd.read_csv(current_file, sep='\t', header=None, skiprows=1, usecols=[0, 2], dtype='float')

    # Normalize intensity
    minimum, maximum = df[2].min(), df[2].max()
    df[2] = (df[2] - minimum) / (maximum - minimum)
    df[0] = df[0] * factor

    # Add wavenumber and wavelength to identify spectra
    ligne_1 = pd.DataFrame({0: wave, 2: (10000000 / wave)}, index=[0])
    current_df = pd.concat([ligne_1, df]).reset_index(drop=True)

    # Add a blank column to separate data from different input files
    current_df['Blank'] = ''

    # Append the data to the result DataFrame
    result_df = pd.concat([result_df, current_df], axis=1)

# Save the combined data to a CSV file
result_df.to_csv(output_path, index=False, header=False)

print(f'Data has been written to {output_path}')


# --------------------------------
# ---- Continue with the code for image generating:
print("\n")

print("-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_- \n"
      "|       Creating a picture...      | \n"
      "-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_-‾-_- \n")

# Read the CSV file for plotting, skip the first row (header row)
data = pd.read_csv(output_path, skiprows=[0])

# Get the column headers
column_headers = data.columns

# Create a figure and axes for the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Initialize a list to store legend labels
legend_labels = []

# Plot data for all columns
for i, x_col in enumerate(column_headers[::3]):
    y_col = column_headers[i * 3 + 1]
    x_values = data[x_col]
    y_values = data[y_col]

    # Extract the corresponding input file name
    input_file_name = os.path.basename(input_files[i])

    ax.plot(x_values, y_values, label=f'{input_file_name}')

# Set the title and labels
ax.set_title(name + ' Combined Raman Spectra')
ax.set_xlabel('Wavenumber')
ax.set_ylabel('Intensity')

# Add the legend with the labels
ax.legend()

# Set the x-axis -- Can be changed
ax.set_xlim(100, 3000)

# Save the plot to a PNG file
plt.savefig(plot_output_path)

# Show the plot (optional)
plt.show()

print(f'Combined Raman spectra plot saved as {plot_output_path}')