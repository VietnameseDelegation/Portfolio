from database.db_connector import DBConnector
from dao.report_dao import ReportDAO
from models.report import SummaryReportDTO

class ReportService:
    def __init__(self, connector: DBConnector):
        self.report_dao = ReportDAO(connector)

    def generate_summary_report(self) -> SummaryReportDTO:
        return self.report_dao.get_summary_report()
