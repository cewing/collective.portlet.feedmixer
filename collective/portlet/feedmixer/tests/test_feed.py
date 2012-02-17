import unittest
import feedparser
from zope.interface.verify import verifyObject
from collective.portlet.feedmixer.interfaces import IFeedMixer
from collective.portlet.feedmixer.portlet import Assignment

from collective.portlet.feedmixer.tests import FEED_ONE
from collective.portlet.feedmixer.tests import FEED_TWO


class ConstructionTests(unittest.TestCase):

    def testInterface(self):
        feed=Assignment()
        verifyObject(IFeedMixer, feed)

    def testParameterOrder(self):
        feed=Assignment("title", "feeds", "items_shown", "cache_timeout")
        self.assertEqual(feed.title, "title")
        self.assertEqual(feed.feeds, "feeds")
        self.assertEqual(feed.items_shown, "items_shown")
        self.assertEqual(feed.cache_timeout, "cache_timeout")

    def testNamerParameters(self):
        feed=Assignment(title="title", feeds="feeds",
                items_shown="items_shown", cache_timeout="cache_timeout")
        self.assertEqual(feed.title, "title")
        self.assertEqual(feed.feeds, "feeds")
        self.assertEqual(feed.items_shown, "items_shown")
        self.assertEqual(feed.cache_timeout, "cache_timeout")


class UtilityMethodTests(unittest.TestCase):

    def setUp(self):
        self.feed=Assignment(feeds="%s %s" % (FEED_ONE, FEED_TWO))
        self.parsed_one=feedparser.parse(FEED_ONE)
        self.parsed_two=feedparser.parse(FEED_TWO)
        self.feed.cleanFeed(self.parsed_one)
        self.feed.cleanFeed(self.parsed_two)

    def testSingleFeedUrl(self):
        self.feed.feeds=FEED_ONE
        self.assertEqual(list(self.feed.feed_urls), [FEED_ONE])

    def testMultipleFeedUrls(self):
        self.assertEqual(list(self.feed.feed_urls), [FEED_ONE, FEED_TWO])

    def testMergeZeroFeeds(self):
        self.assertEqual(self.feed.mergeEntriesFromFeeds(False), [])
        self.assertEqual(self.feed.mergeEntriesFromFeeds([]), [])

    def testMergedFeedsStructure(self):
        merged = self.feed.mergeEntriesFromFeeds([self.parsed_one])
        self.assertEqual(len(merged), 1)
        self.assertTrue('title' in merged[0])
        self.assertTrue('entries' in merged[0])

    def testMergeSingleFeed(self):
        merged = self.feed.mergeEntriesFromFeeds([self.parsed_one])
        entries = merged[0]['entries']
        self.assertTrue(entries == self.parsed_one.entries)

    def testMergeTwoFeeds(self):
        merged = self.feed.mergeEntriesFromFeeds(
            [self.parsed_one, self.parsed_two])
        self.assertEqual(len(merged), 1)
        entries = merged[0]['entries']
        self.assertEqual(
            len(entries),
            len(self.parsed_one.entries)+len(self.parsed_two.entries))
        links=[entry.link for entry in entries]
        self.assertEqual(links, [
            u"http://test.two/item/1",
            u"http://test.one/item/1",
            u"http://test.two/item/2",
            u"http://test.one/item/2",
            u"http://test.two/item/3",
            u"http://test.one/item/3"])
        # merged feeds have an empty title
        self.assertEqual(merged[0]['title'], u'')

    def testUnmergedFeeds(self):
        self.feed.data.merge_feeds = False
        feeds = [self.parsed_one, self.parsed_two]
        merged = self.feed.mergeEntriesFromFeeds(feeds)
        self.assertEqual(len(merged), 2)
        for idx, expected_feed in enumerate(feeds):
            actual_feed = merged[idx]
            self.assertEqual(actual_feed['title'], expected_feed.feed.title)
            self.assertEqual(actual_feed['entries'], expected_feed.entries)


def test_suite():
    suite=unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ConstructionTests))
    suite.addTest(unittest.makeSuite(UtilityMethodTests))
    return suite
