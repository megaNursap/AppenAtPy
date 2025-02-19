ontology = [
  {
    "display_color": "#9A2517",
    "description": "<h5>testing info icon when description is available</h5>",
    "class_name": "Person",
    "allow_transcription": 1
  },
  {
    "display_color": "#C1561A",
    "description": "<p>another description</p>",
    "class_name": "Pet",
    "allow_transcription": 1
  },
  {
    "display_color": "#BD882C",
    "description": "",
    "class_name": "Background",
    "allow_transcription": 1
  },
  {
    "display_color": "#819356",
    "description": "",
    "class_name": "Noise",
    "allow_transcription": 1
  },
  {
    "display_color": "#6A1D7A",
    "description": "",
    "class_name": "Male voice",
    "allow_transcription": 1
  },
  {
    "display_color": "#CD584A",
    "description": "",
    "class_name": "Female voice",
    "allow_transcription": 1
  },
  {
    "display_color": "#4A8676",
    "description": "",
    "class_name": "Dog",
    "allow_transcription": 1
  },
  {
    "display_color": "#0E7795",
    "description": "",
    "class_name": "Cat",
    "allow_transcription": 1
  },
  {
    "display_color": "#401A87",
    "description": "",
    "class_name": "Music",
    "allow_transcription": 1
  },
  {
    "display_color": "#F4894E",
    "description": "",
    "class_name": "Kids",
    "allow_transcription": 1
  }
]

workflow_audio_annotation_cml= '<cml:audio_annotation source-data="{{audio_url}}" name="annotate the audio" validates="required" aggregation="agg"></cml:audio_annotation>'

workflow_audio_transcription_cml = '<cml:audio_transcription validates="required" source-data="{{audio_url}}" audio-annotation-data="{{annotate_the_audio}}" name="audio_transcription" aggregation="agg"/>'

workflow_audio_transcription_peerreview_cml = '<cml:audio_transcription validates="required" source-data="{{audio_url}}" audio-annotation-data="{{audio_transcription}}" review-data="{{audio_transcription}}" name="audio_transcription_review_from" aggregation="agg" intervals="true" task-type="qa"></cml:audio_transcription>'
