import time
import allure
import datetime
from faker import Faker


def generate_project_name():
    # with allure.step("Generate project name"):
        faker = Faker()
        dt = datetime.datetime.now()
        month_day_year_with_slash = dt.strftime("%s%d/%m/%Y")
        month_day_year_no_delim = dt.strftime("%s%d%m%Y")

        company_name = faker.company()
        company_name = company_name[0:min(len(company_name), 22)]
        zip_code = faker.zipcode()
        assert len(company_name) > 0, "Project name did not generated"
        # full_company_name = [(company_name + month_day_year_with_slash), zip_code + month_day_year_no_delim]
        name = f"{company_name} {dt.strftime('%d/%m/%Y')}"
        full_company_name = [name, name]

        print(f"Project name: {full_company_name}")
        assert len(full_company_name) > 0, "Full Project name did not generated"
        return full_company_name


def tomorrow_date(days=1, format_pattern="%m/%d/%Y"):
    return (datetime.date.today() + datetime.timedelta(days=days)).strftime(format_pattern)


print(generate_project_name())