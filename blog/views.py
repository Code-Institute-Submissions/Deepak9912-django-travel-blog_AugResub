from django.shortcuts import(
    render, get_object_or_404, reverse, redirect)
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic, View
from .models import Post, Comment
from .forms import CommentForm
from django.views.generic.edit import UpdateView
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail, BadHeaderError
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages


class PostList(generic.ListView):
    model = Post
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'index.html'
    paginate_by = 6


class DetailBlog(View):
    """View to read the blog post in detail"""
    def get(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            True

        return render(
            request,
            "detail_blog.html",
            {
                "post": post,
                "comments": comments,
                "commented": False,
                "liked": liked,
                "comment_form": CommentForm()
            },
        )

    def post(self, request, slug, *args, **kwargs):

        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
        else:
            comment_form = CommentForm()

        return render(
            request,
            "detail_blog.html",
            {
                "post": post,
                "comments": comments,
                "commented": True,
                "comment_form": comment_form,
                "liked": liked
            },
        )


# To like a post
class LikePost(View):
    """View to like or unlike the post"""
    
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return HttpResponseRedirect(reverse('detail_blog', args=[slug]))


# Delete a comment
@login_required
def delete_comment(request, comment_id):
    """View to delete a comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    print(f"Comment slug: {comment.post.slug}")
    messages.success(request, 'The comment was deleted successfully')
    return redirect(reverse_lazy('detail_blog', args=[comment.post.slug]))


class EditComment(UpdateView):
    """View to edit a comment"""
    model = Comment
    template_name = 'edit_comment.html'
    form_class = CommentForm
    success_message = 'The comment was successfully updated'
