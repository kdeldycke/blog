---
date: '2015-11-05'
title: Pandas snippets
category: English
tags: Pandas, Computer programming, date, development, Python, Data, Analytics, NumPy
---

Import Numpy and Pandas:

```pycon
>>> import numpy as np
>>> import pandas as pd
```

Create a 5 rows and 3 columns frame with random integers between 0 and 99:

```pycon
>>> df = pd.DataFrame(np.random.randint(100, size=(5, 3)))
>>> df
    0   1   2
0  35  66  14
1  30   3  13
2  17  69  97
3  99  27   0
4  30  53  64
```

Add labels to columns:

```pycon
>>> df.columns = ["a", "b", "c"]
>>> df
    a   b   c
0  35  66  14
1  30   3  13
2  17  69  97
3  99  27   0
4  30  53  64
```

Drop all but `a` and `c` columns:

```pycon
>>> df[["a", "c"]]
    a   c
0  35  14
1  30  13
2  17  97
3  99   0
4  30  64
```

Get a NumPy array of index values:

```pycon
>>> df.index.values
array([0, 1, 2, 3, 4])
```

Check if column `a` is already sorted by comparing initial and value-sorted indexes:

```pycon
>>> df.a.index.tolist()
[0, 1, 2, 3, 4]
>>> df.a.sort_values().index.tolist()
[2, 4, 1, 0, 3]
>>> df.a.index.tolist() == df.a.sort_values().index.tolist()
False
```

Make column `a` the index:

```pycon
>>> df.set_index("a", inplace=True)
>>> df
    b   c
a
35  66  14
30   3  13
17  69  97
99  27   0
30  53  64
```

Sort along the index:

```pycon
>>> df.sort_index(inplace=True)
>>> df
    b   c
a
17  69  97
30  53  64
30   3  13
35  66  14
99  27   0
```

Deduplicate `c` data points at the same `a` index, with the highest `c` value
taking precedence:

```pycon
>>> df["c"].reset_index().groupby("a").max()
    c
a
17  97
30  64
35  14
99   0
```

Transform a timeline of [`arrow`](https://arrow.readthedocs.io/) objects to
Pandas' internal Timestamp index:

```pycon
>>> df = pd.DataFrame({"int_ts": pd.Series(np.random.randint(9999999999, size=5))})
>>> df
      int_ts
0  761088975
1  900402905
2  924263705
3  636666598
4  501201802

>>> import arrow
>>> df["dt_arrow"] = df.int_ts.map(arrow.get)
>>> df
      int_ts                   dt_arrow
0  761088975  1994-02-12T21:36:15+00:00
1  900402905  1998-07-14T07:55:05+00:00
2  924263705  1999-04-16T11:55:05+00:00
3  636666598  1990-03-05T19:49:58+00:00
4  501201802  1985-11-18T22:43:22+00:00

>>> from operator import attrgetter
>>> df["dt_index"] = pd.to_datetime(df["dt_arrow"].apply(attrgetter("datetime")), utc=True)
>>> df
      int_ts                   dt_arrow            dt_index
0  761088975  1994-02-12T21:36:15+00:00 1994-02-12 21:36:15
1  900402905  1998-07-14T07:55:05+00:00 1998-07-14 07:55:05
2  924263705  1999-04-16T11:55:05+00:00 1999-04-16 11:55:05
3  636666598  1990-03-05T19:49:58+00:00 1990-03-05 19:49:58
4  501201802  1985-11-18T22:43:22+00:00 1985-11-18 22:43:22

>>> df.set_index("dt_index", inplace=True)
>>> df.sort_index(inplace=True)
>>> df
                        int_ts                   dt_arrow
dt_index
1985-11-18 22:43:22  501201802  1985-11-18T22:43:22+00:00
1990-03-05 19:49:58  636666598  1990-03-05T19:49:58+00:00
1994-02-12 21:36:15  761088975  1994-02-12T21:36:15+00:00
1998-07-14 07:55:05  900402905  1998-07-14T07:55:05+00:00
1999-04-16 11:55:05  924263705  1999-04-16T11:55:05+00:00
```

Now that we have a properly indexed timeline, we can use built-in Pandas
methods. Here is how to compute the maximum value of samples [per year
](https://pandas.pydata.org/docs/user_guide/timeseries.html#offset-aliases):

```pycon
>>> df["int_ts"].resample("AS")
dt_index
1985-01-01    501201802
1986-01-01          NaN
1987-01-01          NaN
1988-01-01          NaN
1989-01-01          NaN
1990-01-01    636666598
1991-01-01          NaN
1992-01-01          NaN
1993-01-01          NaN
1994-01-01    761088975
1995-01-01          NaN
1996-01-01          NaN
1997-01-01          NaN
1998-01-01    900402905
1999-01-01    924263705
Freq: AS-JAN, Name: int_ts, dtype: float64
```

Same as above but taking the highest value by shifting decade:

```pycon
>>> df["int_ts"].resample("10AS", how=max)
dt_index
1985-01-01    761088975
1995-01-01    924263705
Freq: 10AS-JAN, Name: int_ts, dtype: int64
```

Other resources:

- [Pandas official documentation
  ](https://pandas.pydata.org/pandas-docs/stable/), especially its
  [Cookbook](https://pandas.pydata.org/pandas-docs/stable/user_guide/cookbook.html).
- [Pandas Cheat Sheet
  ](https://github.com/pandas-dev/pandas/blob/main/doc/cheatsheet/Pandas_Cheat_Sheet.pdf).
- [Stack Overflow's pandas questions
  ](https://stackoverflow.com/questions/tagged/pandas).
- [Becky Sweger's snippets
  ](https://gist.github.com/bsweger/e5817488d161f37dcbd2).
- [Pandas Exercises](https://github.com/guipsamora/pandas_exercises).
- [100 data puzzles for pandas](https://github.com/ajcr/100-pandas-puzzles).
- [My own Pandas rants tweets
  ](https://twitter.com/search?q=%23pandas%20%40kdeldycke).
- [NumPy Tricks and Pitfalls](https://nbviewer.jupyter.org/github/vlad17/np-learn/blob/master/presentation.ipynb?flush_cache=true)
