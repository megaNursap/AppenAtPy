"""
Manage Workflow tests
"""
import logging
import time

from adap.api_automation.services_config.workflow import Workflow
from adap.e2e_automation.services_config.workflow_api_support import api_create_wf_from_config
from adap.api_automation.utils.data_util import *

pytestmark = [pytest.mark.wf_ui, pytest.mark.regression_wf]

LOGGER = logging.getLogger(__name__)

USER_EMAIL = get_user_email('test_ui_account')
PASSWORD = get_user_password('test_ui_account')
API_KEY = get_user_api_key('test_ui_account')

PAYLOAD1 = {
    "key": API_KEY,
    "job": {
        "title": "Determine If Youtube/Vimeo Videos Are About A Research Paper  {timestamp}".format(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())),
        "instructions": "<h1>Overview</h1><p>We are looking for YouTube or Vimeo Videos that discuss biomedical or "
                        "computer science research papers. Ideally, these videos would show a professor or graduate "
                        "student presenting their paper. You will be given a paper title and video and will determine "
                        "if the video is specifically discussing that paper.&nbsp;</p><hr><h1>Steps</h1><ol><li>Read "
                        "the paper title.&nbsp;</li><li>Watch the first 10-20 seconds of the YouTube or Vimeo "
                        "video.</li><li>Select 'Yes' if the video is a<strong>&nbsp;presentation</strong> that "
                        "describes the paper in detail.</li></ol><hr><h1>Rules &amp; Tips</h1><p>You are assessing "
                        "YouTube or Vimeo videos to determine if the video is about a research "
                        "paper.&nbsp;</p><p><strong>How to Decide:</strong></p><ul><li><strong>YES, the video is "
                        "about the research paper&nbsp;</strong>if:<ul><li>The video discusses &nbsp;the paper in "
                        "detail&nbsp;<ul><li>&nbsp;This means that there is a person presenting the "
                        "concepts/methods/conclusion of the paper in an academic setting &nbsp;</li></ul></li><li>The "
                        "video is <strong>professional and&nbsp;</strong><strong>academic&nbsp;</strong><ul><li>ex: "
                        "scientific conference presentation</li></ul></li><li><strong>Over 1 "
                        "minute</strong>&nbsp;</li><li><strong>The sounds works</strong></li><li><strong>A person is "
                        "talking about the paper</strong></li></ul></li><li><strong>NO, the video is not about the "
                        "research paper</strong> if:<ul><li>The video is not about that specific paper</li><li>The "
                        "video is too general to be about one paper</li><li>From a non-academic "
                        "source&nbsp;<ul><li><strong>no</strong>\n<strong>loud music</strong></li><li><strong>no "
                        "advertisements</strong><ul><li>no videos that show the paper, but don't discuss what the "
                        "paper is about&nbsp;</li><li>no to paid services ('helping with IEEE projects' or 'helping "
                        "with final year projects')</li></ul></li><li><strong>no movie "
                        "clips</strong></li><li><strong>no religious services</strong></li><li><strong>no personal "
                        "opinions</strong></li></ul></li><li>Under or near 1 minute long</li><li><strong>The sound "
                        "doesn't work</strong></li><li>The video is "
                        "<strong>unprofessional</strong></li></ul></li></ul><p><strong>Tips:&nbsp;</strong></p><ol"
                        "><li>The video title may be similar to the paper title.</li><li>Look for the paper author's "
                        "name in the video description.</li></ol><hr><h1>Examples</h1><table style=\"width: "
                        "100%;\"><tbody><tr><td style=\"width: 33.8368%; text-align: center; vertical-align: middle; "
                        "background-color: rgb(143, 158, 178);\"><br><span style=\"color: rgb(255, 255, "
                        "255);\"><strong>Paper Title</strong></span><br><br></td><td style=\"width: 33.2078%; "
                        "text-align: center; background-color: rgb(143, 158, 178);\"><strong><span style=\"color: "
                        "rgb(255, 255, 255);\">Video</span></strong><br></td><td style=\"width: 33.3333%; text-align: "
                        "center; background-color: rgb(143, 158, 178);\"><span style=\"color: rgb(255, 255, "
                        "255);\"><strong>Is the Video about the Paper?</strong></span></td></tr><tr><td "
                        "style=\"width: 33.8368%; text-align: center;\"><h2>Deep Residual Learning for Image "
                        "Recognition</h2></td><td style=\"width: 33.2078%;\"><br><strong>Title:</strong><br>Deep "
                        "Residual Learning for Image "
                        "Recognition<br><br><strong>Link:</strong>&nbsp;<br>https://www.youtube.com/watch?v=C6tLw"
                        "-rPQ2o<br><br><strong>Screenshot</strong><strong>:&nbsp;</strong><br><img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1532709313387-Screen+Shot"
                        "+2018-07-27+at+9.35.02+AM.png\" style=\"width: 268px; height: 211.575px;\" class=\"fr-fic "
                        "fr-dib\"></td><td style=\"width: 33.3333%; vertical-align: "
                        "top;\"><br><strong>Yes:</strong><br><ul><li>Video is about the paper</li><li>Video title and "
                        "paper title are the same</li><li>Video has audio</li><li>Video is over 1 "
                        "minute</li></ul><br></td></tr><tr><td style=\"width: 33.8368%; text-align: center; "
                        "background-color: rgb(245, 246, 249);\"><h2>Genetic Algorithms in Search, Optimization, "
                        "and Machine Learning</h2><br></td><td style=\"width: 33.2078%; vertical-align: top; "
                        "background-color: rgb(245, 246, 249);\"><br><strong>Title:</strong><br>Genetic Algorithms in "
                        "Search, Optimization, and Machine "
                        "Learning<br><br><strong>Link:</strong>&nbsp;<br>https://www.youtube.com/watch?v=Xt2dujBPnTw"
                        "<br><br><strong>Screenshot</strong><strong>:&nbsp;</strong><br><img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1532709399738-Screen+Shot"
                        "+2018-07-27+at+9.36.30+AM.png\" style=\"width: 265px; height: 303.621px;\" class=\"fr-fic "
                        "fr-dib\"></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, "
                        "246, 249);\"><br><strong>No:</strong><br><ul><li>Video is under 1 minute long</li><li>Not a "
                        "presentation about the paper</li><li>Video is an advertisement for "
                        "pdfcart.net</li></ul><br></td></tr><tr><td style=\"width: 33.8368%;\"><h2 "
                        "style=\"text-align: center;\">Refactoring improving the design of existing "
                        "code</h2><br></td><td style=\"width: 33.2078%;\"><strong>Title:</strong><br>Refactoring "
                        "Book(Martin Fowler) Review<br><br><strong>Link:</strong>&nbsp;<br>https://www.youtube.com"
                        "/watch?v=jRRmkyNuKNo<br><br><strong>Screenshot:</strong><br><img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1551896118948-Screen+Shot"
                        "+2019-03-06+at+10.15.10+AM.png\" style=\"width: 300px;\" class=\"fr-fic "
                        "fr-dib\"></td><td><strong>No:</strong><br><ul><li>This is a book review, not a presentation "
                        "of the material</li><li>unprofessional</li></ul><br></td></tr><tr><td style=\"width: "
                        "33.8368%; vertical-align: middle;\"><h2 style=\"text-align: center;\">\"If you can't stand "
                        "the heat, get out of the kitchen\"</h2></td><td style=\"width: 33.2078%; vertical-align: "
                        "top;\"><br><strong>Title:</strong><br>Your Kid Doesn't Need an iPhone "
                        "5<br><br><strong>Link:</strong>&nbsp;<br>https://vimeo.com/87196383<br><br><strong"
                        ">Screenshot</strong><strong>:&nbsp;</strong><br><img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1551896339890-Screen+Shot"
                        "+2019-03-06+at+10.18.46+AM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\"></td><td "
                        "style=\"width: 33.3333%; vertical-align: "
                        "top;\"><br><strong>No:</strong><br><ul><li>Completely unrelated video</li><li>Not about the "
                        "paper</li><li>No personal opinions</li></ul><br></td></tr><tr><td style=\"width: 33.8368%; "
                        "background-color: rgb(245, 246, 249);\"><h2 style=\"text-align: center;\">When all else "
                        "fails, read the instructions</h2></td><td style=\"width: 33.2078%; vertical-align: top; "
                        "background-color: rgb(245, 246, 249);\"><br><strong>Title:</strong><br>WHEN ALL ELSE FAILS "
                        "READ THE INSTRUCTIONS Part "
                        "1<br><br><strong>Link:</strong>&nbsp;<br>https://www.youtube.com/watch?v=WyC16y34-6E<br><br"
                        "><strong>Screenshot:&nbsp;</strong><br><img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1551896529675-Screen+Shot"
                        "+2019-03-06+at+10.22.00+AM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\"></td><td "
                        "style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, 246, "
                        "249);\"><br><strong>No:</strong><br><ul><li>This video is not about the paper</li><li>The "
                        "video is about an unrelated topic</li><li>This is not a scientific "
                        "video</li></ul><br></td></tr></tbody></table>",
        "cml": "\n<div class=\"row-fluid\">\n  <div class=\"span5\">\n    <h2>Step 1: Read Title and Watch "
               "Video</h2>\n    <hr />\n    <div class=\"well\">\n      <table class=\"table\">\n        <tr>\n       "
               "   <td>\n            <b>Paper Title:</b>\n          </td>\n          <td>{{title}}</td>\n        "
               "</tr>\n        <tr>\n        {% assign domain = {{title}} | split: '@' %}\n          <td>\n           "
               " <b>Authors:</b>\n          </td>\n          <td>{{author}}</td>\n        </tr>\n        <tr>\n       "
               "   <td>\n            <b>Video Link:</b>\n          </td>\n          <td>\n            <a "
               "target=\"_blank\" href=\"{{url}}\" class=\"btn\">Click here for Video</a>\n          </td>\n        "
               "</tr>\n      </table>\n    </div>\n  </div>\n  \n  \n  <div class=\"span7\">\n    <h2>Step 2: Answer "
               "Question</h2>\n    <hr />\n    <cml:radios label=\"Does the video discuss the paper?\" "
               "validates=\"required\" name=\"video_found_yn\" gold=\"true\"> \n      <cml:radio "
               "label=\"Yes\"></cml:radio> \n      <cml:radio label=\"No\"></cml:radio> \n    </cml:radios>\n    <br "
               "/>\n  </div>\n</div>",
        "judgments_per_unit": 1,
        "max_judgments_per_worker": 100,
        "project_number": "PN000115"
    }
}

