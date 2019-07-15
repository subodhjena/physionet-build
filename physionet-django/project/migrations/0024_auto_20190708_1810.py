# Generated by Django 2.1.7 on 2019-07-08 22:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0023_auto_20190620_1845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activeproject',
            name='author_approval_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='activeproject',
            name='author_comments',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='activeproject',
            name='copyedit_completion_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='activeproject',
            name='editor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='editing_activeprojects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='activeproject',
            name='editor_accept_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='activeproject',
            name='editor_assignment_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='activeproject',
            name='resubmission_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='activeproject',
            name='revision_request_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='activeproject',
            name='submission_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='archivedproject',
            name='author_approval_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='archivedproject',
            name='author_comments',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='archivedproject',
            name='copyedit_completion_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='archivedproject',
            name='editor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='editing_archivedprojects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='archivedproject',
            name='editor_accept_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='archivedproject',
            name='editor_assignment_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='archivedproject',
            name='resubmission_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='archivedproject',
            name='revision_request_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='archivedproject',
            name='submission_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='publishedproject',
            name='author_approval_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='publishedproject',
            name='author_comments',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='publishedproject',
            name='copyedit_completion_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='publishedproject',
            name='editor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='editing_publishedprojects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='publishedproject',
            name='editor_accept_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='publishedproject',
            name='editor_assignment_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='publishedproject',
            name='resubmission_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='publishedproject',
            name='revision_request_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='publishedproject',
            name='submission_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]