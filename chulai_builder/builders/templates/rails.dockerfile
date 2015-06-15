FROM {{ build.ancestor }}

USER root
{% include "install-extra-libs" %}

USER {{ paas.user }}

{% include "sync-codebase" %}

WORKDIR {{ build.app.work_dir }}
{% include "rails/apply-project-configs" %}

{% include "rails/bundle" %}
