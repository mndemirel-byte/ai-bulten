---
layout: default
title: Bugün
---
{% assign son = site.posts.first %}
{% if son %}
<p><small>Son bülten · <a href="{{ son.url | relative_url }}">kalıcı bağlantı</a> · <a href="{{ '/arsiv/' | relative_url }}">tüm arşiv</a> · <a href="{{ '/feed.xml' | relative_url }}">RSS</a></small></p>
<h1>{{ son.title }}</h1>
{{ son.content }}
{% else %}
<p>Henüz bülten yok.</p>
{% endif %}
