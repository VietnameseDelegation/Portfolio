from processor.CSVETLProcessor import CSVETLProcessor
import multiprocessing as mp
import argparse
import time



def main():
    parser = argparse.ArgumentParser(description='CSV to SQL Server ETL Processor')
    parser.add_argument('--import', dest='do_import', action='store_true', help='Import CSV files from input folder')
    parser.add_argument('--export', nargs='*', metavar='TABLE_NAME', help='Export tables to CSV')
    parser.add_argument('--list-tables', action='store_true', help='List available export tables')
    parser.add_argument('--config', default='config.ini', help='Path to configuration file')

    args = parser.parse_args()

    processor = CSVETLProcessor(args.config)

    if args.list_tables:
        processor.list_export_tables()
    elif args.export is not None:
        # If no table names provided, export all
        table_names = args.export if args.export else None
        processor.export_tables(table_names)
    elif args.do_import:
        processor.import_csv_files()
    else:
        parser.print_help()


if __name__ == "__main__":
    # Required for multiprocessing on Windows
    start = time.time()
    mp.freeze_support()
    main()
    end = time.time()
    print("trvalo {:.6f} sec.".format((end - start)))