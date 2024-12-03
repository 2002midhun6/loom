from django.shortcuts import render,redirect
from . validate import Authentication_check
from . models import *
import random
from django.core.mail import EmailMessage
from django.contrib import messages
from datetime import datetime,timedelta
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth import get_user_model
from django.views.decorators.cache import never_cache
from product.models import *
from django.utils import timezone
from order.models import *
from django.db.models import F
User = get_user_model()

# Create your views here.

def user_login(request):
    if request.user.is_authenticated:
        return redirect('user_app:index')
    
   
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email)
        print(password)
        user_block = CustomUser.objects.get(email = email)
        if user_block.is_block:
                messages.error(request, 'you are blocked by the admin!')
                return render(request,'user/login.html')
        # remember_me = request.POST.get('remember_me')
        user = authenticate(request, email=email, password = password)
        print(user)
        if user is not None:
           
            login(request, user)
           
            
            # if remember_me:
            #     request.session.set_expiry(1209600)  # 2 weeks
            # else:
            #     request.session.set_expiry(0) # expires when browser is closed
            if user.is_staff:
                return redirect('admin_app:admin_home')
            else:
                return redirect('user_app:index')
        else:
            error='Email or Password wrong!'
            return render(request,'user/login.html',{'email':email,'password':password,'error':error})
    else:
        return render(request,'user/login.html')
@never_cache  
def sign_up(request):
    if request.user.is_authenticated:
        return redirect('user_app:index')
    error=None
    if request.method == 'POST':
        

        email = request.POST.get('email')
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        error = {}
        if request.POST.get('referral'):
            referral = request.POST.get('referral')
            code = UserReferral.objects.filter(referral_code=referral)
            if not code:
                error['referral'] = 'Invalid referral'
            else:
                  request.session['referral'] = referral
       
        error=validation_view(request,email,first_name,last_name,password,confirm_password)
        
        
        
        if error:
            return render(request,'user/sign_up.html',{"error":error,"email":email,"username":username,"first_name":first_name,"last_name":last_name,"password":password,"confirm_password":confirm_password})
        elif CustomUser.objects.filter(email = email).exists():
                print('hi')
                error1=None
                user_obj = CustomUser.objects.get(email = email)
                if not user_obj.is_active:  # If user is not active 
                    # Generating OTP
                    otp = random.randint(10000,99999)
                    
                    # Save the OTP to session
                    request.session['registration_otp'] = otp
                    request.session['registered_email'] = email
                    
                       

                    # Send the OTP via email
                    mail_subject = 'Your OTP for email verification'
                    message = f'Your OTP is {otp}. Please enter it to verify your email.'
                    try:
                        email_message = EmailMessage(mail_subject, message, to=[email])
                        email_message.send()
                    except Exception as e:
                        messages.error(request, 'Error sending email. Please try again.')
                        return None
                    print('redirecting to the verify OTP page')
                    valid_time = (datetime.now() + timedelta(minutes=3)).isoformat()  # Convert to string
                    request.session['valid_time'] = valid_time
                    request.session['access']=False
                    return redirect('user_app:enter_otp')  # Redirect to OTP verification page
                else:
                    error1= 'Email already exists!'
                    return render(request,'user/sign_up.html',{"error1":error1,"email":email,"username":username,"first_name":first_name,"last_name":last_name,"password":password,"confirm_password":confirm_password})
    
        elif CustomUser.objects.filter(username = username).exists():   
              error1= 'username already exists! Try another'
              return render(request,'user/sign_up.html',{"error1":error1,"email":email,"username":username,"first_name":first_name,"last_name":last_name,"password":password,"confirm_password":confirm_password})
    

        else:
            # Saving the user with field is_active as False
            
            user = CustomUser(email = email,username = username, first_name = first_name, last_name = last_name)
            user.set_password(password)
            user.is_active = False
            user.save()
            
            # Generating OTP
            otp = random.randint(10000,99999)
            valid_time = (datetime.now() + timedelta(minutes=3)).isoformat()  # Convert to string
            request.session['valid_time'] = valid_time

            print(valid_time)
            # Save the OTP to session
            request.session['registration_otp'] = otp
            request.session['registered_email'] = email
            

            # Send the OTP via email
            mail_subject = 'Your OTP for email verification'
            message = f'Your OTP is {otp}. Please enter it to verify your email.'
            try:
                email_message = EmailMessage(mail_subject, message, to=[email])
                email_message.send()
                messages.success(request, 'OTP has been sent to your email.')
            except Exception as e:
                messages.error(request, 'Error sending email. Please try again.')
                return None
            valid_time = (datetime.now() + timedelta(minutes=3)).isoformat()  # Convert to string
            request.session['valid_time'] = valid_time
            return redirect('user_app:enter_otp')  # Redirect to OTP verification page

    
    return render(request,'user/sign_up.html')  


