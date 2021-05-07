from django.dispatch import Signal, receiver
from .models import end_fetching_data


@receiver(signal=end_fetching_data, sender="")
def process_fetched_data(sender, instance, )
