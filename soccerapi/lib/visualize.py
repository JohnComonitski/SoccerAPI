from .utils import normalize, get_max_idx, get_min_idx, get_median_idx, get_top_quartile_idx, kmeans, get_top_n_idx, get_stat_top_n_idx
import matplotlib.pyplot as plt
from urllib.request import urlopen
from PIL import Image, ImageDraw, ImageOps
from mplsoccer import VerticalPitch, PyPizza, FontManager, add_image

class Visualize:
    def __init__(self):
        self.primary_color = "#3D405B"
        self.secondary_color = "#F87060"
        self.tertiary_color = "#F4F1DE"
        self.highlight_color = "#81B29A"

        self.font = 'Trebuchet MS'

        #self.primary_color = "#0C0C0E"
        self.pitch = VerticalPitch(
            pitch_type='opta', 
            half=True, 
            pitch_color=self.primary_color, 
            pad_bottom=.5, 
            line_color='white',
            linewidth=.75,
            axis=True, label=True
        )

        self.ax1 = None
        self.ax2 = None
        self.ax3 = None
        self.fig = None

    def __set_up_vis(self, params):
        plt.clf()
        width = 8
        height = 9

        #Title
        if( params and "title" in params):
            title = params["title"]

        #Description
        a3_height = .015
        desc = ""
        if( params and "description" in params):
            a3_height = .035
            desc = params["description"]

        #Signature
        signature = ""
        a1_height = 0
        if( params and "signature" in params):
            a1_height = .01
            signature = params["signature"]

        fig = plt.figure(figsize=(width, height))
        fig.patch.set_facecolor(self.primary_color)

        ax1 = fig.add_axes([0, 0, 1, a1_height]) #.09 inches tall
        ax1.set_facecolor(self.primary_color)

        ax1.text(
            x=0, 
            y=0, 
            s=signature, 
            fontname='Trebuchet MS',
            fontsize=10,
            fontweight='bold',
            color=self.tertiary_color, 
            ha='left'
        )
        ax1.set_axis_off()

        ax2 = fig.add_axes([0, 0.05, 1, .8])
        ax2.set_facecolor(self.primary_color)

        plt.grid(True, alpha=0.2, color=self.tertiary_color)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)

        ax2.spines['top'].set_color(self.tertiary_color)
        ax2.spines['right'].set_color(self.tertiary_color)
        ax2.spines['left'].set_color(self.tertiary_color)
        ax2.spines['bottom'].set_color(self.tertiary_color)
        
        ax3 = fig.add_axes([0, .86, 1, a3_height])
        ax3.set_facecolor(self.primary_color)

        ax3.text(
            x=0, 
            y=.85, 
            s=title, 
            fontname='Trebuchet MS',
            fontsize=20, 
            fontweight='bold', 
            color=self.tertiary_color, 
            ha='left'
        )
        
        if(desc != ""):
            ax3.text(
                x=0, 
                y=.05, 
                s=desc, 
                fontname='Trebuchet MS',
                fontsize=14,
                color=self.tertiary_color, 
                ha='left'
            )
        ax3.set_axis_off()

        #X Axis
        ax2.tick_params(axis='x', colors=self.tertiary_color, labelfontfamily='Trebuchet MS')
        ax2.set_xlabel("", c=self.tertiary_color, fontname='Trebuchet MS', fontsize=12, fontweight='bold')

        #Y Axis
        ax2.tick_params(axis='y', colors=self.tertiary_color, labelfontfamily='Trebuchet MS')
        ax2.set_ylabel("", c=self.tertiary_color, fontname='Trebuchet MS', fontsize=12, fontweight='bold')

        self.ax1 = ax1
        self.ax2 = ax2
        self.ax3 = ax3
        self.fig = fig

    def __output_vis(self, params):
        plt.savefig(params["filename"], format="png", bbox_inches="tight")

    def pizza_plot(self, object, params):
        object_type = str(type(object))
        if( "Team" not in object_type and "Player" not in object_type ):
            return { "success" : 0, "res" : {}, "error_string" : "Error: Only Player and Team objects can be used to generate pizza plots" }

        columns = []
        if "columns" not in params:
            columns = ['Non-Penalty Goals', 'Assists', 'Goals Plus Assists', 'Yellow Cards', 'Red Cards', 'Passes',
                'Passes Completed', 'Progressive Passes', 'Through Balls', 'Key Passes', 'Touches','Take Ons', 'Take Ons Won', 'Miscontrols',
                'Dispossessed', 'Tackles', 'Tackles Won', 'Blocked Shots', 'Interceptions', 'Clearances']
        else:
            columns = params["columns"]

        object_data = object.scouting_data()
        if( not object_data ):
            return { "success" : 0, "res" : {}, "error_string" : "Error: No Player Scouting data was found." }
        
        object_img = object.image()
        if( not object_img ):
            object_img = ""

        stat_keys = []
        stat_values = []
        values = []
        for key in object_data:
            stat = object_data[key]
            name = stat.name
            if name in columns:
                stat_keys.append(name)
                values.append(stat.value)
                stat_values.append([stat.value, stat.percentile])
        image = Image.open(urlopen(object_img))

        # Create a circular mask for the image
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + image.size, fill=255)

        # Apply the mask to the image
        masked_img = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
        masked_img.putalpha(mask)

        # color for the slices and text
        slice_colors = ["#bbEE90"] * 5 + ["#FF93ff"] * 5 + ["#FFCCCB"] * 5 + ["#87CEEB"] * 5
        text_colors = ["#000000"] * len(stat_keys)

        # instantiate PyPizza class
        baker = PyPizza(
            params=stat_keys,               # list of parameters
            background_color="#132257",     # background color
            straight_line_color="#000000",  # color for straight lines
            straight_line_lw=1,             # linewidth for straight lines
            last_circle_color="#000000",    # color for last line
            last_circle_lw=1,               # linewidth of last circle
            other_circle_lw=0,              # linewidth for other circles
            inner_circle_size=11            # size of inner circle
        )

        # plot pizza
        fig, ax = baker.make_pizza(
            values,                          # list of values
            figsize=(10, 12),                # adjust the figsize according to your need
            color_blank_space="same",        # use the same color to fill blank space
            slice_colors=slice_colors,       # color for individual slices
            value_colors=text_colors,        # color for the value-text
            value_bck_colors=slice_colors,   # color for the blank spaces
            blank_alpha=0.4,                 # alpha for blank-space colors
            kwargs_slices=dict(
                edgecolor="#000000", zorder=2, linewidth=1
            ),                               # values to be used when plotting slices
            kwargs_params=dict(
                color="#ffffff", fontsize=13, va="center"
            ),                               # values to be used when adding parameter labels
            kwargs_values=dict(
                color="#ffffff", fontsize=11, zorder=3,
                bbox=dict(
                    edgecolor="#000000", facecolor="cornflowerblue",
                    boxstyle="round,pad=0.2", lw=1
                )
            )                                # values to be used when adding parameter-values labels
        )

        # add title
        fig.text(
            0.515, 0.945, object.name(), size=27,
            ha="center", color="#ffffff"
        )

        # add subtitle
        fig.text(
            0.515, 0.925,
            "Percentile Rank vs Top-Five League Players in their Position for LAST 365 DAYS",
            size=13,
            ha="center", color="#ffffff"
        )

        # add credits
        CREDIT_2 = "inspired by: @Worville, @FootballSlices, @somazerofc & @Soumyaj15209314"
        CREDIT_3 = "Automated By @Regmi38"

        fig.text(
            0.99, 0.08, f"\n{CREDIT_2}\n{CREDIT_3}", size=15, color="#ffffff",
            ha="right"
        )

        # add text
        fig.text(
            0.23, 0.9," Standard        Passing        Possession         Defense", size=18, color="#ffffff"
        )

        # add rectangles
        fig.patches.extend([
            plt.Rectangle(
                (0.205, 0.9), 0.025, 0.0196, fill=True, color="#bbEE90",
                transform=fig.transFigure, figure=fig
            ),
            plt.Rectangle(
                (0.365, 0.9), 0.025, 0.0196, fill=True, color="#FF93ff",
                transform=fig.transFigure, figure=fig
            ),
            plt.Rectangle(
                (0.505, 0.9), 0.025, 0.0196, fill=True, color="#FFCCCB",
                transform=fig.transFigure, figure=fig
            ),
            plt.Rectangle(
                (0.695, 0.9), 0.025, 0.0196, fill=True, color="#87CEEB",
                transform=fig.transFigure, figure=fig
            ),
        ])

        # add image
        ax_image = add_image(
            masked_img, fig, left=0.472, bottom=0.457, width=0.086, height=0.08, zorder= -1
        )

        plt.savefig(object.name() + '@my_plot.png', format='png')
        return { "success" : 1, "res" : {}, "error_string" : "" }

    def shot_map(self, object, params):
        object_type = str(type(object))
        if( "Player" not in object_type ):
            return { "success" : 0, "res" : {}, "error_string" : "Error: Only Player objects can be used to generate shot maps" }

        player = object
        shots = player.shots_over_season()
        shot_data = player.analyze_shots(shots)

        # create a subplot with 2 rows and 1 column
        fig = plt.figure(figsize=(8, 12))
        fig.patch.set_facecolor(self.primary_color)

        # Top row for the team names and score
        # [left, bottom, width, height]
        ax1 = fig.add_axes([0, 0.7, 1, .2])
        ax1.set_facecolor(self.primary_color)
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)

        ax1.text(
            x=0.5, 
            y=.85, 
            s=player.first_name + " " + player.last_name, 
            fontsize=20, 
            fontweight='bold', 
            color='white', 
            ha='center'
        )
        ax1.text(
            x=0.5, 
            y=.7, 
            s=f'All shots in the Premier League 2022-23', 
            fontsize=14,
            fontweight='bold',
            color='white', 
            ha='center'
        )
        ax1.text(
            x=0.25, 
            y=0.5, 
            s=f'Low Quality Chance', 
            fontsize=12, 
            color='white', 
            ha='center'
        )

        # add a scatter point between the two texts
        ax1.scatter(
            x=0.37, 
            y=0.53, 
            s=100, 
            color=self.primary_color, 
            edgecolor='white', 
            linewidth=.8
        )
        ax1.scatter(
            x=0.42, 
            y=0.53, 
            s=200, 
            color=self.primary_color, 
            edgecolor='white', 
            linewidth=.8
        )
        ax1.scatter(
            x=0.48, 
            y=0.53, 
            s=300, 
            color=self.primary_color, 
            edgecolor='white', 
            linewidth=.8
        )
        ax1.scatter(
            x=0.54, 
            y=0.53, 
            s=400, 
            color=self.primary_color, 
            edgecolor='white', 
            linewidth=.8
        )
        ax1.scatter(
            x=0.6, 
            y=0.53, 
            s=500, 
            color=self.primary_color, 
            edgecolor='white', 
            linewidth=.8
        )

        ax1.text(
            x=0.75, 
            y=0.5, 
            s=f'High Quality Chance', 
            fontsize=12, 
            color='white', 
            ha='center'
        )

        ax1.text(
            x=0.45, 
            y=0.27, 
            s=f'Goal', 
            fontsize=10, 
            color='white', 
            ha='right'
        )
        ax1.scatter(
            x=0.47, 
            y=0.3, 
            s=100, 
            color='red', 
            edgecolor='white', 
            linewidth=.8,
            alpha=.7
        )

        ax1.scatter(
            x=0.53, 
            y=0.3, 
            s=100, 
            color=self.primary_color, 
            edgecolor='white', 
            linewidth=.8
        )

        ax1.text(
            x=0.55, 
            y=0.27, 
            s=f'No Goal', 
            fontsize=10, 
            color='white', 
            ha='left'
        )

        ax1.set_axis_off()

        ax2 = fig.add_axes([.05, 0.25, .9, .5])
        ax2.set_facecolor(self.primary_color)

        self.pitch.draw(ax=ax2)

        # create a scatter plot at y 100 - average_distance
        ax2.scatter(
            x=90, 
            y=shot_data["avg_shot_distance"].value, 
            s=100, 
            color='white',  
            linewidth=.8
        )
        # create a line from the bottom of the pitch to the scatter point
        ax2.plot(
            [90, 90], 
            [100, shot_data["avg_shot_distance"].value], 
            color='white', 
            linewidth=2
        )

        # Add a text label for the average distance
        ax2.text(
            x=90, 
            y=shot_data["avg_shot_distance"].value - 4, 
            s=f'Average Distance\n{shot_data["avg_actual_shot_distance"].value:.1f} yards', 
            fontsize=10, 
            color='white', 
            ha='center'
        )


        for x in shots:
            self.pitch.scatter(
                float(x['X']) * 100, 
                float(x['Y']) * 100, 
                s=300 * float(x['xG']), 
                color='red' if x['result'] == 'Goal' else self.primary_color, 
                ax=ax2,
                alpha=.7,
                linewidth=.8,
                edgecolor='white'
            )
            
        ax2.set_axis_off()

        # add another axis for the stats
        ax3 = fig.add_axes([0, .2, 1, .05])
        ax3.set_facecolor(self.primary_color)
        ax3.set_xlim(0, 1)
        ax3.set_ylim(0, 1)

        ax3.text(
            x=0.25, 
            y=.5, 
            s='Shots', 
            fontsize=20, 
            fontweight='bold', 
            color='white', 
            ha='left'
        )

        ax3.text(
            x=0.25, 
            y=0, 
            s=f'{shot_data["shots"].value}', 
            fontsize=16, 
            color='red', 
            ha='left'
        )

        ax3.text(
            x=0.38, 
            y=.5, 
            s='Goals', 
            fontsize=20, 
            fontweight='bold', 
            color='white', 
            ha='left'
        )

        ax3.text(
            x=0.38, 
            y=0, 
            s=f'{shot_data["goals"].value}', 
            fontsize=16, 
            color='red', 
            ha='left'
        )

        ax3.text(
            x=0.53, 
            y=.5, 
            s='xG', 
            fontsize=20, 
            fontweight='bold', 
            color='white', 
            ha='left'
        )

        ax3.text(
            x=0.53, 
            y=0, 
            s=f'{shot_data["xg"].value:.2f}', 
            fontsize=16, 
            color='red', 
            ha='left'
        )

        ax3.text(
            x=0.63, 
            y=.5, 
            s='xG/Shot', 
            fontsize=20, 
            fontweight='bold', 
            color='white', 
            ha='left'
        )

        ax3.text(
            x=0.63, 
            y=0, 
            s=f'{shot_data["xg_per_shot"].value:.2f}', 
            fontsize=16, 
            color='red', 
            ha='left'
        )

        ax3.set_axis_off()

        file_name = player.first_name + "_" + player.last_name + "_shots.png"
        plt.savefig(file_name, format="png", bbox_inches="tight")
        return { "success" : 1, "res" : {}, "error_string" : "" }

    def plot_statistics(self, objs, stats_names, params = None):
        color = self.secondary_color
        if( params and "color" in params):
            color = params["color"]
            
        has_obj_highlights = 0
        highlight_color = self.tertiary_color
        obj_highlight = []
        if(params and "highlight" in params):
            if( "objects" in params["highlight"] and len(params["highlight"]["objects"]) > 0):
                obj_highlight = [ str(obj.id) for obj in params["highlight"]["objects"]]
                has_obj_highlights = 1
            if("color" in params["highlight"]):
                highlight_color = params["highlight"]["color"]
            else:
                highlight_color = self.highlight_color

        x_stat = stats_names[0]
        y_stat = stats_names[1]
        z_stat = None
        if(len(stats_names) > 2):
            z_stat = stats_names[2]
            
        stats = []
        for obj in objs:
            if("Player" in str(type(obj)) or "Team" in str(type(obj))):
                stat = { "object" : obj }

                if(x_stat == "Market Value"):
                    stat[x_stat] = obj.market_value()
                else:
                    val = obj.statistic(x_stat)
                    if(str(type(val)) == "<class 'int'>"):
                        stat[x_stat] = 0
                    else:
                        stat[x_stat] = val.value

                if(y_stat == "Market Value"):
                    stat[y_stat] = obj.market_value()
                else:
                    val = obj.statistic(y_stat)
                    if(str(type(val)) == "<class 'int'>"):
                        stat[y_stat] = 0
                    else:
                        stat[y_stat] = val.value

                if(z_stat):
                    if(z_stat == "Market Value"):
                        stat[z_stat] = obj.market_value()
                    else:
                        val = obj.statistic(z_stat)
                        if(str(type(val)) == "<class 'int'>"):
                            stat[z_stat] = 0
                        else:
                            stat[z_stat] = val.value

                stats.append(stat)
            
        x = []
        y = []
        z = []
        c = []
        labels = []
        to_highlight = []
        idx = 0
        for stat in stats:
            if( stat[x_stat] and stat[y_stat] ):
                if has_obj_highlights:
                    if(str(stat["object"].id) in obj_highlight):
                        c.append(highlight_color)
                        to_highlight.append(idx)
                    else:
                        c.append(color)
                else:
                    c.append(color)

                x.append(stat[x_stat])
                y.append(stat[y_stat])
                idx += 1
                labels.append(stat["object"].name())
                if z_stat:
                    z.append(stat[z_stat])

        
        if(len(z) == 0):
            z = None
        else:
            z = normalize(z)

        if(params and "highlight" in params):
            if("kmeans" in params["highlight"]):
                c = kmeans(x, y, params["highlight"]["kmeans"])
            else:
                if("max" in params["highlight"]):
                    idx = get_max_idx(x, y)
                    c[idx] = highlight_color
                    to_highlight.append(idx)
                if("min" in params["highlight"]):
                    idx = get_min_idx(x, y)
                    c[idx] = highlight_color
                    to_highlight.append(idx)
                if("median" in params["highlight"]):
                    idx = get_median_idx(x, y)
                    c[idx] = highlight_color
                    to_highlight.append(idx)
                if("top_n" in params["highlight"]):
                    idxs = get_top_n_idx(x, y, params["highlight"]["top_n"])
                    for idx in idxs:
                        c[idx] = highlight_color
                        to_highlight.append(idx)
                if("stat_top_n" in params["highlight"]):
                    n = params["highlight"]["stat_top_n"]["n"]
                    stat = params["highlight"]["stat_top_n"]["stat"]
                    stats = []
                    if(stat == x_stat):
                        stats = x
                    elif( stat == y_stat):
                        stats = y
                    idxs = get_stat_top_n_idx(stats, n)
                    for idx in idxs:
                        c[idx] = highlight_color
                        to_highlight.append(idx)
                if("top_quartile" in params["highlight"]):
                    idxs = get_top_quartile_idx(x, y)
                    for idx in idxs:
                        c[idx] = highlight_color
                        to_highlight.append(idx)
                
        if(params and "title" not in params):
            params["title"] = x_stat + " vs " + y_stat

        self.__set_up_vis(params)

        self.ax2.scatter(x, y, c=c, marker='o', facecolors='none', s=z, edgecolors=self.tertiary_color, linewidth=.75)

        if( params and "label_highlights" in params and "kmeans" not in params):
            for i, text in enumerate(labels):
                if i in to_highlight:
                    self.ax2.annotate(text, (x[i], y[i]), c=self.tertiary_color, xytext=(5, 5), textcoords='offset points')

        #X Axis
        x_label = x_stat
        if( params and "x_label" in params):
            x_label = params["x_label"]
        self.ax2.set_xlabel(x_label)

        #Y Axis
        y_label = y_stat
        if( params and "y_label" in params):
            y_label = params["y_label"]
        self.ax2.set_ylabel(y_label)

        #Filename
        if( params and "filename" not in params):
            params["filename"] = x_stat + "_vs_" + y_stat + ".png"

        self.__output_vis(params)

        return { "success" : 1, "res" : {}, "error_string" : "" }
