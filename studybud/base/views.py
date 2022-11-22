
# import re
from email import message
import re
from xml.dom.minidom import Document
# import django
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from matplotlib.style import use
# from django.contrib.auth.forms import UserCreationForm

from . models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.contrib import messages

# Create your views here.
from django.http import HttpResponse
# rooms = [{'id':1, 'name':'Hello. this is my home'},
#     {'id':2, 'name':'Hello. this is my room'},
#     {'id':3, 'name':'Hello. this is my new home'}]

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
  
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None: 
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR Password does not exist')

    context = {'page':page}
    return render(request, 'login_register.html' ,context)


def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    context = {'form':form}
    return render(request, 'login_register.html', context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ""

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )

    topics = Topic.objects.all()[:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms':rooms, 'topics':topics, 
                'room_count':room_count,
                'room_messages':room_messages}
    return render(request, 'home.html', context)
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method=="POST":
        message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room':room, 'room_messages':room_messages,'participants':participants}
    return render(request, 'room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms,
             'room_messages':room_messages, "topics":topics
                }
    return render(request, 'profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method=='POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host= request.user,
            topic=topic, 
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        
        return redirect('home')
        
    context = {'form':form, "topics":topics}
    return render(request, 'room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed hear to edit !!")

    if request.method=='POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form':form, "topics":topics, 'room':room}
    return render(request, 'room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room= Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed hear to delete !!")

    if request.method=='POST':
        room.delete()
        return redirect('home')
    return render(request, 'delete.html', {'obj':room})




@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed hear to delete !!")

    if request.method=='POST':
        message.delete()
        return redirect('home')
    return render(request, 'delete.html', {'obj':message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    context = {'user':user, 'form':form}
    if request.method=="POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'update-user.html', context)


def topicPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ""
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics':topics,}
    return render(request, 'topics.html',context)


def activitiesPage(request):
    room_messages = Message.objects.all()[:20]
    return render(request, 'activity.html', {'room_messages':room_messages})