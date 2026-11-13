import pandas as pd

input_file = "Machine_learning_job_level_expo.csv"
output_file = "soc4_job_counts_by_year.csv"

# Load only the columns needed (2 million rows of 3 columns takes ~100MB RAM)
df = pd.read_csv(input_file, usecols=["year", "doc_JobID", "soc4"])

# Drop rows where year or soc4 is missing
df = df.dropna(subset=["year", "soc4"])

# Standardize types so '2135' and '2135.0' never split into separate columns
df["year"] = df["year"].astype(int)
df["soc4"] = df["soc4"].astype(int)

# OPTIONAL: Uncomment the line below if you only want UNIQUE doc_JobIDs counted
# df = df.drop_duplicates(subset=['doc_JobID'])

# Group, count, and pivot soc4 codes into columns
pivoted_df = (
    df.groupby(["year", "soc4"]).size().unstack(level="soc4", fill_value=0)
)

pivoted_df.to_csv(output_file, index=True)
print(f"Done! Processed {len(df):,} rows and saved to {output_file}")
