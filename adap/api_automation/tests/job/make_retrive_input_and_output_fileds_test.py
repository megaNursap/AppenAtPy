import time

import allure

from adap.api_automation.services_config.builder import Builder
from adap.api_automation.services_config.client import Client
from adap.api_automation.services_config.make import Make
from adap.api_automation.services_config.requestor_proxy import RP
from adap.api_automation.utils.data_util import *
from adap.api_automation.utils.helpers import find_authenticity_token


mark_only_envs = pytest.mark.skipif(
    pytest.env not in ["integration"],
    reason="Only integration enabled feature")
pytestmark = [pytest.mark.regression_core, mark_only_envs]


API_KEY = get_test_data('test_ui_account', 'api_key')
TOKEN = get_test_data('test_predefined_jobs', 'jwt_token')
PREDEFINED_JOBS = pytest.data.predefined_data
job1 = PREDEFINED_JOBS['job_with_judgments'][pytest.env]
job2 = PREDEFINED_JOBS['job_for_copying'][pytest.env]
job3 = PREDEFINED_JOBS['audio_annotation'][pytest.env]
job4 = PREDEFINED_JOBS['ipa_job']['what_is_greater'][pytest.env]

email = get_test_data('test_predefined_jobs', 'email')
password = get_test_data('test_predefined_jobs', 'password')


@pytest.fixture(scope="module")
def set_up(app):
    api_key = get_test_data('test_ui_account', 'api_key')
    token = get_test_data('test_ui_account', 'jwt_token')
    email = get_test_data('test_predefined_jobs', 'email')
    password = get_test_data('test_predefined_jobs', 'password')

    client = Client(env=pytest.env, session=True)
    sign_in_resp = client.sign_in(email=email, password=password)
    authenticity_token = find_authenticity_token(sign_in_resp.content)

    app.user.login_as_customer(user_name=email, password=password, close_guide=False)

    flat_cookie_dict = {seleniumCookie['name']: seleniumCookie['value'] for seleniumCookie in
                        app.driver.get_cookies()}

    return {
        "api_key": api_key,
        "jwt_token": token,
        "email": email,
        "password": password,
        "client": client,
        "authenticity_token": authenticity_token,
        "cookies": flat_cookie_dict
    }


@allure.severity(allure.severity_level.NORMAL)
def test_empty_job_ids():
    make = Make(API_KEY)
    res = make.get_output_required_fields(jobs=[])
    res.assert_response_status(422)
    assert res.json_response == {'error': {'job_ids': ["can't be blank"]}}


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.parametrize('name, jobs',
                         [
                             ("one job", ["one"]),
                             ("two jobs", ['one','two']),
                             ("one of job is invalid", [job1, 'one']),
                             ("special char", ['100000!'])
                         ])
def test_invalid_job_ids(name, jobs):
    make = Make(API_KEY)
    res = make.get_output_required_fields(jobs=jobs)
    res.assert_response_status(422)
    assert res.json_response == {'error': {'job_ids': ['ids must be numeric']}}


@allure.severity(allure.severity_level.NORMAL)
def test_invalid_job_id_len_10_char():
    make = Make(API_KEY)
    res = make.get_output_required_fields(jobs=[1233333333])
    res.assert_response_status(200)
    assert res.json_response == []


@allure.severity(allure.severity_level.NORMAL)
def test_invalid_job_not_exist_len_9_char():
    make = Make(API_KEY)
    res = make.get_output_required_fields(jobs=[123333333])
    res.assert_response_status(200)
    assert res.json_response == []


@allure.severity(allure.severity_level.NORMAL)
def test_get_fields_several_jobs():
    make = Make(API_KEY)

    res = make.get_output_required_fields(jobs=[job1, job2, job3, job4])
    res.assert_response_status(200)

    _jobs = []
    for item in res.json_response:
        for key, value in item.items():
            _jobs.append(key)

    assert len(res.json_response) == 4
    assert sorted(_jobs) == sorted([str(job1), str(job2), str(job3), str(job4)])


