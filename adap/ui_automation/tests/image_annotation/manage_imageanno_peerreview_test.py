"""
https://appen.atlassian.net/browse/QED-1583
"""

from adap.api_automation.utils.data_util import *
import time
from adap.data import annotation_tools_cml as data
from adap.ui_automation.services_config.annotation import create_annotation_tool_job

pytestmark = [pytest.mark.regression_image_annotation, pytest.mark.fed_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/image_annotation/fullreport_peerreview.csv")


def test_create_peer_review_job(app):
    job_id = create_annotation_tool_job(API_KEY, DATA_FILE,
                                        data.image_annotation_peer_review_cml,
                                        job_title="Testing create image annotation job", units_per_page=2)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(job_id)

    app.job.open_tab('DESIGN')
    app.navigation.click_link('Manage Image Annotation Ontology')
    
    ontology_file = get_data_file("/image_annotation/ontology.json")
    app.ontology.upload_ontology(ontology_file, rebrand=True)
    app.verification.text_present_on_page("Classes Created")

    app.job.preview_job()
    time.sleep(8)

    app.video_annotation.activate_iframe_by_index(0)
    app.image_annotation.click_image_rotation_button()
    app.image_annotation.image_rotation_slider_bar_available()
    assert int(app.image_annotation.get_image_rotation_degree()[:-1]) == 0
    app.image_annotation.close_image_rotation_bar()
    app.image_annotation.image_rotation_slider_bar_available(is_not=False)
    app.image_annotation.deactivate_iframe()
    # feature changed.
    # value = app.image_annotation.get_annotation_value()
    # assert len(value) == 5
    # annotation = []
    # for i in range(0, 5):
    #     annotation.append(value[i].get("type"))
    # assert 'box' in annotation
    # assert 'ellipse' in annotation
    # assert 'dot' in annotation
    # assert 'line' in annotation
    # assert 'polygon' in annotation
    app.image_annotation.submit_test_validators()
    app.verification.text_present_on_page('Validation succeeded')

