POST_ANNOTATION = "/annotations"
GET_ANNOTATION = "/annotations/%s?job_id=%s&expiration_time=%s"
POST_IMAGE_ANNOTATION = "/image_annotations"
PUT_IMAGE_ANNOTATION = "/image_annotations/generate_expiring_url"
PUT_SECURELINK = "/secure_links/expiring_url"
GET_SECURELINK = "/secure_links?token=%s"
HEALTH_CHECK = "/health_check"

URL = "https://annotation-super-saver.internal.{}.cf3.us"
