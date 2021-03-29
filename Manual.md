# Manual

This manual is intended to help you use the Webnovel Scrapper app.

# How to download novels - **Account Version**

1. Open up the application **`Webnovel Scrapper.exe`**.
2. In the **`Novel Link`** field please introduce the link of the novel you wish to download.
   - The link to the webnovel will look something like this:
     - `https://www.webnovel.com/book/never-judge_17932851106749705`
     - `https://www.webnovel.com/book/17932851106749705`
3. In the **`EPUB Name`** you can introduce a name for your file if you wish to customize it, otherwise leave it empty for the default string.
   - Default String: **`Novel Name 1-999`**
4. You can check the **`Hide titles?`** box if you wish to hide the title of the chapters and leave only its number.
   - This is useful for people that do not wish to be spoiled about the content of the chapter that they are about to read.
5. Inside the **`Login`** tab you have the options to see what the browser is doing with your account information by unchecking the **`Headless?`** checkbox.
6. The **`Email`** and **`Password`** fields are your [**Webnovel**](https://webnovel.com) account credetials needed to be able to log in to get the cookies neccessary to download the novel.
7. Now press the **`Get EPUB | Login`** and wait for your novel to download. The program will be **(Not Responding)** while the download is happening.

# How to download novels - **CSRF Token Version**

1. Open up the application **`Webnovel Scrapper.exe`**.
2. In the **`Novel Link`** field please introduce the link of the novel you wish to download.
   - The link to the webnovel will look something like this:
     - `https://www.webnovel.com/book/never-judge_17932851106749705`
     - `https://www.webnovel.com/book/17932851106749705`
3. In the **`EPUB Name`** you can introduce a name for your file if you wish to customize it, otherwise leave it empty for the default string.
   - Default String: **`Novel Name 1-999`**
4. You can check the **`Hide titles?`** box if you wish to hide the title of the chapters and leave only its number.
   - This is useful for people that do not wish to be spoiled about the content of the chapter that they are about to read.
5. Inside the **`CSRF`** tab you have to input your [**CSRF Token**](#csrf) to able to download any novel. You can click here to see how you can get your [**CSRF Token**](#csrf) or scroll down to the section `How to get your` **`CSRF Token`** `from your browser`.
6. Now press the **`Get EPUB | CSRF`** and wait for your novel to download. The program will be **(Not Responding)** while the download is happening.

# <a name="csrf"></a> How to get your **CSRF Token** from your browser

1. Go to [**Webnovel**](https://webnovel.com) and login into your account.
2. Now press `F12` or `CTRL + SHIFT + I` if you are on Windows, or `CMD + SHIFT + I` if you are on Mac, to open the developer tools.
3. Now go to the `Storage` tab if you are on `Firefox` or the `Application` tab if you are on `Chrome`. Inside here, go to the `Cookies` section and click the `https://www.webnovel.com`. On one of the lines you should be able to see `_csrfToken`. All you have to do is copy its value.
