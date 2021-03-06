# -*- Mode: Python; coding: utf-8; indent-tabs-mode: s; tab-width: 4 -*-
#
# Copyright (C) 2014 Amir Mohammadi <183.amir@gmail.com>
#
# Gahshomar is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Gahshomar is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
from gettext import gettext as _
import logging
logger = logging.getLogger(__name__)

from gi.repository import Gtk, GLib, Gio

from . import khayyam
from .calendar import PersianCalendar, GeorgianCalendar, \
    add_months, add_years
from . import log, calendar


class DayWidget(Gtk.Box):
    """docstring for DayWidget"""
    @log
    def __init__(self, date=None, date_format=None, app=None):
        super().__init__()
        self.date = date
        self.date_format = date_format
        self.app = app
        self.app.handler.updateables.append(self)

        self.ui = Gtk.Builder()
        self.ui.add_from_resource('/org/gahshomar/Gahshomar/day-widget.ui')
        self.pack_start(self.ui.get_object('DayWidget'), True, True, 0)

        self.update()
        # self.show_all()

    @log
    def update(self, date=None, **kwargs):
        if date is None:
            date = self.date
        self.date = self.get_date(date)
        # change the label
        text = calendar.glib_strftime(self.date_format, self.date)
        # self.ui.get_object('DayWidgetLabel').set_label(_(text))
        self.ui.get_object('DayWidgetLabel').set_markup(
            "<span size='large'>"+text+'</span>')
        self.show_all()


class PersianDayWidget(DayWidget, PersianCalendar):
    """docstring for PersianDayWidget"""
    @log
    def __init__(self, date=None, app=None):
        self.settings = Gio.Settings.new('org.gahshomar.Gahshomar')
        try:
            self.date_format = str(
                self.settings.get_value('persian-date-format'))
            self.date_format = self.date_format.replace("'", "")
        except Exception:
            logger.exception(Exception)
            self.date_format = _('%A، %d %B %Y')
            self.settings.set_value('persian-date-format',
                                    GLib.Variant.new_string(self.date_format))
        # logger.debug((type(self.date_format), self.date_format))
        PersianCalendar.__init__(self, date)
        DayWidget.__init__(self, self.date, self.date_format, app)


class GeorgianDayWidget(DayWidget, GeorgianCalendar):
    """docstring for GeorgianDayWidget"""
    @log
    def __init__(self, date=None, app=None):
        self.settings = Gio.Settings.new('org.gahshomar.Gahshomar')
        try:
            self.date_format = str(
                self.settings.get_value('georgian-date-format'))
            self.date_format = self.date_format.replace("'", "")
        except Exception:
            logger.exception(Exception)
            self.date_format = _('%A, %d %B %Y')
            self.settings.set_value('georgian-date-format',
                                    GLib.Variant.new_string(self.date_format))
        GeorgianCalendar.__init__(self, date)
        DayWidget.__init__(self, self.date, self.date_format, app)


class MonthsWidget(Gtk.Box):
    """docstring for MonthsWidget"""
    @log
    def __init__(self, date=None, rtl=None, app=None):
        super().__init__()
        self.date = date
        self.rtl = rtl
        self.app = app
        self.app.handler.updateables.append(self)

        self.ui = Gtk.Builder()
        self.ui.add_from_resource('/org/gahshomar/Gahshomar/months-widget.ui')
        self.pack_start(self.ui.get_object('MonthsWidget'), True, True, 0)

        self.grid = self.ui.get_object('MonthsGrid')
        self.button_list = []
        for i, month in enumerate(self.get_months()):
            if self.rtl:
                if i % 3 == 0:
                    j = i + 3
                elif i % 3 == 1:
                    j = i + 1
                else:
                    j = i - 1
            else:
                j = i + 1
            button_name = 'button{}'.format(j)
            button = self.ui.get_object(button_name)
            logger.debug((button_name, button, i, j))
            self.button_list.append((button, month, i+1))
            button.connect("clicked",
                           self.month_button_pressed, i+1)

        self.update()

    @log
    def update(self, date=None, **kwargs):
        if date is None:
            date = self.date
        self.date = self.get_date(date)
        for button, month, i in self.button_list:
            button.set_label(month)
            if i == self.date.month:
                button.set_relief(Gtk.ReliefStyle.HALF)
                self.grid.set_focus_child(button)
            else:
                button.set_relief(Gtk.ReliefStyle.NONE)
        self.show_all()

    @log
    def month_button_pressed(self, *args):
        month = args[-1]
        date = add_months(self.date, month - self.date.month)
        self.app.handler.update_everything(date=date)
        try:
            self.get_parent().hide()
        except Exception:
            logger.exception(Exception)


