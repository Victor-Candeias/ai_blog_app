from tkinter import Entry
from django.test import TestCase
from django.template.defaultfilters import slugify
import datetime

# Create your tests here.
def test_url(self):
    title = "This is my test title"
    today = datetime.date.today()
    entry = Entry.objects.create(title=title, body="body",
                                 author=self.user)
    slug = slugify(title)
    url = "/{year}/{month}/{day}/{pk}-{slug}/".format(
        year=today.year,
        month=today.month,
        day=today.day,
        slug=slug,
        pk=entry.pk,
    )
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response,
                            template_name='blog/entry_detail.html')