#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Creates document index on Solr.
This script assumes that source files are built with Sphinx,
and second argument is directory where produced by 'make text'.

Usage: python solr-document-indexer.py {SOLR_SERVER_URL} {DOCUMENT_DIR}
"""

import datetime
import hashlib
import logging
import os
import sys

from pysolr import Solr

DOCUMENT_URL = 'http://skitazaki.appspot.com/translation/twisted-intro-ja/'
DOCUMENT_SITE_ID = 2


class Processor(object):

    def __init__(self, solr_server_url):
        self.server = Solr(solr_server_url)

    def process(self, fname):
        base, _ = os.path.splitext(os.path.basename(fname))
        url = DOCUMENT_URL + base + '.html'
        fp = open(fname)
        title = None
        while not title:
            title = fp.next().strip()
        content = ''
        for line in fp:
            s = line.strip()
            if s and not s.startswith(('**', '==', '--')):
                content += s
        fp.close()
        document_id = u"%s-%s" % (DOCUMENT_SITE_ID, title)
        logging.info("new document: %s" % (document_id,))
        t = os.path.getmtime(fname)
        doc = {
            'id': hashlib.sha1(document_id.encode('utf-8')).hexdigest(),
            'site': DOCUMENT_SITE_ID,
            'url': url,
            'title': title,
            'content': content,
            'last_modified': datetime.datetime.fromtimestamp(t)
        }
        self.server.add([doc])


def main():
    args = sys.argv[1:]
    if len(args) != 2:
        raise SystemExit(__doc__)
    solr, directory = args
    files = [os.path.join(directory, f) for f in os.listdir(directory)
                if f.startswith('p') and f.endswith('.txt')]
    processor = Processor(solr)
    for fname in files:
        logging.debug("Start processing: " + fname)
        processor.process(fname)

if __name__ == '__main__':
    main()
