from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from rest_framework.permissions import IsAdminUser

from rest_framework import generics, permissions, status, filters, views
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .models import Product, Order
from .serializers import ProductSerializer, UserSerializer, HistoricalOrderSerializer
# from .permissions import IsOwnerOrReadOnly
from .serializers import OrderSerializer
from .permissions import IsAdminUserOrOwner
class RegisterView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]  # Public read access
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price']

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)  # Only show user's orders

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUserOrOwner]

    def get_object(self):
        # Ensure only the owner or admin can view the order
        return generics.get_object_or_404(Order, pk=self.kwargs['pk'])
    
    def perform_update(self, serializer):
        if serializer.instance.status == 'Completed':
            raise serializers.ValidationError("Cannot update a completed order.")
        serializer.save()


from rest_framework import generics
from .permissions import IsAdminUserOrOwner


class OrderHistoryView(generics.RetrieveAPIView):
    """
    Retrieve the history of an order.
    """
    queryset = Order.objects.all()
    serializer_class = HistoricalOrderSerializer
    permission_classes = [IsAdminUserOrOwner]

    def get_object(self):
        # Ensure only the owner or admin can view the order history
        return generics.get_object_or_404(Order, pk=self.kwargs['pk'])