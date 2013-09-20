import csv
import urllib
import cookielib
import urllib2
from lxml import etree

class Divvy(object):
    def __init__(self):
        self.cookie_jar = cookielib.LWPCookieJar()

    def _post_with_cookie_jar(self, url, params):
        cookie = urllib2.HTTPCookieProcessor(self.cookie_jar)
        opener = urllib2.build_opener(cookie)
        req = urllib2.Request(url, urllib.urlencode(params))
        res = opener.open(req)
        return res

    def _get_with_cookie_jar(self, url):
        cookie = urllib2.HTTPCookieProcessor(self.cookie_jar)
        opener = urllib2.build_opener(cookie)
        req = urllib2.Request(url)
        res = opener.open(req)
        return res

    def login(self, username, password):
        post_data = dict(
            subscriberUsername=username,
            subscriberPassword=password
        )
        html_fl = self._post_with_cookie_jar('https://divvybikes.com/login', post_data)

        parser = etree.HTMLParser()
        tree = etree.parse(html_fl, parser)

        error_box = tree.xpath('//*[@id="content"]/div/div[1]/div')
        if error_box:
            raise Exception(error_box[0].text.strip())

    def get_rides(self):
        html_fl = self._get_with_cookie_jar('https://divvybikes.com/account/trips')

        parser = etree.HTMLParser()
        tree = etree.parse(html_fl, parser)

        table_rows = tree.xpath('//*[@id="content"]/div/table/tbody/tr')
        if table_rows and len(table_rows) == 1 and table_rows[0].xpath('td[@colspan="7"]') and table_rows[0].xpath('td[@colspan="7"]')[0].text.find("any bikes yet"):
            res = []
        else:
            res = []
            for row in table_rows:
                tds = row.xpath('td')

                duration_parts = tds[5].text.split(' ')
                if len(duration_parts) == 1:
                    seconds = int(duration_parts[0][:-1])
                elif len(duration_parts) == 2:
                    seconds = int(duration_parts[0][:-1])*60 + int(duration_parts[1][:-1])

                res.append({
                    "trip_id": tds[0].text,
                    "start_station": tds[1].text,
                    "start_date": tds[2].text,
                    "end_station": tds[3].text,
                    "end_date": tds[4].text,
                    "duration": seconds
                })
        return res

if __name__ == "__main__":
    d = Divvy()
    d.login('iandees', 'password')

    out = csv.DictWriter(open('divvy_rides.csv', 'w'), ['trip_id', 'start_station', 'start_date', 'end_station', 'end_date', 'duration'])

    out.writeheader()
    for ride in d.get_rides():
        out.writerow(ride)
