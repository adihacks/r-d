from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import glob
import os
from datetime import datetime

def add_perfectly_fitted_image(doc, image_path):
    """Add image with perfect fit below heading"""
    # Calculate maximum available width (6.5 inches for standard margins)
    max_width = Inches(6.5)
    
    # Create perfectly tight paragraph for image
    para = doc.add_paragraph()
    para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    para.paragraph_format.space_before = Pt(0)  # No space above image
    para.paragraph_format.space_after = Pt(1)   # No space below image
    para.paragraph_format.line_spacing = 1.0    # Exactly single spacing
    
    # Add image with perfect fit
    image_width = Cm(13.35 )  # to fit inside typical A4 width (max ~6.2 in)
    image_height = Cm(20.00)
    run = para.add_run()
    run.add_picture(image_path, width=image_width, height=image_height)  # Auto-scales height

def create_perfect_fit_report():
    # Find images
    sample_images = sorted(glob.glob("sample*.png") + glob.glob("sample*.jpg"))
    thread_images = sorted(glob.glob("thread*.png") + glob.glob("thread*.jpg"))
    
    # Load template document
    try:
        doc = Document("g.docx")
    except FileNotFoundError:
        print("Error: g.docx not found in directory")
        return
    
    #Remove ALL empty paragraphs that could create gaps
    for para in list(doc.paragraphs):
        if not para.text.strip() and len(para.runs) == 0:
            p = para._element
            p.getparent().remove(p)
    
    #Add SAMPLE section with perfect image fit

    if sample_images:
        # Add heading with zero spacing
        heading = doc.add_paragraph("SAMPLE")
        heading.runs[0].font.bold = True
        heading.runs[0].font.underline = True
        heading.paragraph_format.space_after = Cm(.5)  # No space after heading
        
        # Add first image with perfect fit below heading
        add_perfectly_fitted_image(doc, sample_images[0])
        doc.add_paragraph("")

        # Add remaining sample images if any
        for img in sample_images[1:]:
            add_perfectly_fitted_image(doc, img)
    
    # Add THREAD section with same perfect fit
    if thread_images:
        heading = doc.add_paragraph("THREAD")
        heading.runs[0].font.bold = True
        heading.runs[0].font.underline = True
        heading.paragraph_format.space_after = Cm(.5)
        
        add_perfectly_fitted_image(doc, thread_images[0])
        for img in thread_images[1:]:
            add_perfectly_fitted_image(doc, img)
    
    # Save the perfectly fitted report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = f"breach_report_perfect_fit_{timestamp}.docx"
    doc.save(output_file)
    
    print(f"Perfect fit report generated: {output_file}")

if __name__ == "__main__":
    create_perfect_fit_report()
    