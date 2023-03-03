from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from datetime import datetime


def generate_pdf(data, filename):

    """
    This function generates a PDF file from the data provided.

    Args:
        data: The data to be added to the PDF file

    Returns:
        None

    """

    # Create a list of lists to hold the table data
    table_data = [["ID", "Expense", "Tag", "Timestamp"]]

    # Add data to the table
    total_expenses = 0
    for d in data:
        table_data.append([d["id"], int(d["expense"]), d["tag"], d["timestamp"]])
        total_expenses += int(d["expense"])

    # Add the total expenses row to the table
    table_data.append(["", "Total Expenses", "", "{:.2f}".format(total_expenses)])

    # Set up the PDF document
    pdf_filename = filename + ".pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    styles = getSampleStyleSheet()

    # Add a title to the document
    title = Paragraph("Your Expenditures", styles["Title"])
    elements = [title, Spacer(1, 20)]

    # Add a timestamp to the document
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_paragraph = Paragraph(f"Generated on: {timestamp}", styles["Normal"])
    elements.append(timestamp_paragraph)
    elements.append(Spacer(1, 20))

    # Create the table
    table = Table(table_data, colWidths=[50, 150, 150, 150], hAlign="CENTER")

    # Set the table style
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 14),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -2), colors.beige),
                ("TEXTCOLOR", (0, 1), (-1, -2), colors.black),
                ("FONTNAME", (0, 1), (-1, -2), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -2), 10),
                ("ALIGN", (0, 1), (-1, -2), "CENTER"),
                ("VALIGN", (0, 0), (-1, -2), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    # Add the table to the PDF document
    elements.append(table)
    doc.build(elements)
