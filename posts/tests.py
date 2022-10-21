from http import client
from socket import fromfd
from urllib import response

from django.core.cache import cache
from django.test import Client
from django.test import TestCase
from .models import Post, User, Group
from django.urls import reverse

# проверяют, что срабатывает защита от загрузки файлов не-графических форматов

class ProfileTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.auth_client = Client()

        self.username = 'test_user'
        self.email = 'user@test.com'
        self.password = '123'

        self.user = User.objects.create(username=self.username, email=self.email)
        self.user.set_password(self.password)
        self.user.save()
        self.auth_client.login(username=self.username, password=self.password)

    # После регистрации пользователя создается его персональная страница (profile)
    def test_user_profile(self):
        # формируем GET-запрос к странице сайта
        response = self.auth_client.get(
            reverse("profile", kwargs={"username": self.username})
        )
        # Проверяем, что страница найдена
        self.assertEqual(response.status_code, 200)
        # проверяем, что объект пользователя, переданный в шаблон,
        # соответствует пользователю, которого мы создали
        self.assertIsInstance(response.context["profile_user"], User)
        self.assertEqual(
            response.context["profile_user"].username,
            self.username
        )

    # Неавторизованный посетитель не может опубликовать пост (его редиректит на страницу входа) DONE
    def test_not_auth_user_create_post(self):
        response = self.client.get(reverse('new_post'))
        # Код 302 показывает, что происходит редирект
        self.assertEqual(response.status_code, 302)
        # Находим адрес старниц после редиректа(Также универсальная проверка на
        # незарегистрированного пользователя)
        self.assertTrue(response.url.startswith('/auth/login/'))

    # Авторизованный пользователь может опубликовать пост (new)
    def test_auth_user_create_post(self):
        test_text = 'test test test'
        self.auth_client.post(reverse('new_post'), data={'text': test_text})
        response = self.auth_client.get(
            reverse("profile", kwargs={"username": self.username}))
        # page состоит только из 1 записи
        self.assertEqual(len(response.context['page']), 1)
        # на странице отображается тестовый пост
        self.assertContains(response, test_text)

    # После публикации поста новая запись появляется на главной странице сайта (index), на персональной странице пользователя (profile), и на отдельной странице поста (post)
    def test_auth_user_view_post(self):
        test_text = 'test test test'
        self.auth_client.post(reverse('new_post'), data={'text': test_text})
        post_id = Post.objects.get(author=self.user).pk
        urls = (
            reverse('index'),
            reverse('profile', kwargs={'username': self.username}),
            reverse('post', kwargs={
                    'username': self.username, 'post_id': post_id})
        )
        for element in urls:
            response = self.auth_client.get(element)
            # на странице отображается тестовый пост
            self.assertContains(response, test_text)

    # Авторизованный пользователь может отредактировать свой пост и его содержимое изменится на всех связанных страницах
    def test_auth_user_change_post(self):
        test_text = 'test test test'
        test_text2 = 'change change change'
        self.auth_client.post(reverse('new_post'), data={'text': test_text})
        post_id = Post.objects.get(author=self.user).pk
        self.auth_client.post(reverse('post_edit', kwargs={'username':self.username,'post_id': post_id }), data={'text': test_text2})
        urls = (
            reverse('index'),
            reverse('profile', kwargs={'username': self.username}),
            reverse('post', kwargs={
                    'username': self.username, 'post_id': post_id})
        )
        for element in urls:
            response = self.auth_client.get(element)
            # на странице отображается тестовый пост
            self.assertContains(response, test_text2)


class ImageTests(TestCase):
    def setUp(self) -> None:
        self.auth_client = Client()
        self.username = 'test_user'
        self.email = 'user@test.com'
        self.password = '123'

        self.user = User.objects.create(username=self.username, email=self.email)
        self.user.set_password(self.password)
        self.user.save()
        self.auth_client.login(username=self.username, password=self.password)

        self.test_text = 'test test test'
        self.test_slug = 'test1'
        self.test_title_group = 'test group'
        self.test_description = 'test description'
        self.group = Group.objects.create(title=self.test_title_group, slug=self.test_slug, description=self.test_description)
        with open('posts/1.jpg','rb') as img:
            self.auth_client.post(reverse('new_post'), data={'text': self.test_text,'group': self.group.id,  'image': img}, follow=True)

        self.urls=(
            reverse('index'),
            reverse('profile', kwargs={'username': self.username}),
            reverse('group', kwargs={'slug':self.test_slug})
        )

    # проверяют страницу конкретной записи с картинкой: на странице есть тег <img>
    def test_post_view_has_img(self):
        response = self.auth_client.get(reverse('group', kwargs={'slug':self.test_slug}))
        self.assertEqual(response.status_code,200)
        response = self.auth_client.get(
        reverse("post", kwargs={"username": self.username, 'post_id': Post.objects.get(pk=1).id}))
        self.assertEqual(response.status_code,200)
        self.assertContains(response, '<img')

    # проверяют, что на главной странице, на странице профайла и на странице группы пост с картинкой отображается корректно, с тегом <img>
    def test_img_on_all_views(self):

        for element in self.urls:
            response = self.auth_client.get(element)
            self.assertEqual(response.status_code,200)
            self.assertContains(response, '<img')

    # проверяют, что срабатывает защита от загрузки файлов не-графических форматов
    def test_img_wrong_format(self):
        Post.objects.all().delete()
        with open('posts/test_text.txt','rb') as img:
           self.auth_client.post(reverse('new_post'), data={'text': self.test_text,'group': self.group.id,  'image': img}, follow=True)

        for element in self.urls:
            response = self.auth_client.get(element)
            self.assertEqual(response.status_code,200)
            self.assertNotContains(response, '<img')


class CashTest(TestCase):
    def setUp(self):
        self.auth_client = Client()
        self.username = 'test_user'
        self.email = 'user@test.com'
        self.password = '123'

        self.user = User.objects.create(username=self.username, email=self.email)
        self.user.set_password(self.password)
        self.user.save()
        self.auth_client.login(username=self.username, password=self.password)

    def test_cash(self):
        test_text = 'test test test'
        test_text2 = 'change change change'
        self.auth_client.post(reverse('new_post'), data={'text': test_text})
        response = self.auth_client.get('/')
        # на странице отображается тестовый пост
        self.assertContains(response, test_text)
        self.auth_client.post(reverse('new_post'), data={'text': test_text2})
        self.assertNotContains(response, test_text2)
        cache.clear()
        response = self.auth_client.get('/')
        self.assertContains(response, test_text2)