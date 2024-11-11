import logging
import os
import sqlite3

import pandas as pd
from dotenv import load_dotenv

load_dotenv()
logger = logging.basicConfig(level=logging.INFO)


def get_table_name(filepath: str) -> str:
    return os.path.splitext(os.path.basename(filepath))[0]


def save_to_db(df: pd.DataFrame, filepath: str) -> bool:
    db_name = os.environ.get("DB_NAME")
    table_name = get_table_name(filepath)

    try:
        with sqlite3.connect(db_name) as conn:
            df.to_sql(table_name, conn, if_exists="replace", index=False)
        logger.info(
            f"Data successfully saved to table '{table_name}' in '{db_name}' database."
        )
        return True
    except sqlite3.OperationalError as e:
        logger.error(f"OperationalError: Could not save to database. Details: {e}")
    except sqlite3.DatabaseError as e:
        logger.error(
            f"DatabaseError: An issue occurred with the database schema or connection. Details: {e}"
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

    return False


def load_csv_df(filepath: str) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    try:
        df = pd.read_csv(filepath)
        return df
    except Exception as e:
        raise Exception(f"Error loading CSV file '{filepath}': {e}")


def load_excel_df(filepath: str) -> pd.DataFrame:
    """Load an Excel file into a DataFrame."""
    try:
        with pd.ExcelFile(filepath) as excel_file:  # Use context manager
            sheets = excel_file.sheet_names

            # Check if the workbook has only one sheet
            if len(sheets) > 1:
                # Create an empty list to hold DataFrames for multiple sheets
                df_list = []

                # Loop through the sheets, load them into DataFrames, and append to the list
                for sheet in sheets:
                    try:
                        df = pd.read_excel(
                            excel_file, sheet_name=sheet
                        )  # Read each sheet
                        df["Source_Sheet"] = (
                            sheet  # Optional: Add a column to identify the sheet
                        )
                        df_list.append(df)  # Append the DataFrame to the list
                    except Exception as e:
                        print(f"Error reading sheet '{sheet}': {e}")

                # Concatenate all DataFrames, handling different shapes
                combined_df = pd.concat(df_list, ignore_index=True, sort=False)
                return combined_df

            # If there's only one sheet, read it directly
            return pd.read_excel(excel_file, sheet_name=sheets[0])
    except Exception as e:
        raise Exception(f"Error loading Excel file '{filepath}': {e}")


def load_file_to_df(filepath: str) -> pd.DataFrame:
    """Load a file into a DataFrame based on its extension."""
    _, file_extension = os.path.splitext(filepath)
    if file_extension.lower() == ".csv":
        return load_csv_df(filepath)
    elif file_extension.lower() in [".xls", ".xlsx"]:
        return load_excel_df(filepath)
    else:
        raise Exception(
            f"Unsupported file type '{file_extension}'. Please upload a .csv or .xlsx file."
        )


def load_filebytes_to_df(uploaded_file):
    file_extension = uploaded_file.type
    if file_extension == "text/csv":
        df = pd.read_csv(uploaded_file)
    elif file_extension in [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
    ]:
        df = pd.read_excel(uploaded_file)
    else:
        raise Exception(
            f"Unsupported file type '{file_extension}'. Please upload a .csv or .xlsx file."
        )
    return df
