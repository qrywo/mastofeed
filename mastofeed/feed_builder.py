from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

class FeedBuilder:

    def __init__(self, mastodon_client):
        self.mastodon_client = mastodon_client

    def build_feed(self, feed_url):
        feed_generator = FeedGenerator()

        feed_generator.title("\uf3e0 " + self.mastodon_client.get_user().acct)
        feed_generator.subtitle(f"\uf464: {self.mastodon_client.get_user().display_name} " +
                                f"({self.mastodon_client.get_user().username})\n" +
                                f"\uf310: {self.mastodon_client.get_instance_domain()}")
        feed_generator.id(feed_url)
        feed_generator.link(href=feed_url, rel="self", type="application/atom+xml")
        feed_generator.link(href=self.mastodon_client.get_home_timeline_url(), rel="alternate", type="text/html")
        feed_generator.logo(self.mastodon_client.get_instance_logo())
        feed_generator.updated(datetime.now(timezone.utc))
        feed_generator.icon(self.mastodon_client.get_instance_icon())
        feed_generator.generator(generator="python-feedgen",
                                 version="1.0.0",
                                 uri="https://lkiesow.github.io/python-feedgen")
        feed_generator.language(self.mastodon_client.get_instance_language())

        for status in self.mastodon_client.get_home_timeline():
            feed_entry = feed_generator.add_entry()

            if status.reblog is not None:
                original_status = status.reblog
                feed_entry.title(f"\uf501 [{status.account.display_name}] \u2192 " +
                                 f"\uf4ac [{status.reblog.account.display_name}]")
            else:
                original_status = status
                feed_entry.title(f"\uf4ac [{status.account.display_name}]")

            feed_entry.id(original_status.url)
            feed_entry.link(href=original_status.url, rel="alternate")
            feed_entry.author(name=original_status.account.display_name,
                              uri=original_status.account.url)
            feed_entry.updated(original_status.created_at)

            content_string = str(original_status.content)
            for emoji in original_status.emojis:
                content_string = content_string.replace(f":{emoji.shortcode}:",
                                                        ('<img rel="emoji" '
                                                         'draggable="false" '
                                                         'width="16" '
                                                         'height="16" '
                                                         'class="emojione" '
                                                         'style="height: 1.1em; margin: -.2ex .15em .2ex; object-fit: contain; vertical-align: middle; width: 1.1em;" '
                                                         f'alt=":{emoji.shortcode}:" '
                                                         f'title=":{emoji.shortcode}:" '
                                                         f'src="{emoji.static_url}"/>'))
            feed_entry.content(content=content_string, type="html")
            feed_entry.summary(summary=content_string, type="html")

        return feed_generator.atom_str(pretty=True)
