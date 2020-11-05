# -*- coding: utf-8 -*-

from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/' ,include(('discoauth.urls', 'discoauth'), 'discoauth'), name="discoauth"),
    path('api/v1/', include(('api.urls', 'api'), 'api'), name='api'),
    path('content-manager/', include(('contentmanager.urls', 'contentmanager'), 'contentmanager'), name='content-manager'),
    path('', include(('portal.urls', 'portal'), 'portal'), name='portal'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns


# Admin site related heading and title
admin.site.site_header = 'Discog Administration'
admin.site.site_title = 'Discog Portal Administration'
admin.site.index_title = 'Welcome to Discog Portal Administration'
