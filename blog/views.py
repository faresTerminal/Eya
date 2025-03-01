from django.shortcuts import render, get_object_or_404, redirect, reverse
from blog.forms import ContactForm, CommentForm
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, request
from django.contrib import messages
from blog.models import Article, comment_put
from django.db.models import Q
from store.models import Signboard_Blog
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .forms import ArticleForm

from django.contrib.auth import get_user_model
from notification.models import Notification

from publicite.models import SlideAd, ShowAd

# Create your views here.
def about(request):
    
    return render(request, 'blog/about.html')



def faqs(request):
    
    return render(request, 'blog/faqs.html')


def blog(request):
    blog = Article.objects.all().order_by('-id')
    blog_count = Article.objects.count()
    popular_posts = Article.objects.filter(featured = False).order_by('-id')[:4]
    signbord_blog = Signboard_Blog.objects.all().order_by('-id')[:1]

    paginator = Paginator(blog, 8)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = blog.count()



    context = {

         'blog': paged_products,
         'popular_posts': popular_posts,
         'blog_count': blog_count,
         'signbord_blog': signbord_blog,
         

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
    popular_posts = Article.objects.filter(featured = False).order_by('-id')[:4]


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

from django.contrib.auth.models import User  # or your custom admin model
from accounts.models import Account
def save_contact(request):
    if request.method == 'POST':
        f = ContactForm(request.POST)
        if f.is_valid():
            c = f.save(commit=False)
            c.save()
            messages.success(request, 'Thank you for your intention.')

            # Send notification to all superadmin users
            admins = Account.objects.filter(is_admin=True)
            # Get the sender's profile picture URL
            profile_picture_url = request.user.userprofile.profile_picture.url if request.user.userprofile.profile_picture else '/static/default_profile_picture.png'

            for admin in admins:
                Notification.objects.create(
                    sender=request.user,
                    recipient=admin,
                    message="A new contact form has been submitted.",
                    url='/admin/blog/contact/',
                    profile_picture_url=profile_picture_url  # Add the profile picture URL here
                )

    return HttpResponseRedirect('/blog/contact')





def save_comment(request, id, slug):
    post = get_object_or_404(Article, id=id, slug=slug)  # Use get_object_or_404 for better error handling
    
    if request.method == 'POST':
        f = CommentForm(request.POST)
        if f.is_valid():
            c = f.save(commit=False)
            c.put_to_blog = post
            c.user_comment = request.user
            
            c.save()
            messages.success(request, 'Your comment has been added.')

            # Send notification to the author of the article or relevant users
            profile_picture_url = (
                request.user.userprofile.profile_picture.url if request.user.userprofile.profile_picture else '/static/default_profile_picture.png'
            )
            # You can modify the recipient as needed; currently set to the post author
            Notification.objects.create(
                sender=request.user,
                recipient=post.bloger,  # Assuming the post has an 'author' field
                message=f"New comment on your article \n'{post.title}' \nfrom {request.user.username}.",
                url=f"/blog/blog/{post.id}/{post.slug}/",  # Redirect to the article detail page
                profile_picture_url=profile_picture_url
            )

    # Fetch the latest comment for the context
    add = comment_put.objects.all().order_by('-id')[:1]
    context = {
        'post': post,
        'add': add,
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
            article.bloger = request.user
            article.save()
            messages.success(request, 'Article added successfully!')

            # Get all users except the article creator
            User = get_user_model()
            all_users = User.objects.exclude(id=request.user.id)

            # Show only the first 6 words with "..." if the article title has more than 6 words
            article_title_words = article.title.split()
            if len(article_title_words) > 6:
                article_title_display = ' '.join(article_title_words[:6]) + '...'
            else:
                article_title_display = article.title

            # Fetch profile picture URL or fallback if it’s not set
            profile_picture_url = (
                request.user.userprofile.profile_picture.url if hasattr(request.user, 'userprofile') and request.user.userprofile.profile_picture
                else None
            )

            for user in all_users:
                Notification.objects.create(
                    sender=request.user,
                    recipient=user,
                    message=f"A new article \n'{article_title_display}'\n has been published.",
                    url=article.get_absolute_url(),  # Assuming article has get_absolute_url
                    profile_picture_url=profile_picture_url  # Set profile picture URL or None if not available
                )

            return redirect(article.get_absolute_url())
    else:
        form = ArticleForm()

    return render(request, 'blog/add_article.html', {'form': form})








def Terms_and_conditions(request):
  return render(request, 'blog/terms_and_conditions.html')


def Privacy(request):
  return render(request, 'blog/privacy.html')


