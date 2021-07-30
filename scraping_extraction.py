import os
import csv
from bs4 import BeautifulSoup
import requests

url = "https://registers.maryland.gov/RowNetWeb/Estates/frmEstateSearch2.aspx"

browser_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": 'gzip, deflate, br',
    "Accept-Language": 'en,ar;q=0.9,en-US;q=0.8',
    "Cache-Control": 'max-age=0',
    "Connection": 'keep-alive',
    "Cookie": "ASP.NET_SessionId=ceb666ad-216f-4530-9952-fdec22f4e147",
    "Content-Type": 'application/x-www-form-urlencoded',
    'Host': 'registers.maryland.gov',
    "Origin": "https://registers.maryland.gov",
    "Referer": "https://registers.maryland.gov/RowNetWeb/Estates/frmEstateSearch2.aspx",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
}

request_data = {
    "__VIEWSTATE": "",
    "__VIEWSTATEGENERATOR": "11C1F95B",
    "__EVENTVALIDATION": "",
    "txtEstateNo": "",
    "txtLN": "",
    "cboCountyId": "6",
    "txtFN": "",
    "txtMN": "",
    "cboStatus": "",
    "cboType": "",
    "DateOfFilingFrom": "07/23/2021",
    "DateOfFilingTo": "07/27/2021",
    "txtDOF": "",
    "cboPartyType": "Decedent",
    "cmdSearch": "Search"
}

target = {
    "__EVENTTARGET": "",
    "__EVENTARGUMENT": "",
    "__VIEWSTATE": "",
    "__VIEWSTATEGENERATOR": "11C1F95B",
    "__EVENTVALIDATION": ""
}


def split_name(name):
    name = name.replace(",", " ")
    num = len(name.split())
    if num:
        if num == 1:
            return [name.strip(), "", ""]
        elif num == 2:
            l = name.split()
            l.insert(1, "")
            return l
        elif num == 3:
            l = name.split()
            if len(l[-1].strip()) < 3:
                l[-1] = l[-2] + " " + l[-1]
                l[-2] = ""
            return l
        else:
            l = name.split()
            l[2] = ' '.join(l[2:])
            l = l[:3]
            return l

    return [""]*3


def split_address(address):
    num = address.count(",")
    if num:
        if num == 2:
            l = address.split(",")
            last = l[-1]
            l[-1] = last.split()[0]
            l.append(last.split()[1])
            l.insert(-3, "")
            return l
        elif num == 3:
            l = address.split(",")
            last = l[-1]
            l[-1] = last.split()[0]
            l.append(last.split()[1])
            return l
        else:
            return [""]*5

    return [""]*5


