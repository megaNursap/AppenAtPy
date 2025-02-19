audio_annotation_cml = """
<cml:audio_annotation source-data="{{audio_url}}" name="Annotate the thing" validates="required" />
"""

audio_annotation_peer_review_cml = """
<cml:audio_annotation source-data="{{audio_url}}" review-from="{{annotate_the_thing}}" name="Annotate the audio" validates="required" />
"""

image_annotation_cml = """
<cml:checkbox label="Nothing to box" aggregation="agg" gold="true" value="nothing_to_box" />
<cml:shapes label="Draw Shapes" name="annotation" type="['box','polygon','dot','line','ellipse']"
source-data="{{image_url}}" box-threshold="0.7" class-threshold="0.7" 
ontology="true" validates="required" only-if="!nothing_to_box" class-agg="agg" box-agg="0.7"
allow-box-rotation="false" crosshair="false" dot-threshold="0.7" dot-distance="10" polygon-threshold="0.7" 
line-threshold="0.7" ellipse-threshold="0.7" line-distance="10" allow-ellipse-rotation="false" gold="true" output-format="json" ></cml:shapes>
"""

image_annotation_cml_focus_to_review_data1 = """
<cml:shapes label="Draw Shapes" name="annotation" type="['box']" source-data="{{image_url}}" box-threshold="0.7" 
ontology="true" class-threshold="0.7" validates="required" class-agg="agg" box-agg="0.7" allow-box-rotation="true" output-format="json" 
 gold="true" />
"""

image_annotation_cml_focus_to_review_data2 = """
<cml:shapes label="Draw Shapes" name="annotation-rw" type="['box']" source-data="{{image_url}}" box-threshold="0.7" 
ontology="true" class-threshold="0.7" validates="required" class-agg="agg" box-agg="0.7" allow-box-rotation="false" output-format="json"  
 gold="true" review-data="{{annotation}}" task-type="qa"/>
"""

image_annotation__report_url_cml = """
<cml:checkbox label="Nothing to box" aggregation="agg" gold="true" value="nothing_to_box" />
<cml:shapes label="Draw Shapes" name="annotation" type="['box','polygon','dot','line','ellipse']"
source-data="{{image_url}}" box-threshold="0.7" class-threshold="0.7"
ontology="true" validates="required" only-if="!nothing_to_box" class-agg="agg" box-agg="0.7"
allow-box-rotation="false" crosshair="false" dot-threshold="0.7" dot-distance="10" polygon-threshold="0.7" 
line-threshold="0.7" ellipse-threshold="0.7" line-distance="10" allow-ellipse-rotation="false" gold="true" output-format="url" ></cml:shapes>
"""

image_annotation_only_if_cml = """
<cml:shapes type="['box']" source-data="{{image_url}}" name="annotation" label="" class-threshold="0.2" crosshair="true" box-threshold="0.2" class-agg="agg" box-agg="0.5" gold="true"/>  
<cml:radios label="Sample radio buttons:" validates="required">
  <cml:radio label="Radio 1" value="radio_1" />
  <cml:radio label="Radio 2" value="radio_2" />
</cml:radios>
"""

tile_image_annotation_cml = """
<cml:tiled_image_annotation name="annotation" source-data="{{source_data}}" canvas-options="{{canvas_options}}" validates="required" type="['box', 'polygon', 'line', 'dot']"/>
"""

image_rotation_cml = """
<cml:shapes type="['box','ellipse','polygon','dot','line']" 
source-data="{{image_url}}" validates="required" ontology="true" name="annotation" label="Annotate this image" 
class-threshold="0.7" box-threshold="0.7" class-agg="agg" box-agg="0.7" ellipse-threshold="0.7" ellipse-agg="0.7" 
polygon-threshold="0.7" polygon-agg="0.7" dot-distance="10" dot-threshold="0.7" dot-agg="10" line-distance="10" line-threshold="0.7" 
line-agg="10"  output-format="url" allow-image-rotation="true"></cml:shapes>
"""

image_rotation_peer_review_cml = """
<cml:shapes label="Draw Shapes" name="annotation2" type="['box','polygon','dot','line','ellipse']"
source-data="{{image_url}}" review-from="{{annotation}}" box-threshold="0.7" class-threshold="0.7"
ontology="true" validates="required" class-agg="agg" box-agg="0.7" 
allow-box-rotation="true" crosshair="false" dot-threshold="0.7" dot-distance="10" polygon-threshold="0.7" 
line-threshold="0.7" ellipse-threshold="0.7" line-distance="10" allow-ellipse-rotation="false" gold="true" output-format="url" allow-image-rotation="true"></cml:shapes>
"""

