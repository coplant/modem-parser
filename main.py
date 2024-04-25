# -*- coding: utf-8 -*-
from datetime import datetime

import requests
from bs4 import BeautifulSoup

import utils


class CommonParser:
    def __init__(self, url):
        self.modem_url = url
        self.modem_session = None
        self.modem_headers = {
            "accept": "*/*",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        self.html_template = """<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Document</title>
</head>
<body>
</body>
</html>"""
        self.content_time = None
        self.to_save = {}

    def make_session(self, headers=None, cookies=None):
        self.modem_session = requests.Session()
        if headers is None:
            headers = self.modem_headers

        self.modem_session.headers.update(headers)
        if cookies:
            self.modem_session.cookies.update(cookies)
        return self.modem_session

    def get_content(self, url=""):
        self.content_time = datetime.now()
        if not self.modem_session:
            self.make_session()

        response = self.modem_session.get(self.modem_url + url)
        if response.status_code == 200:
            return {"url": url, "content": response.content.decode("utf-8")}
        else:
            print("Failed to fetch page content:", response.status_code)
            return None

    def parse(self, content):
        if not content:
            return None

        soup = BeautifulSoup(content, "lxml")
        return soup

    def save(self, file_path, title=""):
        soup = BeautifulSoup(self.html_template, "lxml")
        if title:
            soup.title.string = title

        time_string = f"{(self.content_time or datetime.now()).strftime("%Y.%m.%d %H:%M:%S")}"
        soup.body.append(time_string)
        soup.body.append(BeautifulSoup("<hr />", "lxml"))

        for url, content in self.to_save.items():
            soup.body.append(url)
            for k, v in content.items():
                soup.body.append(f"{k}: {v}")
                soup.body.append(BeautifulSoup("<br />", "lxml"))
            soup.body.append(BeautifulSoup("<hr />", "lxml"))

        with open(f"{file_path}.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify(encoding="utf-8").decode("utf-8"))


class EastarParser(CommonParser):
    def parse(self, content):
        if not content:
            return None

        url = content.get("url", "")
        soup = BeautifulSoup(content.get("content", ""), "lxml")

        self.to_save.setdefault(url, {})
        store = self.to_save.get(url, {})

        if url == "sandbox/catalog/":
            store["body"] = utils.remove_whitespace(soup.text)
        elif url == "sandbox/news/":
            store["body"] = utils.remove_whitespace(soup.title.text)
        elif url == "...":
            ...

        return soup


def main():
    modem_parser = EastarParser("https://parsemachine.com/")
    combined_data = {}

    content = modem_parser.get_content("sandbox/catalog/")
    soup_content = modem_parser.parse(content)
    combined_data.update(modem_parser.to_save)

    content = modem_parser.get_content("sandbox/news/")
    soup_content = modem_parser.parse(content)
    combined_data.update(modem_parser.to_save)

    modem_parser.save("report", "Modem")


if __name__ == "__main__":
    main()
