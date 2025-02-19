from adap.settings import Config
from adap.perf_platform.utils.logging import get_logger
from adap.ui_automation.utils.selenium_utils import nav_timing
import random
import time

log = get_logger(__name__)


class Judgments:
    def __init__(self, app, worker_email, worker_password, env, **kwargs):
        self.app = app
        self.env = env
        self.worker_email = worker_email
        self.worker_password = worker_password
        self.channel = kwargs.get('channel') or 'vcare'
        self.url_account = f'https://account.{self.env}.cf3.us'
        self.url_tasks = f"{self.url_account}/channels/{self.channel}/tasks" \
                         f"?uid={self.worker_email}"

    def sign_in(self):
        log.info({
            'message': "sign_in",
            'user_id': self.app.user.user_id})
        self.app.driver.get(self.url_account)
        nav_timing(self.app.driver)
        self.app.user.task.login(
            self.worker_email,
            self.worker_password)
        nav_timing(self.app.driver)

    def go_to_job(self, job_id, job_url=''):
        if job_url:
            # access job by the internal link
            log.info({
                'message': "get job",
                'url': job_url,
                'user_id': self.worker_email})
            self.app.driver.get(job_url)
            nav_timing(self.app.driver)
        else:
            # access job via external channel
            log.info({
                'message': f"get tasks page {self.url_tasks}",
                'user_id': self.worker_email})
            self.app.driver.get(self.url_tasks)
            nav_timing(self.app.driver)
            self.app.user.task.skip_tour()
            log.info({
                'message': "open job by id",
                'user_id': self.worker_email})
            self.app.user.task.account_open_job_by_id(job_id)
            nav_timing(self.app.driver)

    def annotate(self, min_time_per_page=1):
        start_time = time.time()
        submit_btn = self.app.annotation.find_submit_button()
        while submit_btn:
            log.info({
                'message': "get_number_iframes_on_page",
                'user_id': self.worker_email})
            num_iframes = self.app.annotation.get_number_iframes_on_page()
            for index in range(num_iframes):
                log.debug({
                    'message': f"annotating {index} task",
                    'user_id': self.worker_email})
                self.app.annotation.activate_iframe_by_index(index)
                if Config.JOB_TYPE == 'image_annotation':
                    self.annotate_image()
                elif Config.JOB_TYPE == 'video_annotation':
                    self.annotate_video()
                else:
                    raise Exception(f'Unhandled JOB_TYPE {Config.JOB_TYPE}')
                self.app.annotation.deactivate_iframe()

            d_time = time.time() - start_time
            if d_time < min_time_per_page:
                time.sleep(d_time - min_time_per_page)

            log.info({
                'message': "submit_page",
                'user_id': self.worker_email})
            prev_url = self.app.driver.current_url
            log.debug(f'prev_url={prev_url}')
            self.app.annotation.submit_page()
            max_try = 60
            c_try = 1
            while c_try < max_try:
                new_url = self.app.driver.current_url
                log.debug(f'new_url={new_url}')
                if new_url != prev_url:
                    nav_timing(self.app.driver)
                    break
                else:
                    time.sleep(1)
                    c_try += 1
            else:
                raise Exception({
                    'message': "assignment was not submitted",
                    'page_text': self.app.driver.page_source,
                    'user_id': self.worker_email})
            if Config.WORKER_RANDOM_EXIT is not None:
                if random.random() < float(Config.WORKER_RANDOM_EXIT):
                    log.info({
                        'message': 'Worker exited randomly',
                        'user_id': self.worker_email
                        })
                    break

            submit_btn = self.app.annotation.find_submit_button()
        else:
            if "You've completed all your work!" in self.app.driver.page_source:
                log.debug({
                        'message': "Assignment completed",
                        'page_text': self.app.driver.page_source,
                        'user_id': self.worker_email
                        })                
            log.info({
                    'message': "Worker exited from assignments",
                    'page_text': self.app.driver.page_source,
                    'user_id': self.worker_email
                    })

    def annotate_video(self):
        log.debug({
            'message': "annotate_video",
            'user_id': self.worker_email})
        draw_chance = 0.5
        num_frames = self.app.video_annotation.get_num_of_frames_for_video()
        for frame in range(num_frames):
            if random.random() > draw_chance:
                # app.video_annotation.annotate_frame(
                #   mode='random',
                #   value=random.randint(1, 2)
                # )
                self.app.video_annotation.annotate_frame(
                    mode='ontology',
                    value={
                        "Right Hand": 1,
                        "Left Hand": 2},
                    hide_box=False)

            self.app.video_annotation.next_frame()

        if self.app.video_annotation.get_num_of_current_frame() != num_frames:
            assert False, "Something went wrong, user did not view all frames"

    def annotate_image(self):
        log.debug({
            'message': "annotate_image",
            'user_id': self.worker_email})
        self.app.image_annotation.annotate_image(
            mode='ontology',
            value={
                "Cat": random.randint(1, 2),
                "Dog": random.randint(1, 2)
                }
            )