image_rotation_peer_review_error_title = """
<cml:shapes label="Draw Shapes" name="annotation2" type="['box','polygon','dot','line','ellipse']"
source-data="{{image_url}}" review-data="{{annotation}}" task-type="qa" box-threshold="0.7" class-threshold="0.7"
ontology="true" validates="required" class-agg="agg" box-agg="0.7" 
allow-box-rotation="true" crosshair="false" dot-threshold="0.7" dot-distance="10" polygon-threshold="0.7" 
line-threshold="0.7" ellipse-threshold="0.7" line-distance="10" allow-ellipse-rotation="false" gold="true" output-format="url" allow-image-rotation="false"></cml:shapes>
"""

ontology_attribute_url_output = """
<cml:checkbox label="Nothing to box" aggregation="all" gold="true" value="nothing_to_box"></cml:checkbox>
<cml:shapes label="Draw Shapes" name="annotation" type="['box','polygon','dot','line','ellipse']"
source-data="{{image_url}}" box-threshold="0.7" class-threshold="0.7" 
ontology="true" validates="required" only-if="!nothing_to_box" class-agg="all" box-agg="all" 
allow-box-rotation="false" crosshair="false" dot-threshold="0.7" dot-distance="10" polygon-threshold="0.7" line-threshold="0.7" ellipse-threshold="0.7" line-distance="10" allow-ellipse-rotation="false" gold="true" output-format="url" polygon-agg="all" dot-agg="all" line-agg="all" ellipse-agg="all"></cml:shapes>
"""

ontology_attribute_json_output = """
<cml:checkbox label="Nothing to box" aggregation="all" gold="true" value="nothing_to_box"></cml:checkbox>
<cml:shapes label="Draw Shapes" name="annotation" type="['box','polygon','dot','line','ellipse']" 
source-data="{{image_url}}" box-threshold="0.7" class-threshold="0.7" 
ontology="true" validates="required" only-if="!nothing_to_box" class-agg="all" box-agg="all" 
allow-box-rotation="false" crosshair="false" dot-threshold="0.7" dot-distance="10" polygon-threshold="0.7" line-threshold="0.7" ellipse-threshold="0.7" line-distance="10" allow-ellipse-rotation="false" gold="true" output-format="json" polygon-agg="all" dot-agg="all" line-agg="all" ellipse-agg="all"></cml:shapes>
"""

image_annotation_peer_review_cml = """
<cml:shapes label="Draw Shapes" name="annotation2" type="['box','polygon','dot','line','ellipse']"
source-data="{{image_url}}" review-data="{{annotation}}" task-type="qa" box-threshold="0.7" class-threshold="0.7"
ontology="true" validates="required" class-agg="agg" box-agg="0.7" 
allow-box-rotation="true" crosshair="false" dot-threshold="0.7" dot-distance="10" polygon-threshold="0.7" 
line-threshold="0.7" ellipse-threshold="0.7" line-distance="10" allow-ellipse-rotation="false" gold="true" output-format="url" allow-image-rotation="true"></cml:shapes>
"""

image_transcription_ocr_cml = """
<cml:image_transcription label="label this job" name="label this" type="['box']"
source-data="{{image_url}}" box-threshold="0.7" class-threshold="0.7" ontology="true"
ocr="true" validates="required" class-agg="agg" box-agg="0.7" allow-box-rotation="false"
crosshair="true" gold="true" aggregation="agg" output-format="url" ></cml:image_transcription>
"""

image_transcription_language_attribute_cml = """
<cml:image_transcription type="['box']" source-data="{{image_url}}" validates="required" 
class-threshold="0.7" name="transcription" label="Transcribe this image" ocr="true" 
box-threshold="0.7" ontology="true" language="{{lang}}"/>
"""

image_transcription_language_attribute_ocr_false_cml = """
<cml:image_transcription type="['box']" source-data="{{image_url}}" validates="required" 
class-threshold="0.7" name="transcription" label="Transcribe this image" ocr="false" 
box-threshold="0.7" ontology="true" language="{{lang}}"/>
"""

