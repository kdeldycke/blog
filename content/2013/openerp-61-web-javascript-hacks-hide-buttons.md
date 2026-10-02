---
date: '2013-03-14'
title: 'OpenERP 6.1 web client hacks: hide buttons with JavaScript'
category: English
tags: OpenERP, JavaScript, Backbone.js, jQuery, Web
---

Last year I published two articles on hacking OpenERP 6.0 user interface, one to demonstrate [how to monkey-patch native JavaScript behavior]({filename}/2012/how-to-monkey-patch-openerp-native-javascript.md), the other to show how to [tweak widgets]({filename}/2012/hacking-openerp-60-user-interface-javascript.md)

Both methods are based on an injection of inline JavaScript code via XML view definition. In OpenERP 6.1, as [highlighted by Timothy](https://kevin.deldycke.com/2012/how-to-monkey-patch-openerp-native-javascript/#comment-769313088) you can no longer leverage this dirty trick: JavaScript is stripped out of the XML stream.

But I found new ways of hacking OpenERP's web client in 6.1. Following these discoveries, I've created a the [experimental `web_smile_hide_buttons` addon](https://github.com/Smile-SA/smile_openerp_addons_6.1/tree/master/web_smile_hide_buttons/) to hide the hard-coded `create` and `duplicate` buttons on `form` views.

This module is not generic: it just demonstrate how to distribute dirty patches to the web client. It currently:

- Hide `create` buttons on all list views (affect `tree` views and `many2one` search view pop-ups),
- Hide the `save` button on `form` views,
- Hide `create` and `duplicate` button on all read-only `form` views,
- Only apply these transformations to a configurable subset of models.

The core of the module lies in the [`/static/src/js/custom.js`](https://github.com/Smile-SA/smile_openerp_addons_6.1/blob/master/web_smile_hide_buttons/static/src/js/custom.js) file. Here is an excerpt of that file, which sums-up my hacks:

```javascript
openerp.web_smile_hide_buttons = function(openerp) {

    // Models for which we'll hide create and duplicate buttons
    var MODELS_TO_HIDE = ['res.partner'];

    // Hide the create button on all list views, which affect tree views and many2one pop-up search view
    openerp.web.ListView.include({
        start: function() {
            var self = this;
            var ret = this._super.apply(this, arguments);
            var res_model = this.dataset.model;
            if ($.inArray(res_model, MODELS_TO_HIDE) != -1) {
                self.options.addable = false;
            };
            return ret;
        },
    });

    // Hide the save button on form views
    openerp.web.FormView.include({
        on_loaded: function(data) {
            var self = this;
            var ret = this._super.apply(this, arguments);
            var res_model = this.dataset.model;
            if ($.inArray(res_model, MODELS_TO_HIDE) != -1) {
                this.$element.find('button.oe_form_button_save').remove();
            };
            return ret;
        },
    });

    // Hide the create and duplicate button on all page views (i.e. read-only form views)
    openerp.web.PageView.include({
        on_loaded: function(data) {
            var self = this;
            var ret = this._super.apply(this, arguments);
            var res_model = this.dataset.model;
            if ($.inArray(res_model, MODELS_TO_HIDE) != -1) {
                this.$element.find('button.oe_form_button_create').remove();
                this.$element.find('button.oe_form_button_duplicate').remove();
            };
            return ret;
        },
    });

};
```

As you can see in the [full version of the code above](https://github.com/Smile-SA/smile_openerp_addons_6.1/blob/master/web_smile_hide_buttons/static/src/js/custom.js), I tried to hide `create` entries of `many2one` context menus, but failed to.

And to make the module really complete, I still have to find a way to hide `create` & `modify` entries of `many2one` drop-down menus. If you have some working code that's doing this, feel free to send me a pull request on GitHub.
