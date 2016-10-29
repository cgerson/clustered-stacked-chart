import re
import matplotlib.pyplot as plt
import numpy as np

from itertools import cycle

class plotobject(object):

    def __init__(self, df_original, my_two_segments, remove_parenthesis = True):

        """
        df: pandas DataFrame with shape at least (1,3)
        my_two_segments: list of two columns in df. ex: ["Gender","Age"]
        """
        # prepare df

        df = df_original.copy() # copy the dataframe locally

        if remove_parenthesis: # remove reference information in parenthesis if exists
            for segment in my_two_segments:
                df[segment] = df[segment].map(lambda x: re.sub(r'\([^)]*\)', '', x))

        assert np.all([segment in df.columns for segment in my_two_segments]), "Both segments are not in dataframe passed"
        # set index to our two segments, ex: Gender and Age
        df.set_index(my_two_segments, inplace=True) # set multi-level index

        # set class variables

        self.df = df # create DataFrame class object
        self.responses = df.columns # ex: Trump, Hillary, Other

        assert len(self.responses)>=1, "No responses to plot"

        self.outer_segment = {'label': my_two_segments[0], 'level':0} # ex: Gender
        self.inner_segment = {'label': my_two_segments[1], 'level':1} # ex: Age


    def rename_segment_values(self, segment, segment_mapping):

        # ex: "Gender", {"Female": "Women", "Male": "Men"}

        df = self.df.copy()
        df.reset_index(inplace=True)
        df[segment] = df[segment].map(segment_mapping)

        self.df = df


    def plot(self, title = "Untitled", stylesheet = 'seaborn-darkgrid', chart_height = 120, alpha = 0.8, bar_width = None, colors = None, write_to_disk = False, ylabel = "Response Frequency"):

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

        fig, axes = plt.subplots(nrows=1, ncols=num_of_plots, figsize=(12+num_of_plots,6))

        for i, outer_val in enumerate(outer_segment_values):

            # subset data to appropriate segment data
            df_subset = self.df.xs(outer_val, level=self.outer_segment['level']).reset_index()

            # plot one subplot
            # pass in any other variables from the plot function to make the chart more customizable
            self._plot_subplot(df_subset, axes[i], outer_val, chart_height, alpha, ylabel)

            # format y axis ticks with %
            if i==0:
                vals = axes[i].get_yticks()
                axes[i].set_yticklabels(['{:.0f}%'.format(x) for x in vals])

            # only visualize the y label on the left-most subplot
            if i!=0:
                axes[i].set_ylabel("")
                axes[i].set_yticklabels("")

            # only visualize the legend on the right-most subplot
            if i!=num_of_plots-1:
                axes[i].legend().set_visible(False)

        # set title
        fig.suptitle(title, fontsize="x-large")
        plt.tight_layout(pad=0., w_pad=0.0, h_pad=0.0)

        plt.show()

        if write_to_disk:
            full_path = '{0}.png'.format(title)
            plt.savefig(full_path, bbox_inches='tight')
            print "Successfully wrote {0} to disk\n".format(full_path)


    def _plot_subplot(self, df_subset, ax, outer_val, chart_height, alpha, ylabel):

        """
        Plots one subplot based on data in df_subset

        """

        # set the bar width
        bar_width = self.bar_width

        # positions of the left bar-boundaries
        bar_pos = [i+1 for i in range(len(df_subset[self.responses[0]]))]

        # positions of the x-axis ticks (center of the bars as bar labels)
        tick_pos = [i+(bar_width/2) for i in bar_pos]

        # Create first bar plot from data from first response selection
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
                    # data from second response
                    df_subset[self.responses[1]],
                    # set the width
                    width=bar_width,
                    # with Hillary on the bottom
                    bottom=df_subset[self.responses[0]],
                    # with the label
                    label=self.responses[1],
                    # with alpha
                    alpha=alpha,
                    # with color
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

        # set x ticks
        plt.sca(ax)
        plt.xticks(tick_pos, df_subset[self.inner_segment['label']])

        # set limit
        ax.set_ylim(0, chart_height)

        # Set the label and legends
        ax.set_ylabel(ylabel)
        ax.set_xlabel(outer_val)
        ax.legend(loc='upper right')

        # Set a buffer around the edge
        plt.xlim([min(tick_pos)-bar_width, max(tick_pos)+bar_width])