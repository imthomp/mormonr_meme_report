from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Image, Spacer
from reportlab.platypus import Table, TableStyle, PageBreak
from reportlab.lib.units import inch
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

# Retrieve the top 300 memes from the database, sorted by like count
cursor.execute('SELECT date, local_file, likes_count FROM memes ORDER BY likes_count DESC LIMIT 300')

# Fetch meme data
for row in cursor.fetchall():
    date, local_file, likes_count = row
    meme_data.append([date, local_file, likes_count])

# Close the database connection
conn.close()

# Initialize a list to store PDF content
pdf_content = []

# Split meme data into groups of 6 entries per page
entries_per_page = 6
pages = [meme_data[i:i + entries_per_page] for i in range(0, len(meme_data), entries_per_page)]

# Define table style
table_style = TableStyle([
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
])

# Create a PDF page for each group of 6 entries
for page_data in pages:
    # Create a table for the page
    table_data = []
    
    for meme in page_data:
        date, local_file, likes_count = meme
        image_file = os.path.join('twitter_data', 'memes', local_file)
        if os.path.exists(image_file):
            img = Image(image_file, width=1.5*inch, height=1.5*inch)  # Adjust image size here
            img.hAlign = 'CENTER'
            table_data.append([img])
            table_data.append([date])
            table_data.append([f'Likes: {likes_count}'])
            table_data.append([Spacer(1, 0.2*inch)])  # Spacer to add some vertical space
    
    # Create the table for the page
    table = Table(table_data)
    table.setStyle(table_style)
    
    # Add the table to the PDF content
    pdf_content.append(table)
    
    # Add a page break between groups of 6 entries
    pdf_content.append(PageBreak())

# Build the PDF document
doc.build(pdf_content)

print(f'PDF report "{pdf_filename}" generated successfully.')