PAYLOAD2 = {
    "key": API_KEY,
    "job": {
        "title": "Match Youtube Demonstrations To Academic Research Papers {timestamp}".format(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())),
        "instructions": "<h1>Overview</h1>\n<p>Help us determine if Computer Science YouTube Videos are "
                        "demonstrations of Computer Science Papers.&nbsp;</p>\n<hr />\n<h1>Steps</h1>\n<ol><li>Read "
                        "the paper title.&nbsp;</li><li>Watch the first 10-20 seconds of the YouTube "
                        "video.</li><li>Select 'Yes' if the video is a <strong>demonstration</strong> of the "
                        "paper.</li></ol>\n<hr />\n<h1>Rules &amp; Tips</h1>\n<p>You are assessing YouTube videos to "
                        "determine if the video is about an academic research paper.&nbsp;</p>\n<p>We are especially "
                        "looking for <strong>demonstrations of the paper</strong>.&nbsp;</p>\n<p>Such "
                        "as:&nbsp;</p>\n<ol><li>A program from the paper running on a computer</li><li>Code from the "
                        "paper</li></ol>\n<p><strong>How to Decide:&nbsp;</strong></p>\n<ul><li>Choose "
                        "<strong>yes&nbsp;</strong>if:<ul><li>The video is about the paper "
                        "<strong>AND</strong><ul><li>From an professional, <strong>academic source</strong>: ex("
                        "conferences, talks, and presentations)</li><li><strong>Over 1 minute</strong> "
                        "long</li><li><strong>A demonstration of the research</strong></li><li><strong>SILENT VIDEOS "
                        "ARE OK</strong></li></ul></li></ul></li><li>Choose <strong>no</strong> if:<ul><li>The video "
                        "is not about the paper</li><li>From a non-academic source (ex "
                        "<strong>no</strong>\n<strong>loud music</strong>, <strong>large "
                        "graphics/advertisement</strong> [phone number, company name])</li><li>Under or near 1 minute "
                        "long</li><li>The video is very "
                        "unprofessional</li></ul></li></ul>\n<p><strong>Tips:&nbsp;</strong></p>\n<ol><li>The video "
                        "name may be similar to the paper title. &nbsp;</li><li>The paper title may be in the video "
                        "description.&nbsp;</li></ol>\n<hr />\n<h1>Examples</h1>\n<table style=\"width: "
                        "100%;\"><tbody><tr><td style=\"width: 33.3333%; text-align: center; vertical-align: middle; "
                        "background-color: rgb(143, 158, 178);\"><span style=\"color: rgb(255, 255, "
                        "255);\"><strong>Paper Title</strong></span></td><td style=\"width: 33.3333%; text-align: "
                        "center; background-color: rgb(143, 158, 178);\"><strong><span style=\"color: rgb(255, 255, "
                        "255);\">Video</span></strong></td><td style=\"width: 33.3333%; text-align: center; "
                        "background-color: rgb(143, 158, 178);\"><span style=\"color: rgb(255, 255, "
                        "255);\"><strong>Is the Video about the Paper?</strong></span></td></tr><tr><td "
                        "style=\"width: 33.3333%; text-align: center;\"><h2>Real-time 3D reconstruction at scale "
                        "using voxel hashing</h2></td><td style=\"width: 33.3333%;\"><br "
                        "/><strong>Title:</strong>Real-time 3D Reconstruction at Scale using Voxel "
                        "Hashing<strong>Screenshot</strong><strong>:&nbsp;<img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534365384427-Screen+Shot"
                        "+2018-08-15+at+1.36.11+PM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" "
                        "/></strong></td><td style=\"width: 33.3333%; vertical-align: top;\"><br "
                        "/><strong>Yes:</strong><ul><li>Video is a demonstration of the paper</li><li>Video title and "
                        "paper title are the same</li><li>Video is over 1 minute</li><li>Silent videos are "
                        "OK</li></ul><br /></td></tr><tr><td><h2 style=\"text-align: center;\"><span "
                        "data-sheets-userformat=\"{&quot;2&quot;:8403841,&quot;3&quot;:[null,0],&quot;10&quot;:2,"
                        "&quot;11&quot;:0,&quot;12&quot;:0,&quot;14&quot;:[null,2,0],&quot;15&quot;:&quot;Calibri, "
                        "sans-serif&quot;,&quot;16&quot;:12,&quot;26&quot;:400}\" data-sheets-value=\"{"
                        "&quot;1&quot;:2,&quot;2&quot;:&quot;Real-time visual-inertial mapping re-localization and "
                        "planning onboard MAVs in unknown environments&quot;}\">Real-time visual-inertial mapping "
                        "re-localization and planning onboard MAVs in unknown environments</span></h2><br "
                        "/></td><td><strong>Title:&nbsp;</strong>Real-Time Visual-Inertial Mapping, Re-localization "
                        "and Planning Onboard MAVs in Unknown "
                        "Environments<strong>Screenshot</strong><strong>:&nbsp;<img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1535567908185-Screen+Shot"
                        "+2018-08-29+at+11.38.11+AM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" "
                        "/></strong></td><td><strong>Yes:</strong><ul><li>Video is a demonstration of the "
                        "paper</li><li>Video title and paper title are the same</li><li>Video is over 1 "
                        "minute</li><li>Silent videos are OK</li></ul><br /></td></tr><tr><td><h2 style=\"text-align: "
                        "center;\">Playing hard exploration games by watching YouTube</h2><br "
                        "/></td><td><strong>Title:&nbsp;</strong>Learnt agent - Private Eye<br "
                        "/><strong>Screenshot</strong><strong>:&nbsp;<img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1535568194488-Screen+Shot"
                        "+2018-08-29+at+11.41.23+AM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" "
                        "/></strong></td><td><strong>Yes:</strong><ul><li>Video is a demonstration of the "
                        "paper</li><li>paper title is found in the description</li><li>Video is over 1 "
                        "minute</li><li>Silent videos are OK</li></ul><br /></td></tr><tr><td style=\"width: "
                        "33.3333%; text-align: center; background-color: rgb(245, 246, 249);\"><h2>Genetic Algorithms "
                        "in Search, Optimization, and Machine Learning</h2><br /></td><td style=\"width: 33.3333%; "
                        "vertical-align: top; background-color: rgb(245, 246, 249);\"><br "
                        "/><strong>Title:</strong>Genetic Algorithms in Search, Optimization, and Machine "
                        "Learning<strong>Screenshot</strong><strong>:&nbsp;</strong><img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1532709399738-Screen+Shot"
                        "+2018-07-27+at+9.36.30+AM.png\" style=\"width: 265px; height: 303.621px;\" class=\"fr-fic "
                        "fr-dib\" /></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, "
                        "246, 249);\"><br /><strong>No:</strong><ul><li>Video is under 1 minute long</li><li>Not a "
                        "presentation about the paper</li><li>Video is an advertisement for pdfcart.net</li></ul><br "
                        "/></td></tr><tr><td><h2 style=\"text-align: center;\">Object Removal by Exemplar-Based "
                        "Inpainting</h2><br /></td><td><strong>Title:</strong>Object removal by Exemplar based "
                        "Inpainting<strong>Screenshot:<img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534365582122-Screen+Shot"
                        "+2018-08-15+at+1.39.31+PM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" "
                        "/></strong></td><td><strong>No:</strong><ul><li>under 1 minute</li></ul><br "
                        "/></td></tr><tr><td style=\"width: 33.3333%; vertical-align: middle;\"><h2 "
                        "style=\"text-align: center;\">Recent Advances in Augmented Reality</h2></td><td "
                        "style=\"width: 33.3333%; vertical-align: top;\"><br /><strong>Title:&nbsp;</strong>Medical "
                        "Imaging in AR - Laboratory of Pharmacometabolomics and Companion "
                        "Diagnostics<strong>Screenshot</strong><strong>:&nbsp;<img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534455413455-Screen+Shot"
                        "+2018-08-16+at+2.34.00+PM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" "
                        "/></strong></td><td style=\"width: 33.3333%; vertical-align: top;\"><br "
                        "/><strong>No:</strong><ul><li>Video is not a demonstration of the paper</li><li>Video is not "
                        "about the paper</li></ul><br /></td></tr><tr><td style=\"width: 33.3333%; background-color: "
                        "rgb(245, 246, 249);\"><h2 style=\"text-align: center;\">Playing hard exploration games by "
                        "watching YouTube</h2></td><td style=\"width: 33.3333%; vertical-align: top; "
                        "background-color: rgb(245, 246, 249);\"><br /><strong>Title:</strong>Learnt agent - "
                        "&nbsp;Pitfall!<strong>Screenshot:&nbsp;<img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534455637964-Screen+Shot"
                        "+2018-08-16+at+2.40.25+PM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" "
                        "/></strong></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, "
                        "246, 249);\"><br /><strong>Yes:</strong><ul><li>Over 1 minute</li><li>Demonstration of the "
                        "paper</li></ul><br /></td></tr></tbody></table>\n",
        "cml": "\n<div class=\"row-fluid\">\n  <div class=\"span5\">\n    <h2>Step 1: Review the Title and list of "
               "Authors</h2>\n    <hr />\n    <div class=\"well\">\n      <table class=\"table\">\n        <tr>\n     "
               "     <td>\n            <b>Title:</b>\n          </td>\n          <td>{{title}}</td>\n        </tr>\n  "
               "      <tr>\n        {% assign domain = {{title}} | split: '@' %}\n          <td>\n            "
               "<b>Authors:</b>\n          </td>\n          <td>{{author}}</td>\n        </tr>\n        <tr>\n        "
               "  <td>\n            <b>YouTube Video Link:</b>\n          </td>\n          <td>\n            <a "
               "target=\"_blank\" href=\"{{url}}\" class=\"btn\">Click here for Video</a>\n          </td>\n        "
               "</tr>\n      </table>\n    </div>\n  </div>\n  \n  \n  <div class=\"span7\">\n    <h2>Step 2: Collect "
               "Information</h2>\n    <hr />\n    <cml:radios label=\"Is the video about the paper?\" "
               "validates=\"required\" name=\"video_found_yn\" gold=\"true\"> \n      <cml:radio "
               "label=\"Yes\"></cml:radio> \n      <cml:radio label=\"No\"></cml:radio> \n    </cml:radios>\n    <br "
               "/>\n  </div>\n</div>",
        "judgments_per_unit": 1,
        "max_judgments_per_worker": 100,
        "project_number": "PN000115"
    }
}

