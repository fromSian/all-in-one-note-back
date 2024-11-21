# be markdown notes backend

deployment: [https://fromsian.pythonanywhere.com/](https://fromsian.pythonanywhere.com/)

front-end deployment: [https://be-markdown-notes.vercel.app/](https://be-markdown-notes.vercel.app/)

This is the back-end. Using django-rest-framework.

the front-end repo is [https://github.com/fromSian/be-markdown-notes](https://github.com/fromSian/be-markdown-notes)

## Django + Django REST framework + google-auth-oauthlib + drf-yasg + django-filter + django-redis + DRF API Logger + markdownify

## Functions

### i18n

support English Simplified Chinese Traditional Chinese
reference: [https://www.django-rest-framework.org/topics/internationalization/](https://www.django-rest-framework.org/topics/internationalization/)

### handle timezone issues & datetime formatting

For different time zones, the date time will be displayed as the local date time in the exported markdown.

### data encryption

The password that passes between the front end and the back end is encrypted using RSA. The note content stored in the database is encrypted using AES.

And I write EncryptionSerializerMixin to make the encrypt and decrypt operations in every models and views easier.

[EncryptSerializerMixin](./utils/serializers.py)

```python
class EncryptSerializerMixin:
    __ALL__ = "__all__"
    encryption: None

    def to_representation(self, instance):
        ...
        for key, value in representation.items():
            if key in field_list and value:
                if isinstance(representation[key], str):
                    representation[key] = self.encryption.decrypt(value)
                else:
                    raise ImproperlyConfigured(
                        "Field name `%s` is not able to be encrypted for model `%s`."
                        % (key, model_class.__name__)
                    )
        return representation

    def to_internal_value(self, data):
        ...
        for key, value in _data.items():
            if key in field_list and value:
                if isinstance(value, str) and value != "":
                    _data.__setitem__(key, self.encryption.encrypt(value))
                else:
                    raise ImproperlyConfigured(
                        "Field name `%s` is not able to be decrypt for model `%s`."
                        % (key, model_class.__name__)
                    )
        return super().to_internal_value(_data)

```

### request revalidate action_time

Use encrypted action_time to check if the request is valid and reasonable

[RequestValidPermission](./utils/permission.py)

```py
class RequestValidPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        action_time = request.query_params.get("action_time")
        if not action_time:
            return False
        encrypt = RSAEncryption()
        action = encrypt.decrypt(action_time)

        return check_valid(action)
```

### accounts

Use rest_framework_simplejwt to genrate token and store token in redis

#### basic sign up and sign in

- sign up
- send verification code to email
- validate verification code
- sign in
- sign out

#### sign in with google

my post: [https://dev.to/fromsian/integrate-google-oauth2-authentication-into-the-django-rest-framework-39hj
](https://dev.to/fromsian/integrate-google-oauth2-authentication-into-the-django-rest-framework-39hj)

- google authentication access
- google authentication callback
- convert google account to official account

#### no sign-up trial

- trial account for no sign-up trial
- convert trial account to official account

#### account infos

- fetch account infos
- change password
- change avatar

#### destroy account

Users can destroy their account if they want to, because there are so many accounts I've just registered to see if the application is what I want, but it's hard to destroy.

### notes

#### custom list query pagniation

From the front-end needs for scrolling to fetch the rest datas, but at the same time, delete one or add one action is available, so the total number is uncertain, if using the basic 'page' & 'size' as query_params to query data list, may miss or repeat one.

So I use 'since_id' & 'size' & optional ordering params as query_params, since_id means where the results start from, if since_id is None, results will start from the beginning.

```py
class SinceIdPageListMixin:
    def list(self, request, *args, **kwargs):
        since_id = request.query_params.get("since_id", "")
        size = int(request.query_params.get("size", "")) | 10
        queryset = self.filter_queryset(self.get_queryset())
        start = 0
        if since_id:
            since_object = queryset.filter(id=since_id).first()
            if since_object:
                start = list(queryset).index(since_object) + 1
        count = len(queryset)
        page_queryset = queryset[start : start + size]
        hasNext = start + size < count

        serializer = self.get_serializer(page_queryset, many=True)
        return Response(
            {"results": serializer.data, "count": count, "hasNext": hasNext}
        )

```

#### create/query/update/delete notes & note_items

Use django-filter to filter data on a conditional basis.

#### export markdown

Use markdownify to convert html to markdown

### settings

Users can save their own preferences for 'language', 'theme', 'datetime display', 'expand or collapse' and 'default order', which determine how the front-end application is displayed.

### redis to cache token

- in development environment, using local redis
- in production environment, using redis-cloud: [https://redis.io/why-redis-cloud/](https://redis.io/why-redis-cloud/)

### shedular

- in development environment, using django_apscheduler
- in production environment, using pythonanywhere's task ability

### swagger page

Use drf-yasg to generate swagger page.

## deploy

deploy on [https://www.pythonanywhere.com/](https://www.pythonanywhere.com/) platform
database on [https://supabase.com/](https://supabase.com/)
