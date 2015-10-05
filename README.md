# gtfs-manager
This python script manages GTFS updates by merging the two GTFS feeds. It downloads current GTFS file, compares it with the previous one, that was downloaded before. If the GTFS feed has changed it merges both GTFS files into one, otherwise just keeps the latest one. 

```
Usage: 
  gtfsmanager.py [options] <Provider name> <GTFS feed URL>

Options:
  -h, --help                            show this help message and exit
  -o OUTPUT_PATH, --output=OUTPUT_PATH  Output directory for merged GTFS
```
