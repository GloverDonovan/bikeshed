# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals
import io
import json
import os
import urllib2
from contextlib import closing

from ..apiclient.apiclient import apiclient
from ..messages import *

testSuiteDataContentTypes = ["application/json", "application/vnd.csswg.shepherd.v1+json"]

def update(path, dryRun=False):
    try:
        say("Downloading test suite data...")
        shepherd = apiclient.APIClient("https://api.csswg.org/shepherd/", version="vnd.csswg.shepherd.v1")
        res = shepherd.get("test_suites")
        if ((not res) or (406 == res.status)):
            die("This version of the test suite API is no longer supported. Please update Bikeshed.")
            return
        if res.contentType not in testSuiteDataContentTypes:
            die("Unrecognized test suite content-type '{0}'.", res.contentType)
            return
        rawTestSuiteData = res.data
    except Exception, e:
        die("Couldn't download test suite data.  Error was:\n{0}", str(e))
        return

    testSuites = dict()
    for rawTestSuite in rawTestSuiteData.values():
        if "specs" not in rawTestSuite:
            # Looks like test-suites might not have spec data at first.
            # Useless, so just drop them.
            continue
        testSuite = {
            'vshortname': rawTestSuite['name'],
            'title': rawTestSuite.get('title'),
            'description': rawTestSuite.get('description'),
            'status': rawTestSuite.get('status'),
            'url': rawTestSuite.get('uri'),
            'spec': rawTestSuite['specs'][0]
        }
        testSuites[testSuite['spec']] = testSuite

    if not dryRun:
        try:
            with io.open(os.path.join(path, "test-suites.json"), 'w', encoding="utf-8") as f:
                f.write(unicode(json.dumps(testSuites, ensure_ascii=False, indent=2, sort_keys=True)))
        except Exception, e:
            die("Couldn't save test-suite database to disk.\n{0}", e)
    say("Success!")