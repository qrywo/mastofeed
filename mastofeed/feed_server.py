from flask import Flask, redirect, url_for, request, Response, abort
from mastofeed.mastodon_client import MastodonClient
from mastofeed.feed_builder import FeedBuilder

app = Flask("mastofeed")
mastodon_client = MastodonClient()
feed_builder = FeedBuilder(url_for("feed", _external=True), mastodon_client)


@app.route("/")
def default():
    if not mastodon_client.is_access_provided():
        return redirect(mastodon_client.get_access_redirect_url(url_for("oauth_callback", _external=True)))
    return redirect(url_for("feed"))


@app.route("/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    if not mastodon_client.grant_access(code, url_for("oauth_callback", _external=True)):
        abort(401)
    return redirect(url_for("feed"))

@app.route("/feed")
def feed():
    if not mastodon_client.is_access_provided():
        abort(401)
    return Response(feed_builder.build_feed(),
                    mimetype="application/xml")


if __name__ == "__main__":
    app.run()