import requests
from bs4 import BeautifulSoup, Tag
import re
from abc import ABC, abstractproperty
from dateutil import parser


def find_article_content(tag: Tag):
    return tag.name in ("p") and not tag.has_attr("class")


def strip_links(tag: str | Tag):
    if isinstance(tag, Tag):
        return tag.contents[0]
    return tag


class RSSItem:
    def __init__(self, soup_item: BeautifulSoup) -> None:
        self.title = soup_item.title.contents[0]
        self.link = soup_item.link.contents[0]
        self.pubDate = parser.parse(soup_item.pubDate.contents[0])


class RSSChannelInfo:
    def __init__(self, soup_item: BeautifulSoup) -> None:
        self.title = soup_item.title.contents[0]
        self.description = soup_item.description.contents[0]
        self.lastBuildDate = parser.parse(soup_item.lastBuildDate.contents[0])
        self.items = [RSSItem(item) for item in soup_item.find_all("item")]


class Article(ABC):
    @abstractproperty
    def paragraphs(self) -> list[str]:
        pass


class BreakingDefenseArticle(Article):
    @property
    def paragraphs(self) -> list[str]:
        return self._paragraphs

    def __init__(self, soup_item: BeautifulSoup) -> None:
        self._paragraphs = []
        content = soup_item.find_all(id="mainContent")[0]
        [
            div.decompose()
            for div in content.find_all(
                "div", class_=re.compile("sponsored|related|postFooter")
            )
        ]

        for p in content.find_all(find_article_content):
            self._paragraphs.append(p.get_text())


class SpaceNewsArticle(Article):
    @property
    def paragraphs(self) -> list[str]:
        return self._paragraphs

    def __init__(self, soup_item: BeautifulSoup) -> None:
        self._paragraphs = []
        content = soup_item.find_all(
            "article", class_=re.compile(r"\spost\s")
        )[0].find_all("div", class_="entry-content")[0]

        for p in content.find_all(find_article_content):
            self._paragraphs.append(p.get_text())


ARTICLE_PARSERS = {
    "BreakingDefenseArticle": BreakingDefenseArticle,
    "SpaceNewsArticle": SpaceNewsArticle,
}


def get_feed(rss_url: str) -> list[RSSChannelInfo]:
    out = []
    resp = requests.get(rss_url)
    for channel in BeautifulSoup(resp.content, "xml").find_all("channel"):
        out.append(RSSChannelInfo(channel))
    return out


def get_article(article_url: str, article_class_name="BreakingDefenseArticle"):
    resp = requests.get(article_url)
    soup = BeautifulSoup(resp.content, "html5lib")
    article_class = ARTICLE_PARSERS.get(article_class_name)
    if article_class is None:
        raise ValueError(
            f"Article Parser of with name {article_class_name} does not exist"
        )
    return article_class(soup)


if __name__ == "__main__":
    rss_feed = "https://breakingdefense.com/full-rss-feed/?v=2"
    channels = get_feed(rss_feed)
    for channel in channels:
        for item in channel.items:
            # should check to see if we know about this
            # article before grabbing it
            art = get_article(item.link, BreakingDefenseArticle)
            print(art.paragraphs)
            break
