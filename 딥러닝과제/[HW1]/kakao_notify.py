import requests
from typing import Optional

KAKAO_MEMO_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"


def send_kakao_memo(access_token: str, message_text: str) -> Optional[str]:
	"""Send a KakaoTalk memo to self using the default template.

	Returns None on success, or an error message string on failure.
	"""
	if not access_token:
		return "Missing Kakao access token"

	headers = {
		"Authorization": f"Bearer {access_token}",
		"Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
	}

	# Kakao default template requires JSON string for template_object
	template_object = {
		"object_type": "text",
		"text": message_text,
		"link": {"web_url": "https://developers.kakao.com"},
	}

	try:
		resp = requests.post(
			KAKAO_MEMO_URL,
			headers=headers,
			data={"template_object": requests.utils.requote_uri(str(template_object).replace("'", '"'))},
			timeout=15,
		)
		if resp.status_code != 200:
			return f"Kakao API error {resp.status_code}: {resp.text}"
		return None
	except Exception as e:
		return f"Kakao request failed: {e}"


