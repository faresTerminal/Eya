from django.shortcuts import render, get_object_or_404, redirect, reverse
from blog.forms import ContactForm, CommentForm
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, request
from django.contrib import messages
from blog.models import Article, comment_put
from django.db.models import Q
from store.models import Signboard

from .forms import ArticleForm

# Create your views here.
def about(request):
    
    return render(request, 'blog/about.html')



def faqs(request):
    
    return render(request, 'blog/faqs.html')


def blog(request):
    blog = Article.objects.all().order_by('-id')[:10]
    blog_count = Article.objects.count()
    popular_posts = Article.objects.filter(featured = True).order_by('-id')[:4]
    signbord = Signboard.objects.all().order_by('-id')[:1]
    context = {

         'blog': blog,
         'popular_posts': popular_posts,
         'blog_count': blog_count,
         'signbord': signbord,

        }

    return render(request, 'blog/blog.html', context)


def blog_detail(request):
   
    return render(request, 'blog/blog_detail.html')

# show the true link publish(details)
def show_article(request, id, slug):

    post = get_object_or_404(Article, id=id, slug = slug)
    add = comment_put.objects.all().filter(put_to_blog = id).order_by('-id')
    #add = comment_put.objects.all().filter(user_put = id).order_by('-id')
    art = Article.objects.get(pk = id, slug = slug)
    featured = Article.objects.filter(featured=True).order_by('-id')[:3]
    three = Article.objects.order_by('-id')[:4]
    popular_posts = Article.objects.filter(featured = True).order_by('-id')[:4]


    previous_post = Article.objects.filter(publish__lt=post.publish).last()
    next_post = Article.objects.filter(publish__gt=post.publish).first()
    
    context = {
         'art': art,
         'three': three,
         'post': post,
         'add': add,
         'featured': featured,
         'popular_posts': popular_posts,
         'previous_post': previous_post,
         'next_post': next_post,


          }
   
   
  
    return render(request, 'blog/blog_detail.html', context)



def contact(request):
    
      return render(request, 'blog/contact.html')

def save_contact(request):
   
    if request.method == 'POST':
        f = ContactForm(request.POST)
        if f.is_valid():
            c = f.save(commit = False)
            c.save()
            messages.success(request, 'thank you for your Intention.')
    
    return HttpResponseRedirect('/blog/contact')



def save_comment(request, id, slug):
   
    post = Article.objects.get(id = id, slug = slug)
   
    
    if request.method == 'POST':
        f = CommentForm(request.POST)
        if f.is_valid():
            c = f.save(commit = False)
           
            c.put_to_blog = post
            
            c.save()
            messages.success(request, 'Your Comment Added.')

    add = comment_put.objects.all().order_by('-id')[:1]
    context = {
      'post': post,
      
      'add':add,
    
    }
    
    redirect_to = reverse('show_article', kwargs={'id': post.id, 'slug': post.slug})
    return redirect(redirect_to, context)



def Blog_Search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            blog = Article.objects.order_by('-posted_on').filter(Q(body__icontains=keyword) | Q(title__icontains=keyword))
            blog_count = blog.count()
    context = {
        'blog': blog,
        'blog_count': blog_count,
    }
    return render(request, 'blog/blog.html', context)




def create_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.bloger = request.user  # Set the 'bloger' field to the currently logged-in user
            article.save()
            return redirect(article.get_absolute_url())  # Redirect to the article detail page
    else:
        form = ArticleForm()

    
    return render(request, 'blog/add_article.html', {'form': form})




def Terms_and_conditions(request):
  return render(request, 'blog/terms_and_conditions.html')


def Privacy(request):
  return render(request, 'blog/privacy.html')
