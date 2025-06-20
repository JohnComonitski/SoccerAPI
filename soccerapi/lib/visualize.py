from datetime import datetime
from .utils import *
from ..obj.player import Player
from ..obj.team import Team
from urllib.request import urlopen
from PIL import Image, ImageDraw, ImageOps
from mplsoccer import VerticalPitch, PyPizza, FontManager, add_image
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D
from matplotlib.path import Path
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import Polygon
import requests
from io import BytesIO

class Visualize:
    r"""The Visualize object. This class is designed to take in Soccer API 
    objects and a series of parameters and generate visualizations.   
    """
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

    def __radar_factory(self, num_vars, frame='circle'):
        """
        Create a radar chart with `num_vars` Axes.

        This function creates a RadarAxes projection and registers it.

        Parameters
        ----------
        num_vars : int
            Number of variables for radar chart.
        frame : {'circle', 'polygon'}
            Shape of frame surrounding Axes.

        """
        # calculate evenly-spaced axis angles
        theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)
        tertiary_color = self.tertiary_color

        class RadarTransform(PolarAxes.PolarTransform):

            def transform_path_non_affine(self, path):
                # Paths with non-unit interpolation steps correspond to gridlines,
                # in which case we force interpolation (to defeat PolarTransform's
                # autoconversion to circular arcs).
                if path._interpolation_steps > 1:
                    path = path.interpolated(num_vars)
                return Path(self.transform(path.vertices), path.codes)

        class RadarAxes(PolarAxes):

            name = 'radar'
            PolarTransform = RadarTransform

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                # rotate plot such that the first axis is at the top
                self.set_theta_zero_location('N')

            def fill(self, *args, closed=True, **kwargs):
                """Override fill so that line is closed by default"""
                return super().fill(closed=closed, *args, **kwargs)

            def plot(self, *args, **kwargs):
                """Override plot so that line is closed by default"""
                lines = super().plot(*args, **kwargs)
                for line in lines:
                    self._close_line(line)

            def _close_line(self, line):
                x, y = line.get_data()
                # FIXME: markers at x[0], y[0] get doubled-up
                if x[0] != x[-1]:
                    x = np.append(x, x[0])
                    y = np.append(y, y[0])
                    line.set_data(x, y)

            def set_varlabels(self, labels):
                self.set_thetagrids(np.degrees(theta), labels, color=tertiary_color, fontfamily='Trebuchet MS')
                for tick in self.xaxis.get_ticklabels():
                    tick.set_color(tertiary_color)
                    tick.set_fontfamily('Trebuchet MS')
                for tick in self.yaxis.get_ticklabels():
                    tick.set_color(tertiary_color)
                    tick.set_fontfamily('Trebuchet MS')

            def _gen_axes_patch(self):
                # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
                # in axes coordinates.
                if frame == 'circle':
                    return Circle((0.5, 0.5), 0.5)
                elif frame == 'polygon':
                    return RegularPolygon((0.5, 0.5), num_vars,
                                        radius=.5, edgecolor=tertiary_color)
                else:
                    raise ValueError("Unknown value for 'frame': %s" % frame)

            def _gen_axes_spines(self):
                if frame == 'circle':
                    return super()._gen_axes_spines()
                elif frame == 'polygon':
                    # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                    spine = Spine(axes=self,
                                spine_type='circle',
                                path=Path.unit_regular_polygon(num_vars))
                    spine.set_color(tertiary_color)
                    # unit_regular_polygon gives a polygon of radius 1 centered at
                    # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                    # 0.5) in axes coordinates.
                    spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                        + self.transAxes)
                    return {'polar': spine}
                else:
                    raise ValueError("Unknown value for 'frame': %s" % frame)

        register_projection(RadarAxes)
        return theta

    def __set_up_vis(self, params):
        plt.clf()
        width = 8
        height = 9
        if "height" in params:
            height = params["height"]

        #Title
        title = ''
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

        ax2 = None
        if( "type" in params and params["type"] == "radar" ):
            ax2 = fig.add_axes([0, 0.05, 1, .8], projection='radar')
        else:
            ax2 = fig.add_axes([0, 0.05, 1, .8])
            

            plt.grid(True, alpha=0.2, color=self.tertiary_color)
            plt.gca().spines['top'].set_visible(False)
            plt.gca().spines['right'].set_visible(False)

            ax2.spines['top'].set_color(self.tertiary_color)
            ax2.spines['right'].set_color(self.tertiary_color)
            ax2.spines['left'].set_color(self.tertiary_color)
            ax2.spines['bottom'].set_color(self.tertiary_color)

            #X Axis
            ax2.tick_params(axis='x', colors=self.tertiary_color, labelfontfamily='Trebuchet MS')
            ax2.set_xlabel("", c=self.tertiary_color, fontname='Trebuchet MS', fontsize=12, fontweight='bold')

            #Y Axis
            ax2.tick_params(axis='y', colors=self.tertiary_color, labelfontfamily='Trebuchet MS')
            ax2.set_ylabel("", c=self.tertiary_color, fontname='Trebuchet MS', fontsize=12, fontweight='bold')
        ax2.set_facecolor(self.primary_color)
        
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

        self.ax1 = ax1
        self.ax2 = ax2
        self.ax3 = ax3
        self.fig = fig

    def __output_vis(self, params):
        plt.savefig(params["filename"], format="png", bbox_inches="tight")

    def __get_stat(self, stat, obj, year=None):
        if(stat == "Market Value"):
            return obj.market_value()
        else:
            val = obj.statistic(stat, year)
            
            if(str(type(val)) == "<class 'int'>"):
                return 0
            else:
                return val.value

    def __get_img(self, obj):
        profile = obj.profile()
        url = ""
        round_edges = 0
        if "logo" in profile:
            url = profile["logo"]
        elif "photo" in profile:
            round_edges = 1
            url = profile["photo"]
        if(url):
            response = requests.get(url)
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            if round_edges:
                stroke_width = 5
                stroke_color = self.secondary_color
                size = min(img.size)
                img = ImageOps.fit(img, (size, size), centering=(0.5, 0.5))

                # Create mask for the circle
                mask = Image.new("L", (size, size), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, size, size), fill=255)

                # Create background with stroke
                stroke_size = size + 2 * stroke_width
                background = Image.new("RGBA", (stroke_size, stroke_size), (0, 0, 0, 0))
                
                stroke_mask = Image.new("L", (stroke_size, stroke_size), 0)
                stroke_draw = ImageDraw.Draw(stroke_mask)
                stroke_draw.ellipse((0, 0, stroke_size, stroke_size), fill=255)

                # Draw stroke circle
                stroke_circle = Image.new("RGBA", (stroke_size, stroke_size), stroke_color)
                background.paste(stroke_circle, (0, 0), stroke_mask)

                # Paste the image in the center with its alpha mask
                background.paste(img, (stroke_width, stroke_width), mask)
                return background
            return img
        return None

    def __add_fan(self, x0, y0, x1, y1, width=0.75, color=None):
        if not color:
            color = self.secondary_color
        
        dx, dy = x1 - x0, y1 - y0
        length = np.hypot(dx, dy)
        if length == 0:
            return  

        dx /= length
        dy /= length

        perp_dx = -dy
        perp_dy = dx

        points = np.array([
            [x0, y0],  # tip
            [x1 + width * perp_dx, y1 + width * perp_dy],
            [x1 - width * perp_dx, y1 - width * perp_dy]
        ])
        poly = Polygon(points, closed=True, color=color, alpha=0.6, linewidth=0)
        self.ax2.add_patch(poly)

    def radar(self, object: ( Player | Team ), params: dict):
        r"""Generate and export a radar chart for a player or team detailing a series of their statistics.

        :param object: the Player or Team to build a radar chart around.
        :type object: ( Player | Team )
        :param params: params dictionary to define the radar chart customization.
        :type params: dict
        """
        object_type = str(type(object))
        if( "Player" not in object_type ):
            return { "success" : 0, "res" : {}, "error_string" : "Error: Only Player and Team objects can be used to generate pizza plots" }

        columns = []
        if "columns" not in params:
            columns = [ 'Non-Penalty Goals', 'Assists', 'Passes', 'Key Passes', 'Touches', 'Take Ons' ]
        else:
            columns = params["columns"]

        object_data = object.scouting_data()
        if( not object_data ):
            return { "success" : 0, "res" : {}, "error_string" : "Error: No Player Scouting data was found." }

        # Data Prep
        stat_keys = []
        values = []
        for key in object_data:
            stat = object_data[key]
            name = stat.name
            if name in columns:
                stat_keys.append(name)
                values.append(stat.percentile)

        # Build Radar
        N = len(stat_keys)
        theta = self.__radar_factory(N, frame='polygon')
        self.__set_up_vis({"type" : "radar"})

        self.ax2.set_varlabels(stat_keys)
        self.ax2.plot(theta, values, c=self.secondary_color, marker='o', label='_nolegend_')
        self.ax2.fill(theta, values, c=self.secondary_color, alpha=0.25)

        # Create a circular mask for the image
        object_img = object.image()
        if( not object_img ):
            object_img = ""

        image = Image.open(urlopen(object_img))
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + image.size, fill=255)

        # Apply the mask to the image
        masked_img = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
        masked_img.putalpha(mask)

        # Add image
        add_image(
            masked_img, self.fig, left=0.455, bottom=0.415, width=0.086, height=0.08, zorder= -1
        )

        #Filename
        if( params and "filename" not in params):
            params["filename"] = object.name().replace(" ", "_") + "_radar" + ".png"

        self.__output_vis(params)
        return { "success" : 1, "res" : {}, "error_string" : "" }

    def shot_map(self, player: Player, params: dict):
        r"""Generate and export a shot map for a player over a season.

        :param object: the Player or Team to build a shot map of.
        :type object: Player
        :param params: params dictionary to define the shot map customization.
        :type params: dict
        """
        object_type = str(type(player))
        if( "Player" not in object_type ):
            return { "success" : 0, "res" : {}, "error_string" : "Error: Only Player objects can be used to generate shot maps" }

        shots = player.shots_over_season()
        shot_data = player.analyze_shots(shots)

        params["height"] = 8
        self.__set_up_vis(params)

        self.ax2.text(
            x=90.0, 
            y=101, 
            s=f'Low Quality Chance', 
            fontsize=12, 
            color=self.tertiary_color, 
            ha='center',
            fontfamily='Trebuchet MS'
        )

        self.ax2.scatter(
            x=78.5, 
            y=101.5, 
            s=100, 
            color=self.primary_color, 
            edgecolor=self.tertiary_color, 
            linewidth=.8
        )

        self.ax2.scatter(
            x=75, 
            y=101.5, 
            s=150, 
            color=self.primary_color, 
            edgecolor=self.tertiary_color, 
            linewidth=.8
        )
        self.ax2.scatter(
            x=71, 
            y=101.5, 
            s=200, 
            color=self.primary_color, 
            edgecolor=self.tertiary_color, 
            linewidth=.8
        )
        self.ax2.scatter(
            x=66.5, 
            y=101.5, 
            s=250, 
            color=self.primary_color, 
            edgecolor=self.tertiary_color, 
            linewidth=.8
        )
        self.ax2.scatter(
            x=62, 
            y=101.5, 
            s=300, 
            color=self.primary_color, 
            edgecolor=self.tertiary_color, 
            linewidth=.8
        )

        self.ax2.text(
            x=49, 
            y=101, 
            s=f'High Quality Chance', 
            fontsize=12, 
            color=self.tertiary_color,  
            fontfamily='Trebuchet MS',
            ha='center'
        )

        self.ax2.text(
            x=13.5, 
            y=101, 
            s=f'Goal', 
            fontsize=10, 
            color=self.tertiary_color, 
            fontfamily='Trebuchet MS',
            ha='right'
        )

        self.ax2.scatter(
            x=11.5,
            y=101.5, 
            s=100, 
            color=self.secondary_color,
            edgecolor=self.tertiary_color, 
            linewidth=.8,
            alpha=.7
        )

        self.ax2.text(
            x=9.5,
            y=101, 
            s=f'No Goal', 
            fontsize=10, 
            color=self.tertiary_color, 
            ha='left',
            fontfamily='Trebuchet MS'
        )

        self.ax2.scatter(
            x=1, 
            y=101.5, 
            s=100, 
            color=self.primary_color, 
            edgecolor=self.tertiary_color, 
            linewidth=.8
        )

        self.pitch.draw(ax=self.ax2)

        for x in shots:
            self.pitch.scatter(
                float(x['X']) * 100, 
                float(x['Y']) * 100, 
                s=300 * float(x['xG']), 
                color=self.secondary_color if x['result'] == 'Goal' else self.primary_color, 
                ax=self.ax2,
                alpha=.7,
                linewidth=.8,
                edgecolor=self.tertiary_color
            )
            
        self.ax2.set_axis_off()

        self.ax2.text(
            x=95, 
            y=64, 
            s='Shots', 
            fontsize=28, 
            fontweight='bold',
            fontfamily='Trebuchet MS',
            color=self.tertiary_color, 
            ha='left'
        )

        self.ax2.text(
            x=95, 
            y=61,
            s=f'{shot_data["shots"].value}', 
            fontsize=20, 
            fontfamily='Trebuchet MS',
            color=self.secondary_color, 
            ha='left'
        )

        self.ax2.text(
            x=70,
            y=64, 
            s='Goals', 
            fontsize=28, 
            fontweight='bold', 
            fontfamily='Trebuchet MS',
            color=self.tertiary_color, 
            ha='left'
        )

        self.ax2.text(
            x=70, 
            y=61,
            s=f'{shot_data["goals"].value}', 
            fontsize=20, 
            color=self.secondary_color, 
            fontfamily='Trebuchet MS',
            ha='left'
        )

        self.ax2.text(
            x=45,
            y=64,
            s='xG', 
            fontsize=28, 
            fontweight='bold', 
            color=self.tertiary_color, 
            fontfamily='Trebuchet MS',
            ha='left'
        )

        self.ax2.text(
            x=45, 
            y=61,
            s=f'{shot_data["xg"].value:.2f}', 
            fontsize=20, 
            color=self.secondary_color, 
            fontfamily='Trebuchet MS',
            ha='left'
        )

        self.ax2.text(
            x=25,
            y=64,
            s='xG/Shot', 
            fontsize=28, 
            fontweight='bold', 
            color=self.tertiary_color, 
            fontfamily='Trebuchet MS',
            ha='left'
        )

        self.ax2.text(
            x=25, 
            y=61,
            s=f'{shot_data["xg_per_shot"].value:.2f}', 
            fontsize=20, 
            color=self.secondary_color, 
            fontfamily='Trebuchet MS',
            ha='left'
        )

        #Filename
        if( params and "filename" not in params):
            params["filename"] = player.first_name + "_" + player.last_name + "_shots.png"

        self.__output_vis(params)
        return { "success" : 1, "res" : {}, "error_string" : "" }

    def plot_statistics(self, objs: list[(Player | Team )], stats_names: list[str], params: ( dict | None ) = None):
        r"""Generate and export a scatter plot for a series of Players or Teams over a given season and set of statistics.

        :param object: the Players or Teams to plot on the scatter plot.
        :type object: list[(Player | Team )]
        :param object: statistics to define the X, Y and (optional) Z axis of the scatter plot.
        :type object: list[str]
        :param params: params dictionary to define the shot map customization.
        :type params: dict
        """
        for obj in objs:
            if("Player" not in str(type(obj)) and "Team" not in str(type(obj))):
                return { "success" : 0, "res" : {}, "error_string" : "Error: Only Player and Teams objects can be used to generate scatter plots" }

        color = self.secondary_color
        if( params and "color" in params):
            color = params["color"]

        if(params and "title" not in params):
            params["title"] = x_stat + " vs " + y_stat

        params["height"] = 9
        self.__set_up_vis(params)

        use_images = 0
        if(params and "use_images" in params):
            use_images = 1

        years = []
        if(params and "years" in params):
            year_end = max(params["years"])
            years.append(year_end)
            year_start = min(params["years"])
            if year_start not in years:
                years.append(year_start)
        else:
            current_date = datetime.now()
            years.append(str([current_date.year]))

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
            
        # Prepping Data
        stats = []
        for obj in objs:
            image = None
            if use_images:
                image = self.__get_img(obj) 
            stat = { "object" : obj, "image" : image }

            if(z_stat):
                stat[z_stat] = self.__get_stat(z_stat, obj, year)

            stat["stats"] = {}
            for year in years:
                    stat["stats"][year] = {}
                    stat["stats"][year][x_stat] = self.__get_stat(x_stat, obj, year)
                    stat["stats"][year][y_stat] = self.__get_stat(y_stat, obj, year)
            stats.append(stat)

        # Consolidate Data into Arrays
        x_start = []
        y_start = []
        has_evolution = 0
        if(len(years) > 1):
            print("has evolution")
            has_evolution = 1
        x_end = []
        y_end = []
        z = []
        c = []
        labels = []
        to_highlight = []
        images = []
        idx = 0
        for obj in stats:
            idx += 1
            labels.append(obj["object"].name())
            images.append(obj["image"])
            if has_obj_highlights:
                if(str(stat["object"].id) in obj_highlight):
                    c.append(highlight_color)
                    to_highlight.append(idx)
                else:
                    c.append(color)
            else:
                c.append(color)

            if z_stat:
                z.append(obj[z_stat])

            end_year = max(years)
            stat = obj["stats"][end_year]

            x_end.append(stat[x_stat])
            y_end.append(stat[y_stat])
            
            if has_evolution:
                start_year = min(years)
                stat = obj["stats"][start_year]
                x_start.append(stat[x_stat])
                y_start.append(stat[y_stat])

        if(len(z) == 0):
            z = None
        else:
            z = normalize(z)

        if(params and "highlight" in params):
            if("kmeans" in params["highlight"]):
                c = kmeans(x_end, y_end, params["highlight"]["kmeans"])
            else:
                if("max" in params["highlight"]):
                    idx = get_max_idx(x_end, y_end)
                    c[idx] = highlight_color
                    to_highlight.append(idx)
                if("min" in params["highlight"]):
                    idx = get_min_idx(x_end, y_end)
                    c[idx] = highlight_color
                    to_highlight.append(idx)
                if("median" in params["highlight"]):
                    idx = get_median_idx(x_end, y_end)
                    c[idx] = highlight_color
                    to_highlight.append(idx)
                if("top_n" in params["highlight"]):
                    idxs = get_top_n_idx(x_end, y_end, params["highlight"]["top_n"])
                    for idx in idxs:
                        c[idx] = highlight_color
                        to_highlight.append(idx)
                if("stat_top_n" in params["highlight"]):
                    n = params["highlight"]["stat_top_n"]["n"]
                    stat = params["highlight"]["stat_top_n"]["stat"]
                    stats = []
                    if(stat == x_stat):
                        stats = x_end
                    elif( stat == y_stat):
                        stats = y_end
                    idxs = get_stat_top_n_idx(stats, n)
                    for idx in idxs:
                        c[idx] = highlight_color
                        to_highlight.append(idx)
                if("top_quartile" in params["highlight"]):
                    idxs = get_top_quartile_idx(x_end, y_end)
                    for idx in idxs:
                        c[idx] = highlight_color
                        to_highlight.append(idx)

        # Plotting Data
        self.ax2.scatter(x_end, y_end, c=c, marker='o', facecolors='none', s=z, edgecolors=self.tertiary_color, linewidth=.75)
        if has_evolution:
            self.ax2.scatter(x_start, y_start, c=c, marker='o', facecolors='none', s=z, edgecolors=self.tertiary_color, linewidth=.75)
            for (x0, y0, x1, y1) in zip(x_start, y_start, x_end, y_end):
                self.__add_fan(x0, y0, x1, y1)

        if(use_images):
            for (x0, y0, img) in zip(x_end, y_end, images):
                if img:
                    im = OffsetImage(img, zoom=.3)
                    ab = AnnotationBbox(im, (x0, y0), frameon=False)
                    self.ax2.add_artist(ab)

        if( params and "label_highlights" in params and "kmeans" not in params):
            for i, text in enumerate(labels):
                if i in to_highlight:
                    self.ax2.annotate(text, (x_end[i], y_end[i]), c=self.tertiary_color, xytext=(5, 5), textcoords='offset points')

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
