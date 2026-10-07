---
layout: default
title: Bültenler
---
{% assign son = site.posts.first %}
{% if son %}
<section class="son-kart">
  <p class="son-etiket">Son bülten · {% include tarih.html date=son.date %}</p>
  <h1 class="son-baslik"><a href="{{ son.url | relative_url }}">{{ son.title }}</a></h1>
  {% if son.one_cikanlar %}
  <ul class="son-liste">
    {% for b in son.one_cikanlar %}<li>{{ b }}</li>{% endfor %}
  </ul>
  {% endif %}
  <a class="son-buton" href="{{ son.url | relative_url }}">Bülteni oku →</a>
</section>

<h2 class="gecmis-baslik">Geçmiş bültenler</h2>
{% assign gecmis = site.posts | where_exp: "p", "p.url != son.url" %}
{% if gecmis.size == 0 %}
<p class="bos">Henüz geçmiş bülten yok — yarından itibaren burada listelenecek.</p>
{% else %}
{% assign gruplar = gecmis | group_by_exp: "p", "p.date | date: '%Y-%m'" %}
{% for g in gruplar %}
{% assign parca = g.name | split: "-" %}
{% assign ay = parca[1] | plus: 0 | minus: 1 %}
<details class="ay"{% if forloop.first %} open{% endif %}>
  <summary>{{ site.aylar[ay] }} {{ parca[0] }} <span class="adet">{{ g.items.size }} bülten</span></summary>
  <ul class="gun-liste">
  {% for p in g.items %}
    <li><a href="{{ p.url | relative_url }}"><span class="gun">{{ p.date | date: "%-d" }} {{ site.aylar[ay] }}</span>{% if p.one_cikanlar %}<span class="ozet">{{ p.one_cikanlar | join: " · " }}</span>{% endif %}</a></li>
  {% endfor %}
  </ul>
</details>
{% endfor %}
{% endif %}
{% else %}
<p>Henüz bülten yok.</p>
{% endif %}
<p class="rss"><a href="{{ '/feed.xml' | relative_url }}">RSS ile takip et</a></p>
