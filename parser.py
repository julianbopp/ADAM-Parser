import requests

username = input("insert username: ")
password = input("insert password: ")

headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
           "Accept-Language": "en-US,en;q=0.5",
           "Content-Type": "application/x-www-form-urlencoded",
           "Upgrade-Insecure-Requests": "1",
           "Sec-Fetch-Dest": "document",
           "Sec-Fetch-Mode": "navigate",
           "Sec-Fetch-Site": "same-origin"}

postHeaders = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/x-www-form-urlencoded",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site"
}

firstPostData = {
    "user_idp": "https://aai-logon.unibas.ch/idp/shibboleth",
    "Select": "Select"
}

secondPostData = {
    "shib_idp_ls_exception.shib_idp_session_ss": "",
    "shib_idp_ls_success.shib_idp_session_ss": "true",
    "shib_idp_ls_value.shib_idp_session_ss": "",
    "shib_idp_ls_exception.shib_idp_persistent_ss": "",
    "shib_idp_ls_success.shib_idp_persistent_ss": "true",
    "shib_idp_ls_value.shib_idp_persistent_ss": "",
    "shib_idp_ls_supported": "true",
    "_eventId_proceed": ""
}

thirdPostData = {
    "j_username": username,
    "j_password": password,
    "_eventId_proceed": ""
}

fourthPostData = {
    "shib_idp_ls_exception.shib_idp_session_ss": "",
    "shib_idp_ls_success.shib_idp_session_ss": "false",
    "_eventId_proceed": ""
}