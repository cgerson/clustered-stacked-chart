# clustered-stacked-chart
Visualize difference in survey results by two layers of demographic information

<img style= "width: 780px;" src="http://cgerson.github.io/images/Election_Preferences_by_Gender_and_Age.png">


### How to use
`clustered_stacked_chart.plot(data, my_two_segments = ['Segment1','Segment2'])`,

where `Segment1` and `Segment2` are columns in the Pandas DataFrame `data` object.

### Resources

Matplotlib stacked bar chart help: <a href = "http://chrisalbon.com/python/matplotlib_stacked_bar_plot.html">Stacked Bar Plot In MatPlotLib by Chris Albon</a>

Matplotlib subplot help: <a href = "http://stackoverflow.com/a/35060572">Cord Kaldemeyer on StackOverflow</a>

Election Survey Data: <a href = "http://www.pewresearch.org/fact-tank/2016/07/28/a-closer-look-at-the-gender-gap-in-presidential-voting/ft_16-7-29-gender2/">Pew Research Center</a>