class PersianMonthsWidget(MonthsWidget, PersianCalendar):
    """docstring for PersianMonthsWidget"""
    @log
    def __init__(self, date=None, rtl=True, app=None):
        PersianCalendar.__init__(self, date)
        MonthsWidget.__init__(self, self.date, rtl, app)


class GeorgianMonthsWidget(MonthsWidget, GeorgianCalendar):
    """docstring for GeorgianMonthsWidget"""
    @log
    def __init__(self, date=None, rtl=False, app=None):
        GeorgianCalendar.__init__(self, date)
        MonthsWidget.__init__(self, self.date, rtl, app)


class CalendarWidget(Gtk.Box):
    """docstring for CalendarWidget"""
    @log
    def __init__(self, date=None, rtl=None, app=None):
        super().__init__()
        self.date = date
        self.rtl = rtl
        self.app = app
        self.app.handler.updateables.append(self)

        self.ui = Gtk.Builder()
        self.ui.add_from_resource('/org/gahshomar/Gahshomar/calendar-widget.ui')
        calendar_widget = self.ui.get_object('CalendarWidget')
        self.pack_start(calendar_widget, True, True, 0)

        self.MonthMenuButton = self.ui.get_object('MonthMenuButton')
        self.MonthMenuButton.set_size_request(150, -1)
        self.MonthMenuButton.connect('toggled', self.display_months)
        self.MonthLabel = self.ui.get_object('MonthLabel')
        try:
            self.popover = Gtk.Popover.new(self.MonthMenuButton)
            self.MonthMenuButton.set_popover(self.popover)
            self.popover.add(self.months_widget)
        except AttributeError:
            logger.warn(_('You need at least Gtk 3.12 for cool ui features!'))
            # create a button
            self.MonthButton = Gtk.Button(relief=Gtk.ReliefStyle.NORMAL)
            self.MonthButton.set_size_request(150, -1)
            self.MonthLabel = Gtk.Label()
            self.MonthButton.set_image(self.MonthLabel)
            self.MonthButton.connect('clicked', self.display_months)
            # remove the menu button
            self.ui.get_object('MonthYearHeader').remove(self.MonthMenuButton)
            self.MonthMenuButton.destroy()
            self.MonthMenuButton = None
            # add button instead
            self.ui.get_object('MonthYearHeader').pack_start(self.MonthButton,
                                                             False, False, 0)
            self.popover = Gtk.Window(
                transient_for=self.app._window,
                window_position=Gtk.WindowPosition.MOUSE,
                modal=True,
                decorated=False)
            self.popover.add(self.months_widget)

        self.YearEntry = self.ui.get_object('YearEntry')
        self.YearEntry.set_alignment(0.5)
        self.YearEntry.connect("icon-press", self.year_arrow_pressed)
        self.YearEntry.connect('activate', self.year_entered)

        rtl = -1 if self.rtl else 1
        self.week_days = self.get_week_days()[::rtl]

        self.days_button_list = []
        for i in range(1, 43):
            button = self.ui.get_object('button{}'.format(i))
            self.days_button_list.append([button, None])

        self.update()

    @log
    def update(self, date=None, **kwargs):
        if date is None:
            date = self.date
        self.date = self.get_date(date)

        month_label = self.get_months()[self.date.month-1]
        self.MonthLabel.set_label(month_label)

        self.YearEntry.set_text(calendar.glib_strftime(_('%Y'), self.date))

        self.setup_weekdays()

        self.show_all()
        self.setup_days_grid()

    @log
    def setup_days_grid(self):
        self.gen_grid_mat()
        for button, __ in self.days_button_list:
            button.hide()
        for j, row in enumerate(self.grid_mat):
            for i, (date, day) in enumerate(row):
                if date.month == self.date.month:
                    text = '<span fgcolor="black">{}</span>'
                else:
                    text = '<span fgcolor="gray">{}</span>'
                text = text.format(day)
                button, sig_id = self.days_button_list[j * 7 + i]
                label = Gtk.Label()
                label.set_markup(text)
                button.set_label('')
                button.set_always_show_image(True)
                button.set_image(label)
                button.set_relief(Gtk.ReliefStyle.NONE)
                if date == self.date:
                    button.set_relief(Gtk.ReliefStyle.HALF)
                if sig_id is not None:
                    button.disconnect(sig_id)
                sig_id = button.connect("clicked",
                                        self.date_button_pressed, (i, j, date))
                self.days_button_list[j * 7 + i][1] = sig_id
                button.show()

    @log
    def setup_weekdays(self):
        for i, (week_day, tooltip) in enumerate(self.week_days):
            if self.rtl:
                j = i + 1
            else:
                j = i + 1
            label = self.ui.get_object('WeekDay{}'.format(j))
            label.set_markup(
                "<span foreground='#4A90D9'>" +  # background='#4A90D9'
                week_day + '</span>')
            label.set_tooltip_markup(tooltip)

    @log
    def date_button_pressed(self, *args):
        date = args[-1][-1]
        self.app.handler.update_everything(date=date)

    @log
    def year_entered(self, yearEntry):
        year = yearEntry.get_text()
        try:
            year = int(year)
            self.date = self.date.replace(year=year)
        except Exception:
            logger.exception(Exception)
        self.app.handler.update_everything(date=self.date)

    @log
    def year_arrow_pressed(self, year_entry, icon_pos, event):
        if icon_pos == Gtk.EntryIconPosition.PRIMARY:
            date = add_years(self.date, -1)
        else:
            date = add_years(self.date, 1)
        self.app.handler.update_everything(date=date)

    @log
    def display_months(self, *args):
        if self.MonthMenuButton is not None:
            if self.MonthMenuButton.get_active():
                self.popover.show_all()
            else:
                self.popover.hide()
        else:
            self.popover.show_all()

    #     win = Gtk.Window(Gtk.WindowType.TOPLEVEL)  # POPUP or TOPLEVEL
    #     win.set_transient_for(self.parent)
    #     months = self.MonthWidget(date)
    #     win.add(months)
    #     win.set_position(Gtk.WindowPosition.MOUSE)
    #     win.set_decorated(False)
    #     win.connect('focus-out-event', self.destroy_months_win)
    #     self.month_widget = months
    #     self.month_widget_win = win
    #     self.connect_month_buttons()
    #     win.show_all()

    # def destroy_months_win(self, *args):
    #     self.month_widget_win.destroy()

    # def connect_month_buttons(self):
    #     months = self.month_widget
    #     button_list = months.grid.button_list
    #     for button, _, i in button_list:
    #         button.connect("clicked",
    #                        self.month_button_pressed, i, months.date)

    # def month_button_pressed(self, *args):
    #     month, date = args[-2:]
    #     date = add_months(date, month - date.month)
    #     date = date_to_georgian(date)
    #     self.month_widget_win.close()
    #     self.app.handler.update_everything(date=date)


