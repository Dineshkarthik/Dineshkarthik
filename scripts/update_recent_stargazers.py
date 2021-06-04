"""Update the README.md with recent stargazers."""
import json
import os
from typing import List

import requests
from jinja2 import Environment, FileSystemLoader


url: str = "https://api.github.com/graphql"
query: str = """
{
  user(login: "Dineshkarthik") {
    repositories(first: 200, isFork: false, isLocked: false, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazers(orderBy: {field: STARRED_AT, direction: DESC}, first: 10) {
          edges {
            node {
              id
              avatarUrl
              bio
              name
              login
            }
            starredAt
          }
        }
        name
        url
      }
    }
  }
}
"""


def get_overall_stargazers_list(result: List[dict]) -> List[dict]:
    stargazers_overall_list: list = []
    for r in result["data"]["user"]["repositories"]["nodes"]:
        if r["stargazers"]["edges"]:
            list_ = []
            for edge in r["stargazers"]["edges"]:
                dict_ = {}
                dict_["project_name"] = r["name"]
                dict_["project_url"] = r["url"]
                dict_["name"] = edge["node"]["name"] or edge["node"]["login"]
                dict_["login"] = edge["node"]["login"]
                dict_["avatar"] = edge["node"]["avatarUrl"]
                dict_["bio"] = (
                    edge["node"]["bio"] or "Nothing to 👀 here , no bio...!!"
                ).rstrip()
                dict_["starredAt"] = edge["starredAt"]
                list_.append(dict_)
            stargazers_overall_list.extend(list_)
    return sorted(
        stargazers_overall_list, key=lambda k: k["starredAt"], reverse=True
    )


def get_normalized_stargazers_list(overall_list: List[dict]) -> List[dict]:
    normalized_stargazers_list: List[dict] = []
    stargazer_names: List[str] = []
    for row in overall_list:
        if not row["login"] in stargazer_names:
            stargazer_names.append(row["login"])
            normalized_stargazers_list.append(row)
    return normalized_stargazers_list


def get_api_response() -> List[dict]:
    headers: dict = {
        "Authorization": f"Bearer {os.environ.get('ACCESS_TOKEN')}",
        "Content-Type": "application/json",
    }

    response = requests.request(
        "POST", url, headers=headers, json={"query": query}
    )
    return response.json()


def update_stargazers():
    overall_stargazers_list: List[dict] = get_overall_stargazers_list(
        get_api_response()
    )
    normalized_stargazers_list: List[dict] = get_normalized_stargazers_list(
        overall_stargazers_list
    )

    file_loader = FileSystemLoader("templates")
    env = Environment(loader=file_loader)

    template = env.get_template("readme-template.md")

    rendered_readme = template.render(
        stargazers=normalized_stargazers_list[0:10]
    )
    with open("README.md", "w+") as f:
        f.write(rendered_readme)


if __name__ == "__main__":
    update_stargazers()
