from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

class FeedBuilder:

    def __init__(self, mastodon_client):
        self.mastodon_client = mastodon_client

    def build_feed(self, feed_url):
        feed_generator = FeedGenerator()

        feed_generator.title("\U0001F3E0 " + self.mastodon_client.get_user().username +
                             "@" + self.mastodon_client.get_instance_domain())
        feed_generator.subtitle(f"\U0001F464: {self.mastodon_client.get_user().display_name} " +
                                f"({self.mastodon_client.get_user().username});\t" +
                                f"\U0001F310: {self.mastodon_client.get_instance_domain()}")
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

            feed_entry.published(status.created_at)
            feed_entry.updated(status.editet_at)

            if status.reblog is not None:
                original_status = status.reblog
                feed_entry.title(f"\U0001F501 [{status.account.display_name}] \U00002192 " +
                                 f"\U0001F4AC [{status.reblog.account.display_name}]")
            else:
                original_status = status
                feed_entry.title(f"\U0001F4AC [{status.account.display_name}]")

            feed_entry.id(original_status.url)
            feed_entry.link(href=original_status.url, rel="alternate")
            feed_entry.author(name=original_status.account.display_name,
                              uri=original_status.account.url)

            content = str(original_status.content)
            soup = BeautifulSoup(content, "html.parser")
            summary = soup.get_text()

            for emoji in original_status.emojis:
                emoji_text = f":{emoji.shortcode}:"
                emoji_repr = ('<img rel="emoji" '
                              'draggable="false" '
                              'width="16" '
                              'height="16" '
                              'class="emojione" '
                              'style="height: 1.1em; margin: -.2ex .15em .2ex; object-fit: contain; vertical-align: middle; width: 1.1em;" '
                              f'alt=":{emoji.shortcode}:" '
                              f'title=":{emoji.shortcode}:" '
                              f'src="{emoji.static_url}"/>')
                content = content.replace(emoji_text, emoji_repr)

            feed_entry.summary(summary=summary, type="text")
            feed_entry.content(content=content, type="html")

            for tag in original_status.tags():
                feed_entry.category(term=tag.name, label="#" + tag.name)

        return feed_generator.atom_str(pretty=True)
