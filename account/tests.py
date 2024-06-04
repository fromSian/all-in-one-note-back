from django.test import TestCase

# Create your tests here.

from django.core.cache import cache

cache.set('test', "I don't know how to")
print(cache.get('test'))