def request(checkedItems, in_date_range_from, in_date_range_to, optionsDict, window):
    window.setEnabled(False)
    data = []
    list_header = ["County", "Estate Number", "Filing Date", "Date of Death", "Type", "Status", "Name", "Decedent Name", "Will", "Date of Will", "Personal Reps First", "Personal Reps Middle", "Personal Reps Last", "Personal Reps Address", "PR Address 2", "PR City", "PR State", "PR Zip Code", "Date Opened", "Date Closed", "Attorney First", "Attorney Middle", "Attorney Last", "Attorney Address", "Attorney Address 2", "Attorney City", "Attorney State", "Attorney Zip Code"
                   ]
    idx = 0
    sess = requests.session()
    with open('result.csv', newline='', mode="a") as f:
        csv_writer = csv.writer(f)
        needs_header = os.stat('result.csv').st_size == 0
        if needs_header:
            csv_writer.writerow(list_header)

        for item in checkedItems:
            in_county = item.text()
            # logger.error(in_county)
            
            res = sess.get(url, headers=browser_headers)
            soup = BeautifulSoup(res.content, 'html.parser')

            for key in ["__VIEWSTATEGENERATOR", "__VIEWSTATE", "__EVENTVALIDATION"]:
                request_data[key] = soup.find(
                    name="input", attrs={"id": key})["value"]
            request_data['cboCountyId'] = optionsDict[in_county]
            request_data["DateOfFilingFrom"] = in_date_range_from
            request_data["DateOfFilingTo"] = in_date_range_to

            res = sess.post(url, headers=browser_headers, data=request_data)
            soup = BeautifulSoup(res.content, 'html.parser')

            links = []
            table = soup.find(name="table", attrs={"id": "dgSearchResults"})
            if not table:
                # logger.error(
                #     f"Search Criteria Returned No Results. [{in_county} from {in_date_range_from} to {in_date_range_to}]")
                continue
            # logger.error(f"Counting records for {in_county} from {in_date_range_from} to {in_date_range_to}....")
            HTML_data = table.findAll(name="tr")
            cnt = 0
            for element in HTML_data[1:-1]:
                try:
                    cols = element.findAll("td")
                    cnt += 1
                    col_data = []
                    for col in cols:
                        col_data.append(col.text)
                        try:
                            links.append(
                                f"https://registers.maryland.gov/RowNetWeb/Estates/{col.find('a')['href']}")
                            col_data[-1] = col_data[-1].lstrip("0")
                        except:
                            continue
                    data.append(col_data)
                except:
                    continue

            rest = HTML_data[-1]
            current_page = 1

            while True:
                # logger.error(f"Page {current_page} with total {cnt} records.")
                try:
                    current_page += 1
                    next_link = rest.find(
                        name="a", href=True, text=str(current_page))["href"]
                    for key in target.keys():
                        if key == "__EVENTTARGET":
                            target[key] = next_link[next_link.find(
                                "'")+1:next_link.find(',')-1]
                        else:
                            target[key] = soup.find(
                                name="input", attrs={"id": key})["value"]
                    res = sess.post(url, headers=browser_headers, data=target)

                except:
                    try:
                        next_link = rest.findAll(
                            name="a", href=True, text="...")[-1]
                        if next_link.find_next(name="a", href=True):
                            break
                        next_link = next_link["href"]
                        for key in target.keys():
                            if key == "__EVENTTARGET":
                                target[key] = next_link[next_link.find(
                                    "'")+1:next_link.find(',')-1]
                            else:
                                target[key] = soup.find(
                                    name="input", attrs={"id": key})["value"]
                        res = sess.post(
                            url, headers=browser_headers, data=target)

                    except:
                        break

                soup = BeautifulSoup(res.content, 'html.parser')
                table = soup.find(name="table", attrs={
                                  "id": "dgSearchResults"})

                HTML_data = table.findAll("tr")

                for element in HTML_data[1:-1]:
                    try:
                        cols = element.findAll("td")
                        cnt += 1
                        col_data = []
                        for col in cols:
                            col_data.append(col.text)
                            try:
                                links.append(
                                    f"https://registers.maryland.gov/RowNetWeb/Estates/{col.find('a')['href']}")
                                col_data[-1] = col_data[-1].lstrip("0")
                            except:
                                continue
                        data.append(col_data)
                    except:
                        continue

                rest = HTML_data[-1]

            # logger.error(f"There are total of {cnt} records for {in_county} from {in_date_range_from} to {in_date_range_to}.")
            
            window.progress.setMaximum(cnt)
            for index, link in enumerate(links):
                window.progress.setValue(index+1)
                # logger.error(f"Extracting record #{index+1} with link: {link}")

                response = sess.get(link, headers=browser_headers)
                try:
                    response.raise_for_status()
                except:
                    res = response.text
                    first = res.find("ResetId=")+len("ResetId=")
                    new_id = res[first:res.find('"', first)]
                    browser_headers["Cookie"] = f"ASP.NET_SessionId={new_id}"
                    response = sess.get(link, headers=browser_headers)

                soup = BeautifulSoup(response.content, 'html.parser')
                data[idx].append(
                    soup.find(name="span", attrs={"id": "lblName"}).text)
                data[idx].append(
                    soup.find(name="span", attrs={"id": "lblWill"}).text)
                data[idx].append(soup.find(name="span", attrs={
                    "id": "lblDateOfWill"}).text)
                personal_reps = soup.find(
                    name="span", attrs={"id": "lblPersonalReps"}).text
                personal_reps_name = personal_reps[:personal_reps.find("[")]
                personal_reps_rest = personal_reps[personal_reps.find(
                    "[")+1:personal_reps.find("]")]
                ret = split_name(personal_reps_name)
                for item in ret:
                    data[idx].append(item)

                ret = split_address(personal_reps_rest)
                for item in ret:
                    data[idx].append(item)

                data[idx].append(soup.find(name="span", attrs={
                    "id": "lblDateOpened"}).text)
                data[idx].append(soup.find(name="span", attrs={
                    "id": "lblDateClosed"}).text)
                attorney = soup.find(name="span", attrs={
                    "id": "lblAttorney"}).text
                attorney_name = attorney[:attorney.find("[")]
                attorney_rest = attorney[attorney.find(
                    "[")+1:attorney.find("]")]

                ret = split_name(attorney_name)
                for item in ret:
                    data[idx].append(item)

                ret = split_address(attorney_rest)
                for item in ret:
                    data[idx].append(item)
                csv_writer.writerow(data[idx])
                idx += 1
            # logger.error(
            #     f"Extracting {in_county} records from {in_date_range_from} to {in_date_range_to} is done.")
    # logger.error("Finished.")
    window.setEnabled(True)
