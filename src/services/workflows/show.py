# -*- coding: utf-8 -*-
# Time       : 2021/10/3 17:18
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:

import csv

from utils.toolbox import to_markdown


def format_conversion(input_csv_path: str, output_csv_path: str = None):
    """
    - Format
        theme            author                     License      GitHub Stars  updated
        [theme](ref)      [author](repo/"alias")     text         number        time
    - Title
        theme,description,profile_link,author,github_stars,updated,
        license,theme_tags,theme-repo,theme-ref

    :param input_csv_path: awesome-hugo-themes.csv
    :param output_csv_path: ./new-table.csv
    :return:
    """
    # 数据重新写回不影响
    output_csv_path = output_csv_path if output_csv_path else input_csv_path

    with open(input_csv_path, 'r', encoding="utf8") as f:
        reader = list(csv.reader(f))

    with open(output_csv_path, "w", encoding="utf8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(['Theme', 'Author', 'License', 'GitHub Stars', 'Updated'])
        for i in reader[1:]:
            new_theme = to_markdown(i[0].replace("|", "\\|"), i[-1])
            new_author = to_markdown(i[3].replace("|", "\\|"), i[-2] if i[-2] != 'nil' else "#")
            new_license = i[-4]
            new_github_stars = i[4]
            new_updated = i[5]
            writer.writerow([new_theme, new_author, new_license, new_github_stars, new_updated])
