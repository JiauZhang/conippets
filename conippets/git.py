import httpx
import conippets.json as json
import conippets.lxml as lxml

_repo_data_xpath_ = '//react-partial[@partial-name="repos-overview"]/script[@data-target="react-partial.embeddedData"]'

def createAt(user, repo):
    url = f'https://github.com/{user}/{repo}'
    r = httpx.get(url)
    html = lxml.parse_html(r.text)
    repo_data = html.xpath(_repo_data_xpath_)[0]
    repo_data = json.loads(repo_data.text)
    create_time = repo_data['props']['initialPayload']['repo']['createdAt']
    return create_time

def currentOid(user, repo):
    url = f'https://github.com/{user}/{repo}'
    r = httpx.get(url)
    html = lxml.parse_html(r.text)
    repo_data = html.xpath(_repo_data_xpath_)[0]
    repo_data = json.loads(repo_data.text)
    commit_id = repo_data['props']['initialPayload']['refInfo']['currentOid']
    return commit_id
