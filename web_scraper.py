import requests
from bs4 import BeautifulSoup
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
import os

def scrape_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")

def extract_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Customize this part to extract the specific content you want
    content = soup.find_all('p')
    return '\n'.join([p.get_text() for p in content])

def save_to_pdf(content, output_file='output.pdf'):
    pdf = SimpleDocTemplate(output_file, pagesize=letter)

    # Customize the margins and font size based on your preferences
    margin = 50
    styles = getSampleStyleSheet()
    style = ParagraphStyle('Custom', parent=styles['Normal'], fontSize=12)
    width, height = letter

    # Split the content into lines to fit within the specified width
    lines = content.split('\n')
    paragraphs = [Paragraph(line, style) for line in lines]

    pdf.build(paragraphs)



def scrape_and_save_pdf(urls):
    for url in urls:
        html_content = scrape_website(url)

        if html_content:
            extracted_content = extract_content(html_content)
            # Use the domain name from the URL as the filename
            domain_name = url.split('//')[1].split('/')[0]
            output_file = f"{domain_name}_output.pdf"
            save_to_pdf(extracted_content, output_file)
            print(f"PDF for {url} saved successfully as {output_file}")

if __name__ == "__main__":
    urls_to_scrape = [
	'https://d18rn0p25nwr6d.cloudfront.net/CIK-0000858877/0935436e-4d0a-4e31-9d8a-80d1b1e3b84c.pdf',
	'https://d18rn0p25nwr6d.cloudfront.net/CIK-0000858877/8d6c12f6-639f-453e-820e-2afdb099e560.pdf',
	'https://d18rn0p25nwr6d.cloudfront.net/CIK-0000858877/5b3c172d-f7a3-4ecb-b141-03ff7af7e068.pdf',
	'https://d18rn0p25nwr6d.cloudfront.net/CIK-0000858877/5e733344-72fb-4894-b954-2401d1e5f203.pdf'
    ]

    scrape_and_save_pdf(urls_to_scrape)