@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.flaky(reruns=2)
@pytest.mark.parametrize('aggregation_method, expected_output',
                         [
                             ("agg", {'ask_question_here': 'String', 'ask_question_here:confidence': 'Float'}),
                             ("all", {}),
                             ("avg", {'ask_question_here': 'Integer', 'ask_question_here:confidence': 'Float'}),
                             # ("agg_x", {'ask_question_here': 'String', 'ask_question_here:confidence': 'Float'}),  500
                             # ("bagg_x", {'ask_question_here': 'String', 'ask_question_here:confidence': 'Float'}),  500
                             # ("cagg_x", {'ask_question_here': 'String', 'ask_question_here:confidence': 'Float'})    500
                         ])
def test_jobs_aggregations(set_up, aggregation_method, expected_output):
    '''
    <div class="html-element-wrapper">
      <img class="liquid-image" src="{{image_url}}"/>
    </div>
    <cml:radios label="Ask question here:" validates="required" aggregation="agg" gold="true">
      <cml:radio label="cat" value="cat"/>
      <cml:radio label="dog" value="dog"/>
      <cml:radio label="something else" value="something_else"/>
    </cml:radios>
    '''

    job = PREDEFINED_JOBS['make_input_output_aggr_test'][pytest.env]

    payload = json.dumps({
        "advancedOptions": {
            "include_tainted": False,
            "null_confidence": False,
            "ignore_gold": False,
            "include_unfinished": True,
            "htl_report": False,
            "logical_aggregation": True,
            "include_single_boxes": False,
            "include_single_dots": False,
            "include_single_polygons": False,
            "include_single_lines": False,
            "include_single_ellipses": False
        },
        "aggregations": [
            {
                "tagName": "ask_question_here",
                "aggregationMethod": aggregation_method,
                # "annotationType": None,
                "availableAggregationMethods": [
                    "agg",
                    "all",
                    "avg",
                    "agg_x",
                    "bagg_x",
                    "cagg_x"
                ]
            }
        ],
        "authenticityToken": set_up['authenticity_token']
    })

    rp = RP(
        jwt_token=TOKEN,
        env=pytest.env,
        service=set_up['client'].service,
        cookies=set_up['cookies']
    )

    res = rp.update_reports_options(job, payload)
    assert res.status_code == 200
    assert res.json_response == {'message': 'Success!'}

    time.sleep(10)

    make = Make(API_KEY)
    res = make.get_output_required_fields(jobs=[job])
    assert res.status_code == 200
    input_fields = res.json_response[0][str(job)]['input_fields']
    output_fields = res.json_response[0][str(job)]['output_fields']
    assert input_fields ==  ['image_url']
    assert output_fields == expected_output


@allure.severity(allure.severity_level.NORMAL)
def test_jobs_aggregations_tagg():
    '''
    <cml:text_annotation label="Label Text" name="annotation" source-type="text" source-data="{{text}}"
    tokenizer="spacy" language="en" search-url="https://www.google.com/search?q=%s"
    span-creation="true" aggregation="tagg" validates="required" allow-nesting="true" gold="true"/>
    '''

    job = PREDEFINED_JOBS['make_input_output_tagg'][pytest.env]

    make = Make(API_KEY)
    res = make.get_output_required_fields(jobs=[job])
    assert res.status_code == 200
    input_fields = res.json_response[0][str(job)]['input_fields']
    output_fields = res.json_response[0][str(job)]['output_fields']

    assert input_fields == ['text']
    assert output_fields == {'annotation': 'String', 'annotation:confidence': 'Float'}


