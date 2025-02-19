from adap.api_automation.utils.data_util import get_data_file
from adap.e2e_automation.services_config.job_api_support import create_job_from_config_api

from adap.e2e_automation.services_config.contributor_ui_support import get_judgments

api_key = "8WizGTstVP1sxCpHCzRP"
ENV = 'qa'

sample_file = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_02_sample_100.csv",
                            env='qa')



config = {
    # 'env': ENV,
    # 'user': {
    #     'api_key': api_key
    # },
    "job": {
        "options": {
            "track_clones": "true",
            "flag_on_rate_limit": "true",
            "warn_at": "90",
            "logical_aggregation": "true",
            "approved": "true",
            "after_gold": "10",
            "max_hits_on_turk": "1000",
            "webhook_attempts": 0,
            "keywords": "CastingWords CW Match Mismatch Text Audio",
            "reject_at": "80",
            "calibrated_unit_time": 30,
            "dynamic_judgment_fields": [
                "",
                "recording_text_match"
            ],
            "req_ttl_in_seconds": 1800,
            "include_unfinished": "true",
            "no_reject": "true"
        },
        "title": "[Fixed] Decide If Audio And Text Are Identical",
        "project_number": "PN000112",
        "judgments_per_unit": 1,
        "units_per_assignment": 10,
        "gold_per_assignment": 1,
        "minimum_account_age_seconds": 0,
        "execution_mode": "worker_ui_remix",
        "payment_cents": 20,
        "design_verified": "true",
        "public_data": "false",
        "variable_judgments_mode": "auto_confidence",
        "max_judgments_per_unit": 4,
        "expected_judgments_per_unit": 2,
        "min_unit_confidence": 0.99,
        "units_remain_finalized": "true",
        # "auto_order_timeout": 10,
        # "auto_order_threshold": 9,
        # "auto_order": "true",
        "language": "en",
        "desired_requirements": {},
        "assignment_duration": 1800,
        "instructions": "<h2>Overview</h2>\n<p>We need you to help us verify transcriptions of short audio files. With your help, we can improve our speech recognition technology. Your task is to listen to a number of audio recordings and tell us whether the spoken words EXACTLY match the text shown.</p>\n<h2>Process</h2>\n<ol><li>Read the given Text</li><li>Play and listen to the audio clip.<ul><li><span style=\"color: #E30909; font-size: 16px;\"><strong>The audio may not play correctly in Internet Explorer</strong></span>. Please use Firefox, Chrome, or Safari.</li></ul></li><li>Do they match?<ul><li>Click YES If text and audio are exactly the same, click YES</li><li>Click NO if they do not</li><li>Click CANT TELL if you can't understand what the user is saying, maybe it is garbled, or not English, or the audio recording has any words that are cut off.</li></ul></li></ol>\n<div class=\"cye-lm-tag\" id=\"audiovalidation_rules\"><h2>Audio Validation Rules</h2><p>Check <strong>YES</strong> if:</p><ul><li>Text and audio are identical.</li><li>If the text says <strong>{SELECT YES IF THIS RECORDING CONTAINS NO MEANINGFUL ENGLISH SPEECH}</strong> and there is no meaningful speech in the audio clip</li></ul><p>Check <strong>NO</strong> if:</p><ul><li>Important words, names or numbers are in text or audio, but not the other: <strong>Google Matt</strong> vs <strong>Google Matt Damon</strong>.</li><li>Important words, names or numbers are different: <strong>Google Matt Dillon</strong> vs <strong>Google Matt Damon</strong>.</li><li>Important words or numbers are said in the different order: <strong>one two three</strong> vs <strong>one three two</strong>.</li><li>Small unimportant words are in text or audio, but not the other: <strong>Walk my dog</strong> vs <strong>Walk dog</strong>.</li><li>Small unimportant words different: <strong>Walk my dog</strong> vs <strong>Walk the dog</strong>.</li><li>Text word is slightly misspelled, but you can still read it: <strong>Go to Sun Frincisco</strong>.</li><li>Contraction is wrong, e.g. user says <strong>I have</strong> and text is <strong>I've</strong></li></ul><p>Check <strong>CAN'T TELL&nbsp;</strong>if:</p><ul><li>If <strong>any&nbsp;</strong>of the user's speech is interrupted or cut off, recording doesn't contain complete phrase or utterance.<ul><li>Even if user repeats phrase, if <strong>any</strong> part of their speech is cut off, check Can't Tell.</li></ul></li><li>There is no audio or you can barely hear it. (check your volume level by listening to several audio clips).</li><li>There are loud disruptive background noises</li><li>There is another speaker, speaking loudly enough to confuse what is being said vs the text you see</li><li>If you have to listen to recording multiple times, and you can't understand exactly what the user is saying.</li><li>The only audio is some unrelated background talking, (pocket dial)</li><li>Text and audio are completely different languages: Text: <strong>English</strong> vs Audio: <strong>French</strong>. (foreign names are okay)<br /></li></ul></div>\n<h3>Thank You!</h3>\n<p>With your contribution, you’re helping us create the best speech recognition technology in the world.<br /><strong>You are ready to begin.</strong><br /><br /></p>\n",
        "cml": "  \n<div class=\"row-fluid scroll_widget-benchmark\">\n  <div class=\"span5 scroll_widget-container panel panel-primary\">\n    <div class=\"scroll_widget-scroller\">\n      <div class=\"panel-heading\">\n        <h3 class=\"panel-title\">Text and Audio</h3>\n      </div>\n      <div class=\"panel-body\">\n        <dl class=\"dl-horizontal\">\n          <p style=\"font-size:larger;font-weight:bold; color:#0e5f14;\">\n                {{display_text}}\n              </p>\n          \n          <audio src=\"{{audio_link}}\" preload=\"none\" controls=\"controls\"></audio>\n          \n        </dl>\n      </div>\n    </div>\n  </div>\n  \n  <div class=\"span7 panel panel-primary\">\n    <div class=\"panel-heading\">\n      <h3 class=\"panel-title\">Are audio and text exactly the same?</h3>\n    </div>\n    <div class=\"panel-body\">\n      <cml:group name=\"\">\n        <cml:radios label=\"\" validates=\"required\" name=\"recording_text_match\" aggregation=\"agg\" gold=\"true\"> \n          <cml:instructions>Check one of these.</cml:instructions>\n          <cml:radio label=\"NO.  There is something different about them.\" value=\"0\"></cml:radio>\n          <cml:radio label=\"YES. 100% identical.\" value=\"1\"></cml:radio>\n          <cml:radio label=\"CAN'T TELL what the user is saying, or the user’s speech is cut off.\" value=\"2\"></cml:radio>\n        </cml:radios>   \n        <button type=\"button\" class=\"btn btn-mini btn-info desc_button\" data-container=\"body\" data-toggle=\"popover\" data-placement=\"right\">\n        Audio Validation Rules\n      </button>  \n      </cml:group>\n    </div>\n  </div>\n</div>\n\n\n\n\n\n\n\n\n\n",
        "js": "require(['jquery-noconflict', 'bootstrap-popover', 'bootstrap-tooltip', 'bootstrap-tab'], function(jQuery) {\n   //Ensure MooTools is where it must be\n  Window.implement('$', function(el, nc){\n    return document.id(el, nc, this.document);\n  });\n  \n  \n  //==================================================\n  //Constants\n  //==================================================\n  var $ = window.jQuery;\n\n\n  $(document).ready(function()\n  { \n    var audiovalidation_rules_divID = '#audiovalidation_rules';\n    var rules_content = $(audiovalidation_rules_divID).html();\n    console.log(rules_content);\n    $('[data-toggle=\"popover\"]').popover({ \n      html : true,\n      content: rules_content\n    });\n\n  });\n  // end scroller widget\n  \n});",
        "css": ".popover{\n    max-width:80%;\n}\n\n.spelling-suggestion-content .row-fluid {\n  font-size: 13px;\n  margin-top: 6px;\n}\n\n.spelling-suggestion-content .row-fluid .span3 {\n  word-wrap: break-word;\n}\n\n.spelling-suggestion-content .row-fluid .spelling-suggestion-headers {\n  font-size: 16px;  \n}\n\n.pad-me-15 {\n  padding: 15px;\n}\n\n.cml-blue {\n  color: #00A6E0;\n}\n\n.flt-center {\n  text-align: center;\n}\n\n.well_background {\n  background-color: #ffffff;\n}\n\n.colored_well_background {\n  background-color: #645188;\n}\n\n.cml-green {\n  color: #228B22;\n}\n.cml-darkgreen {\n  color: #004F00;\n}\n.cml-red {\n  color: red;\n}\n\n.keyword {\n  color: #000000;\n}\n\n.cml-white {\n  color: #F8F8FF;\n}\n\n.back-black {\n  background-color: #000000;\n}\n\n.back-green {\n  background-color: #228B22;\n}\n\n.back-red {\n  background-color: red;\n}\n\n.well_task_ui {\nbackground-color: #f5f5f5;\nborder:2px dashed;\nborder-color:#CCCC9F;\n}\n\n.well_task_ui_reminders {\n background: #cedce7; /* Old browsers */\nbackground: -moz-radial-gradient(center, ellipse cover,  #cedce7 0%, #596a72 100%); /* FF3.6+ */\nbackground: -webkit-gradient(radial, center center, 0px, center center, 100%, color-stop(0%,#cedce7), color-stop(100%,#596a72)); /* Chrome,Safari4+ */\nbackground: -webkit-radial-gradient(center, ellipse cover,  #cedce7 0%,#596a72 100%); /* Chrome10+,Safari5.1+ */\nbackground: -o-radial-gradient(center, ellipse cover,  #cedce7 0%,#596a72 100%); /* Opera 12+ */\nbackground: -ms-radial-gradient(center, ellipse cover,  #cedce7 0%,#596a72 100%); /* IE10+ */\nbackground: radial-gradient(ellipse at center,  #cedce7 0%,#596a72 100%); /* W3C */\nfilter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#cedce7', endColorstr='#596a72',GradientType=1 ); /* IE6-9 fallback on horizontal gradient */\n\n\n\n}\n\n.unit-tabs > .active > a, .unit-tabs > .active > a:hover { \noutline: 0;\ncolor: #ffffff;\nbackground-color: #DB4105;\nborder: 1px solid #ddd;\nborder-bottom-color: transparent;\ncursor: default;\n}\n\n.panel {\n  padding-left: 15px;\n  margin-bottom: 20px;\n  background-color: #ffffff;\n  border-radius: 4px;\n  -webkit-box-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);\n  box-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);\n}\n\n.panel-heading {\n  padding: 10px 15px;\n  margin: -15px -15px 15px;\n  font-size: 17.5px;\n  font-weight: 500;      \n  background-color: #2C3E50;\n  border-bottom: 1px solid #dddddd;\n}\n\n.panel-footer {\n  padding: 10px 15px;\n  margin: 15px -15px -15px;\n  background-color: #f5f5f5;\n  border-top: 1px solid #dddddd;\n  border-bottom-right-radius: 3px;\n  border-bottom-left-radius: 3px;\n}\n\n.panel-primary {\n  border-color: #ff6400;\n}\n\n.panel-primary .panel-heading{\n  color: #ff6400;\n  background-color: #33332D;\n  border-color: #000000;\n}\n\n.panel-primary .panel-heading .panel-title{\n  color: #ffffff;\n  font-size: 20px;\n  font-weight:bold;\n}\n\n\n.scroll_widget-container {\n  position:relative;\n  width:100%;\n}\n\n.scroll_widget-scroller {\n  position:relative;\n  max-width:100%;\n}",
        "dynamic_judgment_fields": [
            "",
            "recording_text_match"
        ],
        "gold": {
            "recording_text_match": "recording_text_match_gold"
        },
        "units_count": 100,
        "golds_count": 0,
        "judgments_count": 10,
        "worker_ui_remix": "true",
        "crowd_costs": 0,
        "quiz_mode_enabled": "false",
        "completed": "false",
        "fields": {
            "recording_text_match": "agg"
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


def test_create_job_02_01():
    job_id = create_job_from_config_api(config, ENV, api_key)

    # if (config['launch'] == 'true') and (config['judgments']['get_judgments'] == 'true'):
    #     get_judgments(job_id, config)


if __name__ == '__main__':
    test_create_job_02_01()