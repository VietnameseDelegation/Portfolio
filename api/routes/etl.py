from fastapi import APIRouter, BackgroundTasks
import logging
import os
from importModule.fileProcess.CSVETLProcessor import CSVETLProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

def get_processor():
    # Helper to create config processor
    # Ensure config.ini is accessible
    return CSVETLProcessor("config.ini")

@router.post("/import")
def run_import(background_tasks: BackgroundTasks):
    processor = get_processor()
    background_tasks.add_task(processor.import_csv_files)
    return {"message": "Import process started in background"}

@router.post("/export")
def run_export(background_tasks: BackgroundTasks):
    processor = get_processor()
    # Export all tables for now
    background_tasks.add_task(processor.export_tables)
    return {"message": "Export process started in background"}

@router.get("/logs")
def get_logs():
    log_file = "etl_process.log"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            # Read last 100 lines maybe? Or full content.
            # Reading full content for now, assuming not huge.
            return {"logs": f.read()}
    return {"logs": "Log file not found"}