image_transcription_withoutocr_cml = """
<cml:image_transcription label="label this job" name="label this" type="['box']"
source-data="{{image_url}}" box-threshold="0.7" class-threshold="0.7" ontology="true"
ocr="false" validates="required" class-agg="agg" box-agg="0.7" allow-box-rotation="false" 
crosshair="true" gold="true" aggregation="agg"></cml:image_transcription>
"""

image_transcription_peer_review_cml = """
<cml:image_transcription label="label this job" name="label this please" review-data="{{label_this}}" task-type="qa" type="['box']"
source-data="{{image_url}}" box-threshold="0.7" class-threshold="0.7" ontology="true"
ocr="false" validates="required" class-agg="agg" box-agg="0.7" allow-box-rotation="false" 
crosshair="true" gold="true" aggregation="agg"></cml:image_transcription>
"""

image_transcription_peer_review_cml_ontology_mismatch = """
<cml:image_transcription name="annotations" review-data="{{review_annotation}}" task-type="qa" type="['box']" 
source-data="{{source_data}}" box-threshold="0.7" ontology="true" class-threshold="0.7" validates="required" 
box-agg="0.7" allow-box-rotation="true" allow-image-rotation="true" output-format="url"/>
"""

image_transcription_image_rotation_cml = """
<cml:image_transcription label="label this job" name="label this" type="['box']"
source-data="{{image_url}}" box-threshold="0.7" class-threshold="0.7" ontology="true"
ocr="true" validates="required" class-agg="agg" box-agg="0.7" allow-box-rotation="false"
crosshair="true" allow-image-rotation="true" output-format="url" gold="true" aggregation="agg"></cml:image_transcription>
"""

image_transcription_rotation_peer_review_cml = """
<cml:image_transcription label="label this job" name="label this please" review-data="{{label_this}}" task-type='qa' type="['box']"
source-data="{{image_url}}" box-threshold="0.7" class-threshold="0.7" ontology="true"
ocr="false" validates="required" class-agg="agg" box-agg="0.7" allow-box-rotation="false" 
crosshair="true" gold="true" allow-image-rotation="true" output-format="url" aggregation="agg"></cml:image_transcription>
"""

plss_cml = """
<cml:image_segmentation label="Label the pixels!" name="annotation" type="['brush', 'polygon', 'fill', 'magic-wand']" source-data="{{image_url}}" validates="required" crosshair="true"/>
"""

plss_invalid_cml = """
<cml:pixellabel label="Label this image" name="annotation" source-data="{{image_url}}" validates="yes"/>
"""

plss_peer_review_cml = """
<cml:image_segmentation label="Label the pixels!" name="orgi_annotation" review-data="{{annotation}}" task-typy="qa" type="['brush', 'polygon', 'fill', 'magic-wand']" source_data="{{image_url}}" validates="required" crosshair="true" task-type='qa'/>
"""

text_annotation_invalid_source_type_cml = """
<cml:text_annotation source-data="{{text}}" name="my_annotations" tokenizer="spacy" source-type="ss" search-url="https://www.google.com/search?q=%s" validates="required" label="Label Text" span-creation="true" aggregation="tagg" language="en" allow-nesting="false"></cml:text_annotation>
"""

text_annotation_invalid_tokenizer_cml = """
<cml:text_annotation source-data="{{text}}" name="my_annotations" tokenizer="none" source-type="text" search-url="https://www.google.com/search?q=%s" validates="required" label="Label Text" span-creation="true" aggregation="tagg" language="en" allow-nesting="false"></cml:text_annotation>
"""

text_annotation_cml = """
<cml:text_annotation source-data="{{text}}" name="my_annotations" tokenizer="spacy" source-type="text" search-url="https://www.google.com/search?q=%s" validates="required" label="Label Text" span-creation="true" aggregation="tagg" language="en" allow-nesting="false"></cml:text_annotation>
"""

text_annotation_allow_nesting_cml = """
<cml:text_annotation source-data="{{text}}" name="my_annotations" tokenizer="spacy" source-type="text" search-url="https://www.google.com/search?q=%s" validates="required" label="Label Text" span-creation="true" allow-nesting="true" aggregation="tagg" language="en"/>
"""

text_annotation_flat_cml = """
<cml:text_annotation label="Label Text" name="annotation" source-type="text" source-data="{{data_column}}" tokenizer="spacy" language="en" search-url="https://www.google.com/search?q=%s" span-creation="true" aggregation="tagg" validates="required" gold="true" allow-nesting="false"/>
"""

