# coding: utf-8
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category,Page
from forms import CategoryForm,PageForm,UserForm, UserProfileForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

def encode_url(str):
    return str.replace(' ', '_')

def decode_url(str):
    return str.replace('_', ' ')

@login_required
def restricted(request):
	return HttpResponse("Since you're logged in, you can see the text!")

@login_required
def user_logout(request):
	logout(request)

	return HttpResponseRedirect('/rango/')


def index(request):
    request.session.set_test_cookie()
    context = RequestContext(request)

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories':category_list,
    				'pages':page_list
                    }

    # encoding category name url for all the urls
    for cat in category_list:
        cat.url = cat.name.replace(' ','_')

    response = render_to_response('rango/index.html',context_dict,context)

    visits = int(request.COOKIES.get('visits','0'))

    if request.COOKIES.has_key('last_visit'):
        last_visit = request.COOKIES['last_visit']
        last_visit_time = datetime.strptime(last_visit[:-7],"%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).days > 0:
            response.set_cookie('visits',visits+1)
            response.set_cookie('last_visit',datetime.now())
    else:
        response.set_cookie('last_visit',datetime.now())

    return response

@login_required	
def about(request):
	return HttpResponse("This is the about page!\n\n<a href='/rango/'>Go back</a>")

def category(request,category_name_url):
	context = RequestContext(request)

	#decoding of the category name url
	category_name = category_name_url.replace('_',' ')

	context_dict = {'category_name':category_name}

	try:
		category = Category.objects.get(name=category_name)

		pages = Page.objects.filter(category=category)

		context_dict['category'] = category
		context_dict['pages'] = pages
		context_dict['category_name_url'] = category_name_url

	except Category.DoesNotExist:
		pass

	return render_to_response('rango/category.html',context_dict,context)

@login_required
def add_category(request):
	context = RequestContext(request)

	if request.method == 'POST':
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit = True)

			return index(request)

		else:
			print(form.errors)
	else:
		form = CategoryForm()

	return render_to_response('rango/add_category.html',{'form':form}, context)

@login_required
def add_page(request, category_name_url):
    context = RequestContext(request)
    context_dict = {}

    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(data=request.POST)
        
        if form.is_valid():
            page = form.save(commit=False)
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                return render_to_response( 'rango/add_page.html',
                                          context_dict,
                                          context)
            page.views = 0
            page.save()

            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict['category_name_url']= category_name_url
    context_dict['category_name'] =  category_name
    context_dict['form'] = form

    return render_to_response( 'rango/add_page.html',
                               context_dict,
                               context)

# def register(request):
# 	context = RequestContext(request)

# 	registered=False

# 	if request.method=='POST':

# 		user_form = UserForm(data=request.POST)
# 		profile_form = UserProfileForm(data=request.POST)

# 		if user_form.is_valid() and profile_form.is_valid():

# 			user = user_form.save()
# 			user.set_password(user.password)
# 			user.save()

# 			profile = profile_form.save(commit=False)
# 			profile.user = user

# 			if 'picture' in request.FILES:
# 				profile.picture = request.FILES['picture']

# 			profile.save()

# 			registered=True

# 		else:
# 			print(user_form.errors,profile_form.errors)

# 	else:
# 		user_form = UserForm()
# 		profile_form = UserProfileForm()

# 	return render_to_response(
# 		'rango/register.html',
# 		{'user_form':user_form, 'profile_form': profile_form, 'registered': registered},
# 		context)

def register(request):
    if request.session.test_cookie_worked():
        print(">>>>>TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    # Request the context.
    context = RequestContext(request)
    context_dict = {}
    # Boolean telling us whether registration was successful or not.
    # Initially False; presume it was a failure until proven otherwise!
    registered = False

    # If HTTP POST, we wish to process form data and create an account.
    if request.method == 'POST':
        # Grab raw form data - making use of both FormModels.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # Two valid forms?
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data. That one is easy.
            user = user_form.save()

            # Now a user account exists, we hash the password with the set_password() method.
            # Then we can update the account with .save().
            user.set_password(user.password)
            user.save()

            # Now we can sort out the UserProfile instance.
            # We'll be setting values for the instance ourselves, so commit=False prevents Django from saving the instance automatically.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Profile picture supplied? If so, we put it in the new UserProfile.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the model instance!
            profile.save()

            # We can say registration was successful.
            registered = True

        # Invalid form(s) - just print errors to the terminal.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render the two ModelForms to allow a user to input their data.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    context_dict['user_form'] = user_form
    context_dict['profile_form']= profile_form
    context_dict['registered'] = registered

    # Render and return!
    return render_to_response(
        'rango/register.html',
        context_dict,
        context)

def user_login(request):
	context = RequestContext(request)

	if request.method=='POST':

		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(username=username,password=password)

		if user is not None:

			if user.is_active:

				login(request,user)
				return HttpResponseRedirect('/rango/')
			else:
				return HttpResponse('Your account is disabled!')
		else:
			print("Invalid login details - {0}, {1}".format(username,password))
			return HttpResponse('Invalid login details supplied!')
	else :

		return render_to_response('rango/login.html',{},context)


