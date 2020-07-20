from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from article.models import ArticlePost
from .forms import CommentForm
from .models import Comment


@login_required(login_url='/userprofile/login/')
def post_comment(request, article_id):
    article = get_object_or_404(ArticlePost, id=article_id)
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.user = request.user
            new_comment.save()
            return redirect(article)
        else:
            return HttpResponse("表单填写错误，请重新填写。")
    else:
        return HttpResponse("请用POST提交评论。")


@login_required(login_url='/userprofile/login/')
def delete_comment(request, article_id, comment_id):
    article = get_object_or_404(ArticlePost, id=article_id)
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user:
        return HttpResponse("对不起，您无权删除此评论。")
    else:
        comment.delete()
        return redirect(article)
