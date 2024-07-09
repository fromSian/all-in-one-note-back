import django_filters


class NoteFilter(django_filters.FilterSet):
    start = django_filters.DateTimeFilter(field_name="updated", lookup_expr="gte")
    end = django_filters.DateTimeFilter(field_name="updated", lookup_expr="lte")


class NoteItemFilter(django_filters.FilterSet):
    note = django_filters.NumberFilter(
        field_name="note", lookup_expr="exact", required=True
    )
    order = django_filters.OrderingFilter(fields=["created", "updated"])
