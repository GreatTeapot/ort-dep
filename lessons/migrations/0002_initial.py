# Generated by Django 5.0.1 on 2024-08-11 11:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('lessons', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='resultanalysis',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='result_analyses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='resultanswer',
            name='question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='result_associations', to='lessons.questions'),
        ),
        migrations.AddField(
            model_name='results',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='results', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='resultanswer',
            name='result',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='result_answers', to='lessons.results'),
        ),
        migrations.AddField(
            model_name='resultanalysis',
            name='result',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='result_analyses', to='lessons.results'),
        ),
        migrations.AddField(
            model_name='resultanalysis',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='result_analysis', to='lessons.subjects'),
        ),
        migrations.AddField(
            model_name='subscriptions',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='testquestions',
            name='question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_associations', to='lessons.questions'),
        ),
        migrations.AddField(
            model_name='tests',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='lessons.subjects'),
        ),
        migrations.AddField(
            model_name='testquestions',
            name='test',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_questions', to='lessons.tests'),
        ),
        migrations.AddField(
            model_name='results',
            name='test',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='results', to='lessons.tests'),
        ),
        migrations.AddField(
            model_name='testtopic',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_topics', to='lessons.tests'),
        ),
        migrations.AddField(
            model_name='topics',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to='lessons.subjects'),
        ),
        migrations.AddField(
            model_name='testtopic',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topic_tests', to='lessons.topics'),
        ),
        migrations.AddField(
            model_name='questions',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='lessons.topics'),
        ),
        migrations.AlterUniqueTogether(
            name='testquestions',
            unique_together={('test', 'question')},
        ),
        migrations.AlterUniqueTogether(
            name='testtopic',
            unique_together={('test', 'topic')},
        ),
    ]
