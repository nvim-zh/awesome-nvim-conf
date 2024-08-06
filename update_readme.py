from py_markdown_table.markdown_table import markdown_table
import requests
from urllib.parse import urlparse
import yaml


def get_github_stars(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        response = requests.get(url, timeout=5)
    except Exception:
        print("unable to get the repo status")
        return None

    # print(response.json())

    if response.status_code == 200:
        data = response.json()
        return data["stargazers_count"]
    else:
        return None


def get_github_owner_repo(url):
    parsed_url = urlparse(url)

    # Check if it's a valid GitHub URL
    if parsed_url.netloc != "github.com":
        raise ValueError("Not a valid GitHub URL")

    # Split the path and remove empty strings
    path_parts = list(filter(None, parsed_url.path.split("/")))

    # Check if we have at least owner and repo
    if len(path_parts) < 2:
        raise ValueError("URL does not contain both owner and repository")

    owner = path_parts[0]
    repo = path_parts[1]

    return owner, repo


def get_repo_info():
    with open("./data/conf_repo_info.yaml") as f:
        repo_info = yaml.load(f, Loader=yaml.SafeLoader)

    # add additional info to the repo

    for info in repo_info:
        repo_link = info["repo"]

        try:
            owner, repo = get_github_owner_repo(repo_link)
        except ValueError:
            print("Abnormal repo link")
            info["stars"] = "Not available"
            continue

        stars = get_github_stars(owner, repo)
        if stars is not None:
            info["stars"] = stars
        else:
            info["stars"] = "Not available"

    return repo_info


def overwrite_readme(new_content):
    with open("README.md", "r") as file:
        content = file.read()

    # Define the start and end markers for the section to replace
    start_marker = "<!--MARKDOWN_TABLE_START-->"
    end_marker = "<!--MARKDOWN_TABLE_END-->"

    # Find the section to replace
    start = content.index(start_marker)
    end = content.index(end_marker) + len(end_marker)

    # Replace the section
    updated_content = (
        content[:start]
        + start_marker
        + "\n"
        + new_content
        + "\n"
        + end_marker
        + content[end:]
    )

    # Write the updated content back to README.md
    with open("README.md", "w") as file:
        file.write(updated_content)


def update_readme():
    repo_info = get_repo_info()
    table_str = (
        markdown_table(repo_info)
        .set_params(row_sep="markdown", quote=False)
        .get_markdown()
    )
    overwrite_readme(table_str)
    # print(table_str)


if __name__ == "__main__":
    update_readme()
