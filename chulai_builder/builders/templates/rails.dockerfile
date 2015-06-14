FROM {{ build.ancestor }}

USER root
{% include "install-extra-libs" %}

USER {{ paas.user }}
{%- set app_root = "/home/" + paas.user + "/" + build.app.name %}

{% include "sync-codebase" %}

WORKDIR {{ app_root }}
{% include "rails/apply-project-configs" %}

{% include "rails/bundle" %}
