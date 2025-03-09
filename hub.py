import os
import argparse
import logging
from datetime import datetime

# Install dependencies before running:
# pip install anthropic python-docx PyMuPDF reportlab

# Import Claude API client from Anthropics SDK
try:
    from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
except ImportError:
    # If the anthropic SDK is not installed, prompt the user
    raise ImportError("Please install the anthropic SDK with: pip install anthropic")

# Import libraries for reading DOCX/PDF and writing PDF
try:
    import fitz  # PyMuPDF for PDF reading
except ImportError:
    raise ImportError("Please install PyMuPDF for PDF reading: pip install PyMuPDF")
try:
    import docx  # python-docx for DOCX reading
except ImportError:
    raise ImportError("Please install python-docx for DOCX reading: pip install python-docx")
try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
except ImportError:
    raise ImportError("Please install reportlab for PDF generation: pip install reportlab")

def read_input_file(path: str) -> str:
    """Read text from a DOCX, PDF, or TXT file."""
    ext = path.lower().split('.')[-1]
    if ext == 'txt':
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        return text
    elif ext == 'docx':
        doc = docx.Document(path)
        # Extract paragraphs and separate with blank lines
        text = "\n\n".join([para.text for para in doc.paragraphs])
        return text
    elif ext == 'pdf':
        text = ""
        doc = fitz.open(path)
        for page in doc:
            text += page.get_text()  # extract text from each page
            text += "\n"
        return text
    else:
        raise ValueError("Unsupported file format. Please provide a .txt, .docx, or .pdf file.")

def ensure_output_dir(input_path: str, output_dir: str = None) -> str:
    """Determine and create the output directory for this run."""
    if output_dir:
        out_dir = output_dir
    else:
        # default to input filename (without extension) + "_novel"
        base = os.path.splitext(os.path.basename(input_path))[0]
        out_dir = base + "_novel"
    os.makedirs(out_dir, exist_ok=True)
    return out_dir