PAYLOAD3 = {
    "key": API_KEY,
    "job": {
        "title": "Don't Match Youtube Demonstrations To Academic Research Papers {timestamp}".format(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())),
        "instructions": "<h1>Overview</h1>\n<p>Help us determine if Computer Science YouTube Videos are "
                        "demonstrations of Computer Science Papers.&nbsp;</p>\n<hr />\n<h1>Steps</h1>\n<ol><li>Read "
                        "the paper title.&nbsp;</li><li>Watch the first 10-20 seconds of the YouTube "
                        "video.</li><li>Select 'Yes' if the video is a <strong>demonstration</strong> of the "
                        "paper.</li></ol>\n<hr />\n<h1>Rules &amp; Tips</h1>\n<p>You are assessing YouTube videos to "
                        "determine if the video is about an academic research paper.&nbsp;</p>\n<p>We are especially "
                        "looking for <strong>demonstrations of the paper</strong>.&nbsp;</p>\n<p>Such "
                        "as:&nbsp;</p>\n<ol><li>A program from the paper running on a computer</li><li>Code from the "
                        "paper</li></ol>\n<p><strong>How to Decide:&nbsp;</strong></p>\n<ul><li>Choose "
                        "<strong>yes&nbsp;</strong>if:<ul><li>The video is about the paper "
                        "<strong>AND</strong><ul><li>From an professional, <strong>academic source</strong>: ex("
                        "conferences, talks, and presentations)</li><li><strong>Over 1 minute</strong> "
                        "long</li><li><strong>A demonstration of the research</strong></li><li><strong>SILENT VIDEOS "
                        "ARE OK</strong></li></ul></li></ul></li><li>Choose <strong>no</strong> if:<ul><li>The video "
                        "is not about the paper</li><li>From a non-academic source (ex "
                        "<strong>no</strong>\n<strong>loud music</strong>, <strong>large "
                        "graphics/advertisement</strong> [phone number, company name])</li><li>Under or near 1 minute "
                        "long</li><li>The video is very "
                        "unprofessional</li></ul></li></ul>\n<p><strong>Tips:&nbsp;</strong></p>\n<ol><li>The video "
                        "name may be similar to the paper title. &nbsp;</li><li>The paper title may be in the video "
                        "description.&nbsp;</li></ol>\n<hr />\n<h1>Examples</h1>\n<table style=\"width: "
                        "100%;\"><tbody><tr><td style=\"width: 33.3333%; text-align: center; vertical-align: middle; "
                        "background-color: rgb(143, 158, 178);\"><span style=\"color: rgb(255, 255, "
                        "255);\"><strong>Paper Title</strong></span></td><td style=\"width: 33.3333%; text-align: "
                        "center; background-color: rgb(143, 158, 178);\"><strong><span style=\"color: rgb(255, 255, "
                        "255);\">Video</span></strong></td><td style=\"width: 33.3333%; text-align: center; "
                        "background-color: rgb(143, 158, 178);\"><span style=\"color: rgb(255, 255, "
                        "255);\"><strong>Is the Video about the Paper?</strong></span></td></tr><tr><td "
                        "style=\"width: 33.3333%; text-align: center;\"><h2>Real-time 3D reconstruction at scale "
                        "using voxel hashing</h2></td><td style=\"width: 33.3333%;\"><br "
                        "/><strong>Title:</strong>Real-time 3D Reconstruction at Scale using Voxel "
                        "Hashing<strong>Screenshot</strong><strong>:&nbsp;<img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534365384427-Screen+Shot"
                        "+2018-08-15+at+1.36.11+PM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" "
                        "/></strong></td><td style=\"width: 33.3333%; vertical-align: top;\"><br "
                        "/><strong>Yes:</strong><ul><li>Video is a demonstration of the paper</li><li>Video title and "
                        "paper title are the same</li><li>Video is over 1 minute</li><li>Silent videos are "
                        "OK</li></ul><br /></td></tr><tr><td><h2 style=\"text-align: center;\"><span "
                        "data-sheets-userformat=\"{&quot;2&quot;:8403841,&quot;3&quot;:[null,0],&quot;10&quot;:2,"
                        "&quot;11&quot;:0,&quot;12&quot;:0,&quot;14&quot;:[null,2,0],&quot;15&quot;:&quot;Calibri, "
                        "sans-serif&quot;,&quot;16&quot;:12,&quot;26&quot;:400}\" data-sheets-value=\"{"
                        "&quot;1&quot;:2,&quot;2&quot;:&quot;Real-time visual-inertial mapping re-localization and "
                        "planning onboard MAVs in unknown environments&quot;}\">Real-time visual-inertial mapping "
                        "re-localization and planning onboard MAVs in unknown environments</span></h2><br "
                        "/></td><td><strong>Title:&nbsp;</strong>Real-Time Visual-Inertial Mapping, Re-localization "
                        "and Planning Onboard MAVs in Unknown "
                        "Environments<strong>Screenshot</strong><strong>:&nbsp;<img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1535567908185-Screen+Shot"
                        "+2018-08-29+at+11.38.11+AM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" "
                        "/></strong></td><td><strong>Yes:</strong><ul><li>Video is a demonstration of the "
                        "paper</li><li>Video title and paper title are the same</li><li>Video is over 1 "
                        "minute</li><li>Silent videos are OK</li></ul><br /></td></tr><tr><td><h2 style=\"text-align: "
                        "center;\">Playing hard exploration games by watching YouTube</h2><br "
                        "/></td><td><strong>Title:&nbsp;</strong>Learnt agent - Private Eye<br "
                        "/><strong>Screenshot</strong><strong>:&nbsp;<img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1535568194488-Screen+Shot"
                        "+2018-08-29+at+11.41.23+AM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" "
                        "/></strong></td><td><strong>Yes:</strong><ul><li>Video is a demonstration of the "
                        "paper</li><li>paper title is found in the description</li><li>Video is over 1 "
                        "minute</li><li>Silent videos are OK</li></ul><br /></td></tr><tr><td style=\"width: "
                        "33.3333%; text-align: center; background-color: rgb(245, 246, 249);\"><h2>Genetic Algorithms "
                        "in Search, Optimization, and Machine Learning</h2><br /></td><td style=\"width: 33.3333%; "
                        "vertical-align: top; background-color: rgb(245, 246, 249);\"><br "
                        "/><strong>Title:</strong>Genetic Algorithms in Search, Optimization, and Machine "
                        "Learning<strong>Screenshot</strong><strong>:&nbsp;</strong><img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1532709399738-Screen+Shot"
                        "+2018-07-27+at+9.36.30+AM.png\" style=\"width: 265px; height: 303.621px;\" class=\"fr-fic "
                        "fr-dib\" /></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, "
                        "246, 249);\"><br /><strong>No:</strong><ul><li>Video is under 1 minute long</li><li>Not a "
                        "presentation about the paper</li><li>Video is an advertisement for pdfcart.net</li></ul><br "
                        "/></td></tr><tr><td><h2 style=\"text-align: center;\">Object Removal by Exemplar-Based "
                        "Inpainting</h2><br /></td><td><strong>Title:</strong>Object removal by Exemplar based "
                        "Inpainting<strong>Screenshot:<img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534365582122-Screen+Shot"
                        "+2018-08-15+at+1.39.31+PM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" "
                        "/></strong></td><td><strong>No:</strong><ul><li>under 1 minute</li></ul><br "
                        "/></td></tr><tr><td style=\"width: 33.3333%; vertical-align: middle;\"><h2 "
                        "style=\"text-align: center;\">Recent Advances in Augmented Reality</h2></td><td "
                        "style=\"width: 33.3333%; vertical-align: top;\"><br /><strong>Title:&nbsp;</strong>Medical "
                        "Imaging in AR - Laboratory of Pharmacometabolomics and Companion "
                        "Diagnostics<strong>Screenshot</strong><strong>:&nbsp;<img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534455413455-Screen+Shot"
                        "+2018-08-16+at+2.34.00+PM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" "
                        "/></strong></td><td style=\"width: 33.3333%; vertical-align: top;\"><br "
                        "/><strong>No:</strong><ul><li>Video is not a demonstration of the paper</li><li>Video is not "
                        "about the paper</li></ul><br /></td></tr><tr><td style=\"width: 33.3333%; background-color: "
                        "rgb(245, 246, 249);\"><h2 style=\"text-align: center;\">Playing hard exploration games by "
                        "watching YouTube</h2></td><td style=\"width: 33.3333%; vertical-align: top; "
                        "background-color: rgb(245, 246, 249);\"><br /><strong>Title:</strong>Learnt agent - "
                        "&nbsp;Pitfall!<strong>Screenshot:&nbsp;<img "
                        "src=\"https://s3.amazonaws.com/crowdflower-make-cloud/images%2F1534455637964-Screen+Shot"
                        "+2018-08-16+at+2.40.25+PM.png\" style=\"width: 300px;\" class=\"fr-fic fr-dib\" "
                        "/></strong></td><td style=\"width: 33.3333%; vertical-align: top; background-color: rgb(245, "
                        "246, 249);\"><br /><strong>Yes:</strong><ul><li>Over 1 minute</li><li>Demonstration of the "
                        "paper</li></ul><br /></td></tr></tbody></table>\n",
        "cml": "\n<div class=\"row-fluid\">\n  <div class=\"span5\">\n    <h2>Step 1: Review the Title and list of "
               "Authors</h2>\n    <hr />\n    <div class=\"well\">\n      <table class=\"table\">\n        <tr>\n     "
               "     <td>\n            <b>Title:</b>\n          </td>\n          <td>{{title}}</td>\n        </tr>\n  "
               "      <tr>\n        {% assign domain = {{title}} | split: '@' %}\n          <td>\n            "
               "<b>Authors:</b>\n          </td>\n          <td>{{author}}</td>\n        </tr>\n        <tr>\n        "
               "  <td>\n            <b>YouTube Video Link:</b>\n          </td>\n          <td>\n            <a "
               "target=\"_blank\" href=\"{{url}}\" class=\"btn\">Click here for Video</a>\n          </td>\n        "
               "</tr>\n      </table>\n    </div>\n  </div>\n  \n  \n  <div class=\"span7\">\n    <h2>Step 2: Collect "
               "Information</h2>\n    <hr />\n    <cml:radios label=\"Is the video about the paper?\" "
               "validates=\"required\" name=\"video_found_yn\" gold=\"true\"> \n      <cml:radio "
               "label=\"Yes\"></cml:radio> \n      <cml:radio label=\"No\"></cml:radio> \n    </cml:radios>\n    <br "
               "/>\n  </div>\n</div>",
        "judgments_per_unit": 1,
        "max_judgments_per_worker": 100,
        "project_number": "PN000115"
    }
}

