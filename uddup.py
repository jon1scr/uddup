#!/usr/bin/python
# coding=utf-8
import argparse
import sys
import os
from urllib.parse import urlparse

# Check if we are running this on windows platform
is_windows = sys.platform.startswith('win')

# Console Colors
if is_windows:
    # Windows deserves coloring too :D
    G = '\033[92m'  # green
    Y = '\033[93m'  # yellow
    W = '\033[0m'   # white
    try:
        import win_unicode_console, colorama
        win_unicode_console.enable()
        colorama.init()
    except:
        G = Y = W = ''
else:
    G = '\033[92m'  # green
    Y = '\033[93m'  # yellow
    W = '\033[0m'   # white


def banner():
    print("""%s
  _   _ ____      _             
 | | | |  _ \  __| |_   _ _ __  
 | | | | | | |/ _` | | | | '_ \ 
 | |_| | |_| | (_| | |_| | |_) |
  \___/|____/ \__,_|\__,_| .__/ 
                         |_|    

              %s# Coded By @2RS3C
    %s""" % (Y, G, W))


def file_arg(path):
    # from os.path import exists
    if not os.path.isfile(path):
        raise ValueError  # or TypeError, or `argparse.ArgumentTypeError
    return path


def get_ignored_suffixes():
    return (
        'css',
        'js',
        'gif',
        'jpg',
        'png',
        'jpeg',
        'svg',
        'xml',
        'txt',
        'json',
        'ico',
        'webp',
        'otf',
        'ttf',
        'woff',
        'woff2',
        'eot',
        'swf',
        'zip',
        'pdf',
        'doc',
        'ppt',
        'docx',
        'xls',
        'xlsx',
        'ogg',
        'mp4',
        'mp3',
        'mov'
    )


def get_web_suffixes():
    return (
        'htm',
        'html',
        'xhtml',
        'shtml',
        'jhtml',
        'cfm',
        'jsp',
        'jspx',
        'wss',
        'action',
        'php',
        'php4',
        'php5',
        'py',
        'rb',
        'pl',
        'do',
        'xml',
        'rss',
        'cgi',
        'axd',
        'asx',
        'asmx',
        'ashx',
        'asp',
        'aspx',
        'dll'
    )


def get_existing_pattern_urls(pattern):
    results = []
    for uurl in unique_urls:
        uurl_path = uurl.path.strip('/')
        if uurl_path.startswith(pattern):
            results.append(uurl)

    return results


def get_query_params_keys(parsed_url_query):
    keys = []
    qparams = parsed_url_query.split('&')
    for q in qparams:
        keys.append(q.split('=')[0])

    return keys


def is_all_params_exists(old_pattern, new_pattern):
    old_params_keys = get_query_params_keys(old_pattern.query)
    new_params_keys = get_query_params_keys(new_pattern.query)

    for k in old_params_keys:
        if k not in new_params_keys:
            return False

    return True


def has_more_params(old_pattern, new_pattern):
    old_params_keys = get_query_params_keys(old_pattern.query)
    new_params_keys = get_query_params_keys(new_pattern.query)
    return len(new_params_keys) > len(old_params_keys)


def main():
    web_suffixes = get_web_suffixes()
    ignored_suffixes = get_ignored_suffixes()
    # Iterate over the given domains
    with open(args.urls_file, 'r') as f:
        for url in f:
            url = url.rstrip()
            if not url:
                continue

            parsed_url = urlparse(url)

            # @todo Reconsider the rstrip, since it can remove some interesting urls
            url_path = parsed_url.path.strip('/')

            # If the URL doesn't have a path, just add it as is
            # @todo Some dups can still occur, handle it
            if not url_path:
                unique_urls.add(parsed_url)
                continue

            # Do not add paths to common files
            if url_path.endswith(ignored_suffixes):
                continue

            # Add as-is paths that points to a specific web extension (e.g. html).
            if url_path.endswith(web_suffixes):
                unique_urls.add(parsed_url)
                continue

            # Do the more complicated ddup work
            path_parts = url_path.split('/')
            if len(path_parts) == 1:
                unique_urls.add(parsed_url)
                continue

            url_pattern = '/'.join(path_parts[:-1])
            # Get existing URL patterns from our unique patterns.
            existing_pattern_urls = get_existing_pattern_urls(url_pattern)
            if not existing_pattern_urls:
                unique_urls.add(parsed_url)
            elif parsed_url.query:
                for u in existing_pattern_urls:
                    # Favor URL patterns with params over those without params.
                    if not u.query:
                        unique_urls.remove(u)
                        unique_urls.add(parsed_url)
                        continue

                    # Check if it has query params that are extra to the unique URL pattern.
                    if is_all_params_exists(u, parsed_url):
                        if has_more_params(u, parsed_url):
                            unique_urls.remove(u)
                            unique_urls.add(parsed_url)
                            continue
                    else:
                        unique_urls.add(parsed_url)
                        continue


def print_results():
    if args.output:
        try:
            f = open(args.output, "w")

            for url in sorted(unique_urls):
                u = url.geturl()
                f.write(u + "\n")
                print(u)

            f.close()
        except:
            print('[X] Failed to save the output to a file.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Remove URL pattern duplications..')

    # Add the arguments
    parser.add_argument('-u', '--urls', help='File with a list of urls.', type=file_arg, dest='urls_file')
    parser.add_argument('-o', '--output', help='Save results to a file.', dest='output')
    parser.add_argument('-s', '--silent', help='Print only the result URLs.', action='store_true', dest='silent')
    args = parser.parse_args()

    # Every tool needs a banner.
    if not args.silent:
        banner()

    unique_urls = set()
    main()

    print_results()