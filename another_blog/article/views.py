from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ArticlePost
import markdown
from .forms import ArticlePostForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q


# 文章列表
def article_list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    if search:
        if order == 'total_views':
            articles_list = ArticlePost.objects.filter(
                Q(title__icontains=search) | Q(body__icontains=search)
            ).order_by('-total_views')
        else:
            articles_list = ArticlePost.objects.filter(
                Q(title__icontains=search) | Q(body__icontains=search)
            )
    else:
        search = ''
        if order == 'total_views':
            articles_list = ArticlePost.objects.all().order_by('-total_views')
        else:
            articles_list = ArticlePost.objects.all().order_by('-created')


    # if request.GET.get('order') == 'total_views':
    #     articles_list = ArticlePost.objects.all().order_by('-total_views')
    #     order = 'total_views'
    # else:
    #     articles_list = ArticlePost.objects.all()
    #     order = 'normal'

    paginator = Paginator(articles_list, 3)
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    context = {'articles': articles, 'order': order, 'search': search}

    return render(request, 'article/list.html', context)


# 文章详情
def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    article.total_views += 1
    article.save(update_fields=['total_views'])
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            # 目录扩展 有些版本中是大写的 TOC
            'markdown.extensions.toc',
        ])
    article.body = md.convert(article.body)
    context = {'article': article, 'toc': md.toc}
    return render(request, 'article/detail.html', context)


# 新增文章
@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到新表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型要求
        if article_post_form.is_valid():
            # 保存数据，暂时不添加到数据库中。
            new_article = article_post_form.save(commit=False)
            # 指定用户为作者。  这里指定id=1的用户作为作者。
            new_article.author = User.objects.get(id=request.user.id)
            # 新文章保存到数据库中
            new_article.save()
            # 存储完成后，返回文章列表
            return redirect("article:article_list")
        # 如果数据不合法，返回错误信息。
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单实例
        article_post_form = ArticlePostForm()
        context = {'article_post_form': article_post_form}
        # 返回模板
        return render(request, 'article/create.html', context)


# 删除文章
@login_required(login_url='/userprofile/login/')
def article_delete(request, id):
    # 根据id获取要删除的文章
    article = ArticlePost.objects.get(id=id)
    # 调用delete方法删除文章
    article.delete()
    # 删除后返回文章列表
    return redirect("article:article_list")


# 安全删除文章
@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        if request.user != article.author:
            HttpResponse("抱歉，您无全删除此文章。")
        else:
            article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")


# 修改文章
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    article = ArticlePost.objects.get(id=id)
    if request.user != article.author:
        return HttpResponse('抱歉，您无权修改此文章。')
    else:
        if request.method == "POST":
            article_post_form = ArticlePostForm(data=request.POST)
            if article_post_form.is_valid():
                article.title = request.POST['title']
                article.body = request.POST['body']
                article.save()
                return redirect("article:article_detail", id=id)
            else:
                return HttpResponse("表单内容有误，请重新填写。")
        else:
            article_post_form = ArticlePostForm()
            context = {'article': article, 'article_post_form': article_post_form}
            return render(request, 'article/update.html', context)
