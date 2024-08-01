Here is the blog or KL.

# note for Adjustments to templates

- mostly config.yml
- change page variables from `hiddenInHomelist` to `showInHomeList` in `list.html`

```
{{- if .IsHome }}
{{- $pages = where site.RegularPages "Type" "in" site.Params.mainSections }}
{{- $pages = where $pages "Params.showInHomeList" "==" true }}
{{- end }}

```

- footer to display the number of words and articles in`footer.html`
	
``` 
{{- if and .IsHome (not (.Param "hideFooter")) }}
{{/* --- 开始: 添加统计信息 --- */}}
{{ $allPosts := where .Site.RegularPages "Kind" "page" }}
{{ $totalWords := 0 }}
{{ range $allPosts }}
{{ $totalWords = add $totalWords .WordCount }}
{{ end }}

{{ $sectionsData := dict }}
{{ range $allPosts }}
{{ $sectionName := .Section }}
{{ if ne $sectionName "" }}
{{ if not (isset $sectionsData $sectionName) }}
{{ $sectionsData = merge $sectionsData (dict $sectionName (dict "count" 0 "words" 0)) }}
{{ end }}
{{ $count := add (index $sectionsData $sectionName).count 1 }}
{{ $words := add (index $sectionsData $sectionName).words .WordCount }}
{{ $sectionsData = merge $sectionsData (dict $sectionName (dict "count" $count "words" $words)) }}
{{ end }}
{{ end }}

{{ $currentYear := now.Format "2006" }}
{{ $lastYear := sub (int $currentYear) 1 }}
{{ $yearInfo := dict }}
{{ $firstYear := "9999" }}

{{ range $allPosts }}
{{ $year := .Date.Format "2006" }}

{{ if and (lt $year $firstYear) (ge $year "1990") }}
{{ $firstYear = $year }}
{{ end }}

{{ if ge $year "1990" }}
{{ if not (isset $yearInfo $year) }}
{{ $yearInfo = merge $yearInfo (dict $year (dict "count" 0 "words" 0)) }}
{{ end }}

{{ $count := add (index $yearInfo $year).count 1 }}
{{ $words := add (index $yearInfo $year).words .WordCount }}
{{ $yearInfo = merge $yearInfo (dict $year (dict "count" $count "words" $words)) }}
{{ end }}
{{ end }}

{{ $yearsWriting := add (sub (int $currentYear) (int $firstYear)) 1 }}
{{ $avgPostsPerYear := div (len $allPosts) $yearsWriting }}
{{ $avgWordsPerYear := div $totalWords $yearsWriting }}

<span>
<br>total{{ len $allPosts }}篇/{{ div $totalWords 10000 }}万字 
{{ range $section, $data := $sectionsData }}
{{ $section }}{{ $data.count }}篇/{{ div $data.words 10000 }}万字 
{{ end }}
<br>{{ $firstYear }}至今更新{{ $yearsWriting }}年 平均每年{{ $avgPostsPerYear }}篇/{{ div $avgWordsPerYear 10000 }}万字 {{ $currentYear }}年{{ (index $yearInfo $currentYear).count }}篇/{{ div (index $yearInfo $currentYear).words 10000 }}万字 {{ if isset $yearInfo (string $lastYear) }}{{ $lastYear }}年{{ (index $yearInfo (string $lastYear)).count }}篇/{{ div (index $yearInfo (string $lastYear)).words 10000 }}万字 {{ end }}
</span>
```