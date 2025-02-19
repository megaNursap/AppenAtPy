"""
Request DPR UI Smoke Test
"""
import datetime
import time

from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.regression_ac_reports, pytest.mark.regression_ac, pytest.mark.ac_report]

USER_NAME = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
TODAY = (datetime.date.today()).strftime("%m/%d/%Y")
DAY = (datetime.date.today()).day


@pytest.fixture(scope="module")
def login(app):
    app.ac_user.login_as(user_name=USER_NAME, password=PASSWORD)


@pytest.mark.dependency()
def test_open_dpr_page(app, login):
    app.navigation.click_link('Partner Home')
    app.navigation.click_link('Falcon')
    app.navigation.switch_to_frame("page-wrapper")
    app.dpr.find_reports(owner="All user's reports")
    app.verification.text_present_on_page("Daily Performance Report")
    app.verification.text_present_on_page("FILE ID")
    app.verification.text_present_on_page("REPORT TYPE")
    app.verification.text_present_on_page("TEMPLATE NAME")
    app.verification.text_present_on_page("REPORT DATE")
    app.verification.text_present_on_page("CREATED AT")
    app.verification.text_present_on_page("STATUS")


@pytest.mark.dependency(depends=["test_open_dpr_page"])
def test_report_order_by(app, login):
    "Verify that user can order reports by Program, Report date, Creation and Status"
    app.dpr.find_reports(program='', status='')

    app.dpr.sort_dpr_list_by('template name')
    time.sleep(10)
    current_reports = app.dpr.get_all_reports_from_dpr_list()
    time.sleep(2)
    programs = [x['name'] for x in current_reports]
    assert programs == sorted(programs)

    app.dpr.sort_dpr_list_by('template name')
    time.sleep(10)
    current_reports = app.dpr.get_all_reports_from_dpr_list()
    programs = [x['name'] for x in current_reports]
    assert programs == sorted(programs, reverse=True)

    app.dpr.sort_dpr_list_by('created at')
    time.sleep(10)
    current_reports = app.dpr.get_all_reports_from_dpr_list()
    creation_dates = [x['create_date'] for x in current_reports]
    assert creation_dates == sorted(creation_dates)

    # app.dpr.sort_dpr_list_by('CREATION')
    # current_reports = app.dpr.get_all_reports_from_dpr_list()
    # creation_dates = [x['create_date'] for x in current_reports]
    # assert creation_dates == sorted(creation_dates, reverse=True)

    app.dpr.sort_dpr_list_by('status')
    time.sleep(10)
    current_reports = app.dpr.get_all_reports_from_dpr_list()
    status = [x['status'] for x in current_reports]
    assert status == sorted(status)

    app.dpr.sort_dpr_list_by('status')
    time.sleep(10)
    current_reports = app.dpr.get_all_reports_from_dpr_list()
    time.sleep(2)
    status = [x['status'] for x in current_reports]
    assert status == sorted(status, reverse=True)
# TODO Report date


# @pytest.mark.dependency(depends=["test_open_dpr_page"])
# def test_filter_reports_by_program(app, login):
#     "Verify that user can filter reports by Program name"
#     app.dpr.find_reports(program='', status='')
#     no_filters = app.dpr.get_all_reports_from_dpr_list()
#
#     app.dpr.find_reports(program='CCC Labeling')
#     filter_program_name = app.dpr.get_all_reports_from_dpr_list()
#     assert len(list(filter(lambda x: x['name']=='CCC Labeling', filter_program_name))) == len(filter_program_name)
#
#     app.dpr.find_reports(program='Labeling')
#     filter_part_of_program_name = app.dpr.get_all_reports_from_dpr_list()
#     assert len(list(filter(lambda x: 'Labeling' in x['name'], filter_part_of_program_name))) == len(filter_part_of_program_name)
#
#     assert len(no_filters) >= len(filter_program_name)
#     assert len(no_filters) >= len(filter_part_of_program_name)

@pytest.mark.dependency(depends=["test_open_dpr_page"])
def test_filter_reports_by_status(app, login):
    "Verify that user can filter reports by Status"
    app.dpr.find_reports(program='', status='')

    for _status in ['Processing', 'Ready', 'Downloaded', 'Failed']:
        app.dpr.find_reports(status=_status)
        report_with_status = app.dpr.get_all_reports_from_dpr_list()
        time.sleep(3)
        assert len(list(filter(lambda x: x['status'] == _status, report_with_status))) == len(report_with_status)


