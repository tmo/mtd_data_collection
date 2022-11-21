# MTD data collection

Data format:
<pre><code>
| data
+ ─── [date]
│	│ 
│	+ ─── [date]_[time]
│	│	│
│	│	+ ─── attacker _output
│	│	│	│
│	│	│	> ─── log_[date]_[time].txt   <i>- output  of attacker string</i>
│	│	│	+ ─── traces <i>- packet captures </i>
│	│	│	│	│
│	│	│	│	> ─── trace_[num]_[date][time]
│	│	│	│	> ─── …
│	│	+ ─── defender_output
│	│	│	│
│	│	│	> ─── mtd_times_[date]_[time].txt <i>- output of mtd notify, has times and IP changes </i>
│	│	│	+ ─── snort_output
│	│	│	│	│
│	│	│	│	> ─── alert
│	│	│	│	> ─── snort.log.[time_int]
│	│	│	│	> ...
│	|   .   .
│	+ ─── ...
|
+ ─── ...
|
...
> …
</code></pre>

