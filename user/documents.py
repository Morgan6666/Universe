from .models import User
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from post.models import Post

@registry.register_document
class UserDocument(Document):
    class Index:
        name = 'user'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
]