text_annotation_nested_cml = """
<cml:text_annotation label="Label Text" name="nested_annotation" source-type="text" source-data="{{data_column}}" tokenizer="spacy" language="en" search-url="https://www.google.com/search?q=%s" allow-nesting="true" span-creation="true" aggregation="tagg" validates="required" gold="true"/>
"""

video_annotation_object_tracking_cml = """
<cml:video_shapes source-data="{{video_url}}" type="['box']" name="video_annotation" validates="required" labels-required="true" crosshair="true" require-views="false"  output-format="url" assistant="object_tracking"/>
"""

video_annotation_linear_interpolation_cml = """
<cml:video_shapes source-data="{{video_url}}" type="['box','polygon','dot','line', 'point-box', 'ellipse']" name="video_annotation" validates="required" require-views="false" labels-required="true" crosshair="true" assistant="linear_interpolation"/>
"""

video_annotation_frame_rotation_cml = """
<cml:video_shapes source-data="{{video_url}}" type="['box','polygon','dot','line', 'point-box']" 
name="video_annotation" validates="required" require-views="false" labels-required="true" 
crosshair="true" assistant="linear_interpolation" output-format="url" allow-frame-rotation="true"/>
"""

video_annotation_peer_review_cml = """
<cml:video_shapes source-data="{{video_url}}" type="['box','polygon','dot','line', 'point-box']" 
name="video_annotations" review-data="{{video_annotation}}" validates="required" require-views="false" 
labels-required="true" crosshair="true" assistant="linear_interpolation" task-type="qa"/>
"""

video_annotation_peer_review_oa_objecttracking_cml = """
<cml:video_shapes source-data="{{video_url}}" type="['box']" name="video_annotations" review-data="{{video_annotation}}" validates="required"  task-type='qa' require-views="false" labels-required="true" crosshair="true" assistant="object_tracking"/>
"""

video_annotation_frame_rotation_peer_review_cml = """
<cml:video_shapes source-data="{{video_url}}" type="['box','polygon','dot','line', 'point-box']" name="video_annotations" review-data="{{video_annotation}}" task-type='qa' validates="required" require-views="false" labels-required="true" crosshair="true" assistant="linear_interpolation" allow-frame-rotation="true"/>
"""

video_annotation_invalid_cml = """
<cml:video_shapes source-data="{{video_url}}" type="['box','dot']" name="video_annotation" review-from="{{annotation}}" validates="required" labels-required="true" crosshair="true" assistant="object_tracking"/>
"""

audio_transcription_full_Screen_cml = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" audio-annotation-data="{{annotate_the_audio}}" name="audio_transcription" force-fullscreen="true" type="['labeling', 'transcription']"/>"""

audio_transcription_cml = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" audio-annotation-data="{{annotate_the_audio}}" name="audio_transcription" type="['labeling', 'transcription']"/>"""
audio_transcription_span_even_cml = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" audio-annotation-data="{{annotate_the_audio}}" name="audio_transcription" type="['transcription']"/>"""


audio_transcription_invalid_audio_url_cml = """<cml:audio_transcription validates="required" source-data="{{audio_urls}}" audio-annotation-data="{{annotate_the_audio}}" name="audio_transcription" type="['labeling', 'transcription']"/>"""

audio_transcription_invalid_audio_annotation_data_cml = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" audio-annotation-data="{{annotate_the_audios}}" name="audio_transcription" type="['labeling', 'transcription']"/>"""

audio_transcription_segments_data_cml = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" segments-data="{{annotate_the_audio}}" name="audio_transcription" type="['labeling', 'transcription']"/>"""


audio_transcription_review_data_not_found_cml = """<cml:audio_transcription validates="required" source-data="{{audio_url}}"
review-data="{{audio_transcriptions}}" task-type="qas" name="new_audio_transcription" type="['labeling', 'transcription']"/>
"""

audio_transcription_peer_review_cml = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" review-data="{{audio_transcription}}" task-type="qa" name="new_audio_transcription" type="['labeling', 'transcription']"/>
"""

audio_transcription_review_raw_text_cml = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" review-data="{{transcription}}" task-type="qa" name="new_audio_transcription" type="['labeling', 'transcription']"/>
"""

audio_transcription_peer_review_report_cml = """<cml:audio_transcription validates="required" source-data="{{audio_url}}"
review-data="{{audio_transcription}}" task-type="qa" name="new_audio_transcription" type="['transcription']"/>
"""

