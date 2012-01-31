# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
#
# This file is part of Case Conductor.
#
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
URLconf for running tests

"""
from django.conf.urls.defaults import patterns, url



urlpatterns = patterns(
    "cc.view.runtests.views",

    url("^$", "select", name="runtests"),
    url("^environment/(?P<run_id>\d+)/$",
        "set_environment",
        name="runtests_environment"),
    url("^run/(?P<run_id>\d+)/$", "run", name="runtests_run"),

    # finder -----------------------------------------------------------------
    url(
        "^_finder/environments/(?P<run_id>\d+)/$",
        "finder_environments",
        name="runtests_finder_environments")

)