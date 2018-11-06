import logging
import os
import pdb

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.forms import inlineformset_factory, HiddenInput, CheckboxInput
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import AddEmailForm, AssociatedEmailChoiceForm, ProfileForm, RegistrationForm, UsernameChangeForm, CredentialApplicationForm
from .models import AssociatedEmail, Profile, User, CredentialApplication
from physionet import utility
from project.models import Author


logger = logging.getLogger(__name__)

def activate_user(request, uidb64, token):
    """
    Page to active the account of a newly registered user.
    """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and not user.is_active and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        email = user.associated_emails.first()
        email.verification_date = timezone.now()
        email.is_verified = True
        email.save()
        logger.info('User activated - {0}'.format(user.email))
        context = {'title':'Activation Successful', 'isvalid':True}
    else:
        logger.warning('Invalid Activation Link')
        context = {'title':'Invalid Activation Link', 'isvalid':False}

    return render(request, 'user/activate_user.html', context)


# Helper functions for edit_emails view

def remove_email(request, email_id):
    "Remove a non-primary email associated with a user"
    user = request.user
    associated_email = AssociatedEmail.objects.get(id=email_id)
    if associated_email.user == user and not associated_email.is_primary_email:
        email = associated_email.email
        associated_email.delete()
        logger.info('Removed email {0} from user {1}'.format(email, user.id))
        messages.success(request, 'Your email: {0} has been removed from your account.'.format(email))

def set_primary_email(request, primary_email_form):
    "Set the selected email as the primary email"
    user = request.user
    if primary_email_form.is_valid():
        associated_email = primary_email_form.cleaned_data['associated_email']
        # Only do something if they selected a different email
        if associated_email.email != user.email:
            logger.info('Primary email changed from: {0} to {1}'.format(user.email, associated_email.email))
            user.email = associated_email.email
            user.save(update_fields=['email'])
            # Change the email field of author objects belonging to
            # the user. Warn them if they are the corresponding
            # author of any projects
            authors = Author.objects.filter(user=user)
            authors.update(corresponding_email=associated_email)
            messages.success(request, 'Your email: {0} has been set as your new primary email.'.format(user.email))
            if authors.filter(is_corresponding=True):
                messages.info(request, 'The corresponding email in all your authoring projects has been set to your new primary email.')


def set_public_email(request, public_email_form):
    "Set the selected email as the public email"
    user = request.user
    if public_email_form.is_valid():
        associated_email = public_email_form.cleaned_data['associated_email']
        current_public_email = user.associated_emails.filter(is_public=True).first()
        # Only do something if they selected a different email
        if associated_email != current_public_email:
            if current_public_email:
                current_public_email.is_public = False
                current_public_email.save()
            # The selection may be None
            if associated_email:
                associated_email.is_public = True
                associated_email.save()
                messages.success(request, 'Your email: {0} has been set to public.'.format(associated_email.email))
            else:
                messages.success(request, 'Your email: {0} has been set to private.'.format(current_public_email.email))

def add_email(request, add_email_form):
    user = request.user
    if add_email_form.is_valid():
        associated_email = AssociatedEmail.objects.create(user=user,
            email=add_email_form.cleaned_data['email'])
        # Send an email to the newly added email with a verification link
        uidb64 = urlsafe_base64_encode(force_bytes(associated_email.pk))
        token = default_token_generator.make_token(user)
        subject = "PhysioNet Email Verification"
        context = {'name':user.get_full_name(),
            'domain':get_current_site(request), 'uidb64':uidb64, 'token':token}
        body = loader.render_to_string('user/email/verify_email_email.html', context)
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
            [add_email_form.cleaned_data['email']], fail_silently=False)
        messages.success(request, 'A verification link has been sent to: {0}'.format(associated_email.email))

@login_required
def edit_emails(request):
    """
    Edit emails page
    """
    user = request.user

    associated_emails = AssociatedEmail.objects.filter(
        user=user).order_by('-is_verified', '-is_primary_email')
    primary_email_form = AssociatedEmailChoiceForm(user=user,
                                                   selection_type='primary')
    public_email_form = AssociatedEmailChoiceForm(user=user,
                                                  selection_type='public')
    add_email_form = AddEmailForm()

    if request.method == 'POST':
        if 'remove_email' in request.POST:
            # No form. Just get button value.
            email_id = int(request.POST['remove_email'])
            remove_email(request, email_id)
        elif 'set_primary_email' in request.POST:
            primary_email_form = AssociatedEmailChoiceForm(user=user,
                selection_type='primary', data=request.POST)
            set_primary_email(request, primary_email_form)
        elif 'set_public_email' in request.POST:
            public_email_form = AssociatedEmailChoiceForm(user=user,
                selection_type='public', data=request.POST)
            set_public_email(request, public_email_form)

        elif 'add_email' in request.POST:
            add_email_form = AddEmailForm(request.POST)
            add_email(request, add_email_form)

    context = {'associated_emails':associated_emails,
        'primary_email_form':primary_email_form,
        'add_email_form':add_email_form,
        'public_email_form':public_email_form}

    context['messages'] = messages.get_messages(request)

    return render(request, 'user/edit_emails.html', context)