@pytest.mark.dependency(depends=["test_open_dpr_page"])
def test_filter_reports_by_status_and_program(app, login):
    "Verify that user can filter reports by Status and Program"
    app.dpr.find_reports(program='', status='')
    all_reports = app.dpr.get_all_reports_from_dpr_list()

    random_report = random.choice(all_reports)

    _name = random_report['name']
    _status = random_report['status']

    app.dpr.find_reports(program=_name, status=_status)
    filter_reports = app.dpr.get_all_reports_from_dpr_list()
    assert len(list(filter(lambda x: x['status'] == _status and _name in x['name'] , filter_reports))) == len(filter_reports)


@pytest.mark.dependency(depends=["test_open_dpr_page"])
def test_cancel_report_generation(app, login):
    app.dpr.click_generate_new_report()
    app.verification.text_present_on_page("DPR - V1 Report Configuration")
    app.verification.text_present_on_page("Choose Report Template")
    app.verification.text_present_on_page("Start Date")
    app.verification.text_present_on_page("End Date")
    app.verification.text_present_on_page("Template Name")
    print("DAY",DAY)
    app.dpr.new_report_configuration(enddate=int(DAY), program='Civic Classification')
    app.navigation.click_btn('Cancel')

    app.verification.text_present_on_page("Daily Performance Report")


@pytest.mark.dependency(depends=["test_cancel_report_generation"])
def test_create_new_dpr(app, login):
    app.dpr.click_generate_new_report()
    time.sleep(4)
    app.dpr.new_report_configuration(enddate=int(DAY), program='Civic Classification')

    app.verification.text_present_on_page("Civic Classification - FB")
    app.verification.text_present_on_page("Consistency Agreement")
    app.verification.text_present_on_page("Productivity (Workload)")
    app.verification.text_present_on_page("Workload Overall")
    app.verification.text_present_on_page("AHT Sec")

    app.navigation.click_btn('Request DPR - V1 Report')
    app.verification.text_present_on_page("Daily Performance Report")


@pytest.mark.dependency(depends=["test_create_new_dpr"])
def test_search_dpr(app, login):
    app.dpr.find_reports(program='Civic Classification', status="Processing")

    current_reports = app.dpr.get_all_reports_from_dpr_list()

    #assert len(current_reports) == 1
    assert current_reports[0]['name'] == 'Civic Classification'
    assert current_reports[0]['status'] == 'Processing'
#     TODO more assertions
    global report_id
    report_id = current_reports[0]['id']


@pytest.mark.dependency(depends=["test_open_dpr_page"])
def test_filter_reports_by_creator(app, login):
    "Verify that user can filter reports by Creator"
    app.dpr.find_reports(program='', status='')

    # not working - bug!
    full_name = get_user_info('test_ui_account')['full_name']
    # app.dpr.find_reports(program=full_name)
    #
    # creator_filters = app.dpr.get_all_reports_from_dpr_list()
    # assert len(creator_filters)>0
    # assert len(list(filter(lambda x: full_name in x['create_author'], creator_filters))) == len(creator_filters)

    _name = full_name.split(' ')[0]
    app.dpr.find_reports(program=_name)

    creator_filters = app.dpr.get_all_reports_from_dpr_list()
    assert len(creator_filters)>0
    assert len(list(filter(lambda x: _name in x['create_author'], creator_filters))) == len(creator_filters)


@pytest.mark.dependency(depends=["test_open_dpr_page"])
def test_change_report_status(app, login):
    time.sleep(60)
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    report_info = app.dpr.get_report_info_by(search_field='id', value=report_id)
    assert report_info['id']==report_id
    assert report_info['status'] == 'Ready'

    app.dpr.click_download_for_report(search_field='id', value=report_id)

    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")

    report_info = app.dpr.get_report_info_by(search_field='id', value=report_id)
    assert report_info['id'] == report_id
    assert report_info['status'] == 'Downloaded'

