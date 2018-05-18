#!/bin/python3

import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point
import argparse
import csv

def create_time_axis():
    time_axis = pg.AxisItem(orientation='bottom')
    time_axis.setLabel(units='S')
    time_axis.enableAutoSIPrefix(True)
    return time_axis

def get_csv(csv_filename):
    all_csv_rows = None
    with open(csv_filename, 'r') as csvfile:
        all_csv_rows = list(csv.reader(csvfile))
    print(all_csv_rows[0:4])
    xs, ys, _ = tuple((zip(*all_csv_rows[2:])))
    return (list(map(float, xs)), list(map(float, ys)))

def plot_data(plot_target, data, skip=1):
    event_plot = pg.PlotCurveItem(x=data[0][::skip],
                                  y=data[1][::skip],
                                    brush=pg.hsvColor(0))
    plot_target.addItem(event_plot)

def start_application(args):
    app = QtGui.QApplication([])
    win = pg.GraphicsWindow()
    win.setWindowTitle('schedplot')
    layout = pg.GraphicsLayout()
    win.setCentralItem(layout)

    data = get_csv(args.in_filename)
    final_event_time = data[0][-1]
    print(final_event_time)

    noscroll_viewbox = pg.ViewBox()
    noscroll_viewbox.setMouseEnabled(x=False, y=False)
    noscroll_viewbox.setLimits(xMin=0, xMax=final_event_time)
    hscroll_viewbox = pg.ViewBox()
    hscroll_viewbox.setMouseEnabled(x=True, y=False)
    plot_upper = layout.addPlot(row=0, col=0,
        axisItems={'bottom': create_time_axis()},
        viewBox=hscroll_viewbox)
    plot_lower = layout.addPlot(row=1, col=0, viewBox=noscroll_viewbox)
    layout.layout.setRowStretchFactor(0, 3)

    region = pg.LinearRegionItem()
    region.setZValue(10)
    region.setBounds((0, final_event_time))
    region.setRegion((0, final_event_time))

    # Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this
    # item when doing auto-range calculations.
    plot_lower.addItem(region, ignoreBounds=True)

    plot_upper.setAutoVisible(y=True)

    plot_data(plot_upper, data)
    plot_data(plot_lower, data, 3)

    # Set up GUI callbacks
    def update():
        region.setZValue(10)
        minX, maxX = region.getRegion()
        plot_upper.setXRange(minX, maxX, padding=0)
        plot_upper.setYRange(-0.5, 1.5, padding=0)

    region.sigRegionChanged.connect(update)

    def updateRegion(window, viewRange):
        rgn = viewRange[0]
        region.setRegion(rgn)

    plot_upper.sigRangeChanged.connect(updateRegion)

    region.setRegion([1, 2])

    ## Start Qt event loop unless running in interactive mode or using pyside.
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


parser = argparse.ArgumentParser(description='Plot and perform metrics on scheduler dumps')

parser.add_argument('in_filename', help='Filename of scheduler dump to process')

if __name__ == '__main__':
    args = parser.parse_args()
    start_application(args)
