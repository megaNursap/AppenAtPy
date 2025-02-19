import logging
import os

import pytest
from faker import Faker
from adap.ui_automation.services_config.annotation import Annotation
from adap.ui_automation.services_config.audio_transcription import AudioTranscriptionUI
from adap.ui_automation.services_config.audio_transcription_beta import AudioTranscriptionBETA
from adap.ui_automation.services_config.fair_pay.fair_pay_basic import FairPay
from adap.ui_automation.services_config.image_annotation import ImageAnnotationUI
from adap.ui_automation.services_config.ontology import Ontology
from adap.ui_automation.services_config.job.job import Job
from adap.ui_automation.services_config.main_menu import MainMenu
from adap.ui_automation.services_config.navigation import Navigation
from adap.ui_automation.services_config.quality_flow.project.project import QualityFlowProject
from adap.ui_automation.services_config.quality_flow.project_resource.project_resource import Project_Resource
from adap.ui_automation.services_config.scripts import Scripts
from adap.ui_automation.services_config.taxonomy import Taxonomy
from adap.ui_automation.services_config.text_relationship import TextRelationship
from adap.ui_automation.services_config.text_annotation import TextAnnotation
from adap.ui_automation.services_config.verification import GeneralVerification
from adap.ui_automation.services_config.video_annotation import VideoAnnotationUI
from adap.ui_automation.services_config.workflow import Workflow
from adap.ui_automation.services_config.models import Models
from adap.ui_automation.services_config.user import User
from adap.ui_automation.services_config.group_aggregation import GroupAggregation
from adap.ui_automation.services_config.plss import PlssUI
from adap.ui_automation.services_config.audio_annotation import AudioAnnotationUI
from adap.ui_automation.services_config.image_transcription import ImageTranscription
from adap.ui_automation.services_config.job_template import JobTemplate
from adap.ui_automation.services_config.team_funds import TeamFunds
from adap.ui_automation.services_config.video_transcription import VideoTranscriptionUI
from adap.ui_automation.services_config.sda import SDA


from adap.ui_automation.utils.selenium_utils import set_up_driver

LOGGER = logging.getLogger(__name__)


class Application:
    def __init__(self, env=None, temp_path_file=None, driver=None, request=None, driver_type='local'):
        self.env = env
        self.bs_local = None
        if driver:
            self.driver = driver
        else:
            self.driver = set_up_driver(temp_path_file, request=request, session_id=pytest.session_id, driver_type=driver_type)

        self.navigation = Navigation(self)
        self.job = Job(self)
        self.user = User(self)
        self.verification = GeneralVerification(self)
        self.mainMenu = MainMenu(self)
        self.workflow = Workflow(self)
        self.models = Models(self)
        self.ontology = Ontology(self)
        self.text_relationship = TextRelationship(self)
        self.image_annotation = ImageAnnotationUI(self)
        self.video_annotation = VideoAnnotationUI(self)
        self.annotation = Annotation(self)
        self.temp_path_file = temp_path_file
        self.text_annotation = TextAnnotation(self)
        self.audio_transcription = AudioTranscriptionUI(self)
        self.audio_transcription_beta = AudioTranscriptionBETA(self)
        self.group_aggregation = GroupAggregation(self)
        self.plss = PlssUI(self)
        self.audio_annotation = AudioAnnotationUI(self)
        self.image_transcription = ImageTranscription(self)
        self.job_template = JobTemplate(self)
        self.team_funds = TeamFunds(self)
        self.video_transcription = VideoTranscriptionUI(self)
        self.sda = SDA(self)
        self.scripts = Scripts(self)
        self.faker = Faker()
        self.fair_pay = FairPay(self)
        self.taxonomy = Taxonomy(self)
        self.quality_flow = QualityFlowProject(self)
        self.project_resource = Project_Resource(self)

    def save_job_for_tear_down(self, job_id, api_key):
        if os.environ.get("PYTEST_CURRENT_TEST"):
            if job_id is not None and api_key != '':
                pytest.data.job_collections[job_id] = api_key
