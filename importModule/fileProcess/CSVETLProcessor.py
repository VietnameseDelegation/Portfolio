import logging
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

from config.config_processor import ConfigProcessor
from database.db_connector import DBConnector
from importModule.fileProcess.file_processor import FileProcessor
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('etl_process.log')
    ]
)
logger = logging.getLogger(__name__)


class CSVETLProcessor:
    def __init__(self, config_path: str = "config.ini"):
        self.config_processor = ConfigProcessor(config_path)
        self.db_connector = DBConnector(self.config_processor)

    def _get_csv_files(self) -> List[Path]:
        """Return a list of CSV files in the input folder"""
        input_folder = Path(self.config_processor.get_import_config()['input_folder'])
        return list(input_folder.glob("*.csv"))

    def _process_file(self, file_path: Path) -> tuple:
        """Process a single CSV file, returning stats or error"""
        try:
            file_processor = FileProcessor(self.db_connector, self.config_processor.get_import_config())
            success, errors = file_processor.process_csv_file(file_path)
            return file_path.name, success, errors, None
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            return file_path.name, 0, 0, str(e)

    def _get_export_tables(self, table_names: List[str] = None) -> List[str]:
        """Fetch export table names from DB if not provided"""
        if table_names is not None:
            return table_names

        query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE 'EXPORT_%'"
        result = self.db_connector.execute_query(query)
        if result is not None and not result.empty:
            return result['TABLE_NAME'].tolist()
        return []



    def import_csv_files(self):
        """Import all CSV files from input folder using parallel processing"""
        csv_files = self._get_csv_files()
        if not csv_files:
            logger.info("No CSV files found in input folder")
            return

        logger.info(f"Found {len(csv_files)} CSV files to process")
        max_processes = len(csv_files)

        total_success = total_errors = 0
        with ProcessPoolExecutor(max_workers=max_processes) as executor:
            futures = {executor.submit(self._process_file, f): f for f in csv_files}
            for future in as_completed(futures):
                filename, success, errors, error_msg = future.result()
                if error_msg:
                    logger.error(f"Failed to process {filename}: {error_msg}")
                else:
                    logger.info(f"Completed {filename}: {success} successful, {errors} rejected")
                    total_success += success
                    total_errors += errors

        logger.info(f"Import completed: {total_success} total successful rows, {total_errors} total rejected rows")

    def export_tables(self, table_names: List[str] = None):
        """Export specified tables to CSV files"""
        export_config = self.config_processor.get_export_config()
        tables_to_export = self._get_export_tables(table_names)
        if not tables_to_export:
            logger.info("No export tables found")
            return

        file_processor = FileProcessor(self.db_connector, self.config_processor.get_import_config())
        for table in tables_to_export:
            file_processor.export_table(table, export_config)

    def list_export_tables(self):
        """Print all available export tables"""
        tables = self._get_export_tables()
        if tables:
            print("Available export tables:")
            for table in tables:
                print(f"  - {table}")
        else:
            print("No export tables found")
