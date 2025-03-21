import pandas as pd
import argparse


def latex_table(csv_file, output_file):
    """Generate a LaTeX table from a csv file with heading."""
    # Load CSV with first row as column names, first column as row labels
    df = pd.read_csv(csv_file, index_col=0)

    # Specify the column to format in scientific notation
    scientific_col = "update time"  # Change this to your column name

    # Convert the chosen column to scientific notation
    df[scientific_col] = df[scientific_col].apply(lambda x: "{:.2e}".format(x))

    # Convert column names to centered format
    col_labels = " & ".join([r"\thead{" + col + "}" for col in df.columns])

    # Generate LaTeX table
    latex_table = df.to_latex(
        escape=False,  # Allow LaTeX commands
        column_format="|l|" + "c|" * len(df.columns),  # Ensures proper column alignment
        float_format="%.3f",  # Specify the number of decimal places
        index=True,  # Keep the row labels
        bold_rows=True,  # Makes the row labels bol
    )

    # Replace default column names with centered headers
    latex_table = latex_table.replace(" & ".join(df.columns), col_labels, 1)

    # Save to file
    with open(output_file, "w") as f:
        f.write(latex_table)

    print(f"LaTeX table saved as {output_file}!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--robot", help="the robot you want to use", default="drone")
    args = parser.parse_args()

    csv_file = f"{args.robot}_error.csv"
    output_file = f"{args.robot}_data.tex"  # Update output file to match the robot

    latex_table(csv_file, output_file)
