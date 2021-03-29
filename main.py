import re
import json
import PySimpleGUI as GUI
import requests

from time import sleep
from ebooklib import epub
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

# Set the theme for the window
GUI.theme('DarkAmber')

# The layout of the login tab
login_layout = [
    [GUI.Checkbox(text='Headless?', default=True, enable_events=True, key='-HEADLESS-')],
    [GUI.Text(text='Email:')],
    [GUI.Input(default_text='your@email.com', enable_events=True, key='-EMAIL-', justification='center', size=(48,1))],
    [GUI.Text(text='Password:')],
    [GUI.Input(default_text='password', password_char='*', enable_events=True, key='-PASSWORD-', justification='center', size=(48,1))]
]

csrf_layout = [
    [GUI.Text(text='CSRF Token:')],
    [GUI.Input(default_text='', enable_events=True, key='-CSRF TOKEN-', justification='center', size=(48,1))]
]

# The layout of the whole window
layout = [
    [GUI.Text(text='Waiting...', key='-PROGRESS STRING-', justification='center', size=(50,1))],
    [GUI.Text(text='Novel link:')],
    [GUI.Input(default_text="", enable_events=True, key='-NOVEL LINK-', size=(50,1))],
    [GUI.Text(text='EPUB name:')],
    [GUI.Input(default_text="", enable_events=True, key='-EPUB NAME-', size=(50,1))],
    [GUI.Checkbox(text='Hide titles?', default=False, enable_events=True, key='-HIDE TITLES-')],
    [GUI.TabGroup([[GUI.Tab(title="Login", layout=login_layout, border_width=1)], [GUI.Tab(title="CSRF", layout=csrf_layout, border_width=1)]])],
    [GUI.Button(button_text='Get EPUB | Login', enable_events=True, key='-GET EPUB LOGIN-'), GUI.Button(button_text='Get EPUB | CSRF', enable_events=True, key='-GET EPUB CSRF-')]
]

# Initialize the window
window = GUI.Window(title='Webnovel Scrapper', layout=layout, margins=(50,30))

def get_cookies(csrfToken: str): 
    return {
        '_csrfToken': csrfToken,
        '_ga': 'GA1.2.952415655.1610957805',
        'uts_id': 'uts1610957805.896',
        '_fbp': 'fb.1.1610957807974.779048379',
        'e1': '%7B%22pid%22%3A%22qi_p_library%22%2C%22eid%22%3A%22qi_B03%22%2C%22l1%22%3A%223%22%7D',
        'e2': '%7B%22pid%22%3A%22qi_p_library%22%7D',
        'show_lib_tip': '1',
        'para-comment-tip-show': '1',
        'tc': '_color3',
        'bookCitysex': '1',
        '__zlcmid': '12wjr6pw5G6JsEf',
        'dontneedgoogleonetap': '1',
        'ukey': 'uKCnfWmJIdX',
        'uid': '822773383',
        'alk': 'ta90cdb808aa5142e89c5bf28bc0b7088d%7C822773383',
        'googtrans-open': '0',
        'webnovel_uuid': '1614893333_1313839538',
        'webnovel-language': 'en',
        'webnovel-content-language': 'en',
        'alkts': '1618160502',
        'checkInTip': '1',
    }

def get_params_chapter(csrfToken: str, bookId: str, chapterId: str):
    return (
        ('_csrfToken', csrfToken),
        ('bookId', bookId),
        ('chapterId', chapterId),
    )

def get_params_book(csrfToken: str, bookId: str):
    return (
        ('_csrfToken', csrfToken),
        ('bookId', bookId)
    )

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    'TE': 'Trailers',
}

