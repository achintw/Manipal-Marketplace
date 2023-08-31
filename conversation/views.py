from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from item.models import Item

from .forms import ConversationMessageForm
from .models import Conversation

@login_required
def new_conversation(request, item_pk):
    # gets the item from the db
    item = get_object_or_404(Item, pk=item_pk)

    # if the curr user only has uploaded the item redirect them
    if item.created_by == request.user:
        return redirect('dashboard:index')

    # get all the conversations connected to this item, where you are a member
    conversations = Conversation.objects.filter(item=item).filter(members__in=[request.user.id])

    # if a convo already exists, redirect to that convo
    if conversations:
        return redirect('conversation:detail', pk=conversations.first().id)

    # if the form has been submitted
    if request.method == 'POST':
        form = ConversationMessageForm(request.POST)

        if form.is_valid():
            # create a new conversation for db
            conversation = Conversation.objects.create(item=item)

            # adding (you, item) to the members' list
            conversation.members.add(request.user)
            conversation.members.add(item.created_by)
            conversation.save()

            # the conversation written will be saved
            conversation_message = form.save(commit=False)   #temp save
            conversation_message.conversation = conversation
            conversation_message.created_by = request.user
            conversation_message.save()

            return redirect('item:detail', pk=item_pk)
    else:
        # if its not a post request
        form = ConversationMessageForm()
    
    return render(request, 'conversation/new.html', {
        'form': form
    })

@login_required
def inbox(request):
    conversations = Conversation.objects.filter(members__in=[request.user.id])

    return render(request, 'conversation/inbox.html', {
        'conversations': conversations
    })

@login_required
def detail(request, pk):
    conversation = Conversation.objects.filter(members__in=[request.user.id]).get(pk=pk)

    if request.method == 'POST':
        form = ConversationMessageForm(request.POST)

        if form.is_valid():
            conversation_message = form.save(commit=False)
            conversation_message.conversation = conversation
            conversation_message.created_by = request.user
            conversation_message.save()

            conversation.save()

            return redirect('conversation:detail', pk=pk)
    else:
        form = ConversationMessageForm()

    return render(request, 'conversation/detail.html', {
        'conversation': conversation,
        'form': form
    })