@login_required
def edit_profile(request):
    """
    Edit the profile fields
    """
    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        if 'edit_profile' in request.POST:
            # Update the profile and return to the same page. Place a message
            # at the top of the page: 'your profile has been updated'
            form = ProfileForm(data=request.POST, files=request.FILES,
                               instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile has been updated.')
        elif 'delete_photo' in request.POST:
            profile.delete_photo()
            messages.success(request, 'Your profile photo has been deleted.')

        if not form.errors:
            form = ProfileForm(instance=profile)

    return render(request, 'user/edit_profile.html', {'form':form,
        'messages':messages.get_messages(request)})


@login_required
def edit_password_complete(request):
    """
    After password has successfully been changed. Need this view because
    we can't control the edit password view to show a success message.
    """
    return render(request, 'user/edit_password_complete.html')


def public_profile(request, username):
    """
    A user's public profile
    """
    if User.objects.filter(username=username).exists():
        public_user = User.objects.get(username=username)
        public_email = public_user.associated_emails.filter(is_public=True).first()
    else:
        raise Http404()

    return render(request, 'user/public_profile.html', {
        'public_user':public_user, 'profile':public_user.profile,
        'public_email':public_email})


def profile_photo(request, username):
    """
    Serve a user's profile photo
    """
    user = User.objects.get(username=username)
    return utility.serve_file(request, user.profile.photo.path)


def register(request):
    """
    User registration page
    """
    user = request.user
    if user.is_authenticated():
        return redirect('user_home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Create the new user
            user = form.save()
            # Send an email with the activation link
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            subject = "PhysioNet Account Activation"
            context = {'name':user.get_full_name(),
                'domain':get_current_site(request), 'uidb64':uidb64, 'token':token}
            body = loader.render_to_string('user/email/register_email.html', context)
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
                [form.cleaned_data['email']], fail_silently=False)

            # Registration successful
            return render(request, 'user/register_done.html', {'email':user.email})
    else:
        form = RegistrationForm()

    return render(request, 'user/register.html', {'form':form})


@login_required
def user_home(request):
    """
    Home page/dashboard for individual users
    """
    return render(request, 'user/user_home.html', {'user':request.user})


@login_required
def user_settings(request):
    """
    Settings. Redirect to default - settings/profile
    Don't call this 'settings' because there's an import called 'settings'
    """
    return redirect('edit_profile')


def verify_email(request, uidb64, token):
    """
    Page to verify an associated email
    """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        associated_email = AssociatedEmail.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, AssociatedEmail.DoesNotExist):
        associated_email = None

    if associated_email is not None:
        # Test the token with the user
        user = associated_email.user
        if default_token_generator.check_token(user, token):
            associated_email.verification_date = timezone.now()
            associated_email.is_verified = True
            associated_email.save()
            logger.info('User {0} verified another email {1}'.format(user.id, associated_email))
            return render(request, 'user/verify_email.html',
                {'title':'Verification Successful', 'isvalid':True})

    logger.warning('Invalid Verification Link')
    return render(request, 'user/verify_email.html',
        {'title':'Invalid Verification Link', 'isvalid':False})


@login_required
def edit_username(request):
    """
    Edit username settings page
    """
    user = request.user

    form = UsernameChangeForm(instance=user)
    if request.method == 'POST':
        form = UsernameChangeForm(instance=user, data=request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Your username has been updated.')
        else:
            user = User.objects.get(id=user.id)

    return render(request, 'user/edit_username.html', {'form':form,
        'user':user})


@login_required
def edit_credentialing(request):
    """
    Credentials settings page.
    - form to apply for credentialling
    - list of past credential applications

    """
    user = request.user
    profile = user.profile

    credential_applications = CredentialApplication.objects.filter(user=user)
    # Create an application form if the user is not already credentialed
    # and doesn't have one pending
    current_application = credential_applications.filter(status=0)

    if not profile.is_credentialed and not current_application:
        form = CredentialApplicationForm(user=user)
    else:
        current_application = current_application.first()
        form = None

    if request.method == 'POST' and not profile.is_credentialed and not current_application:
        form = CredentialApplicationForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your application has been received and will be reviewed shortly.')
        else:
            messages.error(request, 'Invalid submission. See errors below.')

    return render(request, 'user/edit_credentialing.html', {'form':form,
        'credential_applications':credential_applications,
        'current_application':current_application,
        'messages':messages.get_messages(request)})


@login_required
def credential_application(request):
    """
    Page to apply for credentially
    """
    user = request.user
    profile = user.profile

    if profile.is_credentialed or CredentialApplication.objects.filter(user=user, status=0):
        return redirect(request, 'edit_credentialing')

    form = CredentialApplicationForm(user=user)

    if request.method == 'POST':
        form = CredentialApplicationForm(user=user, data=request.POST,
            files=request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'user/credential_application_complete.html')
        else:
            messages.error(request, 'Invalid submission. See errors below.')
            print(form.errors)

        pdb.set_trace()

    return render(request, 'user/credential_application.html', {'form':form,
        'messages':messages.get_messages(request)})


