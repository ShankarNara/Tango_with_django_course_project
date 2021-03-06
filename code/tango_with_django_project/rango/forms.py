from django import forms
from rango.models import Category, Page, UserProfile
from django.contrib.auth.models import User

class CategoryForm(forms.ModelForm):
	name = forms.CharField(max_length=128, help_text="Please enter the category name : ")
	views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
	likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

	class Meta:
		model=Category

class PageForm(forms.ModelForm):
	title = forms.CharField(max_length=128,help_text="Please enter the title : ")
	url = forms.URLField(max_length=200,help_text="Please enter the URL of the page : ")
	views =  forms.IntegerField(widget=forms.HiddenInput(),initial=0)

	class Meta:
		model = Page

		fields = ('title','url','views')

	def clean(self):
		cleaned_data = self.cleaned_data
		url = cleaned_data.get('url')

		if url and not url.startswith('http://'):
			url = 'http://' + url
			cleaned_data['url'] = url

		return cleaned_data

class UserForm(forms.ModelForm):
	username = forms.CharField(help_text="Please enter a username : ")
	email = forms.CharField(help_text="Please enter email : ")
	password = forms.CharField(widget=forms.PasswordInput(), help_text="Please enter a password : ")

	class Meta:
		model=User
		fields=['username','email','password']

class UserProfileForm(forms.ModelForm):
	website = forms.URLField(help_text="Please enter ypur website.", required = False)
	picture = forms.ImageField("Select an Image to upload.")	

	class Meta:
		model = UserProfile	
		fields=['website','picture']	