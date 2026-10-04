---
date: '2012-08-28'
title: Announcing Matrix Widget for OpenERP 6.0
category: English
tags: GitHub, javascript, mako, matrix, OpenERP, Python, smile, widget, ERP
---

For about a year I'm working on a prototype of a matrix widget for OpenERP.
This component was sponsored by my employer [Smile](https://smile.fr) and is
currently used in
production (`https://www.smile.fr/References/References-par-domaine/Public-et-collectivites/Inra3`)
by two customers. The [code is available on
GitHub](https://github.com/kdeldycke/smile_openerp_matrix_widget) under an
OpenSource license.

The matrix widget looks like what you can expect from a component of that name:

![Read-only matrix of activity report lines, one row per task against days 01 to 31, with a totals row where cells over the daily limit are flagged red](1-level-readonly-matrix.png)

The screenshot above was captured in read-only. Here is its version in editable
mode:

![The same matrix in editable mode, every cell now a clickable button that increments on click, with a resource picker above and a remove button on each row](1-level-editable-increment-matrix.png)

The drop-down menu on top of the matrix allows you to dynamically add a new
line. A new button appeared on the left to remove each line. Sums are
automatically updated when a cell value is updated.

The value of each cell here is set by clicking a button which is cycling
through a list of predefined values. But you are free to replace cell's widget
by simple input fields for floats and integer, as well as selection fields.

Another big feature is the ability to render higher dimensions. I simply render
them as a hierarchical tree on the left:

![Two-level read-only matrix grouping people under a project-manager heading, with monthly columns and totals for productivity and performance](2-level-readonly-additional-lines-matrix.png)

As you can see, I've also added additional information in columns and lines,
after the total column and total line.

Again, intermediate sums are updated dynamically, and lines can be added at any
level in editable mode:

![The two-level matrix in editable mode, each grouped row carrying its own resource selector and per-cell buttons](2-level-editable-additional-lines-matrix.png)

Finally, as you may have probably guessed by the previous screenshots, each
cell can be independently set as read-only or be made invisible. I used this
feature to generate ASCII art:

![The widget's grid of cells filled in so the ones spell out lettering across the calendar, ASCII art drawn out of timesheet entries](ascii-art-matrix.png)

The matrix widget started its life as a proof-of concept. The code base grew
organically until it reached its current prototype status. This explain why it
targets OpenERP 6.0, and why it still requires huge refactoring.
