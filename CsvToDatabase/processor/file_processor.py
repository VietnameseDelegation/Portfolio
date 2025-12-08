import pandas as pd
from pathlib import Path
import logging
from typing import List, Tuple, Dict, Any
from datetime import datetime
import csv
import pyodbc

logger = logging.getLogger(__name__)


class FileProcessor:
    def __init__(self, db_connector, config: Dict[str, Any]):
        self.db_connector = db_connector
        self.config = config

    def infer_data_types(self, file_path: str, delimiter: str) -> Dict[str, str]:
        """Infer SQL data types from CSV sample"""
        scan_rows = self.config.get('scan_rows', 100)
        varchar_length = self.config.get('varchar_length', 255)

        df_sample = pd.read_csv(
                file_path,
                delimiter=delimiter,
                nrows=scan_rows,
                encoding='utf-8',
                quoting=csv.QUOTE_MINIMAL,
                dtype=str
            )

        schema = {}

        for column in df_sample.columns:
            col_data = df_sample[column].dropna()

            if col_data.empty:
                schema[column] = f'VARCHAR({varchar_length})'
                continue

            # Convert to string and clean data
            col_data = col_data.astype(str).str.strip()

            # Remove empty strings after stripping
            col_data = col_data[col_data != '']

            if col_data.empty:
                schema[column] = f'VARCHAR({varchar_length})'
                continue

            # Try to convert to numeric types
            numeric_success = True
            try:
                # Try converting the entire series to numeric
                numeric_series = pd.to_numeric(col_data, errors='coerce')
                if numeric_series.isna().any():
                    numeric_success = False
                else:
                    # Check if it's integer or float
                    if all(numeric_series.apply(lambda x: float(x).is_integer())):
                        schema[column] = 'INT'
                    else:
                        schema[column] = 'FLOAT'
                    continue
            except (ValueError, TypeError):
                numeric_success = False

            # Try to convert to datetime with specific format
            date_success = True
            try:
                # Try multiple date formats
                date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']
                for date_format in date_formats:
                    try:
                        pd.to_datetime(col_data, format=date_format, errors='raise')
                        schema[column] = 'DATETIME'
                        date_success = True
                        break
                    except (ValueError, TypeError):
                        date_success = False
                        continue

                if date_success:
                    continue
            except (ValueError, TypeError):
                date_success = False

            # Default to varchar - calculate actual max length
            max_length = col_data.str.len().max()
            actual_length = min(int(max_length) + 10, varchar_length)  # Add some buffer
            schema[column] = f'VARCHAR({actual_length})'

        return schema

    def validate_row(self, row: List, expected_columns: int, schema: Dict[str, str]) -> Tuple[bool, List]:
        """Validate a single row against schema and constraints"""
        # Check column count
        if len(row) != expected_columns:
            return False, row

        # Check for data type mismatches and empty required values
        for i, (value, (col_name, col_type)) in enumerate(zip(row, schema.items())):
            try:
                if 'INT' in col_type:
                    int(value)
                elif 'FLOAT' in col_type:
                    float(value)
                elif 'DATETIME' in col_type:
                    pd.to_datetime(value)
            except (ValueError, TypeError):
                return False, row

        return True, row

    def process_csv_file(self, file_path: Path) -> Tuple[int, int]:
        """Process a single CSV file and return (success_count, error_count)"""
        import_config = self.config

        try:
            schema = self.infer_data_types(file_path, ',')

            table_name = f"EXPORT_{file_path.stem}"

            if not self.db_connector.table_exists(table_name):
                self.db_connector.create_table_from_schema(table_name, schema)

            batch_size = import_config.get('batch_size', 1000)
            fast_executemany = import_config.get('fast_executemany', True)

            chunk_reader = pd.read_csv(
                file_path,
                sep=",",
                chunksize=batch_size,
                encoding="utf-8",
                quoting=csv.QUOTE_MINIMAL,
                dtype=str,
            )

            total_success = 0
            total_errors = 0

            reject_file_path = Path(import_config['rejects_folder']) / f"{file_path.stem}_rejects.csv"
            reject_file_created = False

            for chunk_idx, chunk in enumerate(chunk_reader):
                valid_rows = []
                invalid_rows = []

                expected_columns = len(chunk.columns)

                for row_idx, row in chunk.iterrows():
                    row_list = row.tolist()
                    is_valid, validated_row = self.validate_row(row_list, expected_columns, schema)

                    if is_valid:
                        valid_rows.append(validated_row)
                    else:
                        invalid_rows.append(validated_row)

                if valid_rows:
                    success_count = self._insert_batch(table_name, chunk.columns.tolist(), valid_rows, fast_executemany)
                    total_success += success_count

                if invalid_rows:
                    self._write_rejects(reject_file_path, chunk.columns.tolist(), invalid_rows, not reject_file_created)
                    reject_file_created = True
                    total_errors += len(invalid_rows)

                logger.info(
                    f"Processed chunk {chunk_idx + 1} for {file_path.name}: {len(valid_rows)} valid, {len(invalid_rows)} invalid")

            # Move processed file
            # self._move_processed_file(file_path)

            logger.info(f"Completed processing {file_path.name}: {total_success} successful, {total_errors} rejected")
            return total_success, total_errors

        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            return 0, 0

    def _insert_batch(self, table_name: str, columns: List[str], rows: List[List], fast_executemany: bool) -> int:
        """Insert a batch of rows into the database"""
        if not rows:
            return 0

        placeholders = ', '.join(['?' for _ in columns])
        columns_str = ', '.join([f'[{col}]' for col in columns])
        insert_sql = f"INSERT INTO [{table_name}] ({columns_str}) VALUES ({placeholders})"

        conn = self.db_connector.get_connection()
        try:
            cursor = conn.cursor()
            if fast_executemany:
                cursor.fast_executemany = True

            cursor.executemany(insert_sql, rows)
            conn.commit()
            return len(rows)
        except pyodbc.Error as e:
            conn.rollback()
            logger.error(f"Batch insert failed: {e}")
            return 0
        finally:
            conn.close()

    def _write_rejects(self, reject_file_path: Path, columns: List[str], invalid_rows: List[List], write_header: bool):
        """Write invalid rows to reject file"""
        # Ensure rejects directory exists
        reject_file_path.parent.mkdir(parents=True, exist_ok=True)

        mode = 'w' if write_header else 'a'
        with open(reject_file_path, mode, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(columns)
            writer.writerows(invalid_rows)

    def _move_processed_file(self, file_path: Path):
        """Move processed file to processed folder with timestamp"""
        processed_dir = Path(self.config['processed_folder'])

        # Ensure processed directory exists
        processed_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        new_path = processed_dir / new_filename

        file_path.rename(new_path)
        logger.info(f"Moved {file_path.name} to processed folder")

    def export_table(self, table_name: str, export_config: Dict[str, str]):
        """Export a table to CSV"""
        try:
            # Query table data
            query = f"SELECT * FROM [{table_name}]"
            df = self.db_connector.execute_query(query)

            if df is not None and not df.empty:
                # Create export filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_filename = f"{table_name}_{timestamp}.csv"
                export_path = Path(export_config['export_folder']) / export_filename

                # Export to CSV
                df.to_csv(export_path, index=False, encoding='utf-8')
                logger.info(f"Exported {table_name} to {export_path}")
            else:
                logger.warning(f"No data found in table {table_name}")

        except Exception as e:
            logger.error(f"Error exporting table {table_name}: {e}")