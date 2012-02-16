from Products.Five.browser import BrowserView

class FullFeedView(BrowserView):

    @property
    def title(self):
        return self.context.title

    @property
    def entries(self):
        return self.aq_acquire('context').entries

    @property
    def merge_feeds(self):
        return self.aq_acquire('context').data.merge_feeds
