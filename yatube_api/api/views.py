from rest_framework import viewsets
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .permissions import AuthorOrReadOnly
from posts.models import Post, Group, Follow
from .serializers import PostSerializer, GroupSerializer
from .serializers import FollowSerializer, CommentSerializer
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters


User = get_user_model()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [AuthorOrReadOnly]


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('following__username',)

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        new_queryset = user.follower.all()
        return new_queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        super(FollowViewSet, self).perform_create(serializer)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [AuthorOrReadOnly]

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        return post.comments.all()
