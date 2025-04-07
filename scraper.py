import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

url = "https://www.utrecsports.org/hours"
gyms = ["Recreational Sports Center", "Gregory Gym", "Bellmont Hall 406"]

def get_facility_name_and_link(cell):
    link = cell.find('a')
    if link:
        name = link.get_text(strip=True)
        facility_url = link['href']
        return name, facility_url
    return cell.get_text(strip=True), None

def get_hours_or_link(cell):
    link = cell.find('a')
    if link:
        return link['href']
    return cell.get_text(strip=True)

def clean_paragraph_text(p):
    text = p.get_text(strip=True)
    text = text.replace('\u00a0', ' ').replace('\u2019', "'")
    text = re.sub(r'(?<=[a-z.,])(?=[A-Z])', ' ', text)
    text = re.sub(r'(?<=[a-zA-Z])(?=\d)', ' ', text)
    text = re.sub(r'(?<=\d)(?=[a-zA-Z])', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def scrape_full_link(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching detailed page: {url}, {e}")
        return {}, {}

    arr = {}
    hours_list = {}

    find_h2 = soup.find_all('h2')
    for h2 in find_h2:
        heading_text = h2.get_text(strip=True)
        arr[heading_text] = []

        if heading_text == "General Information":
            general_info = []
            p_tags = h2.find_all_next('p', limit=5)
            for p in p_tags:
                p_text = clean_paragraph_text(p)
                links = p.find_all('a')
                for link in links:
                    link_text = link.get_text(strip=True)
                    link_url = link.get('href')
                    p_text = p_text.replace(link_text, f"{link_text}: {link_url} ")
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

def scrape_all_facilities():
    print("Scraping UT RecSports data...")
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print("Initial page scraping failed:", e)
        return {}

    table = soup.find('table', {'id': 'large-only'})
    rows = table.find_all('tr') if table else []

    facilities_data = {}

    for row in rows:
        cols = row.find_all('td')
        if len(cols) != 5:
            continue

        facility_name, facility_link = get_facility_name_and_link(cols[0])
        full_url = urljoin(url, facility_link) if facility_link else None

        if facility_name in gyms:
            mon_thu = get_hours_or_link(cols[1])
            friday = get_hours_or_link(cols[2])
            saturday = get_hours_or_link(cols[3])
            sunday = get_hours_or_link(cols[4])

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

    for gym_name in gyms:
        if gym_name not in facilities_data:
            continue
        facility_url = facilities_data[gym_name]['link']
        full_url = urljoin(url, facility_url)
        general_info, hours_list = scrape_full_link(full_url)

        facilities_data[gym_name]['General Info'] = general_info.get('General Information', [])
        facilities_data[gym_name]['Activities'] = general_info.get('Activities at this Facility', [])
        facilities_data[gym_name]['Features'] = general_info.get('Features', [])
        facilities_data[gym_name]['Today \'s Hours'] = hours_list.get(gym_name, 'No specific hours listed')

    print("Scraping complete.")
    return facilities_data
