from django.shortcuts import render, redirect
#from django.http import HttpResponse

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
# mixin to only allow logged in user access some pages/classes
from django.contrib.auth.mixins import LoginRequiredMixin
#import FormView which helps generate forms
from django.views.generic import FormView
from django.contrib.auth.forms import UserCreationForm
#login function to login customer in directly after registration
from django.contrib.auth import login
from .models import Task

# Create your views here.
#function based views
# def tasklist(request):
#     return HttpResponse('To do list working')

#class based views
class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    # Redirect authenticated users
    redirect_authenticated_user = True
    # Override success url once logged in
    def get_success_url(self):
        return reverse_lazy('tasks')

class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
   # redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')
    
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    
    #block authenticated users from this view
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)

class CustomLogoutView(LogoutView):
    next_page = 'login'

class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks' #variable object_list by default
    template = 'base/task_list.html'
    
    def  get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #modifying the data
        context['tasks'] = context['tasks'].filter(user = self.request.user)
        context['count'] = context['tasks'].filter(complete = False).count()
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(title__icontains = search_input)
        #avoid entire page reload
        context['search_input'] = search_input
        return context

class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task' #variable object by default
    template_name='base/task_detail.html'

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'base/task_form.html'
    #fields = '__all__'
    fields = ['title', 'description', 'complete']
    #redirect user after successful update
    success_url = reverse_lazy('tasks')

    #User can only create their own task
    def form_valid(self, form):
        #ensure its the logged in user
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    #template_name = 'base/task_form.html'
    #fields = '__all__'
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task_confirm_delete.html'
    success_url = reverse_lazy('tasks')

