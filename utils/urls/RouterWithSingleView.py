from rest_framework.routers import DefaultRouter
from collections import OrderedDict

class RouterWithSingleView(DefaultRouter):
    '''
    Customized Default Router to include non-viewset views on root page
    '''
    single_views:list
    def __init__(self, single_views:list, *args, **kwargs):
        self.single_views = single_views
        super().__init__(*args, **kwargs)

    def get_api_root_view(self, api_urls=None):
        """
        Return a basic root view.
        """
        api_root_dict = OrderedDict()
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)
        for single_view in self.single_views:
            api_root_dict[single_view['route']] = single_view['name']
        return self.APIRootView.as_view(api_root_dict=api_root_dict)