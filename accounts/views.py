from django.http import JsonResponse

def register(request):
    return JsonResponse({"message": "register endpoint"})

def login(request):
    return JsonResponse({"message": "login endpoint"})

def logout(request):
    return JsonResponse({"message": "logout endpoint"})

def me(request):
    return JsonResponse({"message": "me endpoint"})