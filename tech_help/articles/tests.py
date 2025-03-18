
from django.test import TestCase, RequestFactory
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse

# Импортируйте ваши модели здесь
from .models import Article, Category  # Замените . на путь к вашим моделям

# Импортируйте вашу функцию представления
from .views import article_list  # Замените . на путь к вашему представлению


class ArticleListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем тестовые данные, которые будут использоваться во всех тестах класса
        cls.category1 = Category.objects.create(name="Category 1", slug="category-1")
        cls.category2 = Category.objects.create(name="Category 2", slug="category-2")

        # Создаем RequestFactory для создания поддельных запросов
        cls.factory = RequestFactory()
        request = cls.factory.get(reverse('article_list')) # Замените 'article_list' на имя вашего URL


        # Создаем 25 статей для тестирования пагинации
        for i in range(25):
            if i % 2 == 0:
                category = cls.category1
            else:
                category = cls.category2
            Article.objects.create(title=f"Article {i+1}", category=category, author=request.user)

        


    def test_article_list_no_filter(self):
        """Тест: Отображение всех статей без фильтрации."""
        request = self.factory.get(reverse('article_list')) # Замените 'article_list' на имя вашего URL
        response = article_list(request)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/article_list.html') # Замените путь на ваш шаблон
        self.assertEqual(len(response.context['articles'].object_list), 12) # Проверяем количество статей на первой странице (items_per_page = 12)
        self.assertEqual(response.context['articles'].number, 1) # Проверяем, что это первая страница
        self.assertEqual(response.context['categories'].count(), 2) # Проверяем, что все категории передаются


    def test_article_list_filtered_by_category(self):
        """Тест: Отображение статей, отфильтрованных по категории."""
        request = self.factory.get(reverse('article_list') + '?category=category-1') # Замените 'article_list' на имя вашего URL
        response = article_list(request)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/article_list.html') # Замените путь на ваш шаблон
        filtered_articles = Article.objects.filter(category=self.category1)
        paginator = Paginator(filtered_articles, 12) # Убедитесь, что items_per_page совпадает

        self.assertEqual(len(response.context['articles'].object_list), len(paginator.page(1).object_list)) # Проверяем, что количество статей на странице соответствует отфильтрованным
        self.assertEqual(response.context['categories'].count(), 2) # Проверяем, что все категории передаются


    def test_article_list_pagination(self):
        """Тест: Проверка пагинации."""
        request = self.factory.get(reverse('article_list') + '?page=2')  # Замените 'article_list' на имя вашего URL
        response = article_list(request)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/article_list.html') # Замените путь на ваш шаблон
        self.assertEqual(len(response.context['articles'].object_list), 12)  # Вторая страница должна иметь 12 статей
        self.assertEqual(response.context['articles'].number, 2) # Проверяем, что это вторая страница
        self.assertEqual(response.context['categories'].count(), 2) # Проверяем, что все категории передаются

        request = self.factory.get(reverse('article_list') + '?page=3') # Замените 'article_list' на имя вашего URL
        response = article_list(request)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/article_list.html') # Замените путь на ваш шаблон
        self.assertEqual(len(response.context['articles'].object_list), 1)  # Третья страница должна иметь только 1 статью
        self.assertEqual(response.context['articles'].number, 3) # Проверяем, что это третья страница
        self.assertEqual(response.context['categories'].count(), 2) # Проверяем, что все категории передаются

    def test_article_list_invalid_page(self):
        """Тест: Обработка некорректного номера страницы."""
        # Проверяем, что при запросе некорректной страницы отображается первая страница
        request = self.factory.get(reverse('article_list') + '?page=abc') # Замените 'article_list' на имя вашего URL
        response = article_list(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['articles'].number, 1)

        # Проверяем, что при запросе страницы больше максимальной отображается последняя страница
        request = self.factory.get(reverse('article_list') + '?page=999') # Замените 'article_list' на имя вашего URL
        response = article_list(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['articles'].number, 3) # всего 3 страницы


    def test_article_list_empty_category(self):
      """Тест: Проверка, что ничего не сломается, если нет статей в выбранной категории."""
      category3 = Category.objects.create(name="Category 3", slug="category-3")
      request = self.factory.get(reverse('article_list') + '?category=category-3')
      response = article_list(request)

      self.assertEqual(response.status_code, 200)
      self.assertTemplateUsed(response, 'articles/article_list.html')
      self.assertEqual(len(response.context['articles'].object_list), 0)
      self.assertEqual(response.context['articles'].number, 1)
      self.assertEqual(response.context['categories'].count(), 3)



# --- Замечания ---
# 1. Замените пути импорта (from .models import Article, Category и from .views import article_list) на правильные пути к вашим моделям и представлениям.
# 2. Замените 'article_list' на имя вашего URL для представления article_list.  Используйте reverse() для динамического получения URL по имени.
# 3. Замените 'articles/article_list.html' на путь к вашему шаблону.
# 4. Убедитесь, что ваши тестовые данные (setup) создают минимально необходимое количество объектов для эффективного тестирования.
# 5.  Убедитесь, что  `items_per_page`  в тестах соответствуют  `items_per_page`  в вашем представлении.
# 6. Добавлены тесты на граничные случаи: некорректный номер страницы и пустая категория.
# 7.  Убедитесь, что у вас настроен `reverse` для URL-шаблона `article_list` в `urls.py`.
