import re
import json
import PySimpleGUI as GUI

from time import sleep
from ebooklib import epub
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# The layout of the login tab
login_layout = [
    [GUI.Text(text='Email:')],
    [GUI.Input(default_text='your@email.com', enable_events=True, key='-EMAIL-', justification='center', size=(48,1))],
    [GUI.Text(text='Password:')],
    [GUI.Input(default_text='password', password_char='*', enable_events=True, key='-PASSWORD-', justification='center', size=(48,1))]
]

# The layout of the whole window
layout = [
    [GUI.Text(text='Waiting...', key='-PROGRESS STRING-', justification='center', size=(50,1))],
    [GUI.Text(text='Novel link:')],
    [GUI.Input(default_text="Ex: https://www.webnovel.com/book/11766562205519505", enable_events=True, key='-NOVEL LINK-', size=(50,1))],
    [GUI.Text(text='EPUB name:')],
    [GUI.Text(text='Leave empty for the default name')],
    [GUI.Input(default_text="", enable_events=True, key='-EPUB NAME-', size=(50,1))],
    [GUI.Checkbox(text='Headless?', default=True, enable_events=True, key='-HEADLESS-')],
    [GUI.TabGroup([[GUI.Tab(title="Login", layout=login_layout, border_width=1)]])],
    [GUI.Button(button_text='Get EPUB', enable_events=True, key='-GET EPUB-')]
]

# Initialize the window
window = GUI.Window(title='Webnovel Scrapper', layout=layout, margins=(50,30))

# Neccessary so that it listens to all events inside the window
while True:
    event, values = window.read()

    def get_id(link):
        split = link.split('/')[-1]
        split = split.split('_')[-1]
        return split
    # end def

    def update(text):
        window['-PROGRESS STRING-'].update(text)
    
    if event == '-GET EPUB-':
        # Get the neccessary values from the inputs
        novel_link = values['-NOVEL LINK-']
        email = values['-EMAIL-']
        password = values['-PASSWORD-']
        epub_name = values['-EPUB NAME-']

        # Set selenium to be headless
        options = Options()
        options.headless = bool(values['-HEADLESS-'])

        # Initialize the browser
        driver = webdriver.Firefox(options=options)

        # Go to webnovel.com to login
        driver.get('https://webnovel.com')

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

        # Get the CSRF Token from the cookies of the page
        csrf_token = driver.get_cookies()[0]['value']

        # Links for getting the list of chapters and the chapter body
        chapter_list_link = f'https://www.webnovel.com/apiajax/chapter/GetChapterList?_csrfToken={csrf_token}&bookId=%s'
        chapter_body_url = f'https://www.webnovel.com/go/pcm/chapter/getContent?_csrfToken={csrf_token}&bookId=%s&chapterId=%s'

        # ID of the novel extracted from the inputted URL
        novel_link_id = get_id(novel_link)

        # Function to get the name of the book
        def get_book_name(novel_id):
            driver.get('view-source:' + chapter_list_link % novel_id)
            content = driver.page_source
            content = driver.find_element_by_tag_name('pre').text
            parsed_content = json.loads(content)['data']['bookInfo']
            return parsed_content['bookName']
        # end def

        # Function to get the IDs of all the chapters of the novel
        def get_chapters_list(novel_id):
            driver.get('view-source:' + chapter_list_link % novel_id)
            content = driver.page_source
            content = driver.find_element_by_tag_name('pre').text
            parsed_content = json.loads(content)['data']['volumeItems']
            chapter_ids = []
            for volume in parsed_content:
                for chapter in volume['chapterItems']:
                    chapter_ids.append(str(chapter['id']))
                # end for
            # end for
            return chapter_ids
        # end def

        # Function to get the data of the chapter
        def get_chapter_body(novel_id, chapter_id):
            driver.get('view-source:' + chapter_body_url % (novel_id, chapter_id))
            content = driver.page_source
            content = driver.find_element_by_tag_name('pre').text
            parsed_content = (json.loads(content))

            # Condition to check if the GET request was not successful to re-try
            if parsed_content['msg'] != 'Success':
                return get_chapter_body(novel_id, chapter_id)

            return parsed_content['data']
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
            chapter_name = chapter_body['chapterInfo']['chapterName']
            chapter_index = chapter_body['chapterInfo']['chapterIndex']
            chapter_content = f'Chapter {chapter_index}: {chapter_name}'
            for cc in chapter_body['chapterInfo']['contents']:
                content = cc['content']
                content = format_text(content)
                chapter_content = chapter_content + '\n' + str(content)
            # end for
            return {
                'chapter_name': chapter_name,
                'chapter_index': chapter_index,
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
            title = chapter_data['chapter_name']
            index = chapter_data['chapter_index']
            content = chapter_data['chapter_content']
            # If the content of the chapter is empty stop the function and return nothing... in theory at least
            # Not working
            if len(content) < 1:
                return
            chapter = epub.EpubHtml(title=title,file_name=f'{index}.xhtml',content=content)
            book.add_item(chapter)
            spine.append(chapter)
            update(f'Adding... Chapter {index}')
        # end def

        update('Getting chapter list...')
        chapter_list = get_chapters_list(novel_link_id)
        chapters_count = len(chapter_list)
        update(f'Found {chapters_count} chapters')

        # Iterate through the chapter list and add all the chapters inside it in the book
        for chapter_id in chapter_list:
            chapter = get_chapter(novel_link_id, chapter_id)
            # If the content of the chapter is not empty, set it as the last chapter number... in theory... again
            # Not working
            if len(chapter['chapter_content']) > 1:
                chapters_count = chapter['chapter_index']
            add_chapter(chapter)
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
            title = epub_name
        else:
            title = f'{formatted_title} 1-{chapters_count}.epub'

        # Create the EPUB file
        epub.write_epub(title, book)

        update('EPUB file created.')

    if event == GUI.WIN_CLOSED:
        if driver:
            driver.close()
        break

window.close()
