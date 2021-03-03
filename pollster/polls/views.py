import datetime
from time import timezone

from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from ipware import get_client_ip

from .models import Question, Choice, DailyVote


# Get questions and display them


def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)


def voting(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/vote.html', context)


# Show specific question and choices


def detail(request, question_id):
    ip, is_routable = get_client_ip(request)
    already_visited = False

    try:
        dailyVote = DailyVote.objects.get(client_ip=ip)
        if (dailyVote.last_vote_date.date() != datetime.date.today()):
            dailyVote.last_vote_date = datetime.date.today()
            dailyVote.save()
        else:
            already_visited = True
    except DailyVote.DoesNotExist:
        new_user_vote = DailyVote(client_ip=ip, last_vote_date=datetime.date.today())
        new_user_vote.save()

    try:
        question = Question.objects.get(pk=question_id)

    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'polls/detail.html', {'question': question, 'already_visited': already_visited})


# Get question and display results


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})


# Vote for a question choice


def vote(request, question_id):
    # print(request.POST['choice'])
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:

        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
