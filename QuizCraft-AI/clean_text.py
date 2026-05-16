#The raw text extracted from the PDF will have weird formatting — double spaces, newline characters
#mid-sentence, stray symbols. clean_text() collapses all of that into clean readable text. Then chunk_text() splits
#that text into smaller pieces. This is necessary because you can't dump an entire chapter into the AI in one go — it
#works better and stays within token limits when you feed it one focused chunk at a time, like feeding pages to a
#reader one at a time instead of the whole book.

import re

def clean_text(text):
    # Remove bullets and weird symbols
    text = re.sub(r'[•■►▪]', '', text)

    # Replace newlines with space (fix broken sentences)
    text = re.sub(r'\n+', ' ', text)

    # Remove unwanted characters (keep useful punctuation)
    text = re.sub(r'[^a-zA-Z0-9.,()\-+*/= ]', '', text)

    # Normalize multiple spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def chunk_text(text, size=500):
    # Split into smaller chunks for API
    chunks = []
    for i in range(0, len(text), size):
        chunks.append(text[i:i+size])
    return chunks
#returns the text after cleaning up extra spaces and all that
# \s represetns all the space(" ") , tab(\t) , newline (\n)
#\s+ represetns all doubled up 
#if bymistake we did some spacing twice than needed
#strip function removes any unecessary spaces in the start and the end 
# of the string

