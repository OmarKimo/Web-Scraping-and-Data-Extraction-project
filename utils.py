from string import capwords

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
            if len(last.split()) > 1:
                l.append(' '.join(last.split()[1:]))
            else:
                l.append("")
            l.insert(-3, "")
            for i in range(5):
                if i != 3:
                    l[i] = capwords(l[i])
            return l
        elif num == 3:
            l = address.split(",")
            last = l[-1]
            l[-1] = last.split()[0]
            if len(last.split()) > 1:
                l.append(' '.join(last.split()[1:]))
            else:
                l.append("")
            for i in range(5):
                if i != 3:
                    l[i] = capwords(l[i])
            return l
        else:
            return [""]*5

    return [""]*5
