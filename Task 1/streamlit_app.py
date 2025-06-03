import streamlit as st
from pdf2docx import Converter
from docx import Document
from PIL import Image
from io import BytesIO
from fpdf import FPDF
import os
import tempfile

st.title("PDF to DOCX Image and Text Extractor")

uploaded_pdf = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded_pdf:
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "input.pdf")
        docx_path = os.path.join(tmpdir, "converted.docx")
        images_folder = os.path.join(tmpdir, "images")
        os.makedirs(images_folder, exist_ok=True)

        with open(pdf_path, "wb") as f:
            f.write(uploaded_pdf.read())

        st.info("Converting PDF to Word")
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
        st.success("Conversion complete.")

        doc = Document(docx_path)

        full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        st.subheader("Extracted Text from Document")
        st.text_area("Text Content", full_text, height=300)

        st.subheader("Extracted Images")
        image_count = 0
        images_with_page = []
        for rel in doc.part._rels:
            rel_obj = doc.part._rels[rel]
            if "image" in rel_obj.target_ref:
                image_data = rel_obj.target_part.blob
                image = Image.open(BytesIO(image_data))
                images_with_page.append((image_count + 1, image))
                image_count += 1

        st.info("Generating PDF from images")
        pdf = FPDF()
        for _, img in images_with_page:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_img:
                img_path = tmp_img.name
                img.save(img_path, format="JPEG")
                pdf.add_page()
                pdf.image(img_path, x=10, y=10, w=190)
        image_pdf_path = os.path.join(tmpdir, "images.pdf")
        pdf.output(image_pdf_path)

        with open(image_pdf_path, "rb") as f:
            st.download_button("Download Images as PDF", f, "images.pdf", "application/pdf")

        st.download_button(
            "Download Extracted Text",
            full_text,
            "document_text.txt",
            "text/plain"
        )
