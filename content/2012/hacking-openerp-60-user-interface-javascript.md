---
date: '2012-05-29'
title: Hacking OpenERP 6.0 User Interface with JavaScript
category: English
tags: HTML, javascript, jquery, OpenERP, smile, ERP
---

OpenERP 6.1's web client comes with a cleaner JavaScript framework which [features some hook mechanism](https://web.archive.org/web/20120210124531/http://planet.domsense.com/en/2012/01/openerp-new-web-client-6-1-javascript-hooks/) to simplify customization. In the mean time, I still have to work on older OpenERP 6.0 for customers who haven't migrated yet. So let me present you a tiny collection of ugly (but working) JavaScript hacks I use to customize some aspects of the user interface.

First, you have to learn how to inject JavaScript code in the web client. My method is described in details in an article on [how-to monkey-patch OpenERP’s native JavaScript]({filename}/2012/how-to-monkey-patch-openerp-native-javascript.md). Please read the later to understand how my hacks are supposed to work.

That being said, let's start with this simple snippet that will let you force the focus on a particular field, which is great to speed-up user data input on some complicated forms:

```js
$('#my_field_id').focus();
```

Once, in an heavily customized form, I had to simulate a click on a custom button each time a user would press the ++enter++ key, hence simulating a form submission. This can be done with the following code:

```js
$("input").keydown(function(e) {
    if (e.keyCode === 13) {
        $("#my_custom_button_id").trigger('click');
    };
});
```

In another case of a highly customized view, I had to change the behavior of a `attrs="{'invisible': [('my_column_id', '=', True)]}"` directive, which make, by default, the targeted field invisible by using a `display: none;` CSS statement. I wanted the `attrs` to use the `visibility: hidden;` CSS instead, to let my field occupy its rendering area and not break the layout. Here is how I managed to take control of the default behavior:

```js
// Monkey-patch form_setVisible from addons/openerp/static/javascript/form_state.js
var original_setVisible = form_setVisible;
form_setVisible = function(container, field, visible) {
    original_setVisible(container, field, visible);
    // Revert OpenERP's invisible attribute default behaviour by removing the "display: none;" it has just set,
    // then replace it by a "visibility: hidden;" statement to let our "*template_id_*" fields keeps their rendering area.
    $("td.item-group[attrs*='template_id_']:hidden").show().css('visibility', 'hidden');
};
```

Here is the view type selector widget, which is appearing everywhere in OpenERP in the top-right corner:

![OpenERP view-type selector, a small strip of icons for list, form, chart and calendar views with the second one active in red](openerp-view-type-selector-widget.png)

To hide it, running the following jQuery is enough:

```js
$('#view-selector').hide();
```

Here are the action buttons and the object navigation pager:

![OpenERP action bar with New, Edit, Duplicate and Delete buttons on the left and record navigation reading 2 of 4 on the right](openerp-action-buttons-and-object-navigation.png)

If you want to hide the whole thing, then the following code will do:

```js
$('.wrapper.action-buttons').hide();
```

If you're only interested to hide the pager, use:

```js
$(".wrapper .pager").hide();
```

And if you want to hide all action buttons but the "Save and Edit" one, the JavaScript code is:

```js
$(".wrapper.action-buttons li a:not([onclick*='save_and_edit'])").hide();
```

For the last set of hacks, there is a better way to act on each action button's visibility. You can use the smile_buttons_access (`https://github.com/Smile-SA/smile_openerp_addons_6.0/tree/master/smile_buttons_access`) module which was created by my co-workers from [Smile](https://smile.fr). This web add-on will by default make the "create", "edit" and "delete" buttons sensible to the "create", "write" and "unlink" rights of the current user. But this module will let you pass some variables in the context to hide each one of these buttons independently.