@allure.severity(allure.severity_level.NORMAL)
def test_jobs_aggregations_avg_array():
    '''
    <div class="html-element-wrapper">
      <p>
        <em>Read prompt below and speak the appropriate phrase in SWAHILI. After recording please transcribe the recording in SWAHILI. Prepare to speak with you hit</em> "START":
      </p>
      <p>
        NOTE: When you save the recording you will no longer be able to replay it.
      </p>
      <p>
        <b>Prompt (English):</b> {{prompt}}
      </p>
    </div>

    <cml:textarea label="Please transcribe the voice command from above" validates="required" aggregation="avg"/>
    <cml:checkbox class="confirm-checkbox" label="I confirm that I have submitted a recording" validates="required" aggregation="avg"/>
    <div>
      <cml:text label="" class="audiofilename" default="" name="file_name" aggregation="avg"/>
      <cml:text label="" class="audiofileurl" default="" name="file_download" aggregation="avg"/>
    </div>
    '''
    job = PREDEFINED_JOBS['make_input_output_avg_array'][pytest.env]

    make = Make(API_KEY)
    res = make.get_output_required_fields(jobs=[job])
    assert res.status_code == 200
    input_fields = res.json_response[0][str(job)]['input_fields']
    output_fields = res.json_response[0][str(job)]['output_fields']

    assert input_fields == ["prompt"]
    assert output_fields == {
                "please_transcribe_the_voice_command_from_above": "Array",
                "please_transcribe_the_voice_command_from_above:confidence": "Float",
                "i_confirm_that_i_have_submitted_a_recording": "Array",
                "i_confirm_that_i_have_submitted_a_recording:confidence": "Float",
                "file_name": "Array",
                "file_name:confidence": "Float",
                "file_download": "Array",
                "file_download:confidence": "Float",
                "rate_me": "Array",
                "rate_me:confidence": "Float",
                "sample_select_box": "String",
                "sample_select_box:confidence": "Float"
            }


@allure.severity(allure.severity_level.NORMAL)
def test_jobs_input_fields():
    '''
    <div class="row-fluid">
      <div class="span6">
        <div class="well">
          <img src="{{img_url1}}" class="img-polaroid img-responsive"/>
          <br/>

          <table class="table table-bordered">
            <tr>
              <td>
                Name
              </td>
              <td>
                Value
              </td>
            </tr>
            <tr>
              <td>
                Price:
              </td>
              <td>
                ${{price1}}
              </td>
            </tr>
            <tr>
              <td>
                Color:
              </td>
              <td>
                {{color1}}
              </td>
            </tr>
            <tr>
              <td>
                Size:
              </td>
              <td>
                {{size1}}
              </td>
            </tr>
          </table>
        </div>
      </div>

      <div class="span6">
        <div class="well">

          <img src="{{img_url2}}" class="img-polaroid img-responsive"/>

          <br/>

          <table class="table table-bordered">
            <tr>
              <td>
                Name
              </td>
              <td>
                Value
              </td>
            </tr>
            <tr>
              <td>
                Price:
              </td>
              <td>
                {{price2}}
              </td>
            </tr>
            <tr>
              <td>
                Color:
              </td>
              <td>
                {{color2}}
              </td>
            </tr>
            <tr>
              <td>
                Size:
              </td>
              <td>
                {{size2}}
              </td>
            </tr>

          </table>
        </div>
      </div>
    </div>



    <cml:radios label="Are these items variations of the same product?" value="varations" validates="required" gold="true">
      <cml:radio label="Yes" value="Yes"/>
      <cml:radio label="No" value="No"/>
    </cml:radios>

    '''
    job = PREDEFINED_JOBS['make_input_output_input_fields'][pytest.env]

    make = Make(API_KEY)
    res = make.get_output_required_fields(jobs=[job])
    assert res.status_code == 200
    input_fields = res.json_response[0][str(job)]['input_fields']
    output_fields = res.json_response[0][str(job)]['output_fields']

    assert input_fields == [
                            "img_url1",
                            "price1",
                            "color1",
                            "size1",
                            "img_url2",
                            "price2",
                            "color2",
                            "size2"
                        ]

    assert output_fields == {
                "are_these_items_variations_of_the_same_product": "String",
                "are_these_items_variations_of_the_same_product:confidence": "Float"
            }


@allure.severity(allure.severity_level.NORMAL)
def test_jobs_no_input_fields():
    '''
    <div class="html-element-wrapper">Show data to contributors here</div>
    <cml:radios label="Ask question here:" validates="required" gold="true">
      <cml:radio label="First option" value="first_option" />
      <cml:radio label="Second option" value="second_option" />
    </cml:radios>
    '''
    job = PREDEFINED_JOBS['make_input_output_no_input_fields'][pytest.env]

    make = Make(API_KEY)
    res = make.get_output_required_fields(jobs=[job])
    assert res.status_code == 200
    input_fields = res.json_response[0][str(job)]['input_fields']
    output_fields = res.json_response[0][str(job)]['output_fields']

    assert input_fields == []

    assert output_fields == {
                "ask_question_here": "String",
                "ask_question_here:confidence": "Float"
            }
