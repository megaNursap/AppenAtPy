import pytest

mark_only_envs = pytest.mark.skipif(not pytest.running_in_preprod_subset, reason="Only enabled in preprod")

# pytestmark = [pytest.mark.sda, pytest.mark.regression_core, mark_only_envs]
#TODO fix QED-3400
urls = pytest.data.predefined_data['sda'][pytest.env]

@pytest.mark.parametrize(
    'team,unit_page_url',
    [
        ('s3', urls['s3_new_unit_url']),
        ('s3', urls['s3_judgable_unit_url']),
        ('azure', urls['azure_new_unit_url']),
        ('azure', urls['azure_judgable_unit_url'])
    ]
)
def test_sda_unit_view(app, team, unit_page_url):
    if team == 'azure' and pytest.env == 'integration':
        pytest.skip("No test data setup for Azure SDA in Integration")

    app.sda.sign_in_as(team)
    print(f"Unit page url {unit_page_url}")
    app.driver.get(unit_page_url)
    app.navigation.close_tour_guide_popup()
    app.sda.enter_unit_page_iframe()
    secure_img_src = app.sda.scroll_to_secure_img()
    job_window = app.driver.window_handles[0]
    app.navigation.open_page(secure_img_src)
    app.sda.verify_image(tag='img-alone')

    app.navigation.browser_back()
    app.navigation.switch_to_window(job_window)
    app.navigation.close_tour_guide_popup()
    app.sda.enter_unit_page_iframe()
    app.sda.verify_image(tag='img')

    app.sda.enter_shapes_iframe()
    app.sda.scroll_to_canvas()
    app.sda.verify_image(tag='shapes')

