from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from social.exceptions import SocialAuthBaseException, \
    NotAllowedToDisconnect, AuthException, AuthFailed, \
    AuthCanceled, AuthUnknownError, AuthAlreadyAssociated, \
    AuthForbidden

class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        self.strategy = getattr(request, 'social_strategy', None)
        if self.strategy is None or self.raise_exception(request, exception):
            return
        print "---------------------------------------"
        print exception
        return redirect('misc.views.err404', kwargs={'messages':['Ouchie. Social', message]})
        if isinstance(exception, AuthAlreadyAssociated):
            return redirect('misc.views.err404', kwargs={'messages':['Ouchie. Social', message]})
        if 1 or isinstance(exception, SocialAuthBaseException):
            message = self.get_message(request, exception)
            return redirect('misc.views.err404', kwargs={'messages':['Ouchie. Social', message]})

        raise exception