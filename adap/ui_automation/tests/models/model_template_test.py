"""
https://appen.atlassian.net/browse/QED-1400
Automate tests for Models template library page
"""
import time
import pytest
from adap.api_automation.utils.data_util import *

# pytestmark = [pytest.mark.regression_smart_workflow, pytest.mark.regression_wf]


@pytest.fixture(scope="module")
def login(app):
    email = get_user_email('test_ui_account')
    password = get_user_password('test_ui_account')
    app.user.login_as_customer(user_name=email, password=password)


def test_models_template_library(app, login):
    app.mainMenu.open_menu_item('models')
    app.navigation.click_link('Create Model')
    app.models.open_menu('All Templates')

    all_templates = app.models.get_templates_on_page()

    assert  ['Appen ASR - (en-uk)',
         'Appen ASR - (en-us)',
         'Blur Faces in Images',
         'Blur Faces in Videos',
         'Blur Plates in Images',
         'Box and Transcribe PII',
         'Box and Transcribe Words',
         'Box and Transcribe Words (Orthogonal)',
         'Box and Transcribe Words (Rotated)',
         'Box Plates in Images',
         'Deskew Image for MLAIT',
         'Detect Angle of Rotation',
         'Detect Explicit Content',
         'Exif Rotation',
         'Four Point Transform',
         'Identify Face Landmarks',
         'Label Bounding Boxes in Street Scene Images',
         'Label Bounding Boxes in Street Scene Videos',
         'Label Pixels for Objects',
         'Label Pixels in Images of People',
         'Label Pixels in Street Scene Images',
         'OCR Auto-rotate',
         'OCR Rotate',
         'Pre-render URLs for Project Bane',
         'Rectify Receipt',
         'Satellite Image PLSS (Buildings)',
         'Segment Audio',
         'Segment Audio Based on Signal-to-Noise Ratio',
         'Spacy Named Entity Recognition',
         'Speaker Diarization',
         'Superpixel Model',
         'Trainable Semantic Segmentation'] == [x['name'] for x in all_templates]


def test_models_datatypes(app, login):
    app.mainMenu.open_menu_item('models')
    app.navigation.click_link('Create Model')

    app.models.open_menu(menu_name='Datatypes', sub_menu='Text')
    app.verification.text_present_on_page('Spacy Named Entity Recognition')

    app.models.open_menu(menu_name='Datatypes', sub_menu='Image')
    all_image_template = app.models.get_templates_on_page()

    app.models.open_menu(menu_name='Datatypes', sub_menu='Image,Annotate')
    image_annotation_templates = app.models.get_templates_on_page()

    app.models.open_menu(menu_name='Datatypes', sub_menu='Image,Classify')
    image_classify_templates = app.models.get_templates_on_page()

    app.models.open_menu(menu_name='Datatypes', sub_menu='Image,Transcribe')
    image_transcribe_templates = app.models.get_templates_on_page()

    _image_templates = image_annotation_templates + image_classify_templates + image_transcribe_templates
    assert all_image_template == sorted_list_of_dict_by_value(_image_templates, 'name')

    app.models.open_menu(menu_name='Datatypes', sub_menu='Image,Collect')
    app.verification.text_present_on_page('No Available Templates')

    app.models.open_menu(menu_name='Datatypes', sub_menu='Audio')
    audio_templates = app.models.get_templates_on_page()

    app.models.open_menu(menu_name='Datatypes', sub_menu='Video')
    video_templates = app.models.get_templates_on_page()

    app.models.open_menu(menu_name='Datatypes', sub_menu='3D')
    app.verification.text_present_on_page('No Available Templates')

    app.models.open_menu(menu_name='Datatypes', sub_menu='Website')
    app.verification.text_present_on_page('No Available Templates')

    _all_templates = all_image_template + audio_templates + video_templates
    app.models.open_menu(menu_name='All Templates')

    all_templates = app.models.get_templates_on_page()
    assert all_templates == sorted_list_of_dict_by_value(_all_templates, 'name')