audio_transcription_subset_cml = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" 
review-data="{{audio_transcription}}"  task-type="qa" name="new_audio_transcription" subset="0.3" type="['labeling', 'transcription']"/>
"""

audio_transcription_subset_cml_2 = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" 
review-data="{{audio_transcription}}" task-typy="qa" name="new_audio_transcription" subset="0.5" type="['labeling', 'transcription']"/>
"""

audio_transcription_subset_cml_outside_range = """<cml:audio_transcription validates="required" source-data="{{audio_url}}"
review-data="{{audio_transcription}}" taask-typy="qa" name="new_audio_transcription" subset="1.5" type="['labeling', 'transcription']"/>
"""

audio_transcription_subset_cml_without_review_from = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" audio-annotation-data="{{annotate_the_thing}}"
name="new_audio_transcription" subset="0.5" type="['labeling', 'transcription']"/>
"""

audio_transcription_sda_cml = """<cml:audio_transcription validates="required" source-data="{{audio_url|secure: 's3_test'}}" audio-annotation-data="{{annotate_the_audio}}" name="audio transcription" type="['labeling', 'transcription']"/>"""

audio_transcription_peer_review_correct_task = """<cml:audio_transcription validates="required" source-data="{{audio_url}}"  review-data="{{audio_transcription}}" name="audio_transcription_rd" task-type="correction" type="['labeling', 'transcription']"/>"""

audio_transcription_acknowledge_task_type = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" name="audio_transcription_acknowledgment" task-type="acknowledge" review-data="[{{audio_transcription_original}}, {{audio_transcription_correction}}]" type="['labeling', 'transcription']"/>"""

audio_transcription_arbitration_task_type = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" name="audio_transcription_arbitration" task-type="arbitration" review-data="[{{audio_transcription_original}}, {{audio_transcription_correction}}, {{audio_transcription_acknowledgment}}]" type="['labeling', 'transcription']"/>"""


cml_group_aggregation = """
<cml:group multiple="true" aggregation="true" group_name="group1" >
<cml:text name="output_first_name" label="First Name:" aggregation="all"></cml:text>
<cml:text name="output_last_name" label="Last Name:" validates="required"></cml:text>
</cml:group>
"""

cml_group_aggregation_missing_group_name = """
<cml:group multiple="true" aggregation="true">
<cml:text name="first_name" label="First Name:" aggregation="all"></cml:text>
<cml:text name="last_name" label="Last Name:" validates="required"></cml:text>
</cml:group>
 """

cml_group_aggregation_missing_aggregation = """
<cml:group multiple="true" group_name="group1">
<cml:text name="first_name" label="First Name:" aggregation="all"></cml:text>
<cml:text name="last_name" label="Last Name:" validates="required"></cml:text>
</cml:group>
"""

cml_group_aggregation_duplicate_name = """
<cml:group multiple="true" aggregation="true" group_name="group1" name="name" >
<cml:text name="first_name" label="First Name:" aggregation="all"></cml:text>
<cml:text name="last_name" label="Last Name:" validates="required"></cml:text>
</cml:group>
"""

file_uplaod_cml_mandatory = """<cml:file_upload name="file upload" validates="required"/>"""
file_upload_cml_all = """<cml:file_upload name="file upload" validates="required" min-size="5" max-size="10.5" allowed-extensions="['JPEG', 'PNG']" />"""

quiz_work_mode_switch_cml = """
<div class="html-element-wrapper">
  <p>Column1: {{column_1}}</p>
  <p>Column2: {{column_2}}</p>
  <p>marker: {{marker}}</p>
</div>
<cml:radios label="What is greater?" validates="required" name="what_is_greater" gold="true">
  <cml:radio label="Column1" value="col1" />
  <cml:radio label="Column2" value="col2" />
  <cml:radio label="Equals" value="equals" />
</cml:radios>
"""

taxonomy_cml = """<cml:taxonomy_beta name="my_taxonomy_example" label="Topics" aggregation="agg" validates="required" source="taxonomy_1"/> """
taxonomy_cml_without_source = """<cml:taxonomy_beta name="my_taxonomy_example" label="Topics" aggregation="agg" validates="required"/> """

