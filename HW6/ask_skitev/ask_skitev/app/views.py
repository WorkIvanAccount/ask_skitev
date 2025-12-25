from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import models
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

from app.models import Question, QuestionLike, Profile, Answer, AnswerLike, Tag
from app.forms import LoginForm, SignUpForm, UserForm, ProfileForm, QuestionForm, AnswerForm

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json

@login_required
@require_POST
def like_question_ajax(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    profile = request.user.profile  # ← профиль должен существовать

    like, created = QuestionLike.objects.get_or_create(
        user=profile,  # ← используем имя поля "user", как в модели
        question=question
    )

    if not created:
        like.delete()

    return JsonResponse({
        'success': True,
        'new_rating': question.likes.count()  # ← если related_name='likes'
    })


def paginate(objects_list, request, per_page=10):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(objects_list, per_page)

    try:
        page = paginator.page(page_num)
    except (PageNotAnInteger, ValueError):
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page

def index(request):
    tag_name = request.GET.get("tag")

    if tag_name:
        questions = Question.objects.by_tag(tag_name)
    else:
        questions = Question.objects.new()

    page = paginate(questions, request)

    popular_tags = Tag.objects.annotate(
        num_questions=models.Count('question')
    ).order_by('-num_questions')[:15]

    return render(request, 'index.html', {
        'questions': page.object_list,
        'page_obj': page,
        'tags': popular_tags,
        'active_tag': tag_name,
    })



def hot(request):
    questions = Question.objects.hot()
    page = paginate(questions, request, per_page=3)

    popular_tags = Tag.objects.annotate(num_questions=models.Count('question')).order_by('-num_questions')[:15]

    return render(request, 'hotquestion.html', {
        'page_obj': page,
        'questions': page.object_list,
        'tags': popular_tags,
    })


@login_required
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, user=request.user)
        if form.is_valid():
            question = form.save()
            messages.success(request, 'Вопрос успешно добавлен!')
            return redirect('question', question_id=question.id)
    else:
        form = QuestionForm(user=request.user)

    return render(request, 'ask.html', {'form': form})

def reg(request):
    return render(request, 'register.html')


def settings(request):
    return render(request, 'settings.html')


def login_view(request):

    next_url = request.GET.get('continue') or request.POST.get('next') or '/'
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect(request.POST.get('next') or '/')
            else:
                form.add_error(None, 'Неверный логин или пароль')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form, 'next': next_url})


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Регистрация прошла успешно')
            return redirect('/')
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})


def logout_view(request):
    referer = request.META.get('HTTP_REFERER', '/')
    auth_logout(request)
    return redirect(referer)


@login_required
def profile_edit(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    if request.method == 'POST':
        uform = UserForm(request.POST, instance=user)
        pform = ProfileForm(request.POST, request.FILES, instance=profile)
        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, 'Профиль обновлён')
            return redirect(request.path)
    else:
        uform = UserForm(instance=user)
        pform = ProfileForm(instance=profile)
    return render(request, 'profile_edit.html', {'uform': uform, 'pform': pform})



def question(request, question_id):
    current_question = get_object_or_404(Question, id=question_id)
    answers = current_question.answer_set.all()
    page = paginate(answers, request, per_page=5)

    if request.method == 'POST':
        form = AnswerForm(request.POST, user=request.user, question=current_question)
        if form.is_valid():
            answer = form.save()
            messages.success(request, 'Ответ успешно добавлен!')
            return redirect(f'/question/{current_question.id}/#answer-{answer.id}')
    else:
        form = AnswerForm(user=request.user, question=current_question)

    return render(request, 'question.html', {
        'question': current_question,
        'answers': page.object_list,
        'page_obj': page,
        'form': form
    })


@login_required
def like_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    profile, _ = Profile.objects.get_or_create(user=request.user)

    like, created = QuestionLike.objects.get_or_create(user=profile, question=question)

    if not created:
        like.delete()

    return redirect(request.META.get('HTTP_REFERER', '/'))
@login_required
def like_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    profile, _ = Profile.objects.get_or_create(user=request.user)

    like, created = AnswerLike.objects.get_or_create(user=profile, answer=answer)

    if not created:
        like.delete()

    return redirect(request.META.get('HTTP_REFERER', '/'))