def validation_view(request,email,first_name,last_name,password,confirm_password):
    #created object for user validation Authentication_check
    user_validation = Authentication_check()

    errors = {}
    #email validation
    email_valid = user_validation.email_validator(email)
    if email_valid:
        errors['email_error'] = email_valid
        
    #first_name validation
    first_name_valid = user_validation.first_name_validator(first_name)
    if first_name_valid:
        errors['first_name_error'] = first_name_valid
    
    #last_name validation
    last_name_valid = user_validation.last_name_validator(last_name)
    if last_name_valid:
        errors['last_name_error'] = last_name_valid
        
    #password validation
    password_valid = user_validation.pass_validator(password)
    if password_valid:
        errors['password_error'] = password_valid
    
    #password mismatch checking
    password_mismatch = user_validation.password_mismatch(password, confirm_password)
    if password_mismatch:
        errors['password_mismatch'] = password_mismatch
    
   
    
    return errors
@never_cache   
def enter_otp(request):
    
    error1=None
    if request.method=='POST':
        
        otp=request.POST['otp']
        print(otp)
        time_now=datetime.now()
        print('timenow: ',time_now)
        
        email=request.session['registered_email'] 
        print(email)
        valid_time=request.session.get('valid_time')
        print(valid_time)
        otp_send=request.session['registration_otp']
        print(type(otp_send))
        print(otp_send)
        if time_now.isoformat() > valid_time:
             error='time limit exceeded'
             return render(request,'user/otp_enter.html',{"error1":error,"otp_entered":otp})
      
        elif str(otp_send) != otp:
            error='invalid otp'
            
            return render(request,'user/otp_enter.html',{"error1":error,"otp_entered":otp})
        else:
            
            user = CustomUser.objects.get(email =email)
            user.is_active = True
            user.save()
            
            # Clear the OTP session
            del request.session['registration_otp']
            del request.session['registered_email']
            del request.session['valid_time']

            messages.success(request, "Your email has been verified! You can now log in.")
            return redirect('user_app:user_login')
    return render(request,'user/otp_enter.html')
@never_cache
def resend_otp(request):
        
            email=request.session['registered_email']
            
     # Clear the OTP session
            del request.session['registration_otp']
            del request.session['valid_time']
            
    # Generating OTP
            otp = random.randint(10000,99999)
            valid_time = (datetime.now() + timedelta(minutes=3)).isoformat()  # Convert to string
            request.session['valid_time'] = valid_time

            print(valid_time)
            # Save the OTP to session
            request.session['registration_otp'] = otp
            
            

            # Send the OTP via email
            mail_subject = 'Your OTP for email verification'
            message = f'Your OTP is {otp}. Please enter it to verify your email.'
            try:
                email_message = EmailMessage(mail_subject, message, to=[email])
                email_message.send()
                messages.success(request, 'OTP has been sent to your email.')
            except Exception as e:
                messages.error(request, 'Error sending email. Please try again.')
                return None
            valid_time = (datetime.now() + timedelta(minutes=3)).isoformat()  # Convert to string
            request.session['valid_time'] = valid_time
            if request.session['access']:
                return redirect('user_app:enter_otp_password')
            else:
                return redirect('user_app:enter_otp')  
# forget_password
@never_cache
def forget_password(request):
    
        if request.method == 'POST':
            email = request.POST.get('email')

            
            # Check the email is already exists in the database or not
            if CustomUser.objects.filter(email = email).exists():
                # Generating OTP
                    
                    otp = random.randint(10000,99999)
                    
                    # Save the OTP to session
                    request.session['registration_otp'] = otp
                    request.session['registered_email'] = email
                    request.session['access'] = True
                    

                    # Send the OTP via email
                    mail_subject = 'Your OTP for email verification'
                    message = f'Your OTP is {otp}. Please enter it to verify your email.'
                    try:
                        email_message = EmailMessage(mail_subject, message, to=[email])
                        email_message.send()
                    except Exception as e:
                        messages.error(request, 'Error sending email. Please try again.')
                        return None
                    print('redirecting to the verify OTP page')
                    valid_time = (datetime.now() + timedelta(minutes=3)).isoformat()  # Convert to string
                    request.session['valid_time'] = valid_time
                    return redirect('user_app:enter_otp_password')  # Redirect to OTP verification page
            else:
                messages.error(request, 'Email does not exists!')
                
                
        return render(request,'user/forget_password.html')
