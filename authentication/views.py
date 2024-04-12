from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout


def signup(request):
    if request.method=='POST':
        username, email, pass1, pass2 = request.POST['username'], request.POST['email'], request.POST['pass1'], request.POST['pass2']
               
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('signup')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username Already Taken!!")
            return redirect('signup')
        
        if len(username)>20:
            messages.error(request, "Name must be under 20 charcters!!")
            return redirect('signup')
                
        if len(pass1)<8:
            messages.error(request, "Password must be atleast 8 charcters!!")
            return redirect('signup')

        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('signup')
        
        user=User.objects.create_user(username, email, pass1)
        user.first_name=username
        user.save()
        messages.success(request, 'Your account has been created successfully')
        return redirect('login')
    return render(request,'authentication/signup.html')
    
def login(request):
    if request.method=='POST':
        email, password = request.POST['email'], request.POST['password']
        try:
            user= User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')
            return redirect('login')
        if user is not None and user.check_password(password):
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('login')
    return  render(request,'authentication/login.html')
def logout(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')