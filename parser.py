import json
import os
import requests
from bs4 import BeautifulSoup as bs
import re
import cchardet


class Parser:
    def __init__(self):
        with open("userdata.txt") as userdata:
            self.username = userdata.readline().replace('\n', '')
            self.password = userdata.readline().replace('\n', '')
            self.home = userdata.readline().replace('\n', '')

        self.session = self.getSession()
        self.courses = None
        self.semesterURL = self.getSemesterURL()

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
        URL = "https://adam.unibas.ch/goto_adam_file_1243214_download.html"
        response = self.session.get(URL)
        open("test.pdf", "wb").write(response.content)
        parser.downloadCourse("20996-01 – Wahrscheinlichkeitstheorie","https://adam.unibas.ch/goto_adam_crs_1257264.html")

    def getSemesterURL(self):
        soup = bs(self.session.get("https://adam.unibas.ch/ilias.php?baseClass=ilDashboardGUI&cmd=jumpToSelectedItems").text, "lxml")
        semester = soup.find("button", {"aria-label": "Herbstsemester 2022"})
        semesterURL = "https://adam.unibas.ch/" + semester["data-action"]

        return semesterURL


    def getCourses(self):
        semesterURL = self.semesterURL

        semester = bs(self.session.get(semesterURL).text, "lxml")

        # save dictionary of name : url pairs
        courses = {}
        for item in semester.find_all("div", {"class": "il-item-title"}):
            course = item.find("a")

            # check if it's really a course url and not something else before adding
            if "crs" in course["href"]:
                courses[course.text] = course["href"]

        self.courses = courses

    def saveCourses(self):
        file = json.dumps(self.courses)
        f = open("courses.json", "w")
        f.write(file)
        f.close()

    def loadCourses(self):
        file = open("courses.json")
        self.courses = json.load(file)

        print(self.courses)

    def createCourseDirectories(self):
        for item in self.courses:
            path = os.path.join(self.home, item)
            if not os.path.exists(path):
                os.mkdir(path)

    def downloadFile(self, path, url):
        response = self.session.get(url)
        headers = response.headers

        if "content-disposition" in headers.keys():
            # then it's likely a pdf
            contentdispo = headers["content-disposition"]
            name = re.findall('filename=\"(.+)\"', contentdispo)[0]

            path = os.path.join(path, name)

            if not os.path.exists(path):
                open(path, "wb").write(response.content)

        elif "adam_fold" in url:
            soup = bs(response.text, "lxml")
            name = soup.find("a", {"name": "il_mhead_t_focus"}).text

            path = os.path.join(path, name)

            if not os.path.exists(path):
                os.mkdir(path)

            # get links from inside folder
            self.downloadFolder(path, "", url)

        elif "adam_exc" in url:
            soup = bs(response.text, "lxml")
            name = soup.find("a", {"name": "il_mhead_t_focus"}).text

            path = os.path.join(path, name)

            if not os.path.exists(path):
                os.mkdir(path)

            self.downloadExerciseFolder(path, "", url)



    def getExerciseLinks(self, url):
        soup = bs(self.session.get(url).text, "lxml")
        files = soup.find_all("a", text="Download")

        links = []
        for item in files:
            if "https://adam.unibas.ch/" not in item["href"]:
                links.append("https://adam.unibas.ch/" + item["href"])
            else:
                links.append(item["href"])

        return links

    def downloadExerciseFolder(self, path, folderName, folderURL):
        links = self.getExerciseLinks(folderURL)
        for link in links:
            newpath = os.path.join(path, folderName)
            self.downloadFile(newpath, link)

    def getFileLinks(self, url):
        soup = bs(self.session.get(url).text, "lxml")
        files = soup.find_all("a", {"class": "il_ContainerItemTitle"})

        links = []
        for item in files:
            print(item)
            if "https://adam.unibas.ch/" not in item["href"]:
                links.append("https://adam.unibas.ch/" + item["href"])
            else:
                links.append(item["href"])

        return links

    def downloadFolder(self, path, courseName, courseURL):
        links = self.getFileLinks(courseURL)
        for link in links:
            newpath = os.path.join(path, courseName)
            self.downloadFile(newpath, link)

    def downloadAllCourses(self):
        for course in self.courses:
            self.downloadFolder(self.home, course, self.courses[course])


if __name__ == "__main__":
    parser = Parser()
    parser.getCourses()
    parser.saveCourses()
    parser.loadCourses()
    parser.createCourseDirectories()
    parser.downloadAllCourses()

