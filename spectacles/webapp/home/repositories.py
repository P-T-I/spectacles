from collections import defaultdict

from flask import render_template
from flask_login import login_required

from . import home
from ..app.models import registry, repository, namespaces
from ..run import db


@home.route("/repositories")
@login_required
def get_repositories():

    ret_dict = defaultdict(lambda: defaultdict(list))

    all_registries = db.session.query(registry.uri, registry.id).all()

    for register in all_registries:
        ret_dict[register.uri] = (
            repository.query.filter(
                repository.namespacesid.in_(
                    db.session.query(namespaces.id)
                    .filter(namespaces.registryid == register.id)
                    .all()
                )
            )
            .order_by(repository.path)
            .all()
        )

    return render_template(
        "pages/repositories.html", header="Repositories", ret_dict=ret_dict
    )
