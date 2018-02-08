import webbrowser

class snopes_article(object):
    def __init__(self, pub_date=None, mod_date=None, url=None, claim=None, is_valid=None, tags=None, title=None, post_num=None, **kwargs):
        self.pub_date = pub_date
        self.mod_date = mod_date
        self.url = url
        self.claim = claim
        self.is_valid = is_valid
        self.tags = tags
        self.title = title
        self.post_num = post_num

    @property
    def goto(self):
        try:
            webbrowser.open(self.url)
        except:
            logger.info(" No can do. Something is wrong with this url: {}".format(self.url))
