import pymysql
import requests
import urllib.request
import urllib.parse
import time
from datetime import date
from googletrans import Translator
translator=Translator()
today = date.today()
conn=pymysql.connect(host="localhost",user="root",passwd="",db="farmer_db")
f = open("alert.txt", "a")
#send sms
def sendSMS(apikey, numbers, sender, message):
    url = "https://www.fast2sms.com/dev/bulk"
    f = open("alert1.txt", "r", encoding="utf-8")
    tr = f.read()
    querystring = {"authorization": "NVtnDk43B7YsEp2iC1yAUI0u9mdRH8GegMlcvwjWfOLrQXPoTzsDRKbvyx0wAcgpk514P3u7hrUZWOHC",
                   "sender_id": "FSTSMS", "message": tr.encode(encoding="utf-8"), "language": "unicode", "route": "p",
                   "numbers": numbers}

    headers = {
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)

    return response.text
#Alert function
def alertfun(r):
    record_dict={}
    lang={}
    for j in r:
        pest = j[2]
        cropid=j[1]
        pestminTemp = j[3]
        pestmaxTemp = j[4]
        pestminHumidity = j[5]
        pestmaxHumidity = j[6]
        if (current_temperature >= pestminTemp and current_temperature <= pestmaxTemp) or (
                current_humidity >= pestminHumidity and current_humidity <= pestmaxHumidity):
            farmerquery="select farmer_name,mobile_no,language,fid,start_date,end_date from farmer_details where district=3 and crop='"+str(cropid)+"';"
            farmerCursor.execute(farmerquery)
            res=farmerCursor.fetchall()
            cropcurs.execute("select crop_name from crop_details where crop_id='"+str(cropid)+"';")
            cropname=cropcurs.fetchone()

            #print(res)
            for i in res:
                farmer_name = i[0]
                mobile_no = i[1]
                language = i[2]
                fid = i[3]
                start_date = i[4]
                end_date=i[5]

                if(start_date<=today<=end_date):
                    if not fid in record_dict.keys():
                        record_dict[fid] = []
                        record_dict[fid].append("Dear " + farmer_name + ",\n")
                        record_dict[fid].append("Mobile :"+mobile_no+"\n")
                        record_dict[fid].append("Because of the immediate change in weather, the following pests may occur to your crop \n" + cropname[0] + ":\n")
                        record_dict[fid].append("pest :"+pest + "\n")
                        record_dict[fid].append("Language :"+language)
                    else:
                        record_dict[i[3]].append(pest + "\n")

                elif(start_date>today):
                    continue
                elif(end_date>today):
                    deleteQ="delete from farmer_details where fid='"+str(fid)+"';"
                    farmerCursor.execute(deleteQ)
                    conn.commit()

    for record in record_dict:
        f = open("alert.txt", "w")
        #print(record_dict[record][1])
        for to_be_write in record_dict[record]:
            if not to_be_write.startswith("Mobile") and not to_be_write.startswith("Language"):
                f.write(to_be_write)
        f.write("for more information please contact to Kisan Call Centre"+"\n18001801551")


        f.close()
        fr = open("alert.txt", "r")
        fw = open("alert1.txt", "w", encoding="utf-8")
        newfile = fr.read()
        if (record_dict[record][4] == "Language :MARATHI"):
            transfile = translator.translate(newfile, 'mr').text
            fw.write(transfile)
        elif (record_dict[record][4] == "Language :HINDI"):
            transfile = translator.translate(newfile, 'hi').text
            fw.write(transfile)
        elif (record_dict[record][4] == "Language :KANNADA"):
            transfile = translator.translate(newfile, 'kn').text
            fw.write(transfile)
        elif (record_dict[record][4] == "Language :TELUGU"):
            transfile = translator.translate(newfile, 'te').text
            fw.write(transfile)
        else:
            fw.write(newfile)
        fw.close()
        fr.close()
        fw = open("alert1.txt", "r", encoding="utf-8")
        filenew = fw.read()
        #print(filenew)
        resp = sendSMS('apikey',record_dict[record][1].split(":")[1],
                       'Jims Autos', filenew)
        print(resp)
        fr.close()
        fw.close()
farmerCursor=conn.cursor()
pestCusr=conn.cursor()
pestQuery="select * from pest_details;"
pestCusr.execute(pestQuery)
r=pestCusr.fetchall()
cropcurs=conn.cursor()

#openweathermap api
url="http://dataservice.accuweather.com/currentconditions/v1/204849?apikey=e06qpBzgJHB2A8TAS961UlHjKgOA7bXA&details=true"
response=requests.get(url)
x=response.json()
current_temperature=x[0]["Temperature"]["Metric"]["Value"]
current_humidity=x[0]["RelativeHumidity"]
print(current_humidity)
print(current_temperature)
while(1):
    alertfun(r)
    #print("Hii")
    time.sleep(100000)
farmerCursor.close()
pestCusr.close()
cropcurs.close()
conn.close()






