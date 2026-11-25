class Profile:
    def __init__(self, first_name, last_name, email, linkedin, github, resume):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.linkedin = linkedin
        self.github = github
        self.resume = resume

    def getFirstName(self):
        return self.first_name
    def getLastName(self):
        return self.last_name
    def getName(self):
        return f"{self.first_name} {self.last_name}"
    def getEmail(self):
        return self.email
    def getLinkedIn(self):
        return self.linkedin
    def getGithub(self):
        return self.github
    def getResume(self):
        return self.resume


Andre = Profile(
    "Andre", 
    "Austin", 
    "andreaustinx@gmail.com", 
    "https://www.linkedin.com/in/andre-austin",
    "https://www.github.com/andreaustin",
    r"C:\Users\andre\OneDrive\Documents\coding_projects\jobclick\Andre_Resume.pdf"
)
