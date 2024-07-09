import django_filters


class NoteFilter(django_filters.FilterSet):
    start = django_filters.DateTimeFilter(field_name="updated", lookup_expr="gte")
    end = django_filters.DateTimeFilter(field_name="updated", lookup_expr="lte")
