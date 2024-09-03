# # signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Tests
#
# @receiver(post_save, sender=Tests)
# def reassign_question_ids(sender, instance, created, **kwargs):
#     if created:
#         questions = instance.questions.order_by('id')
#         for index, question in enumerate(questions, start=1):
#             question.id = index
#             question.save()
#         for question in questions:
#             variants = question.variantsquestions_set.order_by('id')
#             for index, variant in enumerate(variants, start=1):
#                 variant.id = index
#                 variant.save()