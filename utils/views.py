from rest_framework.renderers import JSONRenderer


class EnvelopedJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context and renderer_context["response"].status_code < 400:
            enveloped_data = {"success": True, **data} if data else {"success": True}
        else:
            enveloped_data = {"success": False, **data} if data else {"success": False}
        return super().render(enveloped_data, accepted_media_type, renderer_context)
