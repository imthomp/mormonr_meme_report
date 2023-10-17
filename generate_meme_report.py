from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, PageBreak, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import date
import sqlite3
import os

# Define the PDF filename and page size
pdf_filename = 'meme_report.pdf'
page_size = letter

# Create a PDF document with adjusted margins
# You can adjust the margins as needed
doc = SimpleDocTemplate(pdf_filename, pagesize=page_size, leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)

# Define data source (SQLite database)
db_filename = 'memes.db'

# Initialize a list to store meme data
meme_data = []

# Connect to the SQLite database
conn = sqlite3.connect(db_filename)
cursor = conn.cursor()

# Retrieve the top 100 memes from the database, sorted by like count
cursor.execute('SELECT date, local_file, likes_count FROM memes ORDER BY likes_count DESC LIMIT 100')
top_100_memes = [(row[0], row[1], row[2]) for row in cursor.fetchall()]

# Retrieve the bottom 100 memes from the database, sorted by like count
cursor.execute('SELECT date, local_file, likes_count FROM memes ORDER BY likes_count ASC LIMIT 100')
bottom_100_memes = [(row[0], row[1], row[2]) for row in cursor.fetchall()]

# Close the database connection
conn.close()

# Initialize a list to store PDF content
pdf_content = []

# Split meme data into groups of 9 entries per page
entries_per_page = 9
pages = [meme_data[i:i + entries_per_page] for i in range(0, len(meme_data), entries_per_page)]

# Register the font (assuming you have the .ttf files)
pdfmetrics.registerFont(TTFont('Vollkorn', 'Vollkorn-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Vollkorn-Bold', 'Vollkorn-Bold.ttf'))

# Convert hex to ReportLab Color
def hex_to_color(hex_code):
    return Color(*[int(hex_code[i:i+2], 16)/255.0 for i in (1, 3, 5)])

# Define colors
mormonr_white = hex_to_color("#EFEFEF")  # Mormonr white
mormonr_black = hex_to_color("#444444")  # Mormonr black
mormonr_orange = hex_to_color("#cb5a4e") # Mormonr orange

# Define page size
PAGE_WIDTH, PAGE_HEIGHT = letter  # Assuming letter page size

# Draw background
def draw_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(mormonr_white)
    canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=True)
    canvas.restoreState()

# Add background to the PDF document
doc = SimpleDocTemplate(pdf_filename, pagesize=page_size, leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
doc.build(pdf_content, onFirstPage=draw_background, onLaterPages=draw_background)

# Define table style with general attributes
table_style = TableStyle([
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('BOTTOMPADDING', (0, 0), (-1, -1), .20*inch),
    ('LEFTPADDING', (0, 0), (-1, -1), .25*inch),
    ('RIGHTPADDING', (0, 0), (-1, -1), .25*inch),
    ('FONT', (0, 0), (-1, -1), 'Vollkorn', 12),
    ('TEXTCOLOR', (0, 0), (-1, -1), mormonr_black),
    ('BACKGROUND', (0, 0), (-1, -1), mormonr_white),
])

# Define a function to create the main title page
def create_main_title_page():
    # Load the logo
    logo_path = 'logo.png'
    if os.path.exists(logo_path):
        logo_img = Image(logo_path, width=1951*.2, height=1723*.2)  # You can adjust the dimensions if necessary
        logo_img.hAlign = 'CENTER'
        pdf_content.append(Spacer(1, 1*inch))
        pdf_content.append(logo_img)
        pdf_content.append(Spacer(1, 0.25*inch))  # Adds a small space between the logo and the title

    # Add the title "Twitter Meme Report"
    main_title_style = ParagraphStyle('MainTitle', parent=getSampleStyleSheet()['Heading1'], fontName='Vollkorn-Bold', alignment=1, fontSize=30, leading=30*1.2, textColor=mormonr_orange)
    title = Paragraph("Twitter Meme Report", main_title_style)
    pdf_content.append(title)
    pdf_content.append(Spacer(1, 0.25*inch))  # Adds a small space between the title and the date

    # Add the compilation date
    compilation_date = "October 10, 2023"
    date_paragraph = Paragraph(f"{compilation_date}", main_title_style)
    pdf_content.append(date_paragraph)
    pdf_content.append(PageBreak())

# Use a function to process meme data to avoid repetitive code
def process_meme_data(meme_data_section):
    # Split meme data into groups of 9 entries per page
    pages = [meme_data_section[i:i + entries_per_page] for i in range(0, len(meme_data_section), entries_per_page)]

    # Create a PDF page for each group of 9 entries
    for page_data in pages:
        # Create a table for the page
        table_data = []
        
        date_rows = []   # List to store row indices of dates
        like_rows = []   # List to store row indices of like counts
        
        # Iterate over the page_data in steps of 3 to form rows
        for i in range(0, len(page_data), 3):
            img_row = []
            date_row = []
            likes_count_row = []
            
            # Collect data for 3 memes to form a single row
            for j in range(i, min(i + 3, len(page_data))):
                date, local_file, likes_count = page_data[j]
                image_file = os.path.join('twitter_data', 'memes', local_file)
                if os.path.exists(image_file):
                    img = Image(image_file, width=1.5*inch, height=1.5*inch)
                    img.hAlign = 'CENTER'
                    img_row.append(img)
                    date_row.append(date)
                    likes_count_row.append(f'Likes: {likes_count}')
                else:
                    img_row.append('')
                    date_row.append('')
                    likes_count_row.append('')
            
            # Append the collected data for the 3 memes as rows to table_data
            table_data.append(img_row)
            
            date_rows.extend(range(len(table_data), len(table_data) + 3))   # Store the row indices of date
            table_data.append(date_row)
            
            like_rows.extend(range(len(table_data), len(table_data) + 3))   # Store the row indices of like count
            table_data.append(likes_count_row)
            
            table_data.append([''] * 3)  # Spacer to add some vertical space
        
        # Create the table for the page
        table = Table(table_data)
        table.setStyle(table_style)

        # Applying specific styles for dates and like counts
        for col in range(3):
            for row in date_rows:
                table.setStyle(TableStyle([('TEXTCOLOR', (col, row), (col, row), mormonr_black)]))
            
            for row in like_rows:
                table.setStyle(TableStyle([('TEXTCOLOR', (col, row), (col, row), mormonr_orange)]))

        # Add the table to the PDF content
        pdf_content.append(table)
        
        # Add a page break between groups of 9 entries
        pdf_content.append(PageBreak())

# Add the main title page at the beginning of the document
create_main_title_page()

# Define a large style for the section titles
title_style = ParagraphStyle('TitleStyle', parent=getSampleStyleSheet()['Heading1'], fontName='Vollkorn-Bold', alignment=1, spaceAfter=12, fontSize=80, leading=80*1.2, textColor=mormonr_black)

# Add Top 100 Memes
pdf_content.append(Spacer(1, PAGE_HEIGHT / 4))  # Subtracting half the font size to center more accurately
pdf_content.append(Paragraph("Top 100 Memes", title_style))
pdf_content.append(PageBreak())
process_meme_data(top_100_memes)

# Add Bottom 100 Memes
pdf_content.append(Spacer(1, PAGE_HEIGHT / 4))  # Subtracting half the font size to center more accurately
pdf_content.append(Paragraph("Bottom 100 Memes", title_style))
pdf_content.append(PageBreak())
process_meme_data(bottom_100_memes)

# Build the PDF document
doc.build(pdf_content)

print(f'PDF report "{pdf_filename}" generated successfully.')