# Necessary so that it listens to all events inside the window
while True:
    event, values = window.read()
    logged = False

    def get_id(link):
        split = link.split('/')[-1]
        split = split.split('_')[-1]
        return split
    # end def

    def update(text):
        window['-PROGRESS STRING-'].update(text)

    if event in (None, 'Cancel'):
        break

    if event == '-GET EPUB LOGIN-':
        # Get the neccessary values from the inputs
        email = values['-EMAIL-']
        password = values['-PASSWORD-']

        # Set selenium to be headless
        options = Options()
        options.headless = bool(values['-HEADLESS-'])

        # Initialize the browser
        driver = webdriver.Firefox(options=options, executable_path='./geckodriver.exe')

        # Go to webnovel.com to login
        driver.get('https://webnovel.com')

        if not logged:
            update('Logging in...')

            # Close the popup that shows when you access the page for the first time
            random_popup = driver.find_element_by_xpath('/html/body/div[31]/div/a')
            random_popup.click()

            sleep(1)

            # Click the Sign In button
            login_form_button = driver.find_element_by_xpath('/html/body/header/div/div/div/a')
            login_form_button.click()

            # Wait for the iframe to appear and fully load
            sleep(3)

            # Switch to the iframe
            driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))

            # Find the email login button and click it
            email_login_button = driver.find_element_by_xpath("/html/body/div/div/div/div[2]/div[2]/div[2]/div[2]/a[2]")
            email_login_button.click()

            # Find and input the account's email address
            email_input = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/form/div/p[1]/input')
            email_input.send_keys(email)

            # Find and input the account's password
            password_input = driver.find_element_by_xpath('/html/body/div/div/div/div[2]/form/div/p[2]/input')
            password_input.send_keys(password)

            # Click the login button
            login_button = driver.find_element_by_xpath('//*[@id="submit"]')

            # Wait for the page to realize you have inputted the account's informat
            sleep(2)

            # Click the login button
            login_button.click()

            # Switch to the root page
            driver.switch_to.default_content()

            # Wait to be redirected to the main page
            sleep(2)

            # Set the the user is logged in
            logged = True

        # Get the CSRF Token from the cookies of the page
        csrf_token = driver.get_cookies()[0]['value']

        driver.close()

        get_book(csrf_token)

    if event == '-GET EPUB CSRF-':
        # Get the neccessary values from the inputs
        csrf_token = values['-CSRF TOKEN-']

        get_book(csrf_token)

    def get_book(csrf: str):
        # Get the neccessary values from the inputs
        novel_link = values['-NOVEL LINK-']
        epub_name = values['-EPUB NAME-']
        hide_title = bool(values['-HIDE TITLES-'])

        # Links for getting the list of chapters and the chapter body
        chapter_list_link = f'https://www.webnovel.com/apiajax/chapter/GetChapterList'
        chapter_body_url = f'https://www.webnovel.com/go/pcm/chapter/getContent'

        # ID of the novel extracted from the inputted URL
        novel_link_id = get_id(novel_link)

        # Function to get the name of the book
        def get_book_name(novel_id):
            params = get_params_book(csrf, str(novel_id))
            cookies = get_cookies(csrf)
            res = requests.get(chapter_list_link, headers=headers, params=params, cookies=cookies)
            content = res.json()
            return content['data']['bookInfo']['bookName']
        # end def

        # Function to get the IDs of all the chapters of the novel
        def get_chapters_list(novel_id):
            params = get_params_book(csrf, str(novel_id))
            cookies = get_cookies(csrf)
            res = requests.get(chapter_list_link, headers=headers, params=params, cookies=cookies)
            content = res.json()
            content = content['data']['volumeItems']
            chapter_ids = []
            for volume in content:
                for chapter in volume['chapterItems']:
                    chapter_ids.append(str(chapter['id']))
                # end for
            # end for
            return chapter_ids
        # end def

        # Function to get the data of the chapter
        def get_chapter_body(novel_id, chapter_id):
            params = get_params_chapter(csrf, str(novel_id), str(chapter_id))
            cookies = get_cookies(csrf)
            res = requests.get(chapter_body_url, headers=headers, params=params, cookies=cookies)
            content = res.json()

            # Condition to check if the GET request was not successful to re-try
            if content['msg'] != 'Success':
                return get_chapter_body(novel_id, chapter_id)
            #end if
            return content['data']
        # end def

        # Function to format the content of the chapter
        # It deletes text inserted by Webnovel and puts each paragraph inside a <p></p>
        def format_text(text):
            text = re.sub(r'Find authorized novels in Webnovel(.*)for visiting\.', '', text, re.MULTILINE)
            text = re.sub(r'\<pirate\>(.*?)\<\/pirate\>', '', text, re.MULTILINE)
            if not (('<p>' in text) and ('</p>' in text)):
                text = re.sub(r'<', '&lt;', text)
                text = re.sub(r'>', '&gt;', text)
                text = [x.strip() for x in text.split('\n') if x.strip()]
                text = '<p>' + '</p><p>'.join(text) + '</p>'
            # end if
            return text.strip()
        # end def

        # Extracts the chapter's name, index and content from inside the provided chapter's body
        def get_chapter(novel_id, chapter_id):
            chapter_body = get_chapter_body(novel_id, chapter_id)
            chapter_name = chapter_body['chapterInfo']['chapterName'] if not hide_title else ''
            chapter_index = chapter_body['chapterInfo']['chapterIndex']
            chapter_title = f'Chapter {chapter_index}: {chapter_name}' if not hide_title else f'Chapter {chapter_index}'
            chapter_content = ''
            for cc in chapter_body['chapterInfo']['contents']:
                content = cc['content']
                content = format_text(content)
                chapter_content = chapter_content + '\n' + str(content)
            # end for
            return {
                'chapter_name': chapter_name,
                'chapter_index': chapter_index,
                'chapter_title': chapter_title,
                'chapter_content': chapter_content
            }
        # end def

        update('Creating EBOOK...')

        # Initialize the epub book
        book = epub.EpubBook()
        
        book_title = get_book_name(novel_link_id)

        # Set the title and language of the book
        book.set_title(book_title)
        book.set_language('en')

        update(f'Setting title... {book_title}')
        update(f'Setting language... english')

        # Initializing an empty doc to store the spine of the book
        spine = []

        # Function to add the chapter to the book
        def add_chapter(chapter_data):
            name = chapter_data['chapter_name']
            title = chapter_data['chapter_title']
            index = chapter_data['chapter_index']
            content = chapter_data['chapter_content']
            # If the content of the chapter is empty stop the function and return nothing
            if len(content) > 1:
                content = name + '\n' + content
                chapter = epub.EpubHtml(title=title,file_name=f'{index}.xhtml',content=content)
                book.add_item(chapter)
                spine.append(chapter)
                update(f'Adding... Chapter {index}')
            # end if
        # end def

        update('Getting chapter list...')
        chapter_list = get_chapters_list(novel_link_id)
        chapters_count = len(chapter_list)
        update(f'Found {chapters_count} chapters')

        # Iterate through the chapter list and add all the chapters inside it in the book
        for chapter_id in chapter_list:
            chapter = get_chapter(novel_link_id, chapter_id)
            # If the content of the chapter is not empty, set it as the last chapter number
            if len(chapter['chapter_content']) > 1:
                chapters_count = chapter['chapter_index']
                add_chapter(chapter)
            # end if
        # end def

        # Set the spine and the table of contents of the book
        book.spine = spine
        book.toc = tuple(spine)

        # Add the spine and the table of contents to the book
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        update('Packing EPUB file...')

        # Format the title of the epub so that it doesn't include any windows forbidden characters
        formatted_title = re.sub(r'([<>:"/\\|?*])+', '', book_title, re.MULTILINE)

        # If a name was inserted in the EPUB name input it will be used, otherwised a default name is used
        if len(epub_name) > 0:
            title = epub_name + '.epub'
        else:
            title = f'{formatted_title} 1-{chapters_count} - Hidden Titles.epub'

        # Create the EPUB file
        epub.write_epub(title, book)

        update('EPUB file created.')

    if event == GUI.WIN_CLOSED:
        if driver:
            driver.close()
        break

window.close()
