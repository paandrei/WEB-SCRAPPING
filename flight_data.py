from urllib.request import urlopen, Request
import re 
from bs4 import BeautifulSoup
import csv

id_aircraft_list = ["N553AS","N661JA", "N820AE", "N27200", "N442SW", "N873AS", "N184JB", 
                    "N842AE", "N148SY", "N679NK", "N557AS", "N614AS", "N926EV", "N695CA"]

def get_aircraft_info(tail_number):

    url1 = "https://www.flightera.net/en/planes/"
    url = url1+tail_number
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html_bytes = urlopen(req).read()
    html = html_bytes.decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    #for finding seat numbers 
    dd = soup.find_all("dd")
    #for finding manufacture and model
    div = soup.find_all('div')

    text = ''
    text2 = ''

    for i in dd: 
        text += i.get_text()

    for elem in div:
        elem = elem.get_text()
        elem.replace('/n', '')
        text2 +=elem

    text2 = "".join([s for s in text2.strip().splitlines(True) if s.strip("\r\n").strip()])
    text2 = text2.replace(' ', '')
    text2 = text2.replace('\n', '') #text with manufacture and model

#find total number of seats 
    reg_ex_manufacture_and_model = '(?<=MANUFACTURER).*?(?=(ENGINES))'
    reg_ex_first = '([0-9]{0,2})+([ ])([F][i][r][s][t])'
    reg_ex_seats = "([0-9]{0,2})+([ ])([s][e][a][t][s])"  
    reg_ex_Business = '([0-9]{0,2})+([ ])([B][u][s][i][n][e][s][s])' 
    reg_ex_Eco_plus = '([0-9]{0,2})+([ ])([E][c][o][+])'
    reg_ex_Economy = '([0-9]{0,2})+([ ])([E][c][o][n][o][m][y])'

    manufacture_and_model = re.search(reg_ex_manufacture_and_model,text2)
    
    num_total_seats = re.search(reg_ex_seats,text)
    num_business_seats = re.search(reg_ex_Business,text)
    num_first_seats = re.search(reg_ex_first,text)
    num_eco_plus_seats = re.search(reg_ex_Eco_plus, text)
    num_economy_seats = re.search(reg_ex_Economy,text)
    
    manufacture, model, model_abbreviation = manufacture_model_verification(manufacture_and_model.group())

    total_seats = num_seats_verification(num_total_seats, 'seats')
    first_seats = num_seats_verification(num_first_seats, "First")
    business_seats = num_seats_verification(num_business_seats, "Business")
    eco_plus_seats = num_seats_verification(num_eco_plus_seats, 'Eco+')
    economy_seats = num_seats_verification(num_economy_seats, "Economy")
    
    return [total_seats, first_seats, business_seats, eco_plus_seats, economy_seats, manufacture, model, model_abbreviation]

def num_seats_verification(num_seats, seat_class):
    if num_seats == None:
        no_seats = ''
    else: 
        num_seats = num_seats.group()
        no_seats = int(num_seats.replace(f' {seat_class}',''))
    
    return no_seats

def manufacture_model_verification(text):
    text = text.replace('MODEL',' ')
    text = text.replace('(',' ')
    text = text.replace(')',' ')
    manufacture_model_list = text.split(' ')
    manufacture = manufacture_model_list[0]
    model = manufacture_model_list[1]
    model_abbreviation = manufacture_model_list[2]
    return manufacture, model, model_abbreviation

def create_file():
    header = ["tail_num", "op_unique", "total_seats", "first", "business", "premium_economy",
              "economy", "manufacture", "model_regular", "model_short"]
    with open ("flight_details.csv", "a+") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
def write_flight_details(tail_num, op_unique, aircraft_details):

    data = [tail_num, op_unique]
    for elem in aircraft_details:
        data.append(elem)
    with open ("flight_details.csv", "a+") as f:
        writer = csv.writer(f)
        writer.writerow(data)

create_file()
for elem in id_aircraft_list:
    aircraft_details = get_aircraft_info(elem)
    write_flight_details(elem, '', aircraft_details)