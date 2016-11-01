import re
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

class plotobject(object):

    def __init__(self, data, my_two_segments, clean_segment_values = True, custom_order_outer = False, custom_order_inner = False, custom_order_values = False):

        """
        df: pandas DataFrame with shape at least (1,3)
        my_two_segments: list of two columns in df. ex: ["Gender","Age"]
        custom_ordering_outer: list of strings with desired order for outer label
        custom_order_inner: list of strings with desired order for inner labels
        custom_order_values: list of strings with desired order for values (stack order)

        """
        # prepare df

        df = data.copy() # copy the dataframe locally

        if clean_segment_values: # remove reference information in parenthesis if exists
            for segment in my_two_segments:
                df[segment] = df[segment].map(lambda x: re.sub(r'\([^)]*\)', '', x))

        assert np.all([segment in df.columns for segment in my_two_segments]), "Both segments are not in dataframe passed"
        # set index to our two segments, ex: Gender and Age
        df = df.set_index(my_two_segments) # set multi-level index

        # allow for custom ordering
        if custom_order_outer:
            df = df.reindex(index=custom_order_outer, level=0)
        if custom_order_inner:
            df = df.reindex(index=custom_order_inner, level=1)

        # set class variables

        self.df = df # create DataFrame class object

        self.responses = custom_order_values or df.columns # ex: Trump, Hillary, Other

        assert len(self.responses)>=1, "No responses to plot"

        self.outer_segment = {'label': my_two_segments[0], 'level':0} # ex: Gender
        self.inner_segment = {'label': my_two_segments[1], 'level':1} # ex: Age

    def _rename_segment_values(self, segment_and_segment_mapping):

        # ex: "Gender", {"Female": "Women", "Male": "Men"}

        segment, segment_mapping = segment_and_segment_mapping

        df = self.df.copy()
        df.reset_index(inplace=True)
        df[segment] = df[segment].map(segment_mapping)

        self.df = df


    def _plot_all(self, title = "Untitled", stylesheet = 'seaborn-darkgrid', chart_height = 120, alpha = 0.8, bar_width = None, colors = None, write_to_disk = False, ylabel = "Response Frequency", display_frequencies = True, fontfamily = 'serif', display_y_axis = True):

        """
        Parameters:
        -----------
        title: string
        stylesheet: one of matplotlob's stylesheets, found with this command: print(plt.style.available)
        chart_height: default is 120 to ensure legend doesn't block bar chart. assumes responses are frequencies out of 100
        alpha: controls transparency of bars
        bar_width: set the bar_width (recommend around 0.80 depending on number of bars), or allow it to be set programmatically
        colors: list of hex values, or use the default

        """

        if stylesheet:
            plt.style.use(stylesheet)

        # set colors for each responses or use default colors here
        colors = colors or ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf"]
        assert len(colors)>=len(self.responses), "Number of color choices is less than number of responses"
        self.color_dict = {k:v for k,v in zip(self.responses, colors)}

        # fetch unique values for each segment to calculate number of subplots and bar width
        outer_segment_values = self.df.index.get_level_values(self.outer_segment['label']).unique()
        inner_segment_values = self.df.index.get_level_values(self.inner_segment['label']).unique()

        # calculate number of subplots and bars
        num_of_plots = len(outer_segment_values)
        num_of_bars = num_of_plots*len(inner_segment_values)

        # set the bar width
        self.bar_width = bar_width or float(6)/num_of_bars

        fig, axes = plt.subplots(nrows=1, ncols=num_of_plots, figsize=(10+num_of_plots,6))

        for i, outer_val in enumerate(outer_segment_values):

            # subset data to appropriate segment data
            df_subset = self.df.xs(outer_val, level=self.outer_segment['level']).reset_index()

            # plot one subplot
            # pass in any other variables from the plot function to make the chart more customizable
            self._plot_subplot(df_subset, axes[i], outer_val, chart_height, alpha, ylabel, display_frequencies)

            # format y axis ticks with %
            if i==0:
                vals = axes[i].get_yticks()
                axes[i].set_yticklabels(['{:.0f}%'.format(x) for x in vals])

            # only visualize the y label on the left-most subplot
            if display_y_axis and i!=0:
                axes[i].set_ylabel("")
                axes[i].set_yticklabels("")
            elif not display_y_axis:
                axes[i].set_ylabel("")
                axes[i].set_yticklabels("")

            # only visualize the legend on the right-most subplot
            if i!=num_of_plots-1:
                axes[i].legend().set_visible(False)

        plt.rcParams['axes.facecolor']='white'
        plt.rcParams['savefig.facecolor']='white'
        mpl.rc('font',family=fontfamily)

        # set title
        fig.suptitle(title, fontsize=22, weight="bold")
        plt.tight_layout(pad=0., w_pad=0.0, h_pad=0.0)

        if write_to_disk:
            filename = title.replace(" ", "_")
            full_path = '{0}.png'.format(filename)
            plt.savefig(full_path, bbox_inches='tight')
            print "Successfully wrote {0} to disk\n".format(full_path)
        else:
            plt.show()


    def _plot_subplot(self, df_subset, ax, outer_val, chart_height, alpha, ylabel, display_frequencies):

        """
        Plots one subplot based on data in df_subset

        """

        # set the bar width
        bar_width = self.bar_width

        # positions of the left bar-boundaries
        bar_pos = [i+1 for i in range(len(df_subset[self.responses[0]]))]

        # positions of the x-axis ticks (center of the bars as bar labels)
        tick_pos = [i+(bar_width/2) for i in bar_pos]

        # create first bar plot from data from first response selection
        ax.bar(bar_pos,
                # data from first response
                df_subset[self.responses[0]],
                # set the width
                width=bar_width,
                # with the label
                label=self.responses[0],
                # with alpha
                alpha=alpha,
                # with color
                color=self.color_dict[self.responses[0]])

        # Create second bar plot from data from second response selection
        if len(self.responses)>1:

            ax.bar(bar_pos,
                    df_subset[self.responses[1]], # data from second response
                    width=bar_width,
                    bottom=df_subset[self.responses[0]], # with Hillary on the bottom
                    label=self.responses[1],
                    alpha=alpha,
                    color=self.color_dict[self.responses[1]])

            # set bottom values for next response
            bottom = df_subset[self.responses[0]]

        if len(self.responses)>2:

            # iterate through all other response options
            for index, response in enumerate(self.responses[2:]):

                ax.bar(bar_pos,
                        df_subset[self.responses[index+2]],
                        width=bar_width,
                        bottom=[i+j for i,j in zip(df_subset[self.responses[index+1]],bottom)], # with the other responses on the bottom
                        label=self.responses[index+2],
                        alpha=alpha,
                        color=self.color_dict[self.responses[index+2]])

                # set bottom value for next response
                bottom = [i+j for i,j in zip(df_subset[self.responses[index+1]],bottom)]

        # annotate chart with response frequencies
        if display_frequencies:
            for i,patch in enumerate(ax.patches):
                x,y = patch.get_xy()
                height = patch.get_height()

                fontsize = 14
                if height < 5:
                    fontsize = fontsize - (7-height)

                format_display = "{:.0f}%".format(height)

                ax.annotate(format_display, (x * 1.005, (height+y)), xytext = (4,-18),
                                                    textcoords='offset points', fontsize=fontsize,
                                                    weight='bold', color='white', family = 'sans-serif')

        # set x ticks
        plt.sca(ax)
        plt.xticks(tick_pos, df_subset[self.inner_segment['label']])

        # set y-axis limit
        ax.set_ylim(0, chart_height)

        # set the labels and legend
        ax.set_ylabel(ylabel)
        ax.set_xlabel("\n"+outer_val)
        ax.legend(loc='upper right', fontsize=12)

        # set a buffer around the edge
        plt.xlim([min(tick_pos)-bar_width, max(tick_pos)+bar_width])