FILTER_PAYLOAD = {
    "filter_rule": {
        "comparison_field": "video_found_yn",
        "comparison_operation": "==",
        "comparison_value": "Yes",
        "rule_connector": "and"}
}

FILTER_PAYLOAD2 = {
    "filter_rule": {
        "comparison_field": "video_found_yn",
        "comparison_operation": "==",
        "comparison_value": "No",
        "rule_connector": "and"}
}

SAMPLE_FILE = get_data_file("/upload_data_files/workflows/shared-test-data-sets/customer_01_sample_22.csv")

WF_CONFIG_3 = {
    "env": pytest.env,
    "user": {
        "api_key": API_KEY
    },
    "jobs": {
        "count": 3,
        "payloads": [PAYLOAD1, PAYLOAD2, PAYLOAD3]
    },
    "workflow": {
        "payload": {
            "name": " Create WF UAT test",
            "description": "3 Job demo workflow, example of using filter_rule to route data between related jobs."
            # "kafka": 'false'
        }
    },
    "routes": {
        "1": {"connect": (1, 2), "filter": FILTER_PAYLOAD},
        "2": {"connect": (1, 3), "filter": FILTER_PAYLOAD2}
    },
    "data_upload": [SAMPLE_FILE],
    "launch": False,
    "row_order": 22
}


