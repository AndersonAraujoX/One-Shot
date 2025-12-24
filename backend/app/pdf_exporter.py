# backend/app/pdf_exporter.py
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from .models import Aventura

class PDFExporter:
    def __init__(self, aventura: Aventura):
        self.aventura = aventura
        self.styles = getSampleStyleSheet()

    def _add_story_element(self, story, title, content):
        story.append(Paragraph(title, self.styles['h2']))
        story.append(Paragraph(content, self.styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))

    def export_to_pdf(self) -> bytes:
        """Exporta a aventura para um arquivo PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, rightMargin=inch/2, leftMargin=inch/2,
                                topMargin=inch/2, bottomMargin=inch/2)
        
        story = []

        # Título
        story.append(Paragraph(self.aventura.titulo, self.styles['h1']))
        story.append(Spacer(1, 0.2*inch))

        # Sinopse
        self._add_story_element(story, "Sinopse", self.aventura.sinopse)

        # Ganchos da Trama
        ganchos = "<ul>" + "".join(f"<li>{gancho}</li>" for gancho in self.aventura.gancho_trama) + "</ul>"
        self._add_story_element(story, "Ganchos da Trama", ganchos)

        # Contexto
        self._add_story_element(story, "Contexto", self.aventura.contexto)

        # Estrutura
        story.append(Paragraph("Estrutura da Aventura", self.styles['h2']))
        for ato in self.aventura.estrutura:
            self._add_story_element(story, f"Ato: {ato.titulo}", ato.descricao)

        # Personagens
        story.append(Paragraph("Personagens Chave", self.styles['h2']))
        for npc in self.aventura.personagens_chave:
            if npc.url_imagem:
                story.append(Image(npc.url_imagem, width=2*inch, height=2*inch))
            self._add_story_element(story, npc.nome, f"Aparência: {npc.aparencia}<br/>Motivação: {npc.motivacao}")

        # Locais
        story.append(Paragraph("Locais Importantes", self.styles['h2']))
        for local in self.aventura.locais_importantes:
            if local.url_imagem:
                story.append(Image(local.url_imagem, width=4*inch, height=3*inch))
            self._add_story_element(story, local.nome, f"Atmosfera: {local.atmosfera}")

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
