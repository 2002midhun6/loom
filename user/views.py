from django.shortcuts import render, redirect
from .validate import Authentication_check
from .models import *
import random
import hashlib
from decimal import Decimal
from django.core.mail import EmailMessage
from django.contrib import messages
from datetime import datetime, timedelta
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth import get_user_model
from django.views.decorators.cache import never_cache
from django.db import transaction
from product.models import *
from django.utils import timezone
from order.models import *
from django.db.models import F

User = get_user_model()

def generate_referral_code(user_id, salt="my_secret_salt"):
    hash_input = f"{user_id}{salt}".encode()
    return hashlib.md5(hash_input).hexdigest()[:6].upper()


def _send_otp_email(email, otp):
    """Send OTP to the given email. Raises on failure."""
    mail_subject = 'Your OTP for email verification'
    message = (
        f"Hello,\n\n"
        f"Your One-Time Password (OTP) is: {otp}\n\n"
        f"This OTP is valid for 3 minutes. Do not share it with anyone.\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"Thank you,\nLOOM Team"
    )
    EmailMessage(mail_subject, message, to=[email]).send()


def _set_otp_session(request, email, otp, access=False):
    
    valid_time = (datetime.now() + timedelta(minutes=3)).isoformat()
    request.session['registration_otp'] = otp
    request.session['registered_email'] = email
    request.session['valid_time'] = valid_time
    request.session['access'] = access


def _clear_otp_session(request):
    for key in ('registration_otp', 'registered_email', 'valid_time'):
        request.session.pop(key, None)


def _validate_otp(request, submitted_otp):
    valid_time = request.session.get('valid_time')
    stored_otp = request.session.get('registration_otp')

    if not valid_time or not stored_otp:
        return False, 'Session expired. Please request a new OTP.'

    if datetime.now().isoformat() > valid_time:
        return False, 'OTP has expired. Please request a new one.'

    if str(stored_otp) != submitted_otp.strip():
        return False, 'Invalid OTP. Please try again.'

    return True, None


def validation_view(request, email, username, first_name, last_name, password, confirm_password):
    user_validation = Authentication_check()
    errors = {}

    for validator, key in (
        (user_validation.email_validator(email), 'email_error'),
        (user_validation.first_name_validator(first_name), 'first_name_error'),
        (user_validation.last_name_validator(last_name), 'last_name_error'),
        (user_validation.username_validator(username), 'username_error'),
        (user_validation.pass_validator(password), 'password_error'),
        (user_validation.password_mismatch(password, confirm_password), 'password_mismatch'),
    ):
        if validator:
            errors[key] = validator

    return errors

def user_login(request):
    if request.user.is_authenticated:
        return redirect('user_app:index')

    if request.method != 'POST':
        return render(request, 'user/login.html')

    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')

    if not email or not password:
        return render(request, 'user/login.html', {
            'email': email,
            'error': 'Email and password are required.',
        })

    try:
        user_obj = CustomUser.objects.filter(email=email).first()

        if not user_obj:
            return render(request, 'user/login.html', {
                'email': email,
                'error': 'No account found with this email.',
            })

        if user_obj.is_block:
            messages.error(request, 'Your account has been blocked. Please contact support.')
            return render(request, 'user/login.html', {'email': email})

        if not user_obj.is_active:
            messages.error(request, 'Please verify your email before logging in.')
            return render(request, 'user/login.html', {'email': email})

        user = authenticate(request, email=email, password=password)

        if user is None:
            return render(request, 'user/login.html', {
                'email': email,
                'error': 'Incorrect email or password.',
            })

        login(request, user)
        if user.is_staff:
            return redirect('admin_app:admin_home')
        return redirect('user_app:index')

    except Exception:
        return render(request, 'user/login.html', {
            'email': email,
            'error': 'Something went wrong. Please try again.',
        })


