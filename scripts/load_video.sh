#!/usr/bin/env bash
set -x
# Get the script directory and its parent
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(cd "$(dirname "${SCRIPT_DIR}/../.." )" && pwd )"


export PYTHONPATH=$PYTHONPATH:$BASE_DIR

cd $BASE_DIR

python sightwire load video \
--input $BASE_DIR/data/video/oi_survey_2115_color_FLIR_LEFT_dm.mp4 \
--platform-type "MINI ROV" \
--mission-name "oi_survey_2115" \
--camera-type "FLIR" --force true



python sightwire load video \
--input $BASE_DIR/data/video/oi_survey_2115_color_FLIR_LEFT_dm.mp4 \
--platform-type "MINI ROV" \
--mission-name "oi_survey_2115" \
--camera-type "FLIR" --force true

python sightwire load stereo-view -l oi_survey_2115_color_FLIR_LEFT_dm.mp4  -r oi_survey_2115_color_FLIR_RIGHT_dm.mp4


python sightwire load video \
--input $BASE_DIR/data/video/oi_survey_1648_color_PROSILICA_LEFT_dm.mp4 \
--platform-type "LASS" \
--mission-name "oi_survey_1648" \
--camera-type "PROSILICA" --force true



python sightwire load video \
--input $BASE_DIR/data/video/oi_survey_1648_color_PROSILICA_RIGHT_dm.mp4 \
--platform-type "LASS" \
--mission-name "oi_survey_1648" \
--camera-type "PROSILICA" --force true



python sightwire load stereo-view -l oi_survey_1648_color_PROSILICA_LEFT_dm.mp4  -r oi_survey_1648_color_PROSILICA_RIGHT_dm.mp4

python sightwire load video \
--input $BASE_DIR/data/video/oi_survey_1913_color_FLIR_LEFT_dm.mp4 \
--platform-type "MINI ROV" \
--mission-name "oi_survey_1913" \
--camera-type "FLIR" --force true



python sightwire load video \
--input $BASE_DIR/data/video/oi_survey_1913_color_FLIR_RIGHT_dm.mp4 \
--platform-type "MINI ROV" \
--mission-name "oi_survey_1913" \
--camera-type "FLIR" --force true



python sightwire load stereo-view -l oi_survey_1913_color_FLIR_LEFT_dm.mp4  -r oi_survey_1913_color_FLIR_RIGHT_dm.mp4
