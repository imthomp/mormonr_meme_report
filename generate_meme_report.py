from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, PageBreak
from reportlab.lib.units import inch
import sqlite3
import os

# Define the PDF filename and page size
pdf_filename = 'meme_report.pdf'
page_size = letter

# Create a PDF document
doc = SimpleDocTemplate(pdf_filename, pagesize=page_size)

# Define data source (SQLite database)
db_filename = 'memes.db'

# Initialize a list to store meme data
meme_data = []

# Connect to the SQLite database
conn = sqlite3.connect(db_filename)
cursor = conn.cursor()

# Retrieve the top 300 memes from the database
cursor.execute('SELECT date, local_file, likes_count FROM memes ORDER BY likes_count DESC LIMIT 300')

# Fetch meme data
for row in cursor.fetchall():
    date, local_file, likes_count = row
    meme_data.append([date, local_file, likes_count])

# Close the database connection
conn.close()

# Initialize a list to store PDF content
pdf_content = []

# Define table headers
table_headers = ['Date', 'Image', 'Likes']

# Create a table with meme data
table_data = [table_headers]  # Initialize table data

# Define table style
table_style = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
])

# Add meme data to the table
image_path = os.path.join('twitter_data', 'memes')

for meme in meme_data:
    date, local_file, likes_count = meme
    image_file = os.path.join(image_path, local_file)
    if os.path.exists(image_file):
        img = Image(image_file, width=1.25*inch, height=1.25*inch)  # Adjust image size here
        table_data.append([date, img, f'Likes: {likes_count}'])

# Create the table
table = Table(table_data, colWidths=[2.5*inch, 3*inch, 1.0*inch])  # Adjust column width here

# Apply the table style
table.setStyle(table_style)

# Add the table to the PDF content
pdf_content.append(table)

# Build the PDF document
doc.build(pdf_content)

print(f'PDF report "{pdf_filename}" generated successfully.')