import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import re

url = "https://www.utrecsports.org/hours"
gyms = ["Recreational Sports Center", "Gregory Gym", "Bellmont Hall 406"]

# Function to get the facility name and link
def get_facility_name_and_link(cell):
    link = cell.find('a')
    if link:
        name = link.get_text(strip=True)
        facility_url = link['href']
        return name, facility_url
    return cell.get_text(strip=True), None

# Function to get the hours, either directly or by following the link
def get_hours_or_link(cell):
    link = cell.find('a')
    if link:
        return link['href']
    return cell.get_text(strip=True)

# Get the page content
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find the table with the id 'large-only'
table = soup.find('table', {'id': 'large-only'})

# Initialize a dictionary to store the hours and links for each facility
facilities_data = {}

# Loop through all rows containing facility and hours data in that table
rows = table.find_all('tr')

for row in rows:
    cols = row.find_all('td')
    if len(cols) != 5:
        continue
    
    # Get the facility name and URL (cell[0])
    facility_name, facility_link = get_facility_name_and_link(cols[0])
    full_url = urljoin(url, facility_link) if facility_link else None

    # Check if the facility matches one of the three specified
    if facility_name in gyms:
        mon_thu = get_hours_or_link(cols[1])
        friday = get_hours_or_link(cols[2])
        saturday = get_hours_or_link(cols[3])
        sunday = get_hours_or_link(cols[4])

        # Add facility data to the dictionary
        facilities_data[facility_name] = {
            'link': full_url,
            'Mon-Thu': mon_thu,
            'Fri': friday,
            'Sat': saturday,
            'Sun': sunday,
            'General Info': [],
            'Activities': [],
            'Features': [],
            'Today \'s Hours': [],
        }
        
def clean_paragraph_text(p):
    text = p.get_text(strip=True)

    # Normalize unicode characters
    text = text.replace('\u00a0', ' ')
    text = text.replace('\u2019', "'")

    # Insert space between:
    # - lowercase or . or , followed by uppercase (e.g., Blvd.Austin)
    text = re.sub(r'(?<=[a-z.,])(?=[A-Z])', ' ', text)

    # - letter followed by digit (e.g., Texas78712)
    text = re.sub(r'(?<=[a-zA-Z])(?=\d)', ' ', text)

    # - digit followed by letter (e.g., 78712Austin)
    text = re.sub(r'(?<=\d)(?=[a-zA-Z])', ' ', text)

    # Reduce multiple spaces to one
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# Function to scrape detailed data for each facility
def scrape_full_link(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialize dictionary to hold information scraped from this page
    arr = {}
    hours_list = {}

    # Find all <h2> elements for section headings (General Info, Activities, etc.)
    find_h2 = soup.find_all('h2')
    for h2 in find_h2:
        heading_text = h2.get_text(strip=True)
        arr[heading_text] = []

        if heading_text == "General Information":
            general_info = []
            # Scrape paragraphs under this heading
            p_tags = h2.find_all_next('p', limit=5)
            for p in p_tags:
                p_text = clean_paragraph_text(p)
                
                # Replace links in text with "Link Text: URL" format
                links = p.find_all('a')
                for link in links:
                    link_text = link.get_text(strip=True)
                    link_url = link.get('href')
                    p_text = p_text.replace(link_text, f"{link_text}: {link_url} ")

                # Append paragraph text if it's not already in the list
                if p_text and p_text not in general_info:
                    general_info.append(p_text)

            general_info_text = ' '.join(general_info)
            arr[heading_text].append(general_info_text)

        elif heading_text != "General Information":
            ul = h2.find_next('ul')
            if ul:
                for li in ul.find_all('li'):
                    item_text = li.get_text(strip=True)
                    arr[heading_text].append(item_text)

    # Now, scrape the table for hours
    find_table = soup.find('table')
    if find_table:
        rows = find_table.find_all('tr')
        for row in rows:
            columns = row.find_all('td')
            if len(columns) >= 2:
                title = columns[0].get_text(strip=True)
                hours = columns[1].get_text(strip=True)
                hours_list[title] = hours

    return arr, hours_list

# Scrape data for each gym facility and update the facilities_data dictionary
for gym_name in gyms:
    facility_url = facilities_data[gym_name]['link']
    full_url = urljoin(url, facility_url)
    general_info, hours_list = scrape_full_link(full_url)

    # Update the facilities_data dictionary with the detailed data
    facilities_data[gym_name]['General Info'] = general_info.get('General Information', [])
    facilities_data[gym_name]['Activities'] = general_info.get('Activities at this Facility', [])
    facilities_data[gym_name]['Features'] = general_info.get('Features', [])
    facilities_data[gym_name]['Today \'s Hours'] = hours_list.get(gym_name, 'No specific hours listed')

# Print the updated facilities data as JSON
print(json.dumps(facilities_data, indent=4))

# Save the data to a JSON file
with open('facilities_data.json', 'w') as f:
    json.dump(facilities_data, f, indent=4)  # Save the data to a JSON file with indentation for readability