taxonomy_cml_multi_select = """<cml:taxonomy_beta name="my_taxonomy_example" label="Topics" aggregation="agg" validates="required" multi-select="true" source="taxonomy_1"/> """
taxonomy_cml_select_all = """<cml:taxonomy_beta name="my_taxonomy" label="Topics" aggregation="agg" validates="required" select-all="true" source="taxonomy_1"/> """
taxonomy_cml_sort = """<cml:taxonomy_beta name="my_taxonomy" label="Topics" aggregation="agg" validates="required" sort="true" source="taxonomy_1"/> """

taxonomy_shape_cml = """<cml:taxonomy_beta name="my_taxonomy" label="Topics" aggregation="agg" validates="required" 
source="taxonomy_1"/> <cml:shapes type="['box']" source-data="{{image_url}}" validates="required" 
name="shape_with_ontology" label="Shape with ontology" class-threshold="0.62" box-threshold="0.7" class-agg="all" 
box-agg="0.72" allow-box-rotation="false" ontology="true" /> """

taxonomy_text_annotation_cml = """<cml:text_annotation source-data="{{text}}" name="annotation_rev" source-type="text" tokenizer="spacy" search-url="https://www.google.com/search?q=%s" validates="required" label="Label Text" span-creation="true" aggregation="tagg"/>
                                  <cml:taxonomy_beta name="my_taxonomy" validates="required" select-all="true" multi-select="true" sort="true" source="taxonomy_2" />"""

taxonomy_source_url_liquid = """<cml:taxonomy_beta name="my_taxonomy" validates="required" source="{{url}}"/>"""
taxonomy_source_url_ref = """<cml:taxonomy_beta name="my_taxonomy" validates="required" source="https://annotation-sandbox.s3.amazonaws.com/correct_tax.json"/>"""

taxonomy_peer_review_incorrect_task_type="""<cml:taxonomy_tool name='my_taxonomy_qa' validates='required' multi-select='true' review-data='{{my_taxonomy}}' task-type='qas'/>"""
taxonomy_peer_review="""<cml:taxonomy_tool name='my_taxonomy_qa' validates='required' multi-select='true' review-data='{{my_taxonomy}}' task-type='qa'/>"""

audio_transcription_beta = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" segments-data="{{annotate_the_audio}}" name="audio_transcription" type="['labeling', 'transcription']" beta='true' allow-timestamping='true'/>"""

audio_transcription_one_segment_beta = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" name="audio_transcription" type="['labeling', 'transcription']" beta='true' allow-timestamping='true'/>"""

audio_transcription_beta_listen_to = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" segments-data="{{annotate_the_audio}}" name="audio_transcription" type="['labeling', 'transcription']" beta='true' allow-timestamping='true' listen-to='[[0, 0.2, 0.1], [0.2, 1, 0.5]]'/>"""

audio_transcription_one_segment_beta_listen_to = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" name="audio_transcription" type="['labeling', 'transcription']" beta='true' allow-timestamping='true' listen-to='[[0, 0.2, 0.1], [0.2, 0.7, 0.5], [0.7, 1, 0.2]]'/>"""


audio_transcription_peer_review_one_segment = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" review-data="{{audio_transcription}}" task-type="qa" name="new_audio_transcription" type="['labeling', 'transcription']" beta="true"/>"""
audio_transcription_peer_review_multi_segment = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" review-data="{{audio_transcription}}" task-type="qa" name="new_audio_transcription" type="['labeling', 'transcription']" beta="true"/>"""

audio_transcription_peer_review_multi_segment_large_data = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" review-data="{{audio_transcription}}" task-type="qa" name="new_audio_transcription" beta="true" type="['transcription']" listen-to="[[0,1,0.01]]"/>"""

audio_transcription_one_segment_with_speed_attribute = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" name="audio_transcription" type="['labeling', 'transcription']" beta='true' allow-timestamping='true' speed="[1,4,6]"/>"""

audio_transcription_one_segment_beta_segmentation = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" name="audio_transcription" type="['segmentation']" beta='true'/>"""
audio_transcription_beta_data_validation = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" segments-data="{{annotate_the_audio}}" name="audio_transcription" type="['transcription']" listen-to="[[0,1,0]]" beta='true' allow-timestamping='true'/>"""

audio_transcription_one_segment_no_listen_to = """<cml:audio_transcription validates="required" source-data="{{audio_url}}" name="audio_transcription" type="['transcription']" beta='true' listen-to="[[0,1,0]]" allow-timestamping='true'/>"""
