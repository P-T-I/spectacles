from collections import namedtuple

repo_rights = namedtuple("repo_rights", "NONE READ WRITE FULL")(
    [], ["pull"], ["push"], ["pull", "push"]
)
