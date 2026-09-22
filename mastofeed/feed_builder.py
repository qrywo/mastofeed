from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

class FeedBuilder:

    def __init__(self, mastodon_client):
        self.mastodon_client = mastodon_client

    def build_feed(self, feed_url):
        feed_generator = FeedGenerator()
        feed_generator.icon(self.mastodon_client.get_instance_icon())
        feed_generator.id(feed_url)
        feed_generator.language("en")
        feed_generator.link(href=feed_url, rel="self")
        feed_generator.title("Your Mastodon Home Timeline")
        feed_generator.author(name=self.mastodon_client.get_instance_name(),
                              uri=self.mastodon_client.get_instance_url())

        for status in self.mastodon_client.get_home_timeline():
            feed_entry = feed_generator.add_entry()

            if status.reblog is not None:
                original_status = status.reblog
                feed_entry.title(f"Boost by [{status.account.display_name}] of a Toot by [{status.reblog.account.display_name}]")
            else:
                original_status = status
                feed_entry.title(f"Toot by [{status.account.display_name}]")

            feed_entry.id(original_status.url)
            feed_entry.link(href=original_status.url, rel="self")
            feed_entry.author(name=original_status.account.display_name,
                              uri=original_status.account.url)
            feed_entry.updated(original_status.created_at)

            content_string = str(original_status.content)
            for emoji in original_status.emojis:
                content_string = content_string.replace(f":{emoji.shortcode}:", f'<img src="{emoji.static_url}"/>')
            feed_entry.content(content=content_string, type="html")
            feed_entry.summary(summary=content_string, type="html")

        feed_generator.updated(datetime.now(timezone.utc))
        return feed_generator.atom_str(pretty=True)
