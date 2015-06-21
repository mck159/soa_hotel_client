from django.shortcuts import redirect
def tokenRequired(func):
    def func_wrapper(*args, **kwargs):
        if not 'token' in args[0].COOKIES or not args[0].COOKIES['token']:
            response = redirect('login')
            response['Location'] += '?warnings=Login required'
            return response
        return func(*args, **kwargs)

    return func_wrapper
