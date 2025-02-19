import time

from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_audio_transcription, pytest.mark.audio_transcription_ui]

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')
DATA_FILE = get_data_file("/audio_transcription/AT-newdata-segments.csv")

@pytest.mark.dependency()
def test_class_info_is_available(app, at_job):
    """
    class Person has predefined decription - TESTING INFO ICON WHEN DESCRIPTION IS AVAILABLE
    class Pet has predefined decription - another description
    """
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(at_job)
    app.job.preview_job()
    app.audio_transcription.activate_iframe_by_index(0)
    time.sleep(3)

    assert app.audio_transcription.info_icon_is_displayed_on_bubble("Person")
    assert app.audio_transcription.info_icon_is_displayed_on_bubble("Pet")

    assert not app.audio_transcription.info_icon_is_displayed_on_bubble("Noise")
    app.image_annotation.deactivate_iframe()



@pytest.mark.dependency(depends=["test_class_info_is_available"])
def test_open_close_info_icon(app, at_job):
     """
     class Person has predefined decription - TESTING INFO ICON WHEN DESCRIPTION IS AVAILABLE
     class Pet has predefined decription - another description
     """
     app.mainMenu.jobs_page()
     app.job.open_job_with_id(at_job)

     app.job.preview_job()
     app.audio_transcription.activate_iframe_by_index(0)


     time.sleep(3)

     app.audio_transcription.click_info_icon_on_bubble("Person")
     app.verification.text_present_on_page('testing info icon when description is available')

     app.audio_transcription.toolbar.close_info_panel()
     app.verification.text_present_on_page('testing info icon when description is available', is_not=False)

     app.audio_transcription.click_info_icon_on_bubble("Pet")
     app.verification.text_present_on_page('another description')

     app.audio_transcription.toolbar.close_info_panel()
     app.verification.text_present_on_page('another description', is_not=False)

     app.image_annotation.deactivate_iframe()

