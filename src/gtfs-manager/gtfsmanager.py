from gtfsmerge import *
import hashlib
import urllib2
import shelve
import shutil
import os.path

class GTFSManager:
    def __init__(self, name, path):
        self.data = []
        self.current_fname = 'gtfs_' + name + '_current.zip'
        self.stored_fname = 'gtfs_' + name + '_old.zip'
        self.merged_fname = path + 'gtfs_' + name + '_merged.zip'
        self.html_output_path = 'merge-results_' + name + '.html'

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
        a_schedule = LoadWithoutErrors(old_feed_path, mem_db)
        b_schedule = LoadWithoutErrors(new_feed_path, mem_db)
        merged_schedule = transitfeed.Schedule()
        accumulator = HTMLProblemAccumulator()
        problem_reporter = MergeProblemReporter(accumulator)
        util.CheckVersion(problem_reporter, latest_version)

        feed_merger = FeedMerger(a_schedule, b_schedule, merged_schedule, problem_reporter)
        feed_merger.AddDefaultMergers()

        feed_merger.GetMerger(StopMerger).SetLargestStopDistance(float(largest_stop_distance))
        feed_merger.GetMerger(ShapeMerger).SetLargestShapeDistance(float(largest_shape_distance))

        if cutoff_date is not None:
            service_period_merger = feed_merger.GetMerger(ServicePeriodMerger)
            service_period_merger.DisjoinCalendars(cutoff_date)

        if feed_merger.MergeSchedules():
            feed_merger.GetMergedSchedule().WriteGoogleTransitFeed(merged_feed_path)
        else:
            merged_feed_path = None

        output_file = file(self.html_output_path, 'w')
        accumulator.WriteOutput(output_file, feed_merger, old_feed_path, new_feed_path, merged_feed_path)
        output_file.close()

    def compare_files(self, fname1, fname2):
        hash1 = hashlib.md5(open(fname1, 'rb').read()).hexdigest()
        hash2 = hashlib.md5(open(fname2, 'rb').read()).hexdigest()
        if hash1 == hash2:
            return True
        else:
            return False

    def is_gtfs_changed(self):
        if self.compare_files(self.stored_fname, self.current_fname):
            return False
        else:
            return True

    def merge(self, url):
        self.download_gtfs(self.current_fname, url)
        if os.path.isfile(self.stored_fname):
            if self.is_gtfs_changed():
            	print "Merging ..."
		if os.path.isfile(self.merged_fname):
		    os.remove(self.merged_fname)
            	self.merge_gtfs(self.stored_fname, self.current_fname, self.merged_fname)
            	shutil.copy2(self.current_fname, self.stored_fname)
            else:
                if not os.path.isfile(self.merged_fname):
                    shutil.copy2(self.current_fname, self.merged_fname)
        else:
            shutil.copy2(self.current_fname, self.stored_fname)
            shutil.copy2(self.current_fname, self.merged_fname)

def main():
    """Run the merge driver program."""
    usage = \
    """%prog [options] <Provider name> <GTFS feed URL>

    For more information see
    https://github.com/amigocloud/gtfs-manager
    """

    parser = util.OptionParserLongError(usage=usage)
    parser.add_option('-o', '--output', dest='output_path', default='./',
                      help=' Output directory for merged GTFS')
    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.error('You did not provide all required command line arguments.')
    else:
        print 'Managing GTFS feed for ' + args[0]
        gtfsm = GTFSManager(args[0], options.output_path);
        gtfsm.merge(args[1])

if __name__ == '__main__':
  util.RunWithCrashHandler(main)