def plot(data, my_two_segments, custom_order_outer = False, custom_order_inner = False, custom_order_values = False, title = "Untitled", stylesheet = 'seaborn-darkgrid', chart_height = 120, alpha = 0.8, bar_width = None, colors = None, write_to_disk = False, ylabel = "Response Frequency", rename_segment_values = False, display_frequencies = True, fontfamily = 'serif', display_y_axis = True):

    """
    Parameters:
    -----------
    df: pandas DataFrame with shape at least (1,3)
    my_two_segments: list of two columns in df. ex: ["Gender","Age"]
    custom_ordering_outer: list of strings with desired order for outer label
    custom_order_inner: list of strings with desired order for inner labels
    custom_order_values: list of strings with desired order for values (stack order)
    title: string
    stylesheet: one of matplotlob's stylesheets, found with this command: print(plt.style.available)
    chart_height: default is 120 to ensure legend doesn't block bar chart. assumes responses are frequencies out of 100
    alpha: controls transparency of bars
    bar_width: set the bar_width (recommend around 0.80 depending on number of bars), or allow it to be set programmatically
    colors: list of hex values, or use the default
    rename_segment_values: tuple where first element is segment label, second element is a mapping of new values. ex: ("Gender", {"Female": "Women", "Male": "Men"})
    display_frequencies: boolean, default True
    fontfamily: string, default 'serif'
    display_y_axis: boolean, default True

    """

    plotobj = plotobject(data, my_two_segments, custom_order_outer = custom_order_outer, custom_order_inner = custom_order_inner, custom_order_values = custom_order_values)

    if rename_segment_values:
        plotobj._rename_segment_values(rename_segment_values)

    plotobj._plot_all(title = title, stylesheet = stylesheet, chart_height = chart_height, alpha = alpha, bar_width = bar_width, colors = colors, write_to_disk = write_to_disk, ylabel = ylabel, display_frequencies = display_frequencies, fontfamily = fontfamily, display_y_axis = display_y_axis)
