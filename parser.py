import requests
from bs4 import BeautifulSoup as bs
import cchardet


class Parser:
    def __init__(self):
        with open("userdata.txt") as userdata:
            self.username = userdata.readline().replace('\n', '')
            self.password = userdata.readline().replace('\n', '')

        self.session = self.getSession()
        self.courses = None

    def getSession(self):

        if self.username is None or self.password is None:
            self.username = input("insert username: ")
            self.password = input("insert password: ")

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
            "j_username": self.username,
            "j_password": self.password,
            "_eventId_proceed": ""
        }

        fourthPostData = {
            "shib_idp_ls_exception.shib_idp_session_ss": "",
            "shib_idp_ls_success.shib_idp_session_ss": "false",
            "_eventId_proceed": ""
        }

        # define url's
        URL1 = "https://adam.unibas.ch/login.php"
        URL2 = "https://adam.unibas.ch/shib_login.php?target="
        URL3 = "https://wayf.switch.ch/SWITCHaai/WAYF?entityID=https%3A%2F%2Fadam.unibas.ch%2Fshibboleth&return=https%3A%2F%2Fadam.unibas.ch%2FShibboleth.sso%2FLogin"
        URL4 = "https://unibas.login.eduid.ch/idp/profile/SAML2/Redirect/SSO?execution=e1s1"
        URL5 = "https://unibas.login.eduid.ch/idp/profile/SAML2/Redirect/SSO?execution=e1s2"
        URL6 = "https://unibas.login.eduid.ch/idp/profile/SAML2/Redirect/SSO?execution=e1s3"

        # start session that collects and keeps cookies
        session = requests.session()

        # get some url's, post some data to login
        first = session.get(URL1, headers=headers)
        second = session.get(URL2, headers=headers)
        third = session.post(URL3, headers=headers, data=firstPostData)
        fourth = session.post(URL4, headers=headers, data=secondPostData)
        fifth = session.post(URL5, headers=headers, data=thirdPostData)
        sixth = session.post(URL6, headers=headers, data=fourthPostData)

        # need to read opensaml_req number from cookies
        cookies = session.cookies

        for cookie in cookies:
            # if everything works this should occur once
            if "opensaml_req" in cookie.name:
                opensaml_req = cookie.name
                opensaml_req = opensaml_req.strip("_opensaml_req_")
                opensaml_req = opensaml_req.replace("%3A", ":")
                opensaml_req = "ss" + opensaml_req

        # need to read SAMLResponse number from sixth.text
        text = sixth.text
        for item in text.split("\n"):
            # if everything works this should occur once
            if "SAMLResponse" in item:
                SAMLResponse = item
                SAMLResponse = SAMLResponse.replace('<input type="hidden" name="SAMLResponse" value="', "")
                SAMLResponse = SAMLResponse.replace('"/>', "")
                break

        # create Post data with opensaml_req and SAMLResponse number
        fifthPostData = {
            "RelayState": opensaml_req,
            "SAMLResponse": SAMLResponse
        }

        # last two steps for creating logged in session
        seventh = session.post("https://adam.unibas.ch/Shibboleth.sso/SAML2/POST", headers=postHeaders,
                               data=fifthPostData)
        eighth = session.get("https://adam.unibas.ch/shib_login.php?target=", headers=headers)

        return session

    def testSession(self):
        session = self.getSession()
        URL = "https://adam.unibas.ch/goto_adam_file_1243214_download.html"
        response = session.get(URL)
        open("test.pdf", "wb").write(response.content)

    def getCourses(self):
        semesterURL = "https://adam.unibas.ch/ilias.php?view=0&show=48657262737473656d65737465722032303232&cmd" \
                      "=jumpToSelectedItems&cmdClass=ildashboardgui&cmdNode=c0&baseClass=ilDashboardGUI"
        semester = bs(self.session.get(semesterURL).text, "lxml")

        # save dictionary of name : url pairs
        courses = {}
        for item in semester.find_all("div", {"class": "il-item-title"}):
            course = item.find("a")
            courses[course.text] = course["href"]

        self.courses = courses



if __name__ == "__main__":
    parser = Parser()
    parser.testSession()
    parser.getCourses()