@never_cache
def sign_up(request):
    if request.user.is_authenticated:
        return redirect('user_app:index')

    if request.method != 'POST':
        return render(request, 'user/sign_up.html')

    email = request.POST.get('email', '').strip()
    username = request.POST.get('username', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirm_password', '')
    referral_code = request.POST.get('referral', '').strip()

    form_data = {
        'email': email, 'username': username,
        'first_name': first_name, 'last_name': last_name,
        'password': password, 'confirm_password': confirm_password,
    }

    if referral_code:
        if not UserReferral.objects.filter(referral_code=referral_code).exists():
            return render(request, 'user/sign_up.html', {
                **form_data,
                'error': {'referral': 'Invalid referral code.'},
            })
        request.session['referral'] = referral_code

    errors = validation_view(request, email, username, first_name, last_name, password, confirm_password)
    if errors:
        return render(request, 'user/sign_up.html', {**form_data, 'error': errors})

    existing = CustomUser.objects.filter(email=email).first()
    if existing:
        if not existing.is_active:
            otp = random.randint(10000, 99999)
            _set_otp_session(request, email, otp, access=False)
            try:
                _send_otp_email(email, otp)
                messages.info(request, 'This email is already registered but unverified. A new OTP has been sent.')
            except Exception:
                messages.error(request, 'Error sending OTP email. Please try again.')
                return render(request, 'user/sign_up.html', form_data)
            return redirect('user_app:enter_otp')
        else:
            return render(request, 'user/sign_up.html', {
                **form_data,
                'error1': 'An account with this email already exists.',
            })


    if CustomUser.objects.filter(username=username).exists():
        return render(request, 'user/sign_up.html', {
            **form_data,
            'error1': 'Username already taken. Please choose another.',
        })

    try:
        user = CustomUser(email=email, username=username, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.is_active = False
        user.save()

        otp = random.randint(10000, 99999)
        _set_otp_session(request, email, otp, access=False)
        _send_otp_email(email, otp)
        messages.success(request, 'OTP sent to your email. Please verify within 3 minutes.')
        return redirect('user_app:enter_otp')

    except Exception:
        CustomUser.objects.filter(email=email, is_active=False).delete()
        messages.error(request, 'Error sending OTP email. Please try again.')
        return render(request, 'user/sign_up.html', form_data)


@never_cache
def enter_otp(request):
    if request.method != 'POST':
        return render(request, 'user/otp_enter.html')

    submitted_otp = request.POST.get('otp', '').strip()
    email = request.session.get('registered_email')

    if not email:
        messages.error(request, 'Session expired. Please sign up again.')
        return redirect('user_app:sign_up')

    ok, error = _validate_otp(request, submitted_otp)
    if not ok:
        return render(request, 'user/otp_enter.html', {'error1': error, 'otp_entered': submitted_otp})

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Account not found. Please sign up again.')
        return redirect('user_app:sign_up')

    try:
        with transaction.atomic():
            user.is_active = True
            user.save()
            if not UserReferral.objects.filter(user=user).exists():
                UserReferral.objects.create(
                    user=user,
                    referral_code=generate_referral_code(user.id),
                )
            referral_code_used = request.session.get('referral')
            if referral_code_used:
                try:
                    referrer_referral = UserReferral.objects.select_related('user').get(
                        referral_code=referral_code_used
                    )
                    referrer = referrer_referral.user

                    if referrer == user:
                        messages.warning(request, 'You cannot use your own referral code.')
                    else:
                        wallet_new, _ = Wallet.objects.get_or_create(user=user)
                        wallet_new.balance = Decimal(str(wallet_new.balance)) + Decimal('100')
                        wallet_new.save()
                        WalletTransation.objects.create(
                            wallet=wallet_new, transaction_type='referral', amount=Decimal('100'),
                        )
                        wallet_referrer, _ = Wallet.objects.get_or_create(user=referrer)
                        wallet_referrer.balance = Decimal(str(wallet_referrer.balance)) + Decimal('500')
                        wallet_referrer.save()
                        WalletTransation.objects.create(
                            wallet=wallet_referrer, transaction_type='referral', amount=Decimal('500'),
                        )

                        messages.success(request, 'Referral bonus applied! ₹100 added to your wallet.')

                except UserReferral.DoesNotExist:
                    messages.warning(request, 'Referral code not found — bonus not applied.')

        _clear_otp_session(request)
        request.session.pop('referral', None)
        messages.success(request, 'Email verified! You can now log in.')
        return redirect('user_app:user_login')

    except Exception:
        messages.error(request, 'Something went wrong during verification. Please try again.')
        return render(request, 'user/otp_enter.html')


@never_cache
def resend_otp(request):
    email = request.session.get('registered_email')
    if not email:
        messages.error(request, 'Session expired. Please start again.')
        return redirect('user_app:sign_up')

    otp = random.randint(10000, 99999)
    access = request.session.get('access', False)
    _set_otp_session(request, email, otp, access=access)

    try:
        _send_otp_email(email, otp)
        messages.success(request, 'A new OTP has been sent to your email.')
    except Exception:
        messages.error(request, 'Error sending OTP. Please try again.')
        return redirect('user_app:enter_otp' if not access else 'user_app:enter_otp_password')

    if access:
        return redirect('user_app:enter_otp_password')
    return redirect('user_app:enter_otp')


@never_cache
def forget_password(request):
    if request.method != 'POST':
        return render(request, 'user/forget_password.html')

    email = request.POST.get('email', '').strip()

    if not email:
        messages.error(request, 'Please enter your email address.')
        return render(request, 'user/forget_password.html')

    if not CustomUser.objects.filter(email=email).exists():
        messages.error(request, 'If this email is registered, you will receive an OTP.')
        return render(request, 'user/forget_password.html')

    otp = random.randint(10000, 99999)
    _set_otp_session(request, email, otp, access=True)

    try:
        _send_otp_email(email, otp)
        return redirect('user_app:enter_otp_password')
    except Exception:
        messages.error(request, 'Error sending OTP. Please try again.')
        return render(request, 'user/forget_password.html')


@never_cache
def enter_otp_password(request):
    if request.method != 'POST':
        return render(request, 'user/otp_password.html')

    submitted_otp = request.POST.get('otp', '').strip()
    email = request.session.get('registered_email')

    if not email:
        messages.error(request, 'Session expired. Please request a new OTP.')
        return redirect('user_app:forget_password')

    ok, error = _validate_otp(request, submitted_otp)
    if not ok:
        return render(request, 'user/otp_password.html', {'error1': error, 'otp': submitted_otp})

    _clear_otp_session(request)
    # Keep registered_email in session so password_check can use it
    request.session['registered_email'] = email
    return redirect('user_app:password_check')


@never_cache
def password_check(request):
    email = request.session.get('registered_email')
    if not email:
        messages.error(request, 'Session expired. Please start the password reset process again.')
        return redirect('user_app:forget_password')

    if request.method != 'POST':
        return render(request, 'user/password_check.html')

    password = request.POST.get('newPassword', '')
    confirm_password = request.POST.get('confirmPassword', '')

    if not password or not confirm_password:
        messages.error(request, 'Both password fields are required.')
        return render(request, 'user/password_check.html')

    if password != confirm_password:
        messages.error(request, 'Passwords do not match.')
        return render(request, 'user/password_check.html')

    if len(password) < 8:
        messages.error(request, 'Password must be at least 8 characters long.')
        return render(request, 'user/password_check.html')

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Account not found.')
        return redirect('user_app:forget_password')

    try:
        user.set_password(password)
        user.save()

        # Create referral code if missing (edge case for legacy accounts)
        if not UserReferral.objects.filter(user=user).exists():
            UserReferral.objects.create(
                user=user,
                referral_code=generate_referral_code(user.id),
            )

        request.session.pop('registered_email', None)
        request.session.pop('referral', None)

        messages.success(request, 'Password changed successfully. Please log in.')
        return redirect('user_app:user_login')

    except Exception:
        messages.error(request, 'Something went wrong. Please try again.')
        return render(request, 'user/password_check.html')


@never_cache
def index(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and getattr(request.user, 'is_block', False):
        return redirect('user_app:user_logout')

    try:
        banner = Banner.objects.all()
    except Exception:
        banner = []

    return render(request, 'user/user_index.html', {'banner': banner})


@never_cache
def user_logout(request):
    logout(request)
    return redirect('user_app:index')