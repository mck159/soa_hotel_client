from django.shortcuts import redirect
def tokenRequired(func):
    def func_wrapper(request):
        token = request.COOKIES['token']
        if(token == 'OKI'):
            return func(request)
        else:
            response = redirect('login')
            response['Location'] += '?warnings=login_required'
            return response
        #return HttpResponse(args[0].session.__str__())

    return func_wrapper
