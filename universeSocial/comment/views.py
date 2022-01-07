from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import DestroyAPIView
from rest_framework.views import APIView

# Django Tools
from django.contrib.auth import get_user_model

from universeSocial.post.models import Post
from universeSocial.comment.models import Comment
from universeSocial.comment.serializers import CommentSerializer


class CreateCommentAPI(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        usertags = []
        for usertag_pk in data.get('tags'):
            try:
                usertag = get_user_model().objects.get(pk=usertag_pk)
            except get_user_model().DoesNotExist:
                usertag = None
            if usertag is not None:
                usertags.append(usertag)
        try:
            post = Post.objects.get(pk=data.get('post'))
            author = get_user_model().objects.get(pk=data.get('author'))
        except Post.DoesNotExist:
            post = None
        except get_user_model().DoesNotExist:
            author = None
        if post is not None and author is not None:
            comment = Comment(
                post=post,
                author=author,
                content=data.get('content'),
                usertags=usertags,
            )
            comment.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_404_NOT_FOUND,
                        data={"error": "Invalid pk values"})

class DeleteCommentAPI(DestroyAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
