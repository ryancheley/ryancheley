import datetime
import pathlib
from platform import platform
import re
import ssl
import typing

import feedparser
import httpx
import jinja2
import requests
from rich.console import Console
from rich.tree import Tree

ROOT_DIR = pathlib.Path(__file__).parent.resolve()
README_FILE = ROOT_DIR / "README.md"
TEMPLATE_FILE = ROOT_DIR / "TEMPLATE.md"
LEDE_FILE = ROOT_DIR / "LEDE.md"
TIL_INDEX = "https://raw.githubusercontent.com/ryancheley/til/main/README.md"
ARTICLE_FEED = "https://ryancheley.com/feeds/all.rss.xml"
MASTODON_USER = "ryancheley"


if hasattr(ssl, "_create_unverified_context") and "macos" in platform().lower():
    ssl._create_default_https_context = ssl._create_unverified_context


class ContentPiece(typing.NamedTuple):
    url: str
    title: str
    date: str


ContentPieces = list[ContentPiece]

# TODO: Implement function to read for TILs


def get_text_inside(text: str, opening_char: str, ending_char: str) -> str:
    initial_position = text.find(opening_char) + 1
    ending_position = text.find(ending_char)
    return text[initial_position:ending_position]


def get_tils(num_items: int = 5):
    readme_list = httpx.get(TIL_INDEX).text.split('\n')
    start_position = [(ind, x) for ind, x in enumerate(readme_list) if x =='<!-- index starts -->'][0][0]
    tils = [x.replace('* ', '') for x in readme_list[start_position+1: ] if x != '' and not x.startswith('##')][:-1]
    data = []
    for til in tils:
        title = get_text_inside(til, "[", "]")
        url = get_text_inside(til, "(", ")")
        post_date = til[-10:]
        data.append(ContentPiece(url=url, title=title, date=post_date))

    data = sorted(data, key=lambda a: a.date, reverse=True)

    return data[:num_items]



def get_repositories():
    repository_list = []
    url = "https://api.github.com/users/ryancheley/repos?per_page=100"
    r = requests.get(url).json()
    for repo in r:
        if repo["topics"]:
            repository_list.add(repo["name"])
    return repository_list


console = Console(record=True, width=100)

tree = Tree(
    "🙂 [link=https://www.ryancheley.com]R. Ryan Cheley", guide_style="bold bright_black"
)

python_tree = tree.add("📦 Open Source Packages", guide_style="bright_black")

url = "https://api.github.com/users/ryancheley/repos?per_page=100"
r = requests.get(url).json()
for repo in r:
    if "oss" in repo["topics"]:
        tree_element = f"[bold link=https://pypi.org/project/{repo['name']}/]{repo['name']}[/] - [bright_black]{repo['description']}"
        python_tree.add(tree_element)

oss_maintainer = tree.add("🧰 OSS Maintainer", guide_style="bright_black")
oss_maintainer.add("[bold link=https://djangopackages.org]Django Packages[/]")

online_tree = tree.add("⭐ Online Projects", guide_style="bright_black")
for repo in r:
    if "online-project" in repo["topics"]:
        tree_element = f"[bold link={repo['homepage']}]{repo['name']}[/] - [bright_black]{repo['description']}"
        online_tree.add(tree_element)

talk_tree = tree.add("🎙️ Podcasts", guide_style="bright_black")
talk_tree.add(
    "[bold link=https://testandcode.com/183]Test & Code 183 - Managing Software Teams[/]"
)

employer_tree = tree.add("👨‍💻 Employer", guide_style="bright_black")
employer_tree.add(
    "[bold link=https://www.mydohc.com]Desert Oasis Healthcare[/] - [bright_black]Your Health. Your Life. Our Passion."
)

certification_tree = tree.add("📜 Certifications", guide_style="bright_black")
certification_tree.add(
    "[bold link=]GCP Cloud Architect[/] - Feb 2023"
)

console.print(tree)
console.print("")
console.print(
    "🦣 [green]Follow me on mastodon [bold link=https://mastodon.social/@ryancheley]@ryancheley[/]"
)

CONSOLE_HTML_FORMAT = """\
<pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">{code}</pre>
"""

console.save_html("LEDE.md", inline_styles=True, code_format=CONSOLE_HTML_FORMAT)


def get_lede():
    return LEDE_FILE.read_text()


def get_latest_articles(num_items: int = 2) -> ContentPieces:
    """
    Get the last articles from ryancheley.com
    """
    entries = feedparser.parse(ARTICLE_FEED).entries
    data = []
    for entry in entries[:num_items]:  # should have newest first
        if entry.summary.count("<p>") > 1:
            # if multiple paragraphs extract the first one
            summary = re.sub(r"^(<p>.*?)</p>.*$", r"\1 ...</p>", entry.summary)
        else:
            summary = entry.summary

        date = datetime.datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")

        data.append(ContentPiece(url=entry.id, title=summary, date=date))

    return data


def _parse_mastodon_feed(username: str) -> list[feedparser.util.FeedParserDict]:
    url = f"https://mastodon.social/@{username}.rss"
    entries = feedparser.parse(url).entries
    return entries


def get_latest_toots(num_items: int = 3) -> ContentPieces:
    """
    Get latest toots from Mastodon.
    """
    entries = _parse_mastodon_feed(MASTODON_USER)

    data = []
    for entry in entries[:num_items]:  # should have newest first
        if entry.summary.count("<p>") > 1:
            # if multiple paragraphs extract the first one
            summary = re.sub(r"^(<p>.*?)</p>.*$", r"\1 ...</p>", entry.summary)
        else:
            summary = entry.summary

        date = datetime.datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")

        data.append(ContentPiece(url=entry.id, title=summary, date=date))

    return data


def generate_readme(content: dict[str, list[ContentPiece]]) -> None:
    """
    Generate Readme file from template file
    """
    template_content = TEMPLATE_FILE.read_text()
    jinja_template = jinja2.Template(template_content)
    updated_content = jinja_template.render(**content)
    README_FILE.write_text(updated_content)


if __name__ == "__main__":
    content = dict(
        articles=get_latest_articles(),
        toots=get_latest_toots(),
        lede=get_lede(),
        tils = get_tils(),
    )
    generate_readme(content)
