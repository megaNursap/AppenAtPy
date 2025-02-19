from adap.perf_platform.test_data.data_generator import (
  generate_csv_data_what_is_greater,
  generate_csv_data_nab_meaning,
  generate_csv_data_catdog,
  generate_csv_data_hands,
  generate_csv_data_text_annotation,
  generate_csv_data_liquid
  )

nab_meaning = """
<div class="html-element-wrapper">
  <div class="row-fluid">
    <div class="span6">
 Target Product:
      <strong>
        <u style="color:blue" id='q_value'>{{inclusion}}</u>
      </strong>
      <span>
        <div class="well">{{message}}</div>
      </span>
    </div>
    <div class="span6">
      <cml:radios label="nab_meaning" name="nab_meaning" validates="required" gold="true" aggregation="agg">
        <cml:radio label="yes &lt;a target='_blank' rel='popover' tabIndex'-1' class='yes_nab_meaning'&gt;&lt;i class='icon-info-sign'&gt;&lt;/i&gt;&lt;/a&gt;" value="yes"></cml:radio>
        <cml:radio label="no &lt;a target='_blank' rel='popover' tabIndex'-1' class='no_nab_meaning'&gt;&lt;i class='icon-info-sign'&gt;&lt;/i&gt;&lt;/a&gt;" value="no"></cml:radio>
      </cml:radios>
      <cml:radios label="consumption_related" name="consumption_related" only-if="nab_meaning:[yes]" validates="required" gold="true" aggregation="agg">
        <cml:radio label="yes &lt;a target='_blank' rel='popover' tabIndex'-1' class='yes_consumption_related'&gt;&lt;i class='icon-info-sign'&gt;&lt;/i&gt;&lt;/a&gt;" value="yes"></cml:radio>
        <cml:radio label="no &lt;a target='_blank' rel='popover' tabIndex'-1' class='no_consumption_related'&gt;&lt;i class='icon-info-sign'&gt;&lt;/i&gt;&lt;/a&gt;" value="no"></cml:radio>
      </cml:radios>
      <cml:radios label="ingredient" name="ingredient" only-if="consumption_related:[yes]" validates="required" gold="true" aggregation="agg">
        <cml:radio label="yes&lt;a target='_blank' rel='popover' tabIndex'-1' class='yes_ingredient'&gt;&lt;i class='icon-info-sign'&gt;&lt;/i&gt;&lt;/a&gt;" value="yes"></cml:radio>
        <cml:radio label="no &lt;a target='_blank' rel='popover' tabIndex'-1' class='no_alone'&gt;&lt;i class='icon-info-sign'&gt;&lt;/i&gt;&lt;/a&gt;" value="no"></cml:radio>
      </cml:radios>
      <cml:radios label="category_related" name="category_related" only-if="nab_meaning:[no]" validates="required" gold="true" aggregation="agg">
        <cml:radio label="yes &lt;a target='_blank' rel='popover' tabIndex'-1' class='yes_category_related'&gt;&lt;i class='icon-info-sign'&gt;&lt;/i&gt;&lt;/a&gt;" value="yes"></cml:radio>
        <cml:radio label="no &lt;a target='_blank' rel='popover' tabIndex'-1' class='no_category_related'&gt;&lt;i class='icon-info-sign'&gt;&lt;/i&gt;&lt;/a&gt;" value="no"></cml:radio>
      </cml:radios>
    </div>
  </div>
</div>
"""

what_is_greater = """
<div class="html-element-wrapper">
<p>Column1: {{column_1}}</p>
<p>Column2: {{column_2}}</p>
<p>marker: {{marker}}</p>
</div><cml:radios label="What is greater?" validates="required" name="what_is_greater" gold="true">
<cml:radio label="Column1" value="col1" />
<cml:radio label="Column2" value="col2" />
<cml:radio label="Equals" value="equals" /></cml:radios>
<!--<cml:radio label="Equals" value="equals" />-->
<!--data validation-->
"""