@never_cache
def enter_otp_password(request):
    error1=None
    request.session['access']
    if request.method=='POST':
        
        otp=request.POST['otp']
        
        time_now=datetime.now()
        print('timenow: ',time_now)
        email=request.session['registered_email'] 
        valid_time=request.session.get('valid_time')
        print(valid_time)
        otp_send=request.session['registration_otp']
        print(type(otp_send))
        print(otp_send)
        if time_now.isoformat() > valid_time:
             error='time limit exceeded'
             return render(request,'user/otp_password.html',{"error1":error,"otp":otp})
      
        elif str(otp_send) != otp:
            error='invalid otp'
            
            return render(request,'user/otp_password.html',{"error1":error,"otp":otp})
        else:
            # Clear the OTP session
            del request.session['registration_otp']
            
            del request.session['valid_time']
            return redirect('user_app:password_check')
    
    return render(request,'user/otp_password.html')
@never_cache
def password_check(request):
   errors = {}
   
   if request.method == 'POST':
        
        password = request.POST.get('newPassword')
        confirm_password = request.POST.get('confirmPassword')
        
      
        email = request.session['registered_email']
        user = CustomUser.objects.get(email = email)
        user.set_password(password)
        user.save()
        users=UserReferral.objects.filter(user=user)
        if users == None:
            new_referral_code = generate_referral_code(user.id)
            print('New user referral code: ',new_referral_code)
            UserReferral.objects.create(
                    user=user,
                    referral_code = new_referral_code,
                )
            referral_code=request.session.get('referral')    
            if referral_code:
                    try:
                        # If signup is using a referral code, credit both users
                        # Creating/Updating wallet for the new user
                        wallet, created = Wallet.objects.get_or_create(user=user)
                        
                        WalletTransation.objects.create(
                            wallet=wallet,
                            transaction_type='referral',
                            amount=1000,  # Amount for the referral reward
                        )
                        wallet.balance = F('balance') + 1000
                        wallet.save()

                        # Credit referrer’s wallet
                        referred_user = UserReferral.objects.get(referral_code=referral_code)
                        referrer_wallet, created = Wallet.objects.get_or_create(user=referred_user.user)
                        WalletTransation.objects.create(
                            wallet=referrer_wallet,
                            transaction_type='referral',
                            amount=1000,
                        )
                        referrer_wallet.balance = F('balance') + 1000
                        referrer_wallet.save()

                    except UserReferral.DoesNotExist:
                        messages.error(request, "Invalid referral code.")
            
            del request.session['registered_email']
            del request.session['referral']  
        messages.success(request,'Password changed successfully')
        
        return redirect('user_app:user_login')
        
   else:
       
        return render(request,'user/password_check.html')
import hashlib

def generate_referral_code(user_id, salt="my_secret_salt"):
    hash_input = f"{user_id}{salt}".encode()
    code = hashlib.md5(hash_input).hexdigest()[:6].upper()  # Take first 8 characters
    return code

@never_cache
def index(request):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('admin_app:admin_home')
        if request.user.is_authenticated and request.user.is_block:
            return redirect('user_app:user_logout')
       
        
        banner = Banner.objects.all()
        print(banner)
        context={
             'banner': banner
        }

        return render(request,'user/user_index.html',context)
    
@never_cache
def user_logout(request):
 if request.user.is_authenticated:
    # if request.method=='POST':
    logout(request)
    return redirect('user_app:index')
 else: 
        logout(request)
        return redirect('user_app:index')

              
        
  

#  <a href="{% url 'cart_app:add_to_cart' product.id %}" class="btn_3">add to cart</a>
#  <a href="{% url 'wishlist_app:add_to_wishlist' product.id %}" class="like_us"> <i class="ti-heart"></i> </a>
            