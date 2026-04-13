class CreatedByQuerysetMixin:
    """
    Mixin for filtering querysets by the current request user as 'created_by'.
    Use by placing this mixin before your Django generic view class.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)
