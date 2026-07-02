from app.utils.pdf_generator import generate_report


class ReportService:

    @staticmethod
    def create(analysis):

        return generate_report(analysis)