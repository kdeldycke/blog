---
date: '2012-07-17'
title: Displaying Upcoming Events from a Google Calendar in JavaScript
category: English
tags: events, Google Calendar, HTML, iCal, JavaScript, JSON, RSS, Cool Cavemen
---

I use Google Calendar to store all the past and future [concerts of my band](https://coolcavemen.com/concerts). Now I want to display on the band's website the list of upcoming events, based on the content of that calendar.

First, you have to make the calendar public. You can then get all its content in iCal format. The URL you'll find in the calendar settings looks like this:

```text
https://www.google.com/calendar/ical/coolcavemen.com_h3432m0aeeq5c6dakki50giqeo%40group.calendar.google.com/public/basic.ics
```

The RSS feed version of that URL looks like:

```text
https://www.google.com/calendar/feeds/coolcavemen.com_h3432m0aeeq5c6dakki50giqeo%40group.calendar.google.com/public/full
```

But the provided events there are messed up and contain all past events. To only get sorted future events, we'll add some extra parameters:

```text
https://www.google.com/calendar/feeds/coolcavemen.com_h3432m0aeeq5c6dakki50giqeo%40group.calendar.google.com/public/full?orderby=starttime&sortorder=ascending&futureevents=true
```

Now that we have a nicely sorted list of upcoming concerts, we'll get it's JSON version:

```text
https://www.google.com/calendar/feeds/coolcavemen.com_h3432m0aeeq5c6dakki50giqeo%40group.calendar.google.com/public/full?orderby=starttime&sortorder=ascending&futureevents=true&alt=json
```

And around this data feed, I've built a quick and dirty JavaScript piece of code to display a nice list of upcoming concerts. Here is the source:

```html
<ul id="next-gigs">
 <li>
  No gig planned yet... :(
 </li>
 <li>
  Feeds:
  <a href="https://www.google.com/calendar/feeds/coolcavemen.com_h3432m0aeeq5c6dakki50giqeo%40group.calendar.google.com/public/full?orderby=starttime&amp;sortorder=ascending&amp;futureevents=true">
   RSS
  </a>
  ,
  <a href="https://www.google.com/calendar/ical/coolcavemen.com_h3432m0aeeq5c6dakki50giqeo%40group.calendar.google.com/public/basic.ics">
   iCal
  </a>
  .
 </li>
</ul>
<script charset="utf-8" type="text/javascript">
 jQuery(function(){
    // Get list of upcoming iCal events formatted in JSON
    jQuery.getJSON("https://www.google.com/calendar/feeds/coolcavemen.com_h3432m0aeeq5c6dakki50giqeo%40group.calendar.google.com/public/full?orderby=starttime&sortorder=ascending&futureevents=true&alt=json", function(data){
      // Utility method to pad a string on the left
      // Source: https://sajjadhossain.com/2008/10/31/javascript-string-trimming-and-padding/
      function lpad(str, pad_string, length) {
        var str = new String(str);
        while (str.length < length)
          str = pad_string + str;
        return str;
      };
      // Parse and render each event
      jQuery.each(data.feed.entry, function(i, item){
        if(i == 0) {
          jQuery("#next-gigs li").first().hide();
        };
        var event_url = jQuery.trim(item.content.$t);
        var event_header = item.title.$t;
        if(event_url.length > 0) {
          event_header = "<a href='" + event_url + "'>" + event_header + "</a>";
        };
        // Format the date string
        var d = new Date(item.gd$when[0].startTime);
        var d_string = '<strong>' + d.getFullYear() + '-' + d.getMonth() + '-' + d.getDate() + '</strong>';
        if(d.getHours() != 0 || d.getMinutes() != 0) {
          d_string = d_string + ' at ' + lpad(d.getHours(), '0', 2) + ':' + lpad(d.getMinutes(), '0', 2);
        };
        // Render the event
        jQuery("#next-gigs li").last().before(
          "<li><strong>"
          + event_header
          + "</strong><br/>Date: "
          + d_string
          + "<br/>Venue: <a href='https://maps.google.com/maps?q="
          + item.gd$where[0].valueString
          + "' target='_blank'>"
          + item.gd$where[0].valueString
          + "</a></li>"
        );
      });
    });
  });
</script>
```
