from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from app.models import Question, Answer

QUESTIONS = [{
    'id' : i,
    'title' : f'Title #{i}',
    'text' : 'Text',
} for i in range(30)]

ANSWERS = [{
    'id' : i,
    'text' : f'Text #{i}',
    'correct' : 'Correct',
} for i in range(15)]



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
    questions = Question.objects.all()
    page = paginate(questions, request)

    return render(request, 'index.html', context={
        'questions' : page.object_list,
        'page_obj' : page
    })

def hot(request):
    questions = Question.objects.hot()  # ← используй менеджер!
    page = paginate(questions, request, per_page=3)
    return render(request, 'hotquestion.html', {
        'questions': page.object_list,
        'page_obj': page
    })


def ask(request):
    return render(request, 'ask.html')
def reg(request):
    return render(request, 'register.html')
def login(request):
    return render(request, 'login.html')
def settings(request):
    return render(request, 'settings.html')



def question(request, question_id):
    current_question = Question.objects.get(id=question_id)
    answers = current_question.answer_set.all()
    page = paginate(answers, request, per_page=5)

    return render(request, 'question.html', {
        'question': current_question,
        'answers': page.object_list,
        'page_obj': page
    })