from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from apps.product.api.views import (
    ProductListByCategorySlugView,
    CategoryListView,
    ProductSearchView,
    ProductBonusView,
    CategoryOnlyListView,
    PopularProducts,
    ArticleListView,
    ProductDetailView
)  # , SetListView

urlpatterns = [
          path('product/search/', ProductSearchView.as_view(), name='product-search'),
          path('bonus/', ProductBonusView.as_view(), name='bonus-list'),
          path('category/<slug:slug>/', ProductListByCategorySlugView.as_view(), name='category'),
          path('categories/', CategoryListView.as_view(), name='category-list'),
          path('categories/only/', CategoryOnlyListView.as_view(), name='category-only-list'),
          path('popular/products/', PopularProducts.as_view(), name='popular-products'),
          path('articles/<int:product_id>', ArticleListView.as_view(), name='article-list'),
          path('product/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
]
