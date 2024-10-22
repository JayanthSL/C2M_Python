import os
import matplotlib

matplotlib.use("Agg")
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")


@app.route("/upload", methods=["POST"])
def upload_file():
    logger.debug("Received request to /upload")

    if "file" not in request.files:
        logger.error("No file part in the request")
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "":
        logger.error("No selected file")
        return "No selected file", 400

    logger.debug(f"Loading CSV data from file: {file.filename}")
    try:
        data = pd.read_csv(file)
        logger.debug("CSV data loaded successfully")
    except Exception as e:
        logger.exception("Failed to load CSV data")
        return "Error loading CSV file", 500
    logger.debug(f"Data columns: {data.columns}")

    if data.shape[1] < 3:
        logger.error("Insufficient columns in CSV file")
        return "CSV file must contain at least 3 columns", 400

    traffic_source_columns = data.columns[1:-1]
    sales_column = data.columns[-1]

    logger.debug(f"Traffic source columns: {traffic_source_columns}")
    logger.debug(f"Sales column: {sales_column}")

    traffic_sources = data[traffic_source_columns].mean()
    months = data[data.columns[0]]
    sales = data[sales_column]

    logger.debug("Creating visualizations")
    fig = plt.figure(figsize=(10, 10))

    plt.subplot(221)
    plt.pie(
        traffic_sources,
        labels=traffic_sources.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"],
    )
    plt.axis("equal")
    plt.title("Average Website Traffic Sources")

    plt.subplot(222)
    plt.bar(months, sales, color="skyblue")
    plt.title("Monthly Sales")
    plt.xlabel("Months")
    plt.ylabel("Sales")

    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)

    logger.debug("Visualizations created and saved to buffer")

    chart_img = Image.open(buffer)
    width, height = chart_img.size

    infographic = Image.new("RGB", (width, height + 200), "white")
    draw = ImageDraw.Draw(infographic)

    title_font = ImageFont.load_default()
    draw.text(
        (10, 10),
        "Infographic: Website Traffic and Sales Data",
        font=title_font,
        fill="black",
    )
    draw.text(
        (10, 40),
        "This infographic visualizes average website traffic sources and monthly sales trends.",
        font=title_font,
        fill="black",
    )

    infographic.paste(chart_img, (0, 80))

    infographic_path = os.path.join(DOWNLOAD_FOLDER, "infographic.png")
    infographic.save(infographic_path)

    logger.debug(f"Infographic saved to: {infographic_path}")

    return f"Infographic saved to: {infographic_path}", 200


if __name__ == "__main__":
    app.run(debug=True)