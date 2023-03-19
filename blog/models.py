from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count, Prefetch
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404


class PostQuerySet(models.QuerySet):
    def year(self, year):
        posts_at_year = self.filter(published_at__year=year).order_by('published_at')
        return posts_at_year

    def popular(self):
        popular_posts = (
            Post.objects
            .annotate(Count('likes', distinct=True))
            .order_by('-likes__count'))
        return popular_posts

    def prefetch_tags_count(self):
        prefetch = Prefetch(
            'tags',
            queryset=Tag.objects.annotate(Count('posts')))
        posts = self.prefetch_related(prefetch)
        return posts

    def fetch_with_comments_count(self):
        '''function working better only on small sets'''
        posts_ids = [post.id for post in self]
        
        posts_with_comments = Post.objects.filter(
            id__in=posts_ids
        ).annotate(Count('comments', distinct=True))
        
        ids_and_comments = posts_with_comments.values_list('id', 'comments__count')  
        count_for_id = dict(ids_and_comments)
        for post in self:
            post.comments__count = count_for_id[post.id]
        posts = list(self)
        return posts

    def get_object_or_404(self, slug):
        try: 
            obj = self.get(slug=slug)
        except ObjectDoesNotExist:
            raise Http404
    
        return obj


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})


class TagQuerySet(models.QuerySet):
    def popular(self):
        popular_tags = (
            self
            .annotate(Count('posts'))
            .order_by('-posts__count')
            )
        return popular_tags


class Tag(models.Model):
    title = models.CharField('Тег', max_length=20, unique=True)
    objects = TagQuerySet.as_manager()

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    def clean(self):
        self.title = self.title.lower()


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост, к которому написан')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')

    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'