@pytest.fixture(scope="module")
def create_wf_ui(app):
    global WF_ID, _JOBS, FILE_ROWS

    FILE_ROWS = count_row_in_file(SAMPLE_FILE)
    wf_info = api_create_wf_from_config(WF_CONFIG_3)
    app.user.login_as_customer(user_name=USER_EMAIL, password=PASSWORD)
    WF_ID = wf_info['id']
    _JOBS = wf_info['jobs']


@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_rows_to_order(app, create_wf_ui):
    """
    As a customer, I can set the number of rows to order
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)

    app.navigation.click_link("Launch")
    app.verification.text_present_on_page("Rows to order")

    rows = app.workflow.get_rows_to_order()

    assert rows['max_rows'] == count_row_in_file(SAMPLE_FILE)
    if rows['max_rows'] <= 100:
        assert rows['rows'] == rows['max_rows']
    else:
        assert rows['rows'] == '100'

    app.workflow.set_rows_to_order(rows['max_rows']-1)
    rows = app.workflow.get_rows_to_order()
    assert rows['rows'] == rows['max_rows'] -1

    app.workflow.set_rows_to_order(rows['max_rows']+1)
    rows = app.workflow.get_rows_to_order()
    assert rows['rows'] == rows['max_rows']

    rows = app.workflow.get_rows_to_order()
    app.workflow.set_rows_to_order('abc')
    assert rows['rows'] == rows['max_rows']

# TODO create wf with more 100 rows and verify default rows to order = 100


@pytest.mark.ui_uat
def test_launch_page_content(app, create_wf_ui):
    """
    As a customer, when I am on the launch page, all jobs and models are displayed as separate entries
    As a customer reviewing the launch page, I should see a max cost estimate on the launch page
    As a customer, I should see my total team funds on the launch page
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)

    app.navigation.click_link("Launch")
    app.verification.text_present_on_page("Estimated Contributor Cost")
    app.verification.text_present_on_page("Available Funds")

    linked_jobs = app.workflow.get_all_operators_on_launch_page()
    assert len(linked_jobs) == 3
    assert linked_jobs.get(str(_JOBS[0]), False)
    assert linked_jobs.get(str(_JOBS[1]), False)
    assert linked_jobs.get(str(_JOBS[2]), False)

    row_cost = round(sum([float(x['price'][1:]) for x in linked_jobs.values()]), 2)

    app.workflow.set_rows_to_order(1)
    rows = app.workflow.get_rows_to_order()
    current_cost = app.workflow.get_estimated_cost()
    assert rows['rows'] == 1
    assert str(row_cost) == current_cost

    app.workflow.set_rows_to_order(10)
    rows = app.workflow.get_rows_to_order()
    current_cost = float(app.workflow.get_estimated_cost())
    assert rows['rows'] == 10
    assert round(row_cost * 10, 2) == current_cost


