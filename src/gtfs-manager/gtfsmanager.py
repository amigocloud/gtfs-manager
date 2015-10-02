import transitfeed
from transitfeed import util
from gtfsmerge import *

import urllib2

class GTFSManager:
    def __init__(self):
        self.data = []

    def download_gtfs(self, filename, url):
        mp3file = urllib2.urlopen(url)
        output = open(filename,'wb')
        output.write(mp3file.read())
        output.close()


    def merge_gtfs(self, old_feed_path, new_feed_path, merged_feed_path):
        mem_db = True
        latest_version = None
        largest_stop_distance = 10
        largest_shape_distance = 10
        cutoff_date = None
        html_output_path = 'merge-results.html'
        a_schedule = LoadWithoutErrors(old_feed_path, mem_db)
        b_schedule = LoadWithoutErrors(new_feed_path, mem_db)
        merged_schedule = transitfeed.Schedule()
        accumulator = HTMLProblemAccumulator()
        problem_reporter = MergeProblemReporter(accumulator)
        util.CheckVersion(problem_reporter, latest_version)

        feed_merger = FeedMerger(a_schedule, b_schedule, merged_schedule,
                               problem_reporter)
        feed_merger.AddDefaultMergers()

        feed_merger.GetMerger(StopMerger).SetLargestStopDistance(float(
          largest_stop_distance))
        feed_merger.GetMerger(ShapeMerger).SetLargestShapeDistance(float(
          largest_shape_distance))

        if cutoff_date is not None:
            service_period_merger = feed_merger.GetMerger(ServicePeriodMerger)
            service_period_merger.DisjoinCalendars(cutoff_date)

        if feed_merger.MergeSchedules():
            feed_merger.GetMergedSchedule().WriteGoogleTransitFeed(merged_feed_path)
        else:
            merged_feed_path = None

        output_file = file(html_output_path, 'w')
        accumulator.WriteOutput(output_file, feed_merger,
                              old_feed_path, new_feed_path, merged_feed_path)
        output_file.close()

#test = GTFSManager();
#test.download_gtfs('vta_gtfs.zip', 'http://www.vta.org/sfc/servlet.shepherd/document/download/069A0000001NUea')
#test.merge_gtfs('gtfs.zip', 'vta_gtfs.zip', 'vta_gtfs_merged.zip')