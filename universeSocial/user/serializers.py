from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User
from universeSocial.post.models import Post

class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer of creating user"""
    class Meta:
        model = get_user_model()
        fields = ['full_name', 'lastname','birthday', 'email', 'password']

        def create(self, validated_data):
            user = super().create(validated_data)
            user.set_password(validated_data['password'])
            user.save()
            return user


class MiniUserSerializer(serializers.ModelSerializer):
    """Mini version of User Serializer"""

    class Meta:
        model = get_user_model()
        fields = ['pk', 'username', 'full_name', 'profile_pic']

class PostSerializer(serializers.ModelSerializer):
    author = MiniUserSerializer(many=True)
    likes = MiniUserSerializer(many = True)
    tags = MiniUserSerializer(many = True)
    class Meta:
        model = Post
        fields = ['pk', 'author', 'image', 'caption', 'location',
                  'likes', 'likes_count', 'tags'
                  ]
    def validate_likes(self, likes):
        if likes < 0:
            raise serializers.ValidationError('likes must be positive or null')



class PublicUserSerializer(serializers.ModelSerializer):
    """Serializer for R operation"""
    followers = MiniUserSerializer(many = True)
    following = MiniUserSerializer(many = True)
    posts = PostSerializer(many = True)
    tagged_posts = PostSerializer(many = True)
    class Meta:
        model = get_user_model()
        fields = ['pk', 'fullname', 'username',
                  'profile_pic', 'followers_count',
                  'following', 'following_count',
                  'posts', 'post_count',
                  'tagged_posts'
                  ]
class PrivateUserSerializer(serializers.ModelSerializer):
    ''' Serializer for R operaton '''
    class Meta:
        model = get_user_model()
        fields = ['pk', 'full_name', 'username',
                  'profile_pic', 'website', 'bio',
                  'followers_count', 'following_count', 'post_count']


class MyProfileSerializer(serializers.ModelSerializer):
    ''' Serializer for RUD operatons '''
    followers = MiniUserSerializer(many=True)
    following = MiniUserSerializer(many=True)
    posts = PostSerializer(many=True)
    tagged_posts = PostSerializer(many=True)
    saved_posts = PostSerializer(many=True)
    class Meta:
        model = get_user_model()
        fields = ['pk', 'full_name', 'email', 'username', 'ph_number',
                  'birthday', 'profile_pic', 'website', 'bio',
                  'followers', 'followers_count',
                  'following', 'following_count',
                  'posts', 'post_count',
                  'tagged_posts', 'saved_posts', 'website', 'media_count',

                  ]
    def validate_followers(self, value):
            if value < 0:
                raise serializers.ValidationError('followers must be positive or null')



    def validate_following(self, value):
        if value < 0:
            return serializers.ValidationError('following must be positive or null')




class UploadUserPicSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['profile_pic']

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