@pytest.mark.dependency()
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_launch_wf(app, create_wf_ui):
    """
    test_launch_wf
    As a customer, I canot edit the workflow after it is launched
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)

    app.navigation.click_link("Launch")
    app.verification.text_present_on_page("Estimated Contributor Cost")

    app.navigation.click_link("Launch Workflow")

    wf_api = Workflow(API_KEY)
    wf_api.wait_until_wf_status('running', wf_id=WF_ID, max_time=60*3)
    current_status = app.workflow.get_wf_status_ui()
    assert current_status == "Running"

    # not working, fix later
    # app.navigation.click_link("Canvas")
    # app.workflow.click_on_canvas_coordinates(720, 480, mode='body')
    # app.verification.text_present_on_page('Workflows cannot be edited once they have been launched.')


@pytest.mark.dependency(depends=["test_launch_wf"])
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
def test_auto_launch_applied_to_jobs(app, create_wf_ui):
    time.sleep(10)
    app.mainMenu.jobs_page()
    app.job.open_job_with_id(_JOBS[0])
    app.job.open_action("Settings")
    app.job.open_settings_tab("API")

    assert app.job.get_checkbox_status('Rows remain finalized') == 'true'
    assert app.job.get_checkbox_status('Turn on automatic launching of rows') == 'true'

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(_JOBS[1])
    app.job.open_action("Settings")
    app.job.open_settings_tab("API")

    assert app.job.get_checkbox_status('Rows remain finalized') == 'true'
    assert app.job.get_checkbox_status('Turn on automatic launching of rows') == 'true'

    app.mainMenu.jobs_page()
    app.job.open_job_with_id(_JOBS[2])
    app.job.open_action("Settings")
    app.job.open_settings_tab("API")

    assert app.job.get_checkbox_status('Rows remain finalized') == 'true'
    assert app.job.get_checkbox_status('Turn on automatic launching of rows') == 'true'


@pytest.mark.dependency(depends=["test_launch_wf"])
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_pause_wf(app, create_wf_ui):
    """
    test_pause_wf
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)

    app.workflow.pause_wf()
    time.sleep(30)

    current_status = app.workflow.get_wf_status_ui()
    assert current_status == "Paused"
    app.verification.text_present_on_page("Resume Workflow")


