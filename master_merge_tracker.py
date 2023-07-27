from github import Github
from github import Auth
from datetime import datetime, timedelta
from slack_sdk import WebClient

import re
import argparse


def github_and_slack_connection(github_token, slack_token, time_range):
    auth = Auth.Token(github_token)
    g = Github(auth=auth)  # авторизации для GitHub
    repo = g.get_repo("ZakonGyka/master_merge_tracker") # указать отслеживаемый репозиторий
    client = WebClient(token=slack_token)  # авторизации для Slack
    if time_range == 'None':
        update_time = datetime.now() - timedelta(minutes=5)
        print(f'{time_range} - запуск по коммиту')  # для отслеживания запуска в консоли
    else:
        update_time = datetime.now() - timedelta(days=int(time_range))
        print(f'Поиск комитов за {time_range} дней')  # для отслеживания запуска в консоли
    commits = repo.get_commits(since=update_time)
    check_merge(commits, client)


def check_merge(commits, client):
    regex_merge = re.compile(fr'{options.regex_merge}')
    regex_pull_request = re.compile(fr'{options.regex_pull_request}')
    first_part_of_fraze_merge = 'Произведен мерж ветки'
    first_part_of_fraze_pull_request = 'Сделан pull request'
    commit_massive = []
    for data in commits:
        commit = data.commit.message
        if re.search(regex_merge, commit):
            parsed_commit = re.search(regex_merge, commit)
            send_message(client, parsed_commit, first_part_of_fraze_merge)
            commit_massive.append(parsed_commit)
        elif re.search(regex_pull_request, commit):
            parsed_commit = re.search(regex_pull_request, commit)
            send_message(client, parsed_commit, first_part_of_fraze_pull_request)
            commit_massive.append(parsed_commit)
    print(commit_massive)  # для отслеживания коммитов в консоли


def send_message(client, parsed_commit, first_part_of_fraze):
    try:
        branch_name = parsed_commit.group("branch")
        full_fraze = f'{first_part_of_fraze}:\n {options.branch_prefix}/{branch_name}\n в master.'
        send_channel = '#' + options.channel
        client.chat_postMessage(channel=send_channel, text=full_fraze)
    except IndexError:
        print(f'{parsed_commit}\nФормат не подошел')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--GitHubToken",
        help="токен для доступа в GitHub",
        dest="github_token",
        required=True,
    )
    parser.add_argument(
        "--SlackToken",
        help="токен для доступа в Slack",
        dest="slack_token",
        required=True,
    )
    parser.add_argument(
        "--TimeRange",
        help="триггер на сбор коммитов за желаемое время",
        dest="time_range",
        required=True,
    )
    parser.add_argument(
        "--Channel",
        help="канал в Slack куда отправлять сообщения",
        dest="channel",
        required=True,
    )
    parser.add_argument(
        "--RegexMerge",
        help="regex для мержа ветки в мастер",
        dest="regex_merge",
        required=True,
    )
    parser.add_argument(
        "--RegexPullRequest",
        help="regex для pull request ветки в мастер",
        dest="regex_pull_request",
        required=True,
    )
    parser.add_argument(
        "--BranchPrefix",
        help="префикс - добавляется в начало названия ветки",
        dest="branch_prefix",
        required=True,
    )

    options = parser.parse_args()
    github_and_slack_connection(options.github_token, options.slack_token, options.time_range)