image_annotation = """
<p>marker: {{marker}}</p>
<cml:checkbox label="Nothing to box" aggregation="agg" gold="true" value="nothing_to_box" />
<cml:shapes label="Draw Shapes" name="annotation" type="['box']"
source_data="{{image_url}}" box-threshold="0.7" class-threshold="0.7"
ontology="true" validates="required" only-if="!nothing_to_box" class-agg="agg" box-agg="0.7"
allow-box-rotation="false" crosshair="false" gold="true"></cml:shapes>
"""


video_annotation = """
<cml:video_shapes name="myvideo" source-data="{{video_link}}" review-from="{{annotation}}"
validates="required" crosshair="true" labels-required="true" type="['box']"
assistant="object_tracking" aggregation="all"/>
"""

server_side_validation = """
<div data-server-side-required="true"></div>
<cml:radios label="Parent Question" validates="required" gold="true">
  <cml:radio label="First option" value="first_option"/>
  <cml:radio label="Second option" value="second_option"/>
</cml:radios>
<cml:radios label="Child Question 1" validates="required" only-if="parent_question:[second_option]" gold="true">
  <cml:radio label="First option" value="first_option"/>
  <cml:radio label="Second option" value="second_option"/>
</cml:radios>
<cml:radios label="Child Question 2" validates="required" only-if="parent_question:[second_option]" gold="true">
  <cml:radio label="First option" value="first_option"/>
  <cml:radio label="Second option" value="second_option"/>
</cml:radios>
<cml:radios label="SubChild Question 1" validates="required" only-if="child_question_2:[second_option]" gold="true">
  <cml:radio label="First option" value="first_option"/>
  <cml:radio label="Second option" value="second_option"/>
</cml:radios>
<cml:radios label="SubChild Question 2" validates="required" only-if="child_question_2:[second_option]" gold="true">
  <cml:radio label="First option" value="first_option"/>
  <cml:radio label="Second option" value="second_option"/>
</cml:radios>
"""

server_side_validation_simple_case = """
<cml:radios name="field1" validates="required" gold="true">
  <cml:radio label="First option" value="first_option" />
  <cml:radio label="Second option" value="second_option" />
</cml:radios>
<cml:text name="field2" validates="required" label="Enter some text" />
<cml:checkbox name="field3" label="A single checkbox" />
"""

server_side_validation_complicated_case = """
<cml:radios name="root" validates="required">
  <cml:radio value="yes" label="yes"/>
  <cml:radio value="no" label="no"/>
</cml:radios>
<cml:checkboxes name="depth2" validates="required" only-if="root:[yes]" exact="true">
  <cml:checkbox value="human" label="human"/>
  <cml:checkbox value="cat" label="cat"/>
  <cml:checkbox value="dog" label="dog"/>
</cml:checkboxes>
<cml:text name="depth3" validates="required" only-if="depth2:[human]"/>
<cml:text name="depth4" validates="required" only-if="depth3"/>
<cml:group only-if="root:[no]">
  <cml:text name="group_field" validates="required"/>
  <cml:text name="or_clause" validates="required" only-if="group_field:[bar]"/>
</cml:group>
<cml:text name="root_and"/>  
<cml:hours name="and_clause" validates="required" only-if="depth2:[dog]++root_and:[baz]">
</cml:hours>
"""


server_side_validation_liquid_case = """
<div class="html-element-wrapper">
  <p>Column1: {{unit_key}}</p>
  <p>Column1: {{unit_key2}}</p>
</div>
<cml:text name="root" validates="required"/>
{% if unit_key contains 'test1' %}
<cml:text name="foo" validates="required"/>
{% elsif unit_key == 'test2' %}
<cml:radios name="bar" label="Label text" validates="required">
  <cml:radio value="yes" label="Yes"></cml:radio>
  <cml:radio value="no" label="No"></cml:radio>
</cml:radios>
{% else %}
<cml:text label="Lorem ipsum" validates="required"/>
{% endif %}
{% if unit_key2 contains 'test1' %}
<cml:text name="field1" validates="required"/>
{% else %}
<cml:text name="field2" validates="required"/>
{% endif %}
<cml:text name="optional_tag"/>
"""

