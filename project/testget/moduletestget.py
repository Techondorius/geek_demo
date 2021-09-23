import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# import chromedriver_binary

from time import sleep
import datetime

import requests
from bs4 import BeautifulSoup
import re


class testget():
    def testinfoget(self, browser, tests, subjects, deadlines, blacklist_testw):
        browserer = browser.find_element_by_tag_name('section')
        one_test = browserer.find_elements_by_tag_name('li')
        for one_test in one_test:
            elems_ts = one_test.find_element_by_tag_name('h3')
            test = elems_ts.text
            for i in blacklist_testw:
                if i in test:
                    test = test.replace(i, '')
            tests.append(test)

            elems_tc = one_test.find_element_by_class_name('info1')
            subject = elems_tc.text
            subjects.append(subject)

            try:
                elems_td = one_test.find_element_by_class_name('info2')
                deadline = elems_td.text
                if deadline == "":
                    deadline = "0"
            except:
                deadline = "0"
            if '受付終了日時' in deadline:
                deadline = deadline.replace('受付終了日時：', '')

            deadlines.append(deadline)

    def timecalculation(self, timer):
        totl = timer.seconds + timer.days * 86400 + timer.microseconds / 1000000
        day, other = divmod(totl, 86400)
        hour, other = divmod(other, 3600)
        minute, secs = divmod(other, 60)
        secs = round(secs, 2)
        return str('%ddays %d:%d:%f' % (day, hour, minute, secs))

    def __init__(self):
        self.subjects = []
        self.tests = []
        self.deadlines = []
        self.blacklist_testw = ['自動採点 ', 'ドリル ', '個別指導']
        self.blacklist_subj = ['資格試験英語Ａ',
                               '学生サポートセンター(数,物,化,英)', 'ソーシャルアクティブラーニング2021']

    def testinfo():
        pass

    def testreturn(self):
        time_now = datetime.datetime.now()
        time = datetime.datetime.now()
        option = Options()
        option.add_argument('--headless')
        browser = webdriver.Chrome(options=option)

        url = 'https://cit.manaba.jp/ct/home_course'
        browser.get(url)

        try:
            elem_username = browser.find_element_by_id('mainuserid')
            elem_username.send_keys('F20A4141')

            elem_password = browser.find_element_by_name('password')
            elem_password.send_keys('tred86vm')

            elem_login_button = browser.find_element_by_id('login')
            elem_login_button.click()
        except:
            pass

        url = 'https://cit.manaba.jp/s/home_summary_query'
        browser.get(url)

        self.testinfoget(browser, self.tests, self.subjects,
                         self.deadlines, self.blacklist_testw)

        url = 'https://cit.manaba.jp/s/home_summary_survey'
        browser.get(url)

        self.testinfoget(browser, self.tests, self.subjects,
                         self.deadlines, self.blacklist_testw)

        url = 'https://cit.manaba.jp/s/home_summary_report'
        browser.get(url)

        self.testinfoget(browser, self.tests, self.subjects,
                         self.deadlines, self.blacklist_testw)
        count = 0
        for i in self.deadlines:
            if i != "0":
                dt = datetime.datetime.strptime(i, "%Y-%m-%d %H:%M")
                self.deadlines[count] = dt - time_now
            count += 1

        calc = 0
        for i in self.deadlines:
            if i != "0":
                self.deadlines[calc] = self.timecalculation(i)
            calc += 1

        import pandas as pd

        df = pd.DataFrame()

        df['課題名'] = self.tests
        df['科目'] = self.subjects
        df['締切'] = self.deadlines

        for blacklist_subj in self.blacklist_subj:
            df = df[df['科目'] != blacklist_subj]

        browser.close()

        response = ""
        for test, subject, deadline in zip(self.tests, self.subjects, self.deadlines):
            response += "{}\n{}\n{}\n".format(test, subject, deadline)

        return str(response)


class utatenres:
    def __init__(self, url):
        self.url = url

    def lyric(self):

        res = requests.get(self.url)

        processed_data = BeautifulSoup(res.text, 'html.parser')

        lyric_text = processed_data.find('div', {'class' : 'hiragana'})

        lyric_text = str(lyric_text)

        lyric_text = lyric_text.replace('<br>','')
        lyric_text = lyric_text.replace('<br/>','')
        lyric_text = lyric_text.replace('</br>', '\n')

        rt_conpile = re.compile(r'<span class="rt">[\u3041-\u309F\u30A1-\u30FF\uFF66-\uFF9F]+</span>')
        lyric_text = rt_conpile.sub('', lyric_text)
        startdiv_conpile = re.compile('<div class="hiragana">\n')
        lyric_text = startdiv_conpile.sub('', lyric_text)
        enddiv_conpile = re.compile('\n+</div>')
        lyric_text = enddiv_conpile.sub('', lyric_text)
        spacebarrage_compile = re.compile(' + ')
        lyric_text = spacebarrage_compile.sub('', lyric_text)

        lyric_text = lyric_text.replace('<span class="ruby"><span class="rb">', '').replace('</span>', '')
        return str(lyric_text)