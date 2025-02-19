import csv

from bs4 import BeautifulSoup
from locust import HttpLocust, TaskSet, task, seq_task, between, TaskSequence, task, between, constant, constant_pacing
import time
from adap.api_automation.utils.http_util import ApiResponse


class submit_judgements(TaskSet):

    authenticity_token = ''
    started_at_next = ''
    started_at = ''
    data_assignment_id = ''
    token = ''
    data_worker_id = ''
    data_job_id = ''
    ls = list()

    def on_start(self):

        if len(datasetup) > 0:
            self.job_id, self.secret, self.email, self.password = datasetup.pop()

        header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        url = "channels/cf_internal/jobs/" + self.job_id + "/work?secret=" + self.secret

# HTTP Request to launch the job link
        with self.client.get(url, headers=header, catch_response=True, allow_redirects=True) as response:
            if response.status_code != 200:
                response.failure("Incorrect launch link")
                exit()
            else:
                api_response = ApiResponse(response)
                soup = BeautifulSoup(api_response.content, 'html.parser')
                value = soup.find('input', {'name': 'authenticity_token'}).get('value')
                self.authenticity_token = value
                print("Success : Launch link" + self.authenticity_token)

        header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Pragma": "no-cache"
        }
        url = "sessions"

        form_data = {"session[email]": self.email,
                     "session[password]": self.password,
                     "commit": "Sign In",
                     "authenticity_token": self.authenticity_token
                     }

# HTTP request to Sign in to Task using contributor credentials
        with self.client.post(url, headers=header, data=form_data, catch_response=True,
                              allow_redirects=True) as response:
            if "You've completed all your work!" in response.text:
                response.failure("Incorrect response")
                print("All your work is completed")
                exit()
            elif "Working on Task &mdash; Tasks by Figure Eight" in response.text:
                response.success()
                print("Success: Sign in")
            else:
                response.failure("Incorrect response")
                print("Sign in Failed" + response.text)
                exit()

        url = "channels/cf_internal/jobs/" + self.job_id + "/work?secret=" + self.secret

# HTTP GET request to retrieve dynamic values in the page
        with self.client.get(url, headers=header, catch_response=True, allow_redirects=True) as response1:
            api_response = ApiResponse(response1)
            soup = BeautifulSoup(api_response.content, 'html.parser')

            value = soup.find('input', {'name': 'authenticity_token'}).get('value')
            self.authenticity_token = value
            print("authentication token: " + self.authenticity_token)

            value2 = soup.find('input', {'name': 'started_at_next'}).get('value')
            value2 = int(value2) ^ 1364934572
            self.started_at_next = str(value2)
            print("started at next: " + self.started_at_next)

            value3 = soup.find('input', {'name': 'started_at'}).get('value')
            self.started_at = value3
            print("started_at: " + self.started_at)

            value4 = soup.find('div', {'class': 'js-assignment-id hidden'}).get('data-assignment-id')
            self.data_assignment_id = value4
            print("data-assignment-id: " + self.data_assignment_id)

            for tag in soup.find_all("div", {'class': 'cml_row'}):
                awesome_id = tag.find('input', {'class': 'ask_question_here validates-required'}).get('name')
                self.ls.append(awesome_id)
            print(self.ls)

            if "You've completed all your work! &mdash; Tasks by Figure Eight" in response1.text:
                print("Completed all work")
                exit()
            if self.authenticity_token == "":
                response1.failure("Incorrect response")
                print("Failed :No dynamic values found" + response1.text)
                exit()
            # You've completed all your work!
            else:
                response1.success()

# HTTP Request for Submitting Judgments
    @task
    def submit(self):
        i = 0
