# django aliases
##### Brandon R. Stoner <monokrome@monokro.me>

# What is this?

This is a small project that I made because I wanted a flexible method
for aliasing extra URLs to different objects. It's provides a more
flexible method for making a URL direct django to display the page for
any Model that has a get_absolute_url method.

As an example, if you were to create a "Page" model that simply described
a page on a website - you could link it to the URL model in django-aliases
and you would end up with a version of django's flatpages module that
had added support for linking multiple URLs to a single item.

