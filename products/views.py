from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductShortSerializer
from .services.product_service import ProductService


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'brand', 'barcode']
    filterset_fields = ['category']

    def get_serializer_class(self):
        if self.action == 'list' and self.request.query_params.get('short'):
            return ProductShortSerializer
        return ProductSerializer

    @action(detail=False, methods=['get'], url_path='barcode/(?P<code>[^/.]+)')
    def by_barcode(self, request, code=None):
        """
        GET api/product/barcode/000000000/
        Сначала локальный поиск, потом в OFF, при успехе - кэшируется
        """
        service = ProductService()
        product, created = service.get_by_barcode(code)

        if not product:
            return Response(
                {'detail': 'Продукт не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductSerializer(product)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'], url_path='import-search')
    def import_search(self, request):
        """
        GET api/product/import-search/?q=гречка
        Поиск локально + импорт из OFF
        """
        query = request.query_params.get('q', '').strip()
        if len(query) < 2:
            return Response(
                {'detail': 'Слишком короткий запрос'},
                status=status.HTTP_400_BAD_REQUEST
            )
        service = ProductService()
        products = service.search_and_import(query)
        return Response(ProductSerializer(products, many=True).data)