# This while loop will continue to submit judgments until there is no more work left for the contributor
        while i != 1:
            header = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                "Content-Type": "application/x-www-form-urlencoded",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Pragma": "no-cache"
            }
            url = "assignments/" + self.data_assignment_id
            # ls = list()
            form_data1 = {
                "_method": "put",
                "authenticity_token": self.authenticity_token,
                "started_at": self.started_at,
                "started_at_next": self.started_at_next,
                "cf_internal": "true",
                self.ls[1]: "first_option",
                self.ls[3]: "first_option",
                self.ls[5]: "first_option",
                self.ls[7]: "first_option",
                self.ls[9]: "first_option"
            }

            print(form_data1)
            with self.client.post(url, headers=header, data=form_data1, catch_response=True,
                                  allow_redirects=False) as response2:
                if response2.status_code != 302 or "<title>You've completed all your work! &mdash; Tasks by Figure Eight</title>" in response2.text:
                    response2.failure("No more work")
                    i = 1
                    print("Failed : no redirect found" + response2.text)
                else:
                    response2.success()
                    api_response = ApiResponse(response2)
                    print("Success : Judgement Submitted" + response2.text)
                    soup = BeautifulSoup(api_response.content, 'html.parser')
                    token = soup.find('a').get('href')
                    print("token is" + token)

            url = token
            del self.ls[:]
            print("After deleting")
            print(self.ls)

            # Retrieve dynamic valyes again
            with self.client.get(url, headers=header, catch_response=True) as response3:
                if ">You've completed all your work!" in response3.text:
                    print("You've completed all your work!")
                    i = 1
                    exit()
                elif "<title>Working on Task &mdash; Tasks by Figure Eight</title>" in response3.text:
                    response3.success()
                    api_response = ApiResponse(response3)
                    print("Success : Submitted Judgment")
                    soup = BeautifulSoup(api_response.content, 'html.parser')
                    tag = soup.find('div', {'class': 'nav-collapse collapse'})
                    value5 = tag.find('span', {'data-module': 'clone-tracker'}).get('data-worker-id')
                    self.data_worker_id = value5
                    print("data_worker_id: " + self.data_worker_id)

                    value6 = tag.find('span', {'data-module': 'clone-tracker'}).get('data-job-id')
                    self.data_job_id = value6
                    print("data_job_id: " + self.data_job_id)

                    value = soup.find('input', {'name': 'authenticity_token'}).get('value')
                    self.authenticity_token = value
                    print("authentication token: " + self.authenticity_token)

                    value2 = soup.find('input', {'name': 'started_at_next'}).get('value')
                    value2 = int(value2) ^ 1364934572
                    self.started_at_next = str(value2)
                    print("started at next: " + self.started_at_next)

                    value3 = soup.find('input', {'name': 'started_at'}).get('value')
                    self.started_at = value3
                    print("started_at: " + self.started_at)

                    value4 = soup.find('div', {'class': 'js-assignment-id hidden'}).get('data-assignment-id')
                    self.data_assignment_id = value4
                    print("data-assignment-id: " + self.data_assignment_id)

                    for tag in soup.find_all("div", {'class': 'cml_row'}):
                        awesome_id = tag.find('input', {'class': 'ask_question_here validates-required'}).get('name')
                        self.ls.append(awesome_id)
                    print(self.ls)
                else:
                    response3.failure("Incorrect response")
                    print("Failed : Submit judgement" + response3.text)
                    exit()

            url = "request_details"
            form_data3 = {
                "val1": self.data_worker_id,
                "val2": self.data_job_id
            }

            with self.client.post(url, headers=header, data=form_data3, catch_response=True,
                                  allow_redirects=True) as response4:
                if response4.status_code != 200:
                    response4.failure("Incorrect response")
                    print("Submit 3 Failed")
                    i = 1
                    exit()
                else:
                    response4.success()
                    print(response4.text)

            time.sleep(1)


class WebsiteUser(HttpLocust):
    task_set = submit_judgements
    wait_time = between(5, 10)
    ENV = "qa"
    host = "https://tasks." + ENV + ".cf3.work"

    def __init__(self):
        super(WebsiteUser, self).__init__()

    def setup(self):
        global datasetup
        with open("adap/data/locust/submit_judgment.csv", 'rt') as f:
            csv_reader = csv.reader(f)
            datasetup = list(csv_reader)
