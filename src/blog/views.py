from django.shortcuts import render
from .forms import PostForm
import requests
import openai
from django.urls import reverse
from .models import Post
from django.contrib.auth.models import User
from django.http import JsonResponse
from .common import process_option_default
import json
from django.shortcuts import redirect



openai.api_key = "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"


def landing(request):
    return render(request, 'blog/landing.html')



def post_form_view(request):
    context = {}
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            # Get the form data
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']

            # Prepare the data to send to the ChatGPT API
            data = {
                'title': title,
                'text': text
            }

            context['title'] = title

            # Make a POST request to the ChatGPT API and retrieve completion message
            completion_message = make_chat_completion(data['title'], data['text'])

            # Create a new User instance (assuming you have the user instance available)
            if completion_message:
                user = request.user
                post = Post(title=title, text=completion_message['content'], user=user)
                post.save()

            # Clear form fields
            form = PostForm()

            # Show the preview
            user_posts = get_user_posts(user.id)
            
            context['user_post'] = user_posts[0]
    else:
        form = PostForm()
    
    context['form'] = form
    

    return render(request, 'blog/post_form.html', context)



def make_chat_completion(title, content):
    

    result = process_option_default(title, content)
    print('resultt', result)

    # Make a POST request to the ChatGPT API
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        temperature=0.8,
        max_tokens=2000,
        messages=[
            {"role": "assistant", "content": result},
        ]
    )

    # Retrieve and return the completion message
    return completion.choices[0].message


def get_user_posts(user_id):
    # Get the User instance based on the user_id
    user = User.objects.get(id=user_id)

    # Retrieve all posts associated with the user
    posts = Post.objects.filter(user=user)

    return posts