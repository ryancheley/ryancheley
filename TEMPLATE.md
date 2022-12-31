> 👋 Hi there, I am a Healthcare IT Professional, with interests in EHRs, Business Processes and turning data into actionable information.

{{ lede }}

<table><tr><td valign="top" width="33%">

## TILs

<ul>
{% for til in tils %}
  <li><a href="{{ til.url }}" target="_blank">{{ til.title }}</a> - {{ til.date }}</li>
{% endfor %}
</ul>


</td><td valign="top" width="34%">

### Latest articles

<ul>
{% for article in articles %}
  <li><a href="{{ article.url }}" target="_blank">{{ article.title }}</a> - {{ article.date }}</li>
{% endfor %}
</ul>

> <a href="https://ryancheley.com/" target="_blank">More articles</a>

</td><td valign="top" width="33%">

### Latest Mastodon toots

{% for toot in toots %}
  <blockquote>
  {{toot.title}}
  - <a href="{{ toot.url }}" target="_blank">{{ toot.date }}</a>
  </blockquote>
{% endfor %}

<br>

> <a href="https://mastodon.social/@ryancheley" target="_blank">More toots</a>


</td></tr></table>