@pytest.mark.dependency(depends=["test_pause_wf"])
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_resume_wf(app, create_wf_ui):
    """
    test_resume_wf
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)

    app.navigation.click_link("Resume Workflow")
    time.sleep(30)

    current_status = app.workflow.get_wf_status_ui()
    assert current_status == "Running"
    app.verification.text_present_on_page("Pause Workflow")


@pytest.mark.dependency(depends=["test_resume_wf"])
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_download_report_wf(app, create_wf_ui):
    """
    test_download_report
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)

    app.navigation.click_link("Results")

    app.verification.text_present_on_page("Workflows Report")
    app.verification.text_present_on_page("Source Report")

    app.workflow.download_report("Workflows Report")
    app.verification.verify_file_present_in_dir("workflow_%s_report.zip" % WF_ID, app.temp_path_file)

    app.workflow.download_report("Source Report")
    app.verification.verify_file_present_in_dir("workflow_%s_source_report.zip" % WF_ID, app.temp_path_file)


@pytest.mark.dependency(depends=["test_resume_wf"])
@pytest.mark.ui_uat
@pytest.mark.adap_ui_uat
@pytest.mark.adap_uat
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_regenerate_wf_report(app, create_wf_ui):
    """
    test_regenerate_report
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)

    app.navigation.click_link("Results")

    app.verification.text_present_on_page("Workflows Report")
    app.verification.text_present_on_page("Source Report")

    app.workflow.regenerate_report("Workflows Report")

    assert app.verification.wait_untill_text_present_on_the_page('The report has been regenerated', 20)

    app.workflow.regenerate_report("Source Report")
    assert app.verification.wait_untill_text_present_on_the_page('The report has been regenerated', 20)


@pytest.mark.dependency(depends=["test_resume_wf"])
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_rows_routed_based_on_routing_rules(app):
    """
    test_rows_routed_based_on_routing_rules
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)

    app.navigation.click_link("Data")
    count_rows_ui = app.workflow.data.count_rows_for_uploaded_file("all")

    assert FILE_ROWS == count_rows_ui
    time.sleep(100)
    app.navigation.click_link("Launch")

    wf_window = app.driver.window_handles[0]
    app.workflow.open_job_from_launch_page(_JOBS[0])
    app.job.open_tab("Monitor")
    time.sleep(30)
    job_row = app.job.monitor.grab_info_from_dashboard('Rows Uploaded')

    assert count_rows_ui == int(job_row)

    current_status = app.job.get_job_status()
    assert current_status == "Running"

    app.navigation.switch_to_window(wf_window)
    wf_current_status = app.workflow.get_wf_status_ui()
    assert wf_current_status == "Running"


