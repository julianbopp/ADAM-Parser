import json
import os
import requests
from bs4 import BeautifulSoup as bs
import re


class Course:
    def __init__(self, name, url):
        self.name = name
        self.url = url


class Parser:
    def __init__(self):
        with open("userdata.txt") as userdata:
            self.username = userdata.readline().replace("\n", "")
            self.password = userdata.readline().replace("\n", "")
            self.home = userdata.readline().replace("\n", "")
            self.currentSemester = userdata.readline().replace("\n", "")

        self.session = self.getSession()
        self.courses = None
        self.coursesDict = None
        self.semesterURL = self.getSemesterURL()

    def getSession(self):
        if self.username is None or self.password is None:
            self.username = input("insert username: ")
            self.password = input("insert password: ")

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
        }

        postHeaders = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
        }

        e1s2Headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Sec-GPC": "1",
            "Accept-Encoding" : "gzip, deflate, br",
            "Origin" : "https://unibas.login.eduid.ch",
            "DNT" : "1",
            "Referer" : "https://unibas.login.eduid.ch/idp/profile/SAML2/Redirect/SSO?execution=e1s2",
            "TE" : "trailers",
        }

        POSTwayf = {
            "user_idp": "https://aai-logon.unibas.ch/idp/shibboleth",
            "Select": "Select",
        }

        secondPostData = {
            "shib_idp_ls_exception.shib_idp_session_ss": "",
            "shib_idp_ls_success.shib_idp_session_ss": "true",
            "shib_idp_ls_value.shib_idp_session_ss": "",
            "shib_idp_ls_exception.shib_idp_persistent_ss": "",
            "shib_idp_ls_success.shib_idp_persistent_ss": "true",
            "shib_idp_ls_value.shib_idp_persistent_ss": "",
            "shib_idp_ls_supported": "true",
            "_eventId_proceed": "",
        }

        emailPostData = {
            "j_username": self.username,
            "_eventId_submit": "",
        } 
        userdataPostData = {
            "j_username": self.username,
            "j_password": self.password,
            "_eventId_proceed": "",
        }

        finalPostData = {
            "shib_idp_ls_exception.shib_idp_session_ss": "",
            "shib_idp_ls_success.shib_idp_session_ss": "false",
            "_eventId_proceed": "",
        }

        # define url's
        URLadam = "https://adam.unibas.ch"
        URLlogin = "https://adam.unibas.ch/login.php"
        URLhelp_screen = "https://adam.unibas.ch/ilias.php?help_screen_id=init//login.&cmdClass=ilhelpgui&cmdNode=gg&baseClass=ilhelpgui&cmdMode=asynch&cmd=showHelp"
        URLshib_login = "https://adam.unibas.ch/shib_login.php?target="
        URLe1s1 = "https://unibas.login.eduid.ch/idp/profile/SAML2/Redirect/SSO?execution=e1s1"
        URLe1s2 = "https://unibas.login.eduid.ch/idp/profile/SAML2/Redirect/SSO?execution=e1s2"
        URLe1s3 = "https://unibas.login.eduid.ch/idp/profile/SAML2/Redirect/SSO?execution=e1s3"
        URLe1s4 = "https://unibas.login.eduid.ch/idp/profile/SAML2/Redirect/SSO?execution=e1s4"

        # start session that collects and keeps cookies
        session = requests.session()

        # get some url's, post some data to login
        shib_login = session.get(URLshib_login)
        wayf = session.post(shib_login.url, data=POSTwayf)
        e1s1 = session.post(URLe1s1, data=secondPostData)
        session.post(URLe1s2, headers=e1s2Headers, data=emailPostData)
        session.post(URLe1s3, data=userdataPostData)
        sixth = session.post(URLe1s4, data=finalPostData)

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
                SAMLResponse = SAMLResponse.replace(
                    '<input type="hidden" name="SAMLResponse" value="', ""
                )
                SAMLResponse = SAMLResponse.replace('"/>', "")
                break

        # create Post data with opensaml_req and SAMLResponse number
        fifthPostData = {"RelayState": opensaml_req, "SAMLResponse": SAMLResponse}

        # last two steps for creating logged in session
        seventh = session.post(
            "https://adam.unibas.ch/Shibboleth.sso/SAML2/POST",
            headers=postHeaders,
            data=fifthPostData,
        )
        eighth = session.get(
            "https://adam.unibas.ch/shib_login.php?target=", headers=headers
        )

        return session

    def testSession(self):
        URL = "https://adam.unibas.ch/goto_adam_file_1243214_download.html"
        response = self.session.get(URL)
        open("test.pdf", "wb").write(response.content)
        parser.downloadFolder(
            self.home,
            "20996-01 – Wahrscheinlichkeitstheorie",
            "https://adam.unibas.ch/goto_adam_crs_1257264.html",
        )

    def getSemesterURL(self):
        soup = bs(
            self.session.get(
                "https://adam.unibas.ch/ilias.php?baseClass=ilDashboardGUI&cmd=jumpToSelectedItems"
            ).text,
            "lxml",
        )
        semester = soup.find("button", {"aria-label": self.currentSemester})
        semesterURL = "https://adam.unibas.ch/" + semester["data-action"]

        return semesterURL

    # Find all courses of the current Semester and save their name + link in dictionary
    def getCourses(self):
        semester = bs(self.session.get(self.semesterURL).text, "lxml")
        print(self.semesterURL)

        # save dictionary of name : url pairs
        courses = {}
        for item in semester.find_all("div", {"class": "il-item-title"}):
            course = item.find("a")

            # check if it's really a course url and not something else before adding
            if course is not None:
                if course["href"] is not None:
                    if "crs" in course["href"]:

                        # add course with link to dict.
                        courses[course.text] = course["href"]

        self.coursesDict = courses

    # Save the courses dictionary to a json file
    def saveCoursesDict(self):
        file = json.dumps(self.coursesDict)
        f = open("courses.json", "w")
        f.write(file)
        f.close()

    # Load courses from courses.json
    def loadCoursesDict(self):
        file = open("courses.json")
        self.coursesDict = json.load(file)

    def courseDictToArray(self):
        courses = []
        for course in self.coursesDict:
            courseName = course[11:]
            courses.append(Course(courseName, self.coursesDict[course]))
        self.courses = courses

    # Create the course folder structure in your filesystem
    def createCourseDirectories(self):
        for item in self.courses:
            path = os.path.join(self.home, item.name)
            if not os.path.exists(path):
                os.mkdir(path)

    # Download from a link. Can be content, folder, and exercise folder
    def downloadFile(self, path, url):
        response = self.session.get(url)
        headers = response.headers

        if "content-disposition" in headers.keys():
            # then it's likely a pdf
            contentdispo = headers["content-disposition"]

            # extract filename and format it
            name = re.findall('filename="(.+)"', contentdispo)[0]

            # create path where the file will be stored
            path = os.path.join(path, name)

            # only write to filesystem if it does not already exist
            if not os.path.exists(path):
                open(path, "wb").write(response.content)

        elif "adam_fold" in url:
            # it's a folder
            # we have to extract all links, names from the folder
            # use beautiful soup object to parse for the folder name
            soup = bs(response.text, "lxml")
            name = soup.find("a", {"name": "il_mhead_t_focus"}).text

            # Check for "/" in folder name and replace with something else.
            # "/" is not allowed in folder names on Linux/macOS but is allowed on ADAM
            if "/" in name:
                name = name.replace("/", " ")
            path = os.path.join(path, name)

            if not os.path.exists(path):
                os.mkdir(path)

            # download folder content
            self.downloadFolder(path, "", url)

        elif "adam_exc" in url:
            # it's an exercise folder
            soup = bs(response.text, "lxml")
            name = soup.find("a", {"name": "il_mhead_t_focus"}).text

            path = os.path.join(path, name)

            if not os.path.exists(path):
                os.mkdir(path)

            # download exercise folder content
            self.downloadExerciseFolder(path, "", url)

    # Inside an Exercise(special adam folder) find all links
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

    # Download content of Exercise(special adam folder) folder
    def downloadExerciseFolder(self, path, folderName, folderURL):
        links = self.getExerciseLinks(folderURL)
        for link in links:
            newpath = os.path.join(path, folderName)
            self.downloadFile(newpath, link)

    # Get download links from insider folder
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

    # Download complete folder
    def downloadFolder(self, path, courseName, courseURL):
        links = self.getFileLinks(courseURL)
        for link in links:
            newpath = os.path.join(path, courseName)
            self.downloadFile(newpath, link)

    # Download each course from current semester
    def downloadAllCourses(self):
        for course in self.courses:
            self.downloadFolder(self.home, course.name, course.url)

    def getExternalSource(self, course):
        externalURL = course.external
        soup = bs(self.session.get(externalURL).text, "lxml")
        h2s = soup.find_all("h2", {"class": "unibas-h2"})


if __name__ == "__main__":
    parser = Parser()
    parser.getCourses()
    parser.saveCoursesDict()
    parser.loadCoursesDict()
    parser.courseDictToArray()
    parser.createCourseDirectories()
    parser.downloadAllCourses()
