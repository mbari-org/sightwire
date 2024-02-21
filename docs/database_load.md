# Database Loading

This document provides a set of recipes for common tasks.

# Setup
See the [README](../README.md) document for instructions on setting up the environment.
See the [database setup](database_setup.md) document for instructions on database setup.
The assumption here is that your environment is setup and the database is running.
For data loading tasks, a TATOR_TOKEN and TATOR_HOST environment variable should be set.
  
## Loading data 

### Step 1. Extracting depth/lat/lon from LCM log files to a CSV file
Choose the LCM log file you want to extract data from and channels to extract data from.
E.g. to get the lat/lon and depth from the LASS_USBL_LATLONG and LASS_DEPTH channels respectively, 
use the following:

```shell
python sightwire convert extract-log \
--log /opt/compas/data/oi_survey_1648/lcmlog.00 \
--usbl-channel USBL_WINFROG  \
--depth-channel DEPTH_KEARFOTT_COMPAS \
--output /opt/compas/logs \
--prefix oi_survey_1648
```
This will create CSV files with the extracted data /opt/compas/data/logs
with the prefix, e.g. oi_survey_1648_USBL_WINFROG.csv oi_survey_1648_DEPTH_KEARFOTT_COMPAS.csv 

### Step 2. Bulk load
Assuming you have a CSV file with the extracted data, you can load the data into the database using the following command:
Note that this uses bulk loading which is faster than loading one row at a time.
This is set to load 500 rows at a time. 

---
**Tip** test the load with a small number of images first.
Use the *--max-images* option to limit the number of images to load before aborting.
---

Grab your HOST_IP.  Here, we assume this is in the private IP 192 range, excluding the subnet 255.
```bash
HOST_IP=$(ifconfig | tail -n +2 | grep -o '192\.168\.[0-9]\+\.[0-9]\+' | grep -v '192\.168\.0\.255' | grep -v '^$')
echo $HOST_IP
```

```text
192.168.0.26
```

Load a few images in bulk.  Here, we assume data is mapped from /opt/compas/data to /data.
**Note** the image data must be mapped in a docker volume map, but the logs do not need to 
be mapped to a volume.

```bash
python sightwire load image \
--input-left /opt/compas/data/oi_survey_1648/PROSILICA_L_PNG \
--input-right /opt/compas/data/oi_survey_1648/PROSILICA_R_PNG \
--base-url http://$HOST_IP:8081 \
--vol-map /opt/compas/data:/data \
--platform-type "LASS" \
--mission-name "oi_survey_1648" \
--camera-type "PROSILICA" \
--log-position /opt/compas/logs/oi_survey_1648_USBL_WINFROG.csv \
--log-depth /opt/compas/logs/oi_survey_1648_DEPTH_KEARFOTT_COMPAS.csv \
--max-images 2 --bulk --force
```
 
### Step 3. Realtime load

Realtime loading is not truly real-time but done from a watchdog at a rate of
1Hz.  The two steps in this workflow are 1) start a watchdog that listens to
a directory for new .png images and queues to a REDIS timeseries queue, 
and 2) start a consumer that consumes that at a rate of 1Hz for loading.

For example, to load images at 1 Hz from a directory 
/opt/compas/data/realtime/oi_survey_1648/ 

First, start the watchdog. This assumes the directories to capture images in has been created,
e.g. /opt/compas/data/realtime/oi_survey_1648/
```bash
python sightwire realtime run_watchdog \
--input /opt/compas/data/realtime/oi_survey_1648/
```

Next, in a separate window, grab images from the queue and load them with whatever
additional metadata you want, e.g. platform-type, etc.
As with bulk loading, the url and volume map needs to be specified.
```bash
python sightwire realtime capture \
--input /opt/compas/data/realtime/oi_survey_1648/
--base-url http://$HOST_IP:8081
--vol-map /opt/compas/data:/data \
--platform-type "LASS" \
--mission-name "oi_survey_1648" \
--camera-type "PROSILICA"
```