---
layout: page
title: Arşiv
permalink: /arsiv/
---
{% assign gruplar = site.posts | group_by_exp: "p", "p.date | date: '%Y-%m'" %}
{% for g in gruplar %}
{% assign parca = g.name | split: "-" %}
{% assign ay = parca[1] | plus: 0 | minus: 1 %}
<h2>{{ site.aylar[ay] }} {{ parca[0] }}</h2>
<ul>
{% for p in g.items %}
  <li><a href="{{ p.url | relative_url }}">{{ p.date | date: "%-d" }} {{ site.aylar[ay] }} {{ parca[0] }}</a></li>
{% endfor %}
</ul>
{% endfor %}
