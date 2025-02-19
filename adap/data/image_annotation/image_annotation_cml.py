shapes_json_report = """
<cml:shapes type="['box','ellipse','polygon','dot','line']" source_data="{{image_url}}" 
validates="required" ontology="true" name="annotation" 
label="Annotate this image" class-threshold="0.7" 
box-threshold="0.7" class-agg="agg" box-agg="0.7" 
ellipse-threshold="0.7" ellipse-agg="0.7" polygon-threshold="0.7"
 polygon-agg="0.7" dot-distance="10" dot-threshold="0.7" 
 dot-agg="10" line-distance="10" line-threshold="0.7" line-agg="10"
  output-format="url" allow-box-rotation="false" allow-ellipse-rotation="false">
  </cml:shapes>
"""