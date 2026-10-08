from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category,Product
from .serializers import CategorySerializer, ProductSerializer, ProductShortSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter,DjangoFilterBackend]
    search_fields = ['name','brand','barcode']
    filterset_fields = ['category']

    def get_serializer_class(self):
        if self.action == 'list' and self.request.query_params.get('short'):
            return ProductShortSerializer
        return ProductSerializer