from rest_framework import response, status, decorators, permissions
from rest_framework.generics import get_object_or_404
from djoser.views import UserViewSet as DjoserViewSet

from core.pagination import PageNumberAndLimit

from .serializers import SubscriptionSerializer, UserAndSubscriptionSerializer

from .models import Subscription, User


class UserViewSet(DjoserViewSet):
    """Пользовательский ViewSet."""

    pagination_class = PageNumberAndLimit

    @decorators.action(detail=False, methods=('get',))
    def me(self, request, *args, **kwargs):
        return response.Response(
            self.get_serializer(request.user).data,
            status.HTTP_200_OK,
        )

    @decorators.action(detail=False, methods=('get',))
    def subscriptions(self, request, *args, **kwargs):
        page = self.paginate_queryset(
            User.objects.filter(subscribed__user=request.user)
        )
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @decorators.action(detail=True, methods=('post', 'delete'))
    def subscribe(self, request, id=None, *args, **kwargs):
        if request.method == 'POST':
            return response.Response(
                self._get_subscribe_data(request, id, *args, **kwargs),
                status.HTTP_201_CREATED,
            )
        subscription = Subscription.objects.filter(
            user_id=request.user.id, subscribed_id=id
        )
        if not subscription.exists():
            return response.Response(
                {'error': 'Нет подписки на данного пользователя!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in ('subscriptions', 'subscribe'):
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'subscriptions':
            return SubscriptionSerializer
        if self.action == 'subscribe':
            return UserAndSubscriptionSerializer
        return super().get_serializer_class()

    def _get_subscribe_data(self, request, pk=None, *args, **kwargs):
        subscribed = get_object_or_404(User, id=pk)
        serializer = self.get_serializer(
            data={
                'user': request.user,
                'subscribed': subscribed,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return SubscriptionSerializer(subscribed).data