@pytest.mark.dependency(depends=["test_rows_routed_based_on_routing_rules"])
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_user_not_able_delete_data_for_launched_wf(app, create_wf_ui):
    """
    test_user_not_able_delete_data_for_launched_wf
    As a customer, the total row count should decrease after rows are launched in the workflow
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)

    app.navigation.click_link("Launch")
    rows = app.workflow.get_rows_to_order()
    assert rows['rows'] == 0
    assert rows['max_rows'] == 0

    app.navigation.click_link("Data")

    app.verification.element_is('disabled', "Delete All Data")

    add_sample_file = get_data_file("/authors.csv")

    app.navigation.click_link("Add More Data")
    app.job.data.upload_file(add_sample_file)
    app.verification.text_present_on_page("authors.csv")
    app.workflow.data.delete_btn_disabled("authors.csv")


@pytest.mark.dependency(depends=["test_rows_routed_based_on_routing_rules"])
def test_order_more_rows(app, create_wf_ui):
    """
    As a customer, the total row count should increase if more rows are uploaded to the workflow
    As a customer, the total row count should decrease after rows are launched in the workflow
    As a customer, I can order additional rows from the launch page while the workflow is running
    """
    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)

    app.navigation.click_link("Launch")

    add_sample_file = get_data_file("/authors.csv")
    new_rows = count_row_in_file(add_sample_file)
    rows = app.workflow.get_rows_to_order()
    assert rows['rows'] == new_rows
    assert rows['max_rows'] == new_rows

    app.navigation.click_link('Order More Rows')
    time.sleep(3)

    rows = app.workflow.get_rows_to_order()
    assert rows['rows'] == 0
    assert rows['max_rows'] == 0


@pytest.mark.dependency(depends=["test_rows_routed_based_on_routing_rules"])
@pytest.mark.ui_uat
@pytest.mark.skipif(pytest.flaky == "false", reason="Flaky test")
def test_user_not_able_delete_launched_wf(app, create_wf_ui):
    """
    As a customer, I cannot delete a launched workflow
    """
    app.mainMenu.workflows_page()

    app.workflow.search_wf_by_name(WF_ID)
    app.workflow.click_on_gear_for_wf(WF_ID, sub_menu='Delete Workflow')
    app.verification.text_present_on_page('Workflows cannot be deleted once they have been launched')

    app.mainMenu.workflows_page()
    app.workflow.open_wf_by_id(WF_ID)


def test_finalized_rows_in_report(app_test, tmpdir):
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('max_colwidth', -1)

    user = get_user_email('test_account')
    password = get_user_password('test_account')

    app_test.user.login_as_customer(user_name=user, password=password)
    predefined_wf = pytest.data.predefined_data["workflow_with_judgments"][pytest.env]

    app_test.mainMenu.workflows_page()

    app_test.workflow.open_wf_by_id(predefined_wf)
    app_test.navigation.click_link("Results")

    app_test.workflow.download_report("Workflows Report")

    filename = "workflow_%s_report" % predefined_wf
    app_test.verification.verify_file_present_in_dir(filename+'.zip', tmpdir)

    unzip_file(tmpdir + '/%s.zip' % filename)
    csv_name = tmpdir + '/%s.csv' % filename

    _df = pd.read_csv(csv_name)
    # verify at least 1 row finalised
    assert _df['row_finalized_at'].count() > 0

    os.remove(csv_name)
    os.remove(tmpdir + '/{0}.zip'.format(filename))

# TODO reports content verification
# TODO pause WF and verify status of jobs - paused
