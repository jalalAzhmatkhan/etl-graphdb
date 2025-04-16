from typing import Any, Literal, Optional

from google import genai

from settings import settings

class GeminiClient:
    """
    GeminiClient is a wrapper around the Google Gemini API.
    """

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def generate_response(
        self,
        attachment: Optional[Any] = None,
        attachment_mime_type: Optional[str] = None,
        model: Literal[
            "gemini-2.5-pro-preview-03-25",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemini-1.5-pro",
            "imagen-3.0-generate-002",
        ] = "gemini-2.0-flash",
        *,
        prompt: str
    ) -> Optional[str]:
        """
        Generate a response from the Gemini API.
        :param attachment: The attachment to send to the API.
        :param attachment_mime_type: The MIME type of the attachment.
        :param model: The model to use for generating the response.
        :param prompt: The prompt to send to the API.
        :return: The generated response.
        """
        sent_contents = [prompt]
        if attachment:
            sent_contents.append({
                "mime_type": attachment_mime_type,
                "data": attachment
            })
        gemini_response = self.client.models.generate_content(
            model=model,
            contents=sent_contents
        )
        return gemini_response.text

gemini_client = GeminiClient()
