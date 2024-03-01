import pandas as pd
import sys

def fill_missing_genotypes(row, unique_positions, df):
    genotype_list = []
    for pos in unique_positions:
        if pos in row['positions']:
            genotype = row['genotypes'][row['positions'].index(pos)]
        else:
            genotype = '0 0'
        genotype_list.append(genotype)
    return ' '.join(genotype_list)

def main(input_csv_path):
    # Load DataFrame
    df = pd.read_csv(input_csv_path)
    
    # Correct column names and logic as needed
    df['gender'] = df['gender'].map({1: '1', 2: '2', 0: '0'})
    df['affection'] = '0'  # Assuming affection status is not provided
    df['genotype'] = df[['ref', 'alt']].apply(lambda x: ' '.join(x), axis=1)
    
    unique_positions = df['position'].unique()

    aggregated_data = []

    for _, group in df.groupby(['family_id', 'participant_id', 'father_id', 'mother_id', 'gender', 'affection']):
        agg_row = {
            'family_id': group.iloc[0]['family_id'],
            'participant_id': group.iloc[0]['participant_id'],
            'father_id': group.iloc[0]['father_id'],
            'mother_id': group.iloc[0]['mother_id'],
            'gender': group.iloc[0]['gender'],
            'affection': group.iloc[0]['affection'],
            'positions': group['position'].tolist(),
            'genotypes': group['genotype'].tolist()
        }
        agg_row['genotype'] = fill_missing_genotypes(agg_row, unique_positions, df)
        aggregated_data.append(agg_row)

    # Convert the aggregated data list to a DataFrame
    aggregated_df = pd.DataFrame(aggregated_data)

    # Write .ped file
    with open('output.ped', 'w') as ped_file:
        for _, row in aggregated_df.iterrows():
            ped_line = f"{row['family_id']} {row['participant_id']} {row['father_id']} {row['mother_id']} {row['gender']} {row['affection']} {row['genotype']}\n"
            ped_file.write(ped_line)

    # Correct spelling mistakes and column names for map file generation
    unique_variants = df[['chromosome', 'variant_id', 'genetic_distance', 'position']].drop_duplicates()
    unique_variants = unique_variants.sort_values(by=['chromosome', 'position'])

    # Write the .map File
    with open('output.map', 'w') as map_file:
        for _, variant in unique_variants.iterrows():
            map_line = f"{variant['chromosome']} {variant['variant_id']} {variant['genetic_distance']} {variant['position']}\n"
            map_file.write(map_line)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_plink_files.py <input_csv_path>")
        sys.exit(1)
    input_csv_path = sys.argv[1]
    main(input_csv_path)
