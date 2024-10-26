from django.shortcuts import render,redirect
from user.models import CustomUser
from django.db.models import Q
from django.contrib.auth import login,authenticate,logout
from django.views.decorators.cache import never_cache


# Create your views here.
@never_cache
def admin_home(request):
    if request.user.is_authenticated and request.user.is_staff:
         
      return render(request,'admin/admin_index.html')
    else:
          return redirect('user_app:index')
@never_cache
def user_details(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search')
        if query:
            user = CustomUser.objects.all().exclude(is_staff = True).filter(Q(first_name__icontains = query) | Q(email__icontains = query))
            return render(request,'admin/admin_user_management.html',{'user':user,'query':query})
        else:
            user=CustomUser.objects.all().exclude(is_staff = True)
            return render(request,'admin/admin_user_management.html',{'user':user})
    return redirect('user_app:index')
@never_cache
def user_block(request,id):
  if request.user.is_authenticated and request.user.is_staff:
    if request.method == 'POST':
        user = CustomUser.objects.get(id = id)
        print(user)
        if user.is_block:
            print(user.is_block)
            user.is_block = False
            user.save()
        elif not user.is_block:
            user.is_block = True
            user.save()
    return redirect('admin_app:user_details')
  return redirect('user_app:index')
@never_cache
def admin_logout(request):
 if request.user.is_authenticated and request.user.is_staff:
    if request.method=='POST':
        logout(request)
        return redirect('user_app:user_login')
 else:
          return redirect('user_app:index')