def setup_logging(log_path: str):
    """Configure logging to file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, mode='w', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def call_claude(client: Anthropic, prompt: str, model: str = "claude-3-opus-20240229", max_tokens: int = 8000) -> str:
    """Call Claude API with the given prompt and return the completion text."""
    # We use Claude in chat mode with a single user prompt followed by assistant response
    # The HUMAN_PROMPT and AI_PROMPT constants help format the prompt for Claude.
    full_prompt = f"{HUMAN_PROMPT}{prompt}{AI_PROMPT}"
    response = client.completions.create(
        model=model,
        max_tokens_to_sample=max_tokens,
        prompt=full_prompt,
        stop_sequences=[HUMAN_PROMPT]  # stop when a new human prompt would start
    )
    # The response object from anthropic SDK (if using `completions.create`) might have .completion attribute
    result = response.completion.strip()
    return result

def generate_outline(client: Anthropic, story_text: str) -> str:
    """Generate a novel outline from the short story text using Claude."""
    logging.info("Generating novel outline from the short story...")
    outline_prompt = (
        "You are a creative writing AI helping to expand a short story into a full-length novel.\n"
        "The novel should follow the events and characters of the short story, but greatly enrich the detail, plot, and character development, adding new chapters or subplots as needed.\n"
        "First, produce a detailed outline for the novel. Include a list of chapters with titles and a brief description of each chapter's events.\n\n"
        f"Short story:\n\"\"\"\n{story_text}\n\"\"\"\n\n"
        "Now provide the complete novel outline with chapter titles and descriptions:"
    )
    outline = call_claude(client, outline_prompt)
    logging.info("Outline generated. Saving outline to file.")
    return outline

def parse_outline(outline_text: str) -> list:
    """Parse the outline text into a list of (chapter_title, chapter_summary)."""
    chapters = []
    lines = [line.strip() for line in outline_text.splitlines() if line.strip()]
    for line in lines:
        # Common formats: "Chapter 1: Title – summary" or "1. Title: summary"
        if line.lower().startswith("chapter"):
            # Split at first colon or dash after chapter number
            parts = line.split(":", 1)
            if len(parts) == 2:
                title_part = parts[1].strip()
                # Sometimes title_part might include a dash then summary
                if " - " in title_part:
                    title, summary = title_part.split(" - ", 1)
                elif " – " in title_part:  # en dash
                    title, summary = title_part.split(" – ", 1)
                else:
                    # If no dash, maybe the rest is title only or summary only
                    # We'll treat the whole part as title (which might include a summary)
                    title, summary = title_part, ""
                chapter_title = title.strip()
                chapter_summary = summary.strip()
            else:
                # If outline line is just "Chapter X: Title" (no summary given)
                chapter_title = parts[0].split(None, 2)[-1]  # last word as title or number
                chapter_summary = ""
            chapters.append((chapter_title if chapter_title else f"Chapter {len(chapters)+1}", chapter_summary))
        elif line[0].isdigit():
            # e.g. "1. Something ..." format
            parts = line.split(".", 1)
            if len(parts) == 2:
                content = parts[1].strip()
                # split into title and summary if possible
                if ": " in content:
                    title, summary = content.split(": ", 1)
                elif " - " in content:
                    title, summary = content.split(" - ", 1)
                else:
                    title, summary = content, ""
                chapter_title = title.strip()
                chapter_summary = summary.strip()
                chapters.append((chapter_title if chapter_title else f"Chapter {len(chapters)+1}", chapter_summary))
    return chapters

def generate_chapter(client: Anthropic, chapter_num: int, chapter_title: str, chapter_summary: str,
                     outline_text: str, previous_text: str = "", continuity_notes: str = "") -> str:
    """Generate the full text of a single chapter using Claude, given the chapter info and context."""
    logging.info(f"Generating Chapter {chapter_num}: {chapter_title}")
    # Build the prompt for the chapter
    prompt_parts = []
    # Include continuity notes from previous chapters if available
    if continuity_notes:
        prompt_parts.append(f"Important details so far to maintain continuity:\n{continuity_notes}\n")
    # Include summary of previous chapter if available (for immediate continuity)
    if previous_text:
        prompt_parts.append(f"Previous chapter summary:\n{previous_text}\n")
    # Include the overall outline to remind structure (especially for longer context)
    prompt_parts.append(f"Novel outline:\n{outline_text}\n")
    # Now specific instruction for this chapter:
    chapter_instruction = (
        f"Write the full text of **Chapter {chapter_num}: {chapter_title}**. "
        f"This chapter is about: {chapter_summary if chapter_summary else 'the next part of the story as per the outline'}. "
        "Expand the story with vivid detail, dialogue, and character development. "
        "Ensure consistency with the events already told and maintain the narrative style. "
        "The chapter should flow naturally from the previous one and lead into the next."
    )
    prompt_parts.append(chapter_instruction)
    full_prompt = "\n".join(prompt_parts)
    chapter_text = call_claude(client, full_prompt, max_tokens=8000)
    logging.info(f"Chapter {chapter_num} generated ({len(chapter_text.split())} words).")
    return chapter_text

def update_continuity_notes(client: Anthropic, current_chapter_text: str, prior_notes: str = "") -> str:
    """Ask Claude to extract or update continuity notes based on the latest chapter."""
    prompt = (
        "You are a writing assistant tasked with tracking continuity. \n"
        "Below is the latest chapter of a novel. Provide a brief list of important facts, events, and character details from this chapter that should be remembered for consistency in future chapters. \n"
        "Combine with the previous continuity notes (if any) given after the chapter. \n\n"
        f"Chapter text:\n\"\"\"\n{current_chapter_text}\n\"\"\"\n\n"
        f"Previous continuity notes:\n{(prior_notes if prior_notes else 'None')}\n\n"
        "Now output the updated continuity notes (merged and summarized, if necessary):"
    )
    notes = call_claude(client, prompt, max_tokens=1000)
    return notes.strip()

def build_pdf(output_path: str, chapters: list):
    """Create a PDF with 1.5 line spacing and chapters starting on new pages."""
    doc = SimpleDocTemplate(output_path, pagesize=LETTER,
                             leftMargin=72, rightMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    # Define a normal style with 1.5 line spacing
    styles.add(ParagraphStyle(name='NovelText', parent=styles['Normal'],
                              fontName='Times-Roman', fontSize=12, leading=18))
    # Define a chapter title style
    styles.add(ParagraphStyle(name='ChapterTitle', parent=styles['Normal'],
                              fontName='Times-Roman', fontSize=16, leading=20, spaceAfter=12, alignment=1))  # centered
    novel_style = styles['NovelText']
    title_style = styles['ChapterTitle']

    flow = []
    for i, (title, text) in enumerate(chapters, start=1):
        # Start each chapter on a new page (except the first, which naturally starts)
        if i != 1:
            flow.append(PageBreak())
        # Chapter heading
        heading = f"Chapter {i}: {title}"
        flow.append(Paragraph(heading, title_style))
        # Split chapter text into paragraphs by blank lines
        paragraphs = [p.strip() for p in text.split("\n") if p.strip() != ""]
        for para in paragraphs:
            flow.append(Paragraph(para, novel_style))
            flow.append(Spacer(1, 12))  # small space between paragraphs
    # Build PDF
    doc.build(flow)
    logging.info(f"PDF novel generated at {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Expand a short story into a novel using Claude API.")
    parser.add_argument("input_file", help="Path to the short story file (.txt, .docx, or .pdf)")
    parser.add_argument("--output_dir", help="Directory to save the output (optional)")
    parser.add_argument("--model", help="Claude model to use (default 'claude-3-opus-20240229')", default="claude-3-opus-20240229")
    args = parser.parse_args()

    input_path = args.input_file
    out_dir = ensure_output_dir(input_path, args.output_dir)

    # Set up logging to a file in the output directory
    log_path = os.path.join(out_dir, "process.log")
    setup_logging(log_path)
    logging.info(f"Starting novel generation for input story: {input_path}")
    logging.info(f"Outputs will be saved to: {out_dir}")

    # Read the input story text
    try:
        story_text = read_input_file(input_path)
    except Exception as e:
        logging.error(f"Failed to read input file: {e}")
        return

    # Initialize Claude API client
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logging.error("Anthropic API key not found. Please set the ANTHROPIC_API_KEY environment variable.")
        return
    client = Anthropic(api_key=api_key)

    # Generate novel outline
    outline = generate_outline(client, story_text)
    outline_file = os.path.join(out_dir, "outline.txt")
    with open(outline_file, 'w', encoding='utf-8') as f:
        f.write(outline)
    logging.info(f"Outline saved to {outline_file}")
    # Parse outline into chapters list
    chapters_outline = parse_outline(outline)
    if not chapters_outline:
        logging.warning("Outline parsing returned no chapters. The outline format might be unexpected.")
    else:
        logging.info(f"Parsed outline: {len(chapters_outline)} chapters identified.")

    # Iterate through chapters and generate content
    generated_chapters = []
    continuity_notes = ""  # initialize continuity notes as empty
    prev_chapter_summary = ""
    for idx, (ch_title, ch_summary) in enumerate(chapters_outline, start=1):
        # For continuity, we include a brief summary of the previous chapter’s events or use continuity notes
        prev_context = ""
        if prev_chapter_summary:
            prev_context = prev_chapter_summary
        # Generate this chapter
        chapter_text = generate_chapter(client, idx, ch_title, ch_summary, outline, previous_text=prev_context, continuity_notes=continuity_notes)
        # Save chapter text to file
        chapter_filename = os.path.join(out_dir, f"Chapter{idx}.txt")
        with open(chapter_filename, 'w', encoding='utf-8') as f:
            f.write(chapter_text)
        logging.info(f"Chapter {idx} saved to {chapter_filename}")
        # Append to list for PDF compilation
        generated_chapters.append((ch_title, chapter_text))
        # Update continuity notes for next iteration
        try:
            continuity_notes = update_continuity_notes(client, chapter_text, prior_notes=continuity_notes)
        except Exception as e:
            logging.warning(f"Could not update continuity notes after chapter {idx}: {e}")
        # Create a short summary of this chapter to use as context for next (e.g., first few sentences)
        summary_prompt = (
            "Summarize the key events of the chapter below in 2-3 sentences (to use as context for the next chapter):\n\n"
            f"Chapter text:\n\"\"\"\n{chapter_text}\n\"\"\""
        )
        try:
            prev_chapter_summary = call_claude(client, summary_prompt, max_tokens=300)
            prev_chapter_summary = prev_chapter_summary.strip()
        except Exception as e:
            logging.warning(f"Failed to summarize Chapter {idx} for context: {e}")
            prev_chapter_summary = ""
        # (The summary and continuity_notes will be used in the next loop iteration)

    # Combine chapters into a PDF with formatting
    pdf_path = os.path.join(out_dir, "novel.pdf")
    try:
        build_pdf(pdf_path, generated_chapters)
    except Exception as e:
        logging.error(f"PDF generation failed: {e}")
    else:
        logging.info("Novel generation complete. All outputs are ready.")

if __name__ == "__main__":
    main()