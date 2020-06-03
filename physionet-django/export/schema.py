import graphene
from graphene_django.types import DjangoObjectType

from project.models import PublishedProject, PublishedAuthor


class PublishedProjectType(DjangoObjectType):
    class Meta:
        model = PublishedProject
        fields = ('title', 'version', 'slug', 'abstract', 'main_storage_size',
                  'compressed_storage_size')


class PublishedAuthorType(DjangoObjectType):
    class Meta:
        model = PublishedAuthor
        fields = ('first_names', 'last_name', 'corresponding_email', 'project')


class Query(object):
    all_published_projects = graphene.List(PublishedProjectType)
    all_published_authors = graphene.List(PublishedAuthorType)

    def resolve_all_published_projects(self, info, **kwargs):
        return PublishedProject.objects.all()

    def resolve_all_published_authors(self, info, **kwargs):
        return PublishedAuthor.objects.all()