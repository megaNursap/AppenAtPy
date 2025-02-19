
import random
from adap.api_automation.services_config.data_validation_service import *

JOB_ID = random.randint(1, 100000)

TEST_DATA = pytest.data.predefined_data['data_validation_api'].get(pytest.env)
if TEST_DATA:
    USER_ID = TEST_DATA['user_id']
    TEAM_ID = TEST_DATA['team_id']
    RP_USER_ID = TEST_DATA['rp_user_id']
    RP_TEAM_ID = TEST_DATA['rp_team_id']

rule_missing_job_id = {
    "user_id": USER_ID,
    "team_id": TEAM_ID,
    "rules": [
        {
            "name": "test_rule_name",
            "description": "test regex rule - punctuation",
            "rule": {
                "regex": "[,.?!]{2,}",
                "type": "REGEX_SEARCH"
            }
        }
    ]
}

rule_missing_user_id = {
    "job_id": JOB_ID,
    "team_id": TEAM_ID,
    "rules": [
        {
            "name": "test_rule_name",
            "description": "test regex rule - punctuation",
            "rule": {
                "regex": "[,.?!]{2,}",
                "type": "REGEX_SEARCH"
            }
        }
    ]
}

rule_missing_team_id = {
    "job_id": JOB_ID,
    "user_id": USER_ID,
    "rules": [
        {
            "name": "test_rule_name",
            "description": "test regex rule - punctuation",
            "rule": {
                "regex": "[,.?!]{2,}",
                "type": "REGEX_SEARCH"
            }
        }
    ]
}

rule_invalid_job_id = {
    "job_id": "abc",
    "user_id": USER_ID,
    "team_id": TEAM_ID,
    "rules": [
        {
            "name": "test_rule_name",
            "description": "test regex rule - punctuation",
            "rule": {
                "regex": "[,.?!]{2,}",
                "type": "REGEX_SEARCH"
            }
        }]
}

rule_invalid_team_id = {
    "job_id": str(JOB_ID),
    "user_id": USER_ID,
    "team_id": "123",
    "rules": [
        {
            "name": "test_rule_name",
            "description": "test regex rule - punctuation",
            "rule": {
                "regex": "[,.?!]{2,}",
                "type": "REGEX_SEARCH"
            }
        }]
}

rule_invalid_user_id = {
    "job_id": str(JOB_ID),
    "user_id": "123",
    "team_id": TEAM_ID,
    "rules": [
        {
            "name": "test_rule_name",
            "description": "test regex rule - punctuation",
            "rule": {
                "regex": "[,.?!]{2,}",
                "type": "REGEX_SEARCH"
            }
        }]
}

rule_missing_name = {
    "job_id": str(JOB_ID),
    "user_id": USER_ID,
    "team_id": TEAM_ID,
    "rules": [
        {
            "description": "test regex rule - punctuation",
            "rule": {
                "regex": "[,.?!]{2,}",
                "type": "REGEX_SEARCH"
            }
        }]
}

validate_rule_missing_job_id = {
    "name": "test",
    "value": "?!"
}

validate_rule_missing_name = {
    "job_id": 1614126,
    "value": "thsi is ok nasa CPU  è ?!"
}

validate_rule_missing_value = {
    "job_id": 1614126,
    "name": "test"
}

create_rule_payload = {
        "job_id": str(JOB_ID),
        "user_id": USER_ID,
        "team_id": TEAM_ID,
        "rules": [
            {
                "name": "test_name",
                "description": "Regex test rule",
                "rule": {
                    "regex": "[,.?!]{2,}",
                    "type": "REGEX_SEARCH"
                }
            },
            {
                "name": "test_name",
                "description": "Spell Check rule",
                "rule": {
                    "type": "LANGUAGE",
                    "lang": "en",
                    "locale": "us-variety",
                    "grammar_check": False,
                    "language_check": True,
                    "spell_check": True,
                    "coherence_check": False,
                    "spell_check_whitelists": []
                }
            }
        ]
    }

invalid_lang_locale_payload = {
  "job_id": JOB_ID,
  "user_id": USER_ID,
  "team_id": TEAM_ID,
  "rules": [
    {
      "name": "audio_transcription",
      "description": "Spell Check only rule",
      "rule": {
        "type": "LANGUAGE",
        "lang": "eng",
        "locale": "us-variety",
        "grammar_check": False,
        "language_check": True,
        "spell_check": True,
        "coherence_check": False,
        "spell_check_whitelists": [
          1
        ]
      }
    }
  ]
}

supported_languages = ["ar", "bg", "ca", "cs", "da", "de", "el", "en", "en-au-variety", "en-ca-variety", "en-gb-variety", "en-null-variety", "en-us-variety", "es", "et", "fa", "fi", "fr", "he", "hi", "hr", "hu", "id", "is", "it", "jp/ja", "ko", "lt", "lv", "nl", "no", "pl", "pt", "ro", "ru", "sk", "sq", "sr", "sv", "th", "tl", "tr", "uk", "vi", "zh", "zh-s-variety", "zh-t-variety"]


rp_create_rule_valid_payload={
  "rules": [
    {
      "name": "audio_transcription",
      "description": "Regex test rule",
      "rule": {
        "regex": "[,.?!]{2,}",
        "type": "REGEX_SEARCH",
        "regex_sub": "."
      }
    },
    {
      "name": "audio_transcription",
      "description": "Spell Check rule",
      "rule": {
        "type": "LANGUAGE",
        "lang": "en",
        "locale": "us-variety",
        "grammar_check": False,
        "language_check": True,
        "spell_check": True,
        "coherence_check": False,
        "spell_check_whitelists": []
      }
    }
  ]
}

rp_rules_test_valid_regex_value={
  "value": "Testing, regex rule where more than one punctuation marks are not allowed.",
  "rules": [
    {
      "name":"",
      "description": "Regex test rule",
      "rule": {
        "type": "REGEX_SEARCH",
        "regex": "[.,?]{2,}",
        "regex_sub": "."
      }
    }
  ]
}

rp_rules_test_invalid_regex_value={
  "value": "Testing, regex rule where more than one punctuation marks are not allowed.,",
  "rules": [
    {
      "name":"",
      "description": "Regex test rule",
      "rule": {
        "type": "REGEX_SEARCH",
        "regex": "[.,?]{2,}",
        "regex_sub": "."
      }
    }
  ]
}

rp_valid_language_rule={
  "job_id": JOB_ID,
  "user_id": RP_USER_ID,
  "team_id": RP_TEAM_ID,
  "rules": [
    {
      "name": "audio_transcription",
      "description": "Spell Check rule",
      "rule": {
        "type": "LANGUAGE",
        "lang": "en",
        "locale": "us-variety",
        "grammar_check": False,
        "language_check": True,
        "spell_check": True,
        "coherence_check": False,
        "spell_check_whitelists": []
      }
    }
  ]
}

rp_non_english_lang_rule={
    "job_id": JOB_ID,
    "user_id": RP_USER_ID,
    "team_id": RP_TEAM_ID,
    "rules": [
        {
            "name": "audio_transcription",
            "description": "Non English lang spell Check rule",
            "rule": {
                "type": "LANGUAGE",
                "lang": "fr",
                "grammar_check": False,
                "language_check": True,
                "spell_check": True,
                "coherence_check": False,
                "spell_check_whitelists": []
            }
        }
    ]
}
