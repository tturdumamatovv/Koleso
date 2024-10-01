from django.utils import translation


class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.META.get('HTTP_ACCEPT_LANGUAGE', 'ru').split(',')[0]
        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        response = self.get_response(request)

        translation.deactivate()

        return response