#
# TODO  write new function for getting program details; ui was changed
# @pytest.mark.dependency(depends=["test_open_dpr_page"])
# @pytest.mark.ac_ui_smoke
# def test_program_content(app, login):
#     app.navigation.refresh_page()
#     app.navigation.switch_to_frame("page-wrapper")
#
#     app.dpr.click_generate_new_report()
#
#     app.dpr.new_report_configuration(enddate=TODAY, program='Golden Program')
#
#     result = app.dpr.get_program_details()
#     assert result == [{'PROJECT NAME': 'Project1218',
#                        # 'EFFECTIVENESS': 'Metric 1\nMetric 2',
#                        'EFFECTIVENESS': '',
#                        'WORKFLOW': 'Workflow 1218-1\nWorkflow 1218-2',
#                        'AC PROJECT ID': '1218\n1218'},
#                       {'PROJECT NAME': 'Workflow 347-1',
#                        # 'EFFECTIVENESS': 'Metric 1\nMetric 3',
#                        'EFFECTIVENESS': '',
#                        'WORKFLOW': 'Workflow 347-1',
#                        'AC PROJECT ID': '347'},
#                       {'PROJECT NAME': 'Workflow 347-2',
#                        # 'EFFECTIVENESS': 'Metric 1\nMetric 3',
#                        'EFFECTIVENESS': '',
#                        'WORKFLOW': 'Workflow 347-2',
#                        'AC PROJECT ID': '347'}]
#

@pytest.mark.dependency(depends=["test_open_dpr_page"])
def test_dpr_show_items(app, login):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")
    app.dpr.find_reports(owner="All user's reports")
    all_reports = app.dpr.get_num_of_all_reports()

    for reports_num in [5, 10, 15,20]:
        app.dpr.set_up_show_items(reports_num)
        expected_reports = min(reports_num, all_reports)
        reports_on_page = app.dpr.get_all_reports_from_dpr_list()
        assert len(reports_on_page) <= expected_reports
        app.verification.text_present_on_page("Showing 1-%s of" % len(reports_on_page))


@pytest.mark.dependency(depends=["test_open_dpr_page"])
def test_dpr_pagination(app, login):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")

    all_reports = app.dpr.get_num_of_all_reports()

    app.dpr.set_up_show_items(10)
    actual_pages = app.dpr.get_num_pages()
    expected_pages = all_reports//10 + 1 if all_reports%10 >0 else 0
    assert expected_pages == int(actual_pages)

    time.sleep(2)
    app.dpr.set_up_show_items(15)
    all_reports = app.dpr.get_num_of_all_reports()
    actual_pages = app.dpr.get_num_pages()
    expected_pages = all_reports//15 + 1 if all_reports%15 >0 else 0
    assert expected_pages ==int(actual_pages)

    active_page = app.dpr.get_active_page_number()
    assert active_page == '1'

    #There is no difference in xpath for Active page or Inactive page, so, this cannot be verified
    '''
    app.dpr.click_pagination_btn('next')
    app.dpr.click_pagination_btn('next')

    active_page = app.dpr.get_active_page_number()
    assert active_page == '3'

    app.dpr.click_pagination_btn('previous')
    app.dpr.click_pagination_btn('previous')

    active_page = app.dpr.get_active_page_number()
    assert active_page == '1'
    '''

@pytest.mark.dependency(depends=["test_open_dpr_page"])
def test_report_content(app, login):
    app.navigation.refresh_page()
    app.navigation.switch_to_frame("page-wrapper")

    app.dpr.click_generate_new_report()
    time.sleep(15)

    app.dpr.new_report_configuration(enddate=DAY, program='Civic Classification')

    # program_details = app.dpr.get_program_details()

    app.navigation.click_btn('Request DPR - V1 Report')

    time.sleep(120)

    app.dpr.find_reports(program='Civic Classification')
    all_reports = app.dpr.get_all_reports_from_dpr_list()
    report_id = all_reports[0]['id']
    app.dpr.click_download_for_report(search_field='index', value=0)
    time.sleep(3)

    file_names = []
    # Iterate directory
    for file in os.listdir(app.temp_path_file):
        # check only specific files
        if file.endswith(f'{report_id[-4:]}.xlsx'):
            file_names.append(file)

    assert len(file_names), "file has not been found"

    file_name = str(app.temp_path_file) + "/" + file_names[0]

    _df = pd.read_excel(file_name, header=1)

    headers = _df.columns.values.tolist()
    start_date_column = headers.index('WTD') + 1
    actual_days_in_report = headers[start_date_column:start_date_column + 7]

    start_day_report = (datetime.datetime.today() + datetime.timedelta(days=-6)).strftime("%m/%d/%Y")
    expected_dates = pd.date_range(start_day_report, TODAY, freq='d').to_pydatetime().tolist()

    assert expected_dates == actual_days_in_report
    assert _df['Civic Classification'].dropna().tolist()[:4] == ['Effectiveness', 'Consistency Agreement', 'Workload', 'Workload Overall']
    assert _df['Unnamed: 2'].dropna().tolist()[:3] == ['Civic Classification - FB', 'Civic Classification - IG', 'Civic Classification - FB']


# 1 filter by partial programm name
# Golden Program - effectiveness empty and not able to generate report - error