text_annotation = """
<p>marker: {{marker}}</p>
<div class="html-element-wrapper">
  <ul>
    <li> <div class="html-element-wrapper"> <span>show_number: {{show_number}}</span> </div> </li>
    <li> <div class="html-element-wrapper"> <span>air_date: {{air_date}}</span> </div> </li>
    <li> <div class="html-element-wrapper"> <span>round: {{round}}</span> </div> </li>
    <li> <div class="html-element-wrapper"> <span>category: {{category}}</span> </div> </li>
    <li> <div class="html-element-wrapper"> <span>value: {{value}}</span> </div> </li>
    <li> <div class="html-element-wrapper"> <span>question: <span class="input_text">{{question}}</span></span> </div> </li>
    <li> <div class="html-element-wrapper"> <span>answer: {{answer}}</span> </div> </li>
  </ul>
</div>
<cml:text_annotation label="Label Text" name="annotation" source-type="text" source-data="{{question}}"
tokenizer="stanford" language="en" search-url="https://www.google.com/search?q=%s" context-column="category"
allow-nesting="false" span-creation="true" aggregation="tagg" validates="required all_tokens"
gold="true"></cml:text_annotation>
"""


jobs_data = {
    'what_is_greater': {
        'cml': what_is_greater,
        'data_generator': generate_csv_data_what_is_greater,
        'fields': 'what_is_greater'
        },
    'server_side_validation': {
        'cml': server_side_validation,
        'data_generator': generate_csv_data_what_is_greater,
        'fields': 'what_is_greater'
        },
    'server_side_validation_simple_case': {
        'cml': server_side_validation_simple_case,
        'data_generator': generate_csv_data_what_is_greater,
        'fields': 'A single checkbox'
        },
    'server_side_validation_complicated_case': {
        'cml': server_side_validation_complicated_case,
        'data_generator': generate_csv_data_what_is_greater,
        'fields': ['human', 'cat', 'dog']
        },
    'server_side_validation_liquid_case': {
        'cml': server_side_validation_liquid_case,
        'data_generator': generate_csv_data_liquid,
        'fields': 'server_side_validation_liquid_case'
        },
    'nab_meaning': {
        'cml': nab_meaning,
        'data_generator': generate_csv_data_nab_meaning,
        'fields': None  # todo
        },
    'image_annotation': {
        'cml': image_annotation,
        'data_generator': generate_csv_data_catdog,
        'ontology': [
          {'description': "", 'class_name': "Cat", 'display_color': "#FF1744", 'relationship_types': []},
          {'description': "", 'class_name': "Dog", 'display_color': "#651FFF", 'relationship_types': []}
          ],
        'fields': ['nothing_to_box', 'annotation']
        },
    'video_annotation': {
        'cml': video_annotation,
        'data_generator': generate_csv_data_hands,
        'ontology': [
          {'description': "", 'class_name': "Right Hand", 'display_color': "#FF1744", 'relationship_types': []},
          {'description': "", 'class_name': "Left Hand", 'display_color': "#651FFF", 'relationship_types': []}
          ],
        'fields': ['myvideo']
        },
    'text_annotation': {
        'cml': text_annotation,
        'data_generator': generate_csv_data_text_annotation,
        'ontology': [
          {'description': "", 'class_name': "verb", 'display_color': "#FF1744", 'relationship_types': []},
          {'description': "", 'class_name': "noun", 'display_color': "#C1561A", 'relationship_types': []},
          {'description': "", 'class_name': "punctuation", 'display_color': "#EFBB61", 'relationship_types': []},
          {'description': "", 'class_name': "other", 'display_color': "#651FFF", 'relationship_types': []}
          ],
        'fields': ['annotation']
        },

}
