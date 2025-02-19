ontology = [
   {
      "display_color": "#9A2517",
      "description": "<h5>testing info icon when description is available<\/h5>\n",
      "class_name": "Person"
   },
   {
      "display_color": "#C1561A",
      "description": "<p>another description<\/p>\n",
      "class_name": "Pet"
   },
   {
      "display_color": "#BD882C",
      "class_name": "Background"
   },
   {
      "display_color": "#819356",
      "class_name": "Noise"
   },
   {
      "display_color": "#6A1D7A",
      "class_name": "Male voice"
   },
   {
      "display_color": "#CD584A",
      "class_name": "Female voice"
   },
   {
      "display_color": "#4A8676",
      "class_name": "Dog"
   },
   {
      "display_color": "#0E7795",
      "class_name": "Cat"
   },
   {
      "display_color": "#401A87",
      "class_name": "Music"
   },
   {
      "display_color": "#F4894E",
      "class_name": "Kids"
   }
]

required_cml = """
<cml:video_transcription source-data="{{url}}" validates="required" name="video transcription"/>
"""

full_cml = """
<cml:video_transcription source-data="{{url}}" validates="required" name="video transcription" turn-id="Select turn ID" ontology="true" allow-transcription="true" />
"""

invalid_cml = """
<cml:video_transcription source-data="{{url}}" validates="required" name="video transcription" turn-id="Select turn ID" ontology="yes" allow-transcription="no" />
"""