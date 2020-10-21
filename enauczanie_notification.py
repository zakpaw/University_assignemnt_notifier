from bs4 import BeautifulSoup as bs
import requests
import time
import os

login_url = 'https://logowanie.pg.edu.pl/login?service=https%3A%2F%2Fenauczanie.pg.edu.pl%2Fmoodle%2Flogin%2Findex.php%3FauthCAS%3DCAS'

subjects = {'english':'https://enauczanie.pg.edu.pl/moodle/course/view.php?id=7484',
            'statistics':'https://enauczanie.pg.edu.pl/moodle/course/view.php?id=7774',
            'accounting':'https://enauczanie.pg.edu.pl/moodle/course/view.php?id=6870',
            'data_bases':'https://enauczanie.pg.edu.pl/moodle/course/view.php?id=1745',
            'software_engineering':'https://enauczanie.pg.edu.pl/moodle/course/view.php?id=2405',
            'k_mngmnt':'https://enauczanie.pg.edu.pl/moodle/course/view.php?id=1920',
            'marketing':'https://enauczanie.pg.edu.pl/moodle/course/view.php?id=6672',
            'programming_languages':'https://enauczanie.pg.edu.pl/moodle/course/view.php?id=7221',
            'technical_physics':'https://enauczanie.pg.edu.pl/moodle/course/view.php?id=1680',
            'IT_tools':'https://enauczanie.pg.edu.pl/moodle/course/view.php?id=1716',}

login_data = {
    'username':'',
    'password':'',
    '_eventId':'submit',
    'geolocation':'',
    'submit':'Login',
}

accept_after_login = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'pl,en-US;q=0.7,en;q=0.3',
    'Connection':'keep-alive',
    'Content-Length':'6942',
    'Content-Type':'application/x-www-form-urlencoded',
    'Cookie':'_ga=GA1.3.1688160081.1603209769; _gid=GA1.3.55663446.1603209769; TGC=eyJhbGciOiJIUzUxMiJ9.ZXlKNmFYQWlPaUpFUlVZaUxDSmhiR2NpT2lKa2FYSWlMQ0psYm1NaU9pSkJNVEk0UTBKRExVaFRNalUySW4wLi5MTXBWZGNMSm1nZUlxclcyNmEzXzh3LklUNndzYzdwcHFrR0RzZFVkUVByME5CRlM0aDI0WkhDb3lOUVdJWTQwVWFvZlNQdlhNQnFIVHhTallTazBET2FaOFR5SjdPSTVYUEJ0dmJQaW9FTW1ZWmlfREpKb1JweUFBSTFneGRDUzRja0djdVNtM045M2N6LXRRSUtLYk9ENGtXQlZfVlhQTXZKNFZUajMwd0FPVllERFAwYVp2eXNOVWZpNmZXYjRLVFFfM0JXazBBd0N5UUUyaE50R2U4U0t3cXlXdEliSDBvOHVkdWtjWjU4QXM2aGV2QmU1YVpoMVN5dkRTdkRGY3cuREJBdTBFdFNhWjhCOGxUWHYtR3I5QQ==.Ck9RjylOUcuj_NDRw5j-OjbDUJqdEeaDMePjTPigqLNl8XE8syWIYGrbC_gPvHlC0xIKsgrj9vX1wpCfm_UuVg',
    'Host':'logowanie.pg.edu.pl',
    'Origin':'https://logowanie.pg.edu.pl',
    'Referer':'https://logowanie.pg.edu.pl/login?service=https%3A%2F%2Fenauczanie.pg.edu.pl%2Fmoodle%2Flogin%2Findex.php%3FauthCAS%3DCAS',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
 }


def change_in_course(new_links, path):
    f = open(path, 'r')
    return not f.read() == new_links


def scrape_all_links(session, urls):
    change = False
    message = ''
    for subject in urls:
        r = session.get(urls[subject])
        soup = bs(r.content, 'html.parser')
        
        strlinks = str()
        content = soup.find('ul', attrs={'class':'topics'})
        for el in content.findAll('li', attrs={'role':'region'}):
            for link in el.findAll('a'):
                l = link.get('href')
                if isinstance(l, str):
                    if l[0] != '#':
                        strlinks += str(l)+'\n'
        
        script_dir = os.path.dirname(__file__)
        file_path = f'data/{subject}.txt'
        path = os.path.join(script_dir, file_path)
        try:
            if change_in_course(strlinks, path):
                open(path, 'w').close()  # clear content of the file
                f = open(path, 'a')
                f.write(strlinks)
                f.close()
                message += f'CHANGE in {subject}!\n'
                change = True
        except FileNotFoundError:
                print(f'Created {str(file_path)}')
                f = open(path, 'a')
                f.write(strlinks)
                f.close() 
    if not change:
        message = 'No new assignments :)'
    return message


if __name__ == '__main__':
    login_data['username'] = input('Dawaj username:')
    login_data['password'] = input('teraz password:')
    logged_in = False
    with requests.session() as s:
        try:
            r = s.get(login_url)
        except ConnectionError:
            print('Check your internet connection!')
        try:
            if not logged_in:
                soup = bs(r.content, 'html.parser')
                login_data['execution'] = soup.find('input', attrs={'name':'execution'})['value']
                r = s.post(login_url, data=login_data)
                s.post(r.url, data=accept_after_login)
                logged_in = True
        except AttributeError:
            print('Wrong username or password')
        # scrape course sites
        notification = scrape_all_links(s, subjects)
        print(notification)
