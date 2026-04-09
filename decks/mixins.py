class OwnerQuerysetMixin:
    """
    Mixin for filtering querysets by the current request user as 'owner'.
    Use by placing this mixin before your Django generic view class.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user)
