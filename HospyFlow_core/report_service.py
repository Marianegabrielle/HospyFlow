import csv
import os
from abc import ABC, abstractmethod
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class ExportStrategy(ABC):
    @abstractmethod
    def export(self, data, filename):
        pass

class PDFExportStrategy(ExportStrategy):
    def export(self, data, filename):
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        
        c = canvas.Canvas(filepath, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "Rapport ClinicFlow Analytics")
        c.setFont("Helvetica", 12)
        c.drawString(100, 730, f"Plage de dates: {data['plage_date']}")
        c.drawString(100, 710, "Métriques clés:")
        
        y = 690
        for key, value in data['metrics'].items():
            c.drawString(120, y, f"- {key}: {value}")
            y -= 20
        
        c.save()
        print(f"[EXPORT] PDF generated at {filepath}")
        return filepath

class CSVExportStrategy(ExportStrategy):
    def export(self, data, filename):
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Metrique', 'Valeur'])
            writer.writerow(['Plage de dates', data['plage_date']])
            for key, value in data['metrics'].items():
                writer.writerow([key, value])
        
        print(f"[EXPORT] CSV generated at {filepath}")
        return filepath

class ReportGenerator:
    def __init__(self, strategy: ExportStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: ExportStrategy):
        self._strategy = strategy

    def generate(self, report_instance, format="pdf"):
        filename = f"rapport_{report_instance.id}.{format}"
        data = {
            'plage_date': report_instance.plage_date,
            'metrics': report_instance.donnees_metriques
        }
        return self._strategy.export(data, filename)
