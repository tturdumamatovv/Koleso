from django import forms
from django.forms import Form
from rest_framework import generics, status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response

from apps.product.models import Category
from apps.pages.models import (
    Banner,
    MainPage,
    Contacts,
    StaticPage, Stories, StoriesUserCheck
)
from apps.pages.api.serializers import (
    HomePageSerializer,
    ContactsSerializer,
    StaticPageSerializer,
    LayOutSerializer,
    BannerSerializer, MetaDataSerializer, StoriesSerializer, StoriesCheckSerializer
)


class HomePageView(generics.GenericAPIView):
    serializer_class = HomePageSerializer

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        banners = Banner.objects.filter(is_active=True)
        main_page = MainPage.objects.first()

        serializer = self.get_serializer({'categories': categories, 'banners': banners, 'main_page': main_page})
        return Response(serializer.data)


class MetaDataView(generics.GenericAPIView):
    serializer_class = MetaDataSerializer

    def get(self, request, *args, **kwargs):
        main_page = MainPage.objects.first()
        serializer = self.get_serializer(main_page, context={'request': request})

        return Response(serializer.data)


class ContactsView(generics.GenericAPIView):
    serializer_class = ContactsSerializer

    def get(self, request, *args, **kwargs):
        contacts = Contacts.objects.first()
        serializer = self.get_serializer(contacts)
        return Response(serializer.data)


class StaticPageDetailView(generics.RetrieveAPIView):
    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer
    lookup_field = 'slug'

    def get_serializer(self, *args, **kwargs):
        return StaticPageSerializer(*args, **kwargs, context={'request': self.request})

    def get_object(self):
        slug = self.kwargs['slug']
        instance = None

        try:
            instance = StaticPage.objects.get(slug=slug)
        except StaticPage.DoesNotExist:
            if slug == 'about-us':
                instance = StaticPage.objects.create(
                    title='О нас',
                    title_ru='О нас',
                    title_ky='Биз жөнүндө',

                    description='О нас',
                    description_ru='О нас',
                    description_ky='Биз жөнүндө',
                    slug="about-us"
                )
            elif slug == 'delivery':
                instance = StaticPage.objects.create(
                    title='Доставка',
                    title_ru='Доставка',
                    title_ky='Доставка',

                    description='Доставка',
                    description_ru='Доставка',
                    description_ky='Доставка',
                    slug="delivery"
                )

        return instance

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class LayOutView(generics.ListAPIView):
    queryset = MainPage.objects.all()
    serializer_class = LayOutSerializer


class BannersView(ListAPIView):
    queryset = Banner.objects.filter(is_active=True).order_by('-created_at')

    def get_serializer(self, *args, **kwargs):
        return BannerSerializer(*args, **kwargs, context={'request': self.request})


class StoriesView(ListAPIView):
    queryset = Stories.objects.filter(is_active=True)

    def get_serializer(self, *args, **kwargs):
        return StoriesSerializer(*args, **kwargs, context={'request': self.request})


class StoriesViewedView(CreateAPIView):
    serializer_class = StoriesCheckSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            stories = Stories.objects.get(id=serializer.validated_data['stories'])
            user = request.user
            StoriesUserCheck.objects.create(stories=stories, user=user)
            return Response({"message": "Story checked successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