class PersianCalendarWidget(CalendarWidget, PersianCalendar):
    """docstring for PersianCalendarWidget"""
    @log
    def __init__(self, date=None, rtl=True, app=None):
        logger.debug('init PersianCalendar')
        PersianCalendar.__init__(self, date)
        logger.debug('init PersianMonthsWidget')
        self.months_widget = PersianMonthsWidget(self.date, rtl, app)
        logger.debug('init CalendarWidget')
        CalendarWidget.__init__(self, self.date, rtl, app)
        logger.debug('CalendarWidget loaded')

    @log
    def year_arrow_pressed(self, year_entry, icon_pos, event):
        old_year = self.date.year
        if icon_pos == Gtk.EntryIconPosition.PRIMARY:
            date = add_years(self.date, -1)
            date = khayyam.JalaliDate.from_date(date.to_date())
            while old_year == date.year:
                date -= datetime.timedelta(days=1)
        else:
            date = add_years(self.date, 1)
            date = khayyam.JalaliDate.from_date(date.to_date())
            while date.year - old_year > 1:
                date -= datetime.timedelta(days=1)
        self.app.handler.update_everything(date=date)


class GeorgianCalendarWidget(CalendarWidget, GeorgianCalendar):
    """docstring for GeorgianCalendarWidget"""
    @log
    def __init__(self, date=None, rtl=False, app=None):
        GeorgianCalendar.__init__(self, date)
        self.months_widget = GeorgianMonthsWidget(self.date, rtl, app)
        CalendarWidget.__init__(self, self.date, rtl, app)
