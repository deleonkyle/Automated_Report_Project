import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Configure logging
logging.basicConfig(filename="report.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ensure output directory exists
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load and preprocess data
def load_data():
    try:
        df = pd.read_csv(os.path.join("data", "insurance.csv"))
        df = df.dropna()  # Remove missing values if any
        logging.info("Data loaded successfully")
        return df
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        return None

# Generate charts
def create_charts(df):
    try:
        sns.set(style="whitegrid")

        # Chart 1: Age distribution histogram
        plt.figure(figsize=(8, 5))
        sns.histplot(df['age'], bins=20, kde=True, color="skyblue")
        plt.title('Age Distribution of Patients')
        plt.xlabel('Age')
        plt.ylabel('Count')
        plt.savefig(os.path.join(OUTPUT_DIR, "age_distribution.png"))
        plt.close()

        # Chart 2: Average charges by region
        plt.figure(figsize=(8, 5))
        avg_charges = df.groupby("region")["charges"].mean()
        sns.barplot(x=avg_charges.index, y=avg_charges.values, palette="coolwarm")
        plt.title("Average Medical Charges by Region")
        plt.xlabel("Region")
        plt.ylabel("Average Charges ($)")
        plt.savefig(os.path.join(OUTPUT_DIR, "avg_charges_by_region.png"))
        plt.close()

        logging.info("Charts generated successfully")

    except Exception as e:
        logging.error(f"Error generating charts: {e}")

# Generate PDF report
def generate_pdf(client_name, df):
    try:
        pdf_path = os.path.join(OUTPUT_DIR, f"{client_name}_Report.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph(f"Medical Insurance Report for {client_name}", styles["Title"]))
        story.append(Spacer(1, 12))

        # Summary statistics
        summary_text = f"""
        <b>Total Records:</b> {len(df)}<br/>
        <b>Average Age:</b> {df['age'].mean():.2f}<br/>
        <b>Average Charges:</b> ${df['charges'].mean():,.2f}<br/>
        <b>Top Region (Highest Charges Avg.):</b> {df.groupby("region")["charges"].mean().idxmax()}
        """
        story.append(Paragraph(summary_text, styles["BodyText"]))
        story.append(Spacer(1, 12))

        # Add charts
        story.append(Paragraph("Age Distribution of Patients", styles["Heading2"]))
        story.append(Image(os.path.join(OUTPUT_DIR, "age_distribution.png"), width=400, height=300))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Average Charges by Region", styles["Heading2"]))
        story.append(Image(os.path.join(OUTPUT_DIR, "avg_charges_by_region.png"), width=400, height=300))
        story.append(Spacer(1, 12))

        # Table: Average charges per region
        avg_charges_table = [[region, f"${value:,.2f}"] for region, value in df.groupby("region")["charges"].mean().items()]
        table = Table([["Region", "Average Charges ($)"]] + avg_charges_table)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(Paragraph("Average Charges by Region (Table)", styles["Heading2"]))
        story.append(table)

        # Build PDF
        doc.build(story)
        logging.info(f"Report generated: {pdf_path}")

    except Exception as e:
        logging.error(f"Error generating PDF: {e}")

# Full workflow
def main(client_name="ClientXYZ"):
    df = load_data()
    if df is not None:
        create_charts(df)
        generate_pdf(client_name, df)

# Run script
if __name__ == "__main__":
    main()
