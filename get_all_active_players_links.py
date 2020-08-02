from basic_lebron_stats import *
import csv

alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
base_URL = "https://www.basketball-reference.com/players/"
current_year = '[2020]'
player_hrefs = []
#d = {'col1': '', 'col2': ''}
#df = pd.DataFrame(data=d)

def extract_player_links_from_url(url):
    html = urlopen(url)
    print('hi')
    soup = BeautifulSoup(html, 'html.parser')
    player_data = soup.find_all('tr')
    for i in range(len(player_data)):
        end_year = str(player_data[i].find_all('td', {'data-stat': 'year_max'}))
        clean = re.compile('<.*?>')
        end_year_string = (re.sub(clean, '',end_year))
        if (end_year_string == '[2020]'):
            ayy = str(player_data[i].find_all('a', href=True)[0])
            clean_href = re.compile('href=.*html')
            clean2 = (re.search(clean_href, ayy))
            str_href = clean2.group(0)[6:]
            player_hrefs.append(str_href)

def get_all_links():
    for letter in alphabet:
        extract_player_links_from_url(base_URL + letter)


    with open('links.csv', 'w') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writecol(player_hrefs)
   
"""     
def main():
    for letter in alphabet:
        extract_player_links_from_url(base_URL + letter)
    print(player_hrefs)

main()
"""