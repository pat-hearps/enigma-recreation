from factory import Factory
from faker import Faker, providers

from tests.models import Window3

fake = Faker()
fake.add_provider(providers.BaseProvider)


class WindowFactory(Factory):
    class Meta:
        model = Window3

    letter0 = fake.random_uppercase_letter()
    letter1 = fake.random_uppercase_letter()
    letter2 = fake.random_uppercase_letter()
