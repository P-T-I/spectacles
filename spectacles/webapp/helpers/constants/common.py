from collections import namedtuple

msg_status = namedtuple("msg_status", "OK NOK")("success", "error")

activity_level = namedtuple("activity_level", "INFO SUCCESS WARNING DANGER")(0, 1, 2, 3)

action_types = namedtuple("action_types", "BG_PULL BG_PUSH USER GROUP")(0, 1, 2, 3)

access_level = namedtuple("access_level", "NONE READ WRITE FULL")(0, 1, 2, 3)
