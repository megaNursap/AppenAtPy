from adap.api_automation.utils.data_util import get_data_file
from adap.e2e_automation.services_config.job_api_support import create_job_from_config_api

from adap.e2e_automation.services_config.contributor_ui_support import get_judgments

api_key = ""
ENV = 'qa'

sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_03_sample_25_rose.csv",
                            env='qa')

config = {
    # 'env': ENV,
    # 'user': {
    #     'api_key': api_key
    # },
    "job": {
        "options": {
            "flag_on_rate_limit": "true",
            "include_unfinished": "true",
            "logical_aggregation": "true",
            "req_ttl_in_seconds": 1800
        },
        "title": "High Priority Review Job (Mature Content)",
        "project_number": "PN000112",
        "judgments_per_unit": 1,
        "units_per_assignment": 5,
        "pages_per_assignment": 1,
        "gold_per_assignment": 1,
        "execution_mode": "worker_ui_remix",
        "payment_cents": 10,
        "design_verified": "true",
        "public_data": "false",
        "variable_judgments_mode": "none",
        "units_remain_finalized": "true",
        # "auto_order_timeout": 10,
        # "auto_order_threshold": 4,
        "state": "unordered",
        # "auto_order": "true",
        "language": "en",
        "minimum_requirements": {
            "skill_scores": {
                "level_1_contributors": 1
            },
            "min_score": 1
        },
        "assignment_duration": 1800,
        "instructions": "<h1>\n  <strong>Overview</strong>\n</h1>\n<p>Help us determine if we should keep or suspend these images. With each option to either keep or suspend, you will have multiple options to flag. These flags are internal only and can be used to filter and help the team understand more about this image.</p>\n<hr/>\n\n<h1>\n  <strong>Steps</strong>\n</h1>\n<ol>\n  <li>Examine the image.</li>\n  <li>Decide whether to <strong>keep</strong> or <strong>suspend</strong> the image, then select accordingly.</li>\n  <li>Once you have chosen to keep or suspend, you will be prompted to include flags.</li>\n</ol>\n<h2>\n  <strong>Explanations of the flags are as follows:</strong>\n</h2>\n<ul>\n  <li>Keep<ul><li><strong>Mature - Language</strong>: Language is permitted on Society, but should be marked as such. (ie. fuck, shit, bitch(es), dick(s), pussy, cunt(s), slut, whore, tits, balls, ass, asshole, cock, twat)</li><li><strong>Mature - Nudity</strong>: Nudity is permitted on Society6, but should be marked as such. Designs featuring nudity that are overtly sexual or portray a sex act taking place should be removed.</li><li><strong>Mature - Illegal Activity</strong>: Some designs that feature drugs or drug use may be permitted on Society6, but should be marked as such.</li><li><strong>Mature - Firearms</strong>:</li><li><strong>Curate</strong>: Designs that should be marked curate are completely original works.</li><li><strong>Blank</strong>: Designs that should be marked with BLANK may be original designs, but may also be stock photography. These designs do not include violations of our terms, but may not align with our brand standards. </li></ul></li>\n  <li>Suspend<ul><li><strong>Logo</strong>: Logos cannot be included in designs sold on Society6 (ie. Nike, Gucci, Supreme, Microsoft, Apple, Louis Vuitton, Adidas). </li><li><strong>Character / IP</strong>: Designs and fan art featuring characters from existing properties cannot be sold on Society (ie. Disney characters, Marvel characters, etc.)</li><li><strong>Celebrity</strong>: Celebrity likenesses cannot be sold on Society6 without the permission of the subject. Certain public figures may be exempt to this rule (ie. Ruth Bader Ginsberg, Frida Kahlo, Donald Trump).</li><li><strong>Too Mature</strong>: Society6 does not permit designs that are obscene, pornographic, explicity sexual, depict sexual violence, or are child exploitative.</li><li><strong>Offensive</strong>: Society6 does not allow designs that are derogatory, racist, religiously offensive, hateful, violent, or discriminatory. Designs that feature illegal activity should also be marked as offensive.</li><li><strong>Art Theft</strong>: Society6 does permit the sale of art that is stolen from another Society6 artist or otherwise. Note: Some masterworks may be part of the public domain and in some cases may be permitted.</li><li><strong>Other</strong>: Other is used to refer to a design that should be removed for a reason other than those listed above.</li></ul></li>\n</ul>\n<hr/>\n\n<h1>Examples</h1>\n<table style=\"width: 100%;\">\n  <tbody>\n    <tr>\n      <td style=\"width: 50.0000%;\">\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915146413-untitled\" style=\"width: 300px;\"/>\n      </td>\n      <td style=\"width: 50.0000%;\">\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915160024-untitled\" style=\"width: 382px;height: 253.515px;\"/>\n      </td>\n    </tr>\n    <tr>\n      <td>\n        <br/>\n        <br/>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915181465-untitled\" style=\"width: 300px;\"/>\n      </td>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915193050-untitled\" style=\"width: 403px;height: 258.544px;\"/>\n      </td>\n    </tr>\n    <tr>\n      <td>\n        <br/>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915209451-untitled\" style=\"width: 300px;\"/>\n      </td>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915221251-untitled\" style=\"width: 413px;height: 243.82px;\"/>\n        <br/>\n      </td>\n    </tr>\n    <tr>\n      <td>\n        <br/>\n      </td>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915293504-untitled\" style=\"width: 401px;height: 259.461px;\"/>\n      </td>\n    </tr>\n    <tr>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915263293-untitled\" style=\"width: 300px;\"/>\n      </td>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915275542-untitled\" style=\"width: 413px;height: 240.216px;\"/>\n      </td>\n    </tr>\n    <tr>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915306916-untitled\" style=\"width: 300px;\"/>\n      </td>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915319005-untitled\" style=\"width: 413px;height: 259.514px;\"/>\n      </td>\n    </tr>\n    <tr>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915438618-untitled\" style=\"width: 300px;\"/>\n      </td>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915346242-untitled\" style=\"width: 413px;height: 252.763px;\"/>\n      </td>\n    </tr>\n    <tr>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915448921-untitled\" style=\"width: 300px;\"/>\n      </td>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915356462-untitled\" style=\"width: 413px;height: 272.408px;\"/>\n      </td>\n    </tr>\n    <tr>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915459092-untitled\" style=\"width: 300px;\"/>\n      </td>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915367398-untitled\" style=\"width: 413px;height: 282.756px;\"/>\n      </td>\n    </tr>\n    <tr>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915470583-untitled\" style=\"width: 300px;\"/>\n      </td>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915378629-untitled\" style=\"width: 413px;height: 284.477px;\"/>\n      </td>\n    </tr>\n    <tr>\n      <td>\n        <br/>\n      </td>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915399426-untitled\" style=\"width: 413px;height: 274.727px;\"/>\n      </td>\n    </tr>\n    <tr>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915483164-untitled\" style=\"width: 300px;\"/>\n      </td>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915409439-untitled\" style=\"width: 413px;height: 262.561px;\"/>\n      </td>\n    </tr>\n    <tr>\n      <td>\n        <br/>\n      </td>\n      <td>\n        <img class=\"fr-dib\" src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1554915419041-untitled\" style=\"width: 386px;height: 250.402px;\"/>\n      </td>\n    </tr>\n  </tbody>\n</table>\n<p>\n  <br/>\n</p>\n",
        "cml": "<div class=\"row-fluid\">\n  <div class=\"span6\">\n    <img src=\"{{image_url}}\"/>\n  </div>\n  <div class=\"span6\">\n    <cml:radios name=\"keep_suspend\" label=\"Should we keep or suspend this image?\" validates=\"required\">\n      <cml:radio value=\"keep\" label=\"Keep\"/>\n      <cml:radio value=\"suspend\" label=\"Suspend\"/>\n    </cml:radios>\n    <cml:checkboxes name=\"keep_types\" label=\"Do you want to add in any flags?\" validates=\"required\" only-if=\"keep_suspend:[keep]\" exact=\"true\">\n      <cml:checkbox value=\"mature_language\" label=\"Mature: Language\"/>\n      <cml:checkbox value=\"mature_nudity\" label=\"Mature: Nudity\"/>\n      <cml:checkbox value=\"mature_illegal\" label=\"Mature: Illegal Activity\"/>\n      <cml:checkbox value=\"mature_firearms\" label=\"Mature: Firearms / Weapons\"/>\n      <cml:checkbox value=\"curate\" label=\"Curate!\"/>\n      <cml:checkbox value=\"none\" label=\"None\"/>\n    </cml:checkboxes>\n    <cml:checkboxes name=\"suspend_types\" label=\"Why are you suspending this image?\" validates=\"required\" only-if=\"keep_suspend:[suspend]\" exact=\"true\">\n      <cml:checkbox value=\"logo\" label=\"Logo\"/>\n      <cml:checkbox value=\"character\" label=\"Character / IP\"/>\n      <cml:checkbox value=\"celebrity\" label=\"Celebrity\"/>\n      <cml:checkbox value=\"too_mature\" label=\"Too Mature\"/>\n      <cml:checkbox value=\"offensive\" label=\"Offensive\"/>\n      <cml:checkbox value=\"art_theft\" label=\"Art Theft\"/>\n      <cml:checkbox value=\"other\" label=\"Other\"/>\n    </cml:checkboxes>\n  </div>\n</div>",
        "js": "",
        "css": "",
        "dynamic_judgment_fields": [
            "keep_suspend",
            "keep_types",
            "suspend_types"
        ],
        "gold": {
            "keep_suspend": "keep_suspend_gold",
            "keep_types": "keep_types_gold",
            "_keep_types_gold_exact": "true",
            "suspend_types": "suspend_types_gold",
            "_suspend_types_gold_exact": "true"
        },
        "units_count": 0,
        "golds_count": 0,
        "judgments_count": 0,
        "worker_ui_remix": "true",
        "crowd_costs": 0,
        "quiz_mode_enabled": "false",
        "completed": "false",
        "fields": {
            "keep_suspend": "agg",
            "keep_types": "agg",
            "suspend_types": "agg"
        },
        "order_approved": "true"
    },
    "data_upload": [sample_file],
    "test_questions": 'false',
    "launch": False,
    "judgments":{
        "get_judgments": 'true',
        "contributors":{"qa+qa_automation9@figure-eight.com":"yvYfUE8nFfQwebwCTLG9!"}
    }
}


def test_create_job_03_02():
    job_id = create_job_from_config_api(config, ENV, api_key)

    # if (config['launch'] == 'true') and (config['judgments']['get_judgments'] == 'true'):
    #     get_judgments(job_id, config)


if __name__ == '__main__':
    test_create_job_03_02()
