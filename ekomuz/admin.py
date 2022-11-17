from django.contrib import admin

class MyAdminSite(admin.AdminSite):
    site_header = 'Платформа EKOMUZ'
    site_title = 'EKOMUZ'

    def get_app_list(self, request):

        ordering = {
            "пользователи и права": 1,
        }
        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: ordering[x['name'].lower()])

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        return app_list

admin_site = MyAdminSite()