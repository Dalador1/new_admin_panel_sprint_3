import datetime

def attention(sender, instance, created, **kwargs):
    if created and instance.creation_date == datetime.date.today():
        print(f"Сегодня премьера {instance.title}! 🥳")
        
        
from django.db.models.signals import post_save

post_save.connect(receiver=attention, sender='movies.Filmwork', 
                  weak=True, dispatch_uid='attention_signal')