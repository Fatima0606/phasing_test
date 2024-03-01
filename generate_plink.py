import pandas as pd
import sys

# Function definitions and logic from your previous code here
# For demonstration, assuming the function definitions are already provided

def main(input_csv_path):
    # Load DataFrame
    df = pd.read_csv(input_csv_path)
    
    # Your processing logic here
# Map gender to PLINK specification
df['genotype'] = df[['ref', 'alt']].apply(lambda x: ' '.join(x), axis=1)
# Identify all unique position
unique_position = df['position'].unique()

# Function to fill missing genotype
def fill_missing_genotype(row, unique_position, df):
    genotype = []
    for pos in unique_position:
        # Check if the individual has a genotype for the position
        if pos in row['position']:
            # Get the genotype for the current position
            genotype = row['genotype'][row['position'].index(pos)]
        else:
            # If not, fill with '0 0'
            genotype = '0 0'
        genotype.append(genotype)
    return ' '.join(genotype)

# Group by individual to aggregate genotype
grouped = df.groupby(['family_id', 'particiapnt_id', 'father_id', 'mother_id', 'gender', 'affection'])

# Initialize an empty DataFrame to store the aggregated data
aggregated_data = []

for name, group in grouped:
    # For each group, create a dictionary of the aggregated information
    agg_row = {
        'family_id': name[0],
        'particiapnt_id': name[1],
        'father_id': name[2],
        'mother_id': name[3],
        'gender': name[4],
        'affection': name[5],
        'position': group['position'].tolist(),
        'genotype': group['genotype'].tolist()
    }
    # Fill missing genotype
    agg_row['genotype'] = fill_missing_genotype(agg_row, unique_position, df)
    # Append the aggregated row to the list
    aggregated_data.append(agg_row)

# Convert the aggregated data list to a DataFrame
aggregated_df = pd.DataFrame(aggregated_data)

# Now, `aggregated_df` contains each individual's information along with a complete set of genotype for all position

# Write .ped file
with open('output.ped', 'w') as ped_file:
    for _, row in aggregated_df.iterrows():
        ped_line = f"{row['family_id']} {row['particiapnt_id']} {row['father_id']} {row['mother_id']} {row['gender']} {row['affection']} {row['genotype']}\n"
        ped_file.write(ped_line)
## write map file
unique_variants = df[['chromomse', 'variant_id', 'genetic_distance', 'position']].drop_duplicates()

# Step 2: Sort Variants (if necessary, by chromomse and then by position)
unique_variants = unique_variants.sort_values(by=['chromomse', 'position'])

# Step 3: Write the .map File
map_file_path = 'output.map'
with open(map_file_path, 'w') as map_file:
    for _, variant in unique_variants.iterrows():
        map_line = f"{variant['chromomse']} {variant['variant_id']} {variant['genetic_distance']} {variant['position']}\n"
        map_file.write(map_line)



    # Write output files
    aggregated_df.to_csv('output.ped', sep='\t', index=False)
    unique_variants.to_csv('output.map', sep='\t', index=False)

if __name__ == "__main__":
    input_csv_path = sys.argv[1]
    main(input_csv_path)
