import json, os, time
import pyds
from gi.repository import Gst

PERSON_CLASS_ID = 2          # ResNet10 reference detector: car, bicycle, person, roadsign
RISE_S, FALL_S = 10, 60      # asymmetric persistence filter (Section 3.6)


class PresenceFilter:
    """Accept presence after RISE_S seconds, absence after FALL_S seconds."""

    def __init__(self, rise=RISE_S, fall=FALL_S):
        self.rise, self.fall = rise, fall
        self.state, self.since = 0, None

    def update(self, raw, now):
        if raw == self.state:
            self.since = None
            return self.state
        if self.since is None:
            self.since = now
        hold = self.rise if raw > self.state else self.fall
        if now - self.since >= hold:
            self.state, self.since = raw, None
        return self.state


filters = {}                 # one filter per region of interest
last_write = 0.0


def osd_sink_pad_buffer_probe(pad, info, u_data):
    global last_write
    buf = info.get_buffer()
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(buf))
    l_frame = batch_meta.frame_meta_list
    now = time.time()
    while l_frame is not None:
        frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        counts = {}
        # per-region person counts written by nvdsanalytics
        l_user = frame_meta.frame_user_meta_list
        while l_user is not None:
            user_meta = pyds.NvDsUserMeta.cast(l_user.data)
            if user_meta.base_meta.meta_type == pyds.nvds_get_user_meta_type(
                    "NVIDIA.DSANALYTICSFRAME.USER_META"):
                fmeta = pyds.NvDsAnalyticsFrameMeta.cast(user_meta.user_meta_data)
                counts = dict(fmeta.objInROIcnt)
            l_user = l_user.next
        # whole-frame person count (office mode)
        n, l_obj = 0, frame_meta.obj_meta_list
        while l_obj is not None:
            obj = pyds.NvDsObjectMeta.cast(l_obj.data)
            if obj.class_id == PERSON_CLASS_ID:
                n += 1
            l_obj = l_obj.next
        counts["frame"] = n
        state = {}
        for roi, c in counts.items():
            f = filters.setdefault(roi, PresenceFilter())
            state[roi] = f.update(1 if c > 0 else 0, now)
        if now - last_write >= 1.0:
            with open("live_state.json.tmp", "w") as fh:
                json.dump({"t": now, "raw": counts, "present": state}, fh)
            # atomic replace so the dashboard never reads a half-written file
            os.replace("live_state.json.tmp", "live_state.json")
            last_write = now
        l_frame = l_frame.next
    return Gst.PadProbeReturn.OK
