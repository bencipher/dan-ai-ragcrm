# @lru.cache
import logging
import os
import sqlite3

import pandas as pd
from dotenv import load_dotenv

load_dotenv()
logger = logging.basicConfig(level=logging.INFO)


def get_uploaded_data():
    # query the db for data or maybe the memory, something like that.

    return "data"


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


def load_excel_to_df(filepath):
    # Load the Excel file
    try:
        excel_file = pd.ExcelFile(filepath)
        sheets = excel_file.sheet_names

        # Check if the workbook has only one sheet
        if len(sheets) > 1:
            # Create an empty list to hold DataFrames for multiple sheets
            df_list = []

            # Loop through the sheets, load them into DataFrames, and append to the list
            for sheet in sheets:
                try:
                    df = pd.read_excel(filepath, sheet_name=sheet)
                    df["Source_Sheet"] = (
                        sheet  # Optional: Add a column to identify the sheet
                    )
                    df_list.append(df)  # Append the DataFrame to the list

                except Exception as e:
                    print(f"Error reading sheet {sheet}: {e}")

            # Concatenate all DataFrames, handling different shapes
            combined_df = pd.concat(df_list, ignore_index=True, sort=False)
            return combined_df
        return pd.read_excel(filepath, sheet_name=sheets[0])
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return None
