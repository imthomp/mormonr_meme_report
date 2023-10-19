## generate_meme_report.py

import os
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, PageBreak, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# CONSTANTS
PDF_FILENAME = 'meme_report.pdf'
DB_FILENAME = 'memes.db'
PAGE_WIDTH, PAGE_HEIGHT = letter
ENTRIES_PER_PAGE = 9
DATE = "October 11, 2023"

# Colors
def hex_to_color(hex_code):
    return Color(*[int(hex_code[i:i+2], 16)/255.0 for i in (1, 3, 5)])

MORMONR_WHITE = hex_to_color("#EFEFEF")
MORMONR_BLACK = hex_to_color("#444444")
MORMONR_ORANGE = hex_to_color("#cb5a4e")

# Register fonts
pdfmetrics.registerFont(TTFont('Vollkorn', 'Vollkorn-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Vollkorn-Bold', 'Vollkorn-Bold.ttf'))

def fetch_data_from_db():
    with sqlite3.connect(DB_FILENAME) as conn:
        cursor = conn.cursor()
        top_100_memes = cursor.execute('SELECT date, local_file, likes_count FROM memes WHERE likes_count > 0 ORDER BY likes_count DESC LIMIT 99').fetchall()
        bottom_100_memes = cursor.execute('SELECT date, local_file, likes_count FROM memes WHERE likes_count > 0 ORDER BY likes_count ASC LIMIT 99').fetchall()
    return top_100_memes, bottom_100_memes

def draw_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(MORMONR_WHITE)
    canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=True)
    canvas.restoreState()

def create_main_title_page():
    pdf_content = []
    logo_path = 'logo.png'
    if os.path.exists(logo_path):
        logo_img = Image(logo_path, width=1951*.2, height=1723*.2)
        logo_img.hAlign = 'CENTER'
        pdf_content.extend([Spacer(1, 1*inch), logo_img, Spacer(1, 0.25*inch)])
    
    main_title_style = ParagraphStyle('MainTitle', parent=getSampleStyleSheet()['Heading1'], fontName='Vollkorn-Bold', alignment=1, fontSize=30, leading=30*1.2, textColor=MORMONR_ORANGE)
    title = Paragraph("X Meme Report", main_title_style)
    pdf_content.extend([title, Spacer(1, 0.25*inch), Paragraph(f"{DATE}", main_title_style), PageBreak()])
    return pdf_content

def process_meme_data(meme_data_section, title, starting_rank=1):
    pdf_content = []

    # Section title
    title_style = ParagraphStyle('TitleStyle', parent=getSampleStyleSheet()['Heading1'], fontName='Vollkorn-Bold', alignment=1, spaceAfter=12, fontSize=80, leading=80*1.2, textColor=MORMONR_BLACK)
    pdf_content.extend([Spacer(1, PAGE_HEIGHT / 4), Paragraph(title, title_style), PageBreak()])

    # Meme data processing
    pages = [meme_data_section[i:i + ENTRIES_PER_PAGE] for i in range(0, len(meme_data_section), ENTRIES_PER_PAGE)]
    table_style = TableStyle([
        # Default styles
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), .2*inch),
        ('LEFTPADDING', (0, 0), (-1, -1), .4*inch),
        ('RIGHTPADDING', (0, 0), (-1, -1), .4*inch),
        ('FONT', (0, 0), (-1, -1), 'Vollkorn', 12),
        ('TEXTCOLOR', (0, 0), (-1, -1), MORMONR_BLACK),
        ('BACKGROUND', (0, 0), (-1, -1), MORMONR_WHITE),
    ])

    current_rank = starting_rank
    for page_data in pages:
        table_data = []
        for i in range(0, len(page_data), 3):
            img_row, date_row, likes_count_row = [], [], []
            for j in range(i, min(i + 3, len(page_data))):
                date, local_file, likes_count = page_data[j]
                image_file = os.path.join('twitter_data', 'memes', local_file)
                if os.path.exists(image_file):
                    img_row.append(Image(image_file, width=1.5*inch, height=1.5*inch))
                    date_row.append(f"{current_rank}. {date}")
                    likes_count_row.append(f'Likes: {likes_count}')
                    current_rank += 1
                else:
                    img_row.extend(['', '', ''])
            table_data.extend([img_row, date_row, likes_count_row, [''] * 3])

        # Apply orange color to likes count rows
        for row_num in range(2, len(table_data), 4):
            table_style.add('TEXTCOLOR', (0, row_num), (-1, row_num), MORMONR_ORANGE)
        
        table = Table(table_data)
        table.setStyle(table_style)
        pdf_content.extend([table, PageBreak()])
    return pdf_content

# MAIN EXECUTION
if __name__ == '__main__':
    doc = SimpleDocTemplate(PDF_FILENAME, pagesize=letter, leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    top_100_memes, bottom_100_memes = fetch_data_from_db()

    pdf_content = create_main_title_page()
    pdf_content.extend(process_meme_data(top_100_memes, "Top 100 Memes"))
    pdf_content.extend(process_meme_data(bottom_100_memes, "Bottom 100 Memes"))

    doc.build(pdf_content, onFirstPage=draw_background, onLaterPages=draw_background)
    print(f'PDF report "{PDF_FILENAME}" generated successfully.